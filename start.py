import os
import yaml
import shutil
import argparse
import subprocess

def parse_yaml_file(file_path, replica_set_override=None, is_core=False):
    with open(file_path, 'r') as file:
        yaml_content = file.read()
    parse_yaml(yaml_content, replica_set_override, is_core=is_core)


def parse_core_yaml(core_yaml_path):
    with open(core_yaml_path, 'r') as file:
        core_yaml_content = file.read()
    parse_yaml(core_yaml_content, is_core=True)

def start_service(name):
    print(f"###############{name}##############")
    kubectl_apply_cmd = f"kubectl apply -f {name}"
    os.system(kubectl_apply_cmd)
    print("")


def stop_service(name):
    print(f"###############{name}##############")
    # Use kubectl to delete the deployment and service
    kubectl_apply_cmd = f"kubectl delete -f {name}"
    os.system(kubectl_apply_cmd)
    print("")


#print("=" * 30)
def generate_deployment(service_name, replica_set, image_address, port, ContainerPath, ServiceLocalPath):
    deployment_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: "{service_name}"
  namespace: "{service_name}"
spec:
  selector:
    matchLabels:
      app: "{service_name}"
  replicas: {replica_set}
  template:
    metadata:
      labels:
        app: "{service_name}"
    spec:
      containers:
      - name: "{service_name}"
        image: {image_address}
        ports:
        - containerPort: {port}
        envFrom:
          - configMapRef:
              name: {service_name}-env
        volumeMounts:
        - name: {service_name}-volume
          mountPath: {ContainerPath}
      volumes:
      - name: {service_name}-volume
        hostPath:
          path: {ServiceLocalPath}
"""
    return deployment_yaml

def generate_service(service_name, namespace, port):
    service_yaml = f"""
apiVersion: v1
kind: Service
metadata:
  name: "{service_name}"
  namespace: "{namespace}"
  labels:
    app: "{service_name}"
spec:
  ports:
    - port: {port}
      targetPort: {port}
      protocol: TCP
  selector:
    app: "{service_name}"
  type: NodePort
"""
    return service_yaml

def generate_configmap(service_name, namespace, config_values):
    config_data = {key.replace('_', '-'): value for key, value in config_values.items()}

    config_data_yaml = yaml.dump(config_data, default_flow_style=False)

    indented_config_data_yaml = '\n'.join(f'  {line}' for line in config_data_yaml.splitlines())

    configmap_yaml = f"""
apiVersion: v1
data:
{indented_config_data_yaml}
kind: ConfigMap
metadata:
  name: {service_name}-env
  namespace: "{namespace}"
"""
    return configmap_yaml

def parse_yaml(yaml_string, replica_set_override=None, is_core=False):
    parsed_data = yaml.safe_load(yaml_string)
    services = parsed_data.get("service", {})
    existing_directories = [directory for directory in os.listdir('.') if os.path.isdir(directory)]

    for service_name, service_info in services.items():
        if not is_core and ("image" not in service_info or "name" not in service_info or
                            "port" not in service_info or "ContainerPath" not in service_info or
                            "ServiceLocalPath" not in service_info):
            print(f"Skipping '{service_name}' - Missing mandatory fields 'image', 'name', 'port', 'ContainerPath', or 'ServiceLocalPath'")
            continue

        image_address = service_info.get("image", "")
        name = service_info.get("name", "")
        port = service_info.get("port", "")
        ContainerPath = service_info.get("ContainerPath", "")
        ServiceLocalPath = service_info.get("ServiceLocalPath", "")
        replica_set = service_info.get("ReplicaSet", "")

        #Create directory if not exist
        if name not in existing_directories:
            os.makedirs(name)
        # Set Replicaset value based on --dev
        if replica_set_override is not None:
            replica_set = replica_set_override
        else:
            replica_set = service_info.get("ReplicaSet", "")





        ns = name.lower()  # Using the name as the namespace for simplicity

        # Check if the namespace already exists
        check_ns = f"kubectl get ns {ns} --no-headers --output=name 2>/dev/null"
        try:
            subprocess.check_output(check_ns, shell=True, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError:
            # Namespace doesn't exist
            create_ns = f"kubectl create ns {ns}"
            os.system(create_ns)
            print(f"Namespace '{ns}' created.")
        else:
            # Namespace already exists
            #print(f"Namespace '{ns}' is already available.")
            print("")   







        #Create configmap
        config_values = service_info.get("configmaps", "")
        if config_values:
            configmap_yaml = generate_configmap(name, ns, config_values)
            with open(f"{name}/configmap.yml", "w") as file:
                file.write(configmap_yaml)

        #service
        service_yaml = generate_service(name, ns, port)
        with open(f"{name}/service.yaml", "w") as file:
            file.write(service_yaml)
        
        #Deployment
        deployment_yaml = generate_deployment(name, replica_set, image_address, port, ContainerPath, ServiceLocalPath)
        # Write the generated Deployment YAML content to the deployment.yml file inside the service directory
        with open(f"{name}/deployment.yml", "w") as file:
            file.write(deployment_yaml)

        # Apply the generated Deployment using kubectl apply
        """ kubectl_apply_cmd = f"kubectl apply -f {name}"
        os.system(kubectl_apply_cmd)
        print("=" * 30) """


############################## MAIN ###################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Kubernetes resources.")
    parser.add_argument("--dev", action="store_true", help="Use dev mode (ReplicaSet = 1)")
    parser.add_argument("--prod", action="store_true", help="Use prod mode (ReplicaSet from config)")
    parser.add_argument("--start", help="Start a specific service by name")
    parser.add_argument("--stop", help="Stop a specific service by name")
    parser.add_argument("--core", action="store_true", help="Parse and apply services from core.yaml")
    args = parser.parse_args()

# Determine the replica_set_override value based on the provided arguments
replica_set_override = None
if args.dev:
    replica_set_override = 1
elif args.prod:
    replica_set_override = None  # Keep the default value from the config

if args.core:
    # Use a separate variable for the core configuration file
    core_yaml_path = './core.yaml'
    parse_core_yaml(core_yaml_path)  # Change this line to use parse_core_yaml
else:
    # Call parse_yaml_file with the determined replica_set_override value for config.yaml
    file_path = './config.yaml'
    parse_yaml_file(file_path, replica_set_override)

# Check if the --start argument is provided and start the specified service
    if args.start:
        if args.start == "all":
            # Start all services
            services = yaml.safe_load(open(file_path, 'r'))["service"]
            for service_name in services.keys():
                start_service(service_name)
        else:
            # Start a specific service
            start_service(args.start)

    # Check if the --stop argument is provided and stop the specified service
    if args.stop:
        stop_service(args.stop)