# 4. Set up Pipeline

## Create a workspace

After selecting Dashboard → New Item → Folder, name the item and click the OK button.

If you go to the configuration screen, select Save to create a folder.

![Screen Shot 2021-11-09 at 8.42.13 AM.png](4%20Set%20up%20Pipeline%20cc3aadbe173e441c91f14526c9852e0c/Screen_Shot_2021-11-09_at_8.42.13_AM.png)

![Screen Shot 2021-11-09 at 8.44.27 AM.png](4%20Set%20up%20Pipeline%20cc3aadbe173e441c91f14526c9852e0c/Screen_Shot_2021-11-09_at_8.44.27_AM.png)

## Create a New Pipeline

### Install Kubectl on Work Executor

access to master pod using under command:

```bash
kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/sh
```

Download the latest release with the following command:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

Since you do not have root access to the target system, install kubectl in the ~/.local/bin directory. At this time, check if the home directory is the directory where EBS is mounted.

```bash
chmod +x kubectl
mkdir -p ~/.local/bin/kubectl
mv ./kubectl ~/.local/bin/kubectl
export PATH=$PATH:~/.local/bin/kubectl
```

kubeconfig 설정

### Configure Credentials

![Screen Shot 2021-11-09 at 3.31.30 AM.png](4%20Set%20up%20Pipeline%20cc3aadbe173e441c91f14526c9852e0c/Screen_Shot_2021-11-09_at_3.31.30_AM.png)

Create a 

Jenkinsfile

```bash
node {
  stage('train') {

    withKubeConfig([credentialsId: 'bc1d331a-ed6c-428b-bbbc-d90389d4fb44', serverUrl: 'https://AFF9E22E65B2F8F7264F14346E54BF58.yl4.ap-northeast-2.eks.amazonaws.com']) {
       sh 'curl -LO "https://storage.googleapis.com/kubernetes-release/release/v1.20.5/bin/linux/amd64/kubectl"'  
        sh 'chmod u+x ./kubectl'  
        sh './kubectl get pods'
    }

  }
    
  stage('deploy') {

        withKubeConfig([credentialsId: 'bc1d331a-ed6c-428b-bbbc-d90389d4fb44', serverUrl: 'https://AFF9E22E65B2F8F7264F14346E54BF58.yl4.ap-northeast-2.eks.amazonaws.com']) {
           sh 'curl -LO "https://storage.googleapis.com/kubernetes-release/release/v1.20.5/bin/linux/amd64/kubectl"'  
            sh 'chmod u+x ./kubectl'  
            sh './kubectl get pods'
            sh './kubectl apply -f /var/jenkins_home/eks-mlops/demo/train.yaml'
        }

  }
}
```