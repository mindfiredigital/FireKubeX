import os, yaml, argparse, subprocess
from jinja2 import Template 

def read_file(file_path):
    file = open(file_path,'r')
    content = file.read()
    file.close()
    return content

def namespace_check(namespace):
    check_ns = f"kubectl get ns {namespace} --no-headers --output=name 2>/dev/null"
    try:
        subprocess.check_output(check_ns, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError:
            create_ns = f"kubectl create ns {namespace}"
            os.system(create_ns)
            print(f"Namespace '{namespace}' created.")
    else:
        print(f"Namespace '{namespace}' is already available.")

def generate_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)

def start_service(name):
    print(f"###############{name}##############")
    print("------------------in--------------------")
    kubectl_apply_cmd = f"kubectl apply -f {name}"
    os.system(kubectl_apply_cmd)

def stop_service(name):
    print(f"###############{name}##############")
    # Use kubectl to delete the deployment and service
    kubectl_apply_cmd = f"kubectl delete -f {name}"
    os.system(kubectl_apply_cmd)
    
def generate_deployment(service_info):
    content =read_file('./templates/deployment.jinja')
    template = Template(content)
    rendered_form = template.render(service_info)
    return rendered_form

def generate_service(service_info):
    content = read_file('./templates/service.jinja')
    template = Template(content)
    rendered_form = template.render(service_info)
    return rendered_form

def generate_configmap(service_info, config_values):
    service_info["config_values"] = config_values
    content = read_file('./templates/configMap.jinja')
    template = Template(content)
    rendered_form = template.render(service_info)
    return rendered_form

def generate_secrets(service_info):
    content = read_file('./templates/secrets.jinja')
    template = Template(content)
    rendered_form = template.render(service_info)
    return rendered_form

def generate_hpa(service_info):
    content = read_file('./templates/hpa.jinja')
    template = Template(content)
    rendered_form = template.render(service_info)
    return rendered_form

def parse_yaml(file_path, is_core):
    yaml_string = read_file(file_path)
    parsed_data = yaml.safe_load(yaml_string)
    services = parsed_data.get("service", {})
    service_directory = './services'
    if not os.path.exists(service_directory):
        os.mkdir(service_directory)
    existing_directories = [directory for directory in os.listdir('.') if os.path.isdir(directory)]

    for service_name, service_info in services.items():
        if not is_core and ("image" not in service_info or "name" not in service_info or
                            "port" not in service_info or "volume" not in service_info):
            print(f"Skipping '{service_name}' - Missing mandatory fields 'image', 'name', 'port', 'Volume''")
            continue
        name = service_info.get("name", "")
        namespace = service_info.get("namespace", "")
        replica_set = service_info.get("ReplicaSet", "")
        namespace = namespace.lower() if namespace else (namespace:= "default")
        service_info["namespace"] = namespace
        replica_set = 1 if namespace == 'dev' else (replica_set:= replica_set)
        service_info["ReplicaSet"] = replica_set
        #Create directory if not exist
        if name not in existing_directories:
            os.makedirs(name)
        namespace_check(namespace)

        ##Create configmap
        config_values = service_info.get("configmaps", "")
        if config_values:
            configmap_yaml = generate_configmap(service_info,config_values)
            file_path = (f"{name}/configmap.yml")
            generate_file(file_path,content=configmap_yaml)

        ##service
        service_yaml = generate_service(service_info)
        file_path=(f"{name}/service.yaml")
        generate_file(file_path,content=service_yaml)
        
        ##Deployment
        deployment_yaml = generate_deployment(service_info)
        file_path = f"{name}/deployment.yml"
        generate_file(file_path,content=deployment_yaml)
        
        ##Secrets
        secrets_yaml = generate_secrets(service_info)
        for key in service_info["secrets"].keys():
            value = service_info["secrets"][key]
            encode_base64 = f"echo -n  {value}"
            service_info["secrets"][key] = [os.system(encode_base64)]    
        file_path = f"{name}/secrets.yml"
        generate_file(file_path,content=secrets_yaml)

        ##HPA
        hpa_yaml = generate_hpa(service_info)
        file_path = f"{name}/hpa.yml"
        generate_file(file_path,content=hpa_yaml)

def main():
    parser = argparse.ArgumentParser(description="Generate Kubernetes resources.")
    parser.add_argument("--start", help="Start a specific service by name")
    parser.add_argument("--stop", help="Stop a specific service by name")
    parser.add_argument("--core", action="store_true", help="Parse and apply services from core.yaml")
    parser.add_argument("--harbor", action="store_true", help="setup harbor repository")
    args = parser.parse_args()
    os.system('pip install jinja2')
    if args.core:
        # Use a separate variable for the core configuration file
        core_yaml_path = './core.yaml'
        parse_yaml(core_yaml_path,is_core=True)  # Change this line to use parse_core_yaml
    else:
        # Call parse_yaml_file with the determined replica_set_override value for config.yaml
        file_path = './config.yaml'
        parse_yaml(file_path, is_core=False )

        # Check if the --start argument is provided and start the specified service
        if args.start == "all":
            # Start all services
            services = yaml.safe_load(open(file_path, 'r'))["service"]
            dependent_services=[]
            for service_name in services.keys():
                if "depends_on" in services[service_name]:
                    dependent_services.append(services[service_name]['name'])
                    service_names = services[service_name]['depends_on']
                    for service in service_names:
                        start_service(service)                
                else:
                    os.system('sleep 15')
                    for service in dependent_services:
                        start_service(service)
        else:
            # Start a specific service
            start_service(args.start)
        # Check if the --stop argument is provided and stop the specified service
        if args.stop:
            stop_service(args.stop)
    
        if args.harbor:
           service = 'harbor'
           namespace_check(service)
           start_service(service)
 
if __name__ == "__main__":
    main()

