# 3. Set up Jenkins on EKS

When `Jenkins` is deployed as `Helm`, `Pod` is automatically recreated even when the corresponding `Pod` is deleted, but all contents in the previous `Pod` are lost. A 'Persistent Volume' that is completely independent of the 'Life Cycle' of a 'Pod' is needed so that the contents remain even if the 'Pod' is deleted and re-created.

In this article, `EBS` will be used as `Persistent Volume`. Deploy `EBS CSI Driver` to the cluster and set `EBS` to be used as a `Persistent Volume`.

## Install Helm on Amazon EKS

install the binaries with the following commands.

```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh
```

## Amazon EBS CSI driver

### **To deploy the Amazon EBS CSI driver to an Amazon EKS cluster**

Create an IAM policy that allows the CSI driver's service account to make calls to AWS APIs on your behalf. You can view the policy document [on GitHub](https://github.com/kubernetes-sigs/aws-ebs-csi-driver/blob/release-1.3/docs/example-iam-policy.json).

Download the IAM policy document from GitHub.

```bash
curl -o example-iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-ebs-csi-driver/release-1.3/docs/example-iam-policy.json
```

Create the policy. You can change `AmazonEKS_EBS_CSI_Driver_Policy` to a different name, but if you do, make sure to change it in later steps too.

```bash
aws iam create-policy \
    --policy-name AmazonEKS_EBS_CSI_Driver_Policy \
    --policy-document file://example-iam-policy.json
```

Create an IAM role and attach the IAM policy to it. You can use either `eksctl` or the AWS CLI.

Replace *`my-cluster`* with the name of your cluster and *`111122223333`* with your account ID.

```bash
eksctl create iamserviceaccount \
    --name ebs-csi-controller-sa \
    --namespace kube-system \
    --cluster my-cluster \
    --attach-policy-arn arn:aws:iam::111122223333:policy/AmazonEKS_EBS_CSI_Driver_Policy \
    --approve \
    --override-existing-serviceaccounts
```

Retrieve the ARN of the created role and note the returned value for use in a later step.

```bash
aws cloudformation describe-stacks \
    --stack-name eksctl-eks-mlops-addon-iamserviceaccount-kube-system-ebs-csi-controller-sa \
    --query='Stacks[].Outputs[?OutputKey==`Role1`].OutputValue' \
    --output text
```

Apply the manifest

```bash
kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/ecr/?ref=master"
```

```bash
kubectl annotate serviceaccount ebs-csi-controller-sa \
    -n kube-system \
    eks.amazonaws.com/role-arn=arn:aws:iam::846732235403:role/eksctl-eks-mlops-addon-iamserviceaccount-kub-Role1-9JG4DJPZZH30
```

## Deploy Jenkins with Helm

### **Create a namespace**

```bash
kubectl create namespace jenkins
```

### StorageClass & PersistentVolumeClaim

Creates a `StorageClass` with `provisioner=ebs.csi.aws.com` by `apply` the following `yaml` file, and also creates a `PersistentVolumeClaim` that uses the corresponding `StorageClass`.

```yaml
# jenkins-pvc.yml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: jenkins-sc
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jenkins-pvc
  namespace: jenkins
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: jenkins-sc
  resources:
    requests:
      storage: 30Gi
```

### ServiceAccount

Create a 'ServiceAccount' called 'jenkins' so that the 'Jenkins Pod' can interact with the 'API server'.

Apply `jenkins-sa.yaml` to create `ClusterRole`, `ClusterRoleBinding` and `ServiceAccount`.

```yaml
#jenkins-sa.yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jenkins
  namespace: jenkins
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "true"
  labels:
    kubernetes.io/bootstrapping: rbac-defaults
  name: jenkins
rules:
- apiGroups:
  - '*'
  resources:
  - statefulsets
  - services
  - replicationcontrollers
  - replicasets
  - podtemplates
  - podsecuritypolicies
  - pods
  - pods/log
  - pods/exec
  - podpreset
  - poddisruptionbudget
  - persistentvolumes
  - persistentvolumeclaims
  - jobs
  - endpoints
  - deployments
  - deployments/scale
  - daemonsets
  - cronjobs
  - configmaps
  - namespaces
  - events
  - secrets
  verbs:
  - create
  - get
  - watch
  - delete
  - list
  - patch
  - update
- apiGroups:
  - ""
  resources:
  - nodes
  verbs:
  - get
  - list
  - watch
  - update
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "true"
  labels:
    kubernetes.io/bootstrapping: rbac-defaults
  name: jenkins
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: jenkins
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: system:serviceaccounts:jenkins
```

### Define values.yaml

1. To enable persistence, we will create an override file and pass it as an argument to the Helm CLI. Paste the content from [raw.githubusercontent.com/jenkinsci/helm-charts/main/charts/jenkins/values.yaml](https://raw.githubusercontent.com/jenkinsci/helm-charts/main/charts/jenkins/values.yaml) into a YAML formatted file called `jenkins-values.yaml`.
    
    The `jenkins-values.yaml` is used as a template to provide values that are necessary for setup.
    
2. Open the `jenkins-values.yaml` file in your favorite text editor and modify the following:

[default]

- controller.servicePort

```yaml
servicePort: 80
```

- controller.serviceType

```yaml
serviceType: LoadBalancer
# Jenkins controller service annotations
serviceAnnotations: 
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-subnets: subnet-0d8d50653b7935fee,subnet-088cab1b1e8d2966c
```

- persistence.exixtingClaim & persistence.storageClass:

```yaml
existingClaim: jenkins-pvc
```

```yaml
storageClass: jenkins-sc
```

- serviceAccount:

```yaml
serviceAccount:
  create: false
  # The name of the service account is autogenerated by default
  name: jenkins
  annotations: {}
  imagePullSecretName:
```

[Slave pod volume mount]

- agent.workingDir

```yaml
workingDir: "/var/jenkins_home"
```

- agent.volumes & agent.workspaceVolume

```yaml
volumes:
- type: PVC
  claimName: jenkins-pvc
  mountPath: /var/jenkins_home
  readOnly: false
```

```yaml
workspaceVolume:
  type: PVC
  claimName: jenkins-pvc
  readOnly: false
```

1. Now you can install Jenkins by running the `helm install` command and passing it the following arguments:

```bash
helm repo add jenkinsci https://charts.jenkins.io
helm repo update

helm install jenkins -n jenkins -f jenkins-values.yml jenkinsci/jenkins
```

### Associate an IAM role to a jenkins service account

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::<ACCOUNT_ID>:role/<IAM_ROLE_NAME>
```

```bash
kubectl annotate serviceaccount -n <SERVICE_ACCOUNT_NAMESPACE> <SERVICE_ACCOUNT_NAME> \
eks.amazonaws.com/role-arn=arn:aws:iam::<ACCOUNT_ID>:role/<IAM_ROLE_NAME>
```

Delete and re-create any existing pods that are associated with the service account to apply the credential environment variables. The mutating web hook does not apply them to pods that are already running.

```bash
kubectl delete po/jenkins-0 -n jenkins
kubectl get po -n jenkins
```

### Connect to Jenkins Dashboard

check network load balancer dns name on EC2 dashboard.

![Screen Shot 2021-11-09 at 2.34.19 AM.png](3%20Set%20up%20Jenkins%20on%20EKS%209dde32f74a61469d9633a54c354bfb2c/Screen_Shot_2021-11-09_at_2.34.19_AM.png)

Jenkins Admin Account Info.

ID: admin

Password: <default password to get under command>

```bash
kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/chart-admin-password && echo
```

![Screen Shot 2021-11-09 at 2.36.48 AM.png](3%20Set%20up%20Jenkins%20on%20EKS%209dde32f74a61469d9633a54c354bfb2c/Screen_Shot_2021-11-09_at_2.36.48_AM.png)

access to master pod using under command:

```bash
kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/sh
```

### Install Jenkins Plugin

Dashboard → Jenkins Configure → Plugin Manager

[Credentials Plugin](https://plugins.jenkins.io/credentials)

[Kubernetes CLI Plugin](https://plugins.jenkins.io/kubernetes-cli)

[Kubernetes Credentials Provider](https://plugins.jenkins.io/kubernetes-credentials-provider)

![Screen Shot 2021-11-09 at 8.39.29 AM.png](3%20Set%20up%20Jenkins%20on%20EKS%209dde32f74a61469d9633a54c354bfb2c/Screen_Shot_2021-11-09_at_8.39.29_AM.png)