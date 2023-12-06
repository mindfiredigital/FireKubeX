## Install K3s in Linux

*Steps*
1. To install K3s, just run:
   ```
   curl -sfL https://get.k3s.io | sh -
   ```
   After running this installation :

* The K3s service will be configured to automatically restart after node reboots or if the process crashes or is killed
* Additional utilities will be installed, including kubectl, crictl, ctr, k3s-killall.sh, and k3s-uninstall.sh
* A kubeconfig file will be written to `/etc/rancher/k3s/k3s.yaml` and the kubectl installed by K3s will automatically use it

*NOTE:*
  `To run kubectl with non-root user, run below command`
  ```
mkdir ~/.kube
cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
export KUBECONFIG=~/.kube/config
sudo chmod 664 ~/.kube/config

  ```
  
