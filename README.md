# Kubernetes Resource Generator

This Python application dynamically generates Kubernetes resource files (Deployment, ConfigMap, etc.) based on the configuration provided in a YAML file. It utilizes Jinja templates to streamline the resource creation process.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Usage](#usage)
- [Configuration](#configuration)
- [Examples](#examples)

## Overview

The `start.py` script reads the configuration from the `config.yaml` file and generates Kubernetes resource files for each specified service. With this script, developers can deploy their applications without requiring in-depth knowledge of Kubernetes.

## Requirements

- [X] **Python 3.X**
- [X] **kubectl installed and configured for the target Kubernetes cluster**
- [X] **Dockerfiles** (for the applications you want to deploy)


## Usage

**1: Clone the repository:**

   ```bash
   git clone https://github.com/mindfiredigital/FireKubeX.git
   cd FireKubeX
   ```

**2: Install the required Python dependencies:**

```bash 
pip install -r requirements.txt 
```

**3: Update the config.yaml file**

- Customize the config.yaml file with your desired service configurations.

**4: Run the script:**

```bash 
python3 start.py
```

## Configuration

The config.yaml file contains configurations for each service, specifying details such as image, port, namespace, volume, replicas, configmaps, secrets, tags, and more. Ensure all required fields are correctly filled.

Sample config.yaml:
``` yaml
# YAML
version: 3.2
service:
  mpsetup:
    image: nginx:latest 
    name: mpsetup
    port: 8080
    namespace: Dev
    volume:
      ContainerPath: /tmp
      ServiceLocalPath: /tmp
    ReplicaSet: 2
    configmaps:
      APP_DEBUG: "true"
      APP_ENV: local
      APP_KEY: base64:1Ykb1MNf9qwdUIUpElWUxReKWr+4iL106Z43SuyqSr0=
    secrets:
      username: YWRtaW4=
      password: YWRtaW4xMjM0
    tags: 
      - core
    hpa:
      max_replicas: 5
      cpu_utilization: 10
      stabilization_window_seconds: 300
    depends_on:
      - mpms1
  mpms1:
    image: mpms1:latest 
    name: mpms1 
    port: 8080
    namespace: Dev
    volume:
      ContainerPath: /tmp
      ServiceLocalPath: /tmp
    ReplicaSet: 3
    configmaps:
      APP_DEBUG: "true"
      APP_ENV: local
      APP_KEY: base64:1Ykb1MNf9qwdUIUpElWUxReKWr+4iL106Z43SuyqSr0=
    secrets:
      username: YWRtaW4=
      password: YWRtaW4xMjM0
    hpa:
      max_replicas: 5
      cpu_utilization: 10
      stabilization_window_seconds: 300
    tags: 
      - dev
```


#### `config.yaml` file configuration 

- `version`: The script version (currently 3.2).

- `service`: A dictionary containing information about each application. You can configure multiple applications in this section. For each application, provide the following details:

  - `image`: The Docker image address for the application.
  
  - `name`: The name of the application, which will be used as the namespace in Kubernetes.

  - `port`: The port on which the application should listen.

  - `ContainerPath`: The path within the container where the application files are stored.

  - `ServiceLocalPath`: The local path on the host machine where the application files are stored.

  - `ReplicaSet`: The number of replicas you want for the application (optional).

  - `configmaps`: Configuration settings for the application. You can specify environment variables and their values here.

  - `tags`: Tags or labels for the application (optional).

### `core.yaml`

For core services, you can use a separate `core.yaml` file with the same structure as `config.yaml`. This allows you to configure core services separately.

## Usage

The script provides several command-line options:

- `--start <name>`: Start a specific service by providing its name. You can also use `--start all` to start all services.

- `--stop <name>`: Stop a specific service by providing its name.

- `--core`: Use this option to parse and apply services from `core.yaml`.

## Examples

Running this script is pretty straight forward.

Generate Kubernetes resources based on the provided config.yaml:

```shell
python3 start.py
```
Generate resources for a specific service:

```shell
python start.py --start <service_name>
```

**For starting a specific service**

```shell
python3 start.py --start <service_name>
```

**For starting all services**

```shell
python3 start.py --start all
```
**For Deleting a specific service and components**

```shell
python3 start.py --stop <service_name>
```

**For Deleting all service and components**

```shell
python3 start.py --stop all
```

**For setting up Harbor image repository and components**

```shell
python3 start.py --harbor
```
For more information on available options, run:

```shell
python start.py --help
```

## Notes
- The Dockerfile for each application must be present in the source code repository.

- This script is designed to work with various Kubernetes setups, including both cloud and on-premises clusters.

## Conclusion

This script simplifies the deployment process for developers by abstracting the complexities of Kubernetes. By providing the necessary configuration in the config.yaml file, developers can quickly deploy their applications to a Kubernetes cluster with ease.
Enjoy deploying your applications without the need for in-depth Kubernetes knowledge!
