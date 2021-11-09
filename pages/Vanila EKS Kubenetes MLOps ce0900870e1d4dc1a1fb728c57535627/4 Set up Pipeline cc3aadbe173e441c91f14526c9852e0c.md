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

### **Configure SageMaker Operator**

Create an mlops folder on the mount volume, download the SageMaker Operatior file below and set it up appropriately.

**[Create a TrainingJob Using a Simple YAML File](https://sagemaker.readthedocs.io/en/v1.57.0/amazon_sagemaker_operators_for_kubernetes.html#id119)**

Download the sample YAML file for training using the following command:

```bash
wget https://raw.githubusercontent.com/aws/amazon-sagemaker-operator-for-k8s/master/samples/xgboost-mnist-trainingjob.yaml
```

Edit the `xgboost-mnist-trainingjob.yaml` file to replace the `roleArn` parameter with your `<sagemaker-execution-role>`, and `outputPath` with your S3 bucket that the Amazon SageMaker execution role has write access to. The `roleArn` must have permissions so that Amazon SageMaker can access Amazon S3, Amazon CloudWatch, and other services on your behalf.

**[Configure a HostingDeployment Resource](https://sagemaker.readthedocs.io/en/v1.57.0/amazon_sagemaker_operators_for_kubernetes.html#id154)**

Download the sample YAML file for the hosting deployment job using the following command:

```bash
wget https://raw.githubusercontent.com/aws/amazon-sagemaker-operator-for-k8s/master/samples/xgboost-mnist-hostingdeployment.yaml
```

The `xgboost-mnist-hostingdeployment.yaml` file has the following components that can be edited as required:

- ProductionVariants. A production variant is a set of instances serving a single model. Amazon SageMaker will load-balance between all production variants according to set weights.
- Models. A model is the containers and execution role ARN necessary to serve a model. It requires at least a single container.
- Containers. A container specifies the dataset and serving image. If you are using your own custom algorithm instead of an algorithm provided by Amazon SageMaker, the inference code must meet Amazon SageMaker requirements. For more information, see [Using Your Own Algorithms with Amazon SageMaker](https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html).

### Configure Credentials

**[kubernetes-cli-plugin](https://github.com/jenkinsci/kubernetes-cli-plugin)** generates a `kubeconfig` file based on the parameters that were provided in the build. This file is stored in a temporary file inside the build workspace and the exact path can be found in the `KUBECONFIG` environment variable. `kubectl` automatically picks up the path from this environment variable. Once the build is finished (or the pipeline block is exited), the temporary `kubeconfig` file is automatically removed.

Configure Credentials in the created folder. Once you have kubeconfig set up on the master node, the credential is configured on the jenkins system by default, you can use it or create a credential using the new kubeconfig.

![Screen Shot 2021-11-09 at 9.19.00 AM.png](4%20Set%20up%20Pipeline%20cc3aadbe173e441c91f14526c9852e0c/Screen_Shot_2021-11-09_at_9.19.00_AM.png)

### Create a job into folder

After clicking the Create a job button on the main dashboard, enter an Item name and create a Pipeline.

In the Pipeline section, configure a pipeline in the form of a groovy script.

**Jenkinsfile**

```bash
node {
  stage('train') {
    withKubeConfig([credentialsId: 'bc1d331a-ed6c-428b-bbbc-d90389d4fb44', serverUrl: 'https://AFF9E22E65B2F8F7264F14346E54BF58.yl4.ap-northeast-2.eks.amazonaws.com']) {
        sh 'kubectl apply -f /var/jenkins_home/eks-mlops/demo/train.yaml'
    }

  }
    
  stage('deploy') {
        withKubeConfig([credentialsId: 'bc1d331a-ed6c-428b-bbbc-d90389d4fb44', serverUrl: 'https://AFF9E22E65B2F8F7264F14346E54BF58.yl4.ap-northeast-2.eks.amazonaws.com']) {
            sh 'kubectl apply -f /var/jenkins_home/eks-mlops/demo/deploy.yaml'
        }

  }
}
```