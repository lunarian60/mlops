# Vanila EKS/Kubenetes MLOps

version2

[Install Jenkins in a EKS cluster](Vanila%20EKS%20Kubenetes%20MLOps%20ce0900870e1d4dc1a1fb728c57535627/Install%20Jenkins%20in%20a%20EKS%20cluster%20737c16740e524c7fac6d95e5e879e1ca.md)

`Jenkins`를 `Helm`으로 배포하면 해당 `Pod`가 삭제되었을 때도 자동으로 `Pod`가 다시 생성되지만 이전 `Pod` 안에 있던 내용은 모두 사라지게 된다. `Pod`가 삭제되었다 다시 생성되어도 내용이 남아있을 수 있도록 `Pod`의 `Life Cycle`과는 완전히 독립적인 `Persistent Volume`이 필요하다.

이 글에서는 `EBS`를 `Persistent Volume`으로 사용할 예정이다. `EBS CSI Driver`를 클러스터에 배포하여 `EBS`를 `Persistent Volume`으로 사용할 수 있도록 세팅해보자

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

(유동님 여기 3번 helm으로 못했음요)

Apply the manifest

```bash
kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/ecr/?ref=master"
```

```bash
kubectl annotate serviceaccount ebs-csi-controller-sa \
    -n kube-system \
    eks.amazonaws.com/role-arn=arn:aws:iam::846732235403:role/eksctl-eks-mlops-addon-iamserviceaccount-kub-Role1-9JG4DJPZZH30
```

## Helm으로 Jenkins 배포

### **Create a namespace**

```bash
kubectl create namespace jenkins
```

### StorageClass & PersistentVolumeClaim

다음 `yaml` 파일을 `apply`하여 `provisioner=ebs.csi.aws.com`인 `StorageClass`를 생성해주고 해당 `StorageClass`를 사용하는 `PersistentVolumeClaim`도 생성해준다.

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

`Jenkins Pod`가 `API 서버`와 상호작용할 수 있도록 `jenkins`라는 `ServiceAccount`를 생성한다.

`jenkins-sa.yaml`을 적용하여 `ClusterRole`, `ClusterRoleBinding` 및 `ServiceAccount`를 생성해준다.

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

### values.yaml 정의

1. To enable persistence, we will create an override file and pass it as an argument to the Helm CLI. Paste the content from [raw.githubusercontent.com/jenkinsci/helm-charts/main/charts/jenkins/values.yaml](https://raw.githubusercontent.com/jenkinsci/helm-charts/main/charts/jenkins/values.yaml) into a YAML formatted file called `jenkins-values.yaml`.
    
    The `jenkins-values.yaml` is used as a template to provide values that are necessary for setup.
    
2. Open the `jenkins-values.yaml` file in your favorite text editor and modify the following:

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

1. Now you can install Jenkins by running the `helm install` command and passing it the following arguments:

```bash
helm repo add jenkinsci https://charts.jenkins.io
helm repo update

helm install jenkins -n jenkins -f jenkins-values.yml jenkinsci/jenkins
```

![Screen Shot 2021-11-07 at 9.40.38 PM.png](Vanila%20EKS%20Kubenetes%20MLOps%20ce0900870e1d4dc1a1fb728c57535627/Screen_Shot_2021-11-07_at_9.40.38_PM.png)

[workflow-aggregator](https://plugins.jenkins.io/workflow-aggregator)

`Credentials`

printf $(kubectl get secret --namespace default jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode);echo

hUVllHLMxD

[Kubernetes Credentials Provider](https://plugins.jenkins.io/kubernetes-credentials-provider)

admin

kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/chart-admin-password && echo

`kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/bash`

Kubernetes Credentials Provider

[Kubernetes CLI Plugin](https://plugins.jenkins.io/kubernetes-cli)

[Kubernetes Continuous Deploy Plugin](https://plugins.jenkins.io/kubernetes-cd)

~/.kube/config

```bash

cat <<EoF > ~/.kube/config
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM1ekNDQWMrZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeE1URXdOekE0TXpJeU1Gb1hEVE14TVRFd05UQTRNekl5TUZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBT09OCkZzd1NnbW9pQlFpamt1Y0dKS0YwdFd3dnFDVlYyNCtLVTB5YmZMYlBweXJZZEtUSUkzUTIyVnY5WWREOGpHV0IKQk51ZVFDbEwwbDh4eTVDejdON0JRNHUxQjc3OURzNzQyK0FkUmFvcm5qZnBVS0R3MFp4djhYR2wwUWhpcFdKMAphY0hlYno0K3dES2Y5YjhOS2VFdVMzS1UxZzlHSm4vOWdCUkNwQThUSXdGTmh0d0pJckhzTWxVU3Y3QlUzTU1qCk5QWFgzZlR6REYvU05NcUVod1hQOVBlekhJQWt2T0xMNVJ5OElEVXZ0ZzRHMWR1d1M0NzBUQ0IyM1JMMjdvdm4KVXlsbFdKdnBEbk8vOVBqWEU0M28wSEdTSU9EUk51U3p6Mk1MS0plazlieWhBSlNYQkFXTGpzSUZHR1ZLZDNENgpEdWkrMTBENkozOGEwbUdqRDdFQ0F3RUFBYU5DTUVBd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZCeWJPVS8ybit5Y1p2WUp3UXhickxIUE5Ra1VNQTBHQ1NxR1NJYjMKRFFFQkN3VUFBNElCQVFBNFNvclR3VDUyS1pxdmVZZzZZS24vaHk0L1lXTlh5a1VRY0dFZU9LK2FDNEk1cVYrcQpLMGx6Vk1SdFNFQS92eUtyOWxWSkpEeXdvUURMellkRGlndW1NaEF5Y2c0cGF6Ui94V1U4aXQ2aFlTYUNid09sCmI4b2c1SGdiSkRWY0xJcmg5Q3B4Um1JR2tld0wxaXhTNHVLZDkvc09kcktXTHkreDhHMVIzUmhDSjA2R1VpSmcKR3ZlUUhyQ1RRb2h4UVZVayt4bWp1TXI4c1hwYTRBd0E5eFo4MFg1L1g5ZFZOL3lUUERMOFI4MzBrM2tCa0JWZgpMWWFwSktRM25laU1EZFNNeDVJUWUwUTEweS93NTU2Nk85SjNUTTl6UWZZZDA5Qm1xbGdZSFlLSkNvUXZucjJpCnpMV0hKeHhwSSsrUjVzUmZMMStVRzBXN2M1SHhXNk1iSWlQMwotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    server: https://AFF9E22E65B2F8F7264F14346E54BF58.yl4.ap-northeast-2.eks.amazonaws.com
  name: eks-mlops.ap-northeast-2.eksctl.io
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM1ekNDQWMrZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeE1URXdOekE0TXpJeU1Gb1hEVE14TVRFd05UQTRNekl5TUZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBT09OCkZzd1NnbW9pQlFpamt1Y0dKS0YwdFd3dnFDVlYyNCtLVTB5YmZMYlBweXJZZEtUSUkzUTIyVnY5WWREOGpHV0IKQk51ZVFDbEwwbDh4eTVDejdON0JRNHUxQjc3OURzNzQyK0FkUmFvcm5qZnBVS0R3MFp4djhYR2wwUWhpcFdKMAphY0hlYno0K3dES2Y5YjhOS2VFdVMzS1UxZzlHSm4vOWdCUkNwQThUSXdGTmh0d0pJckhzTWxVU3Y3QlUzTU1qCk5QWFgzZlR6REYvU05NcUVod1hQOVBlekhJQWt2T0xMNVJ5OElEVXZ0ZzRHMWR1d1M0NzBUQ0IyM1JMMjdvdm4KVXlsbFdKdnBEbk8vOVBqWEU0M28wSEdTSU9EUk51U3p6Mk1MS0plazlieWhBSlNYQkFXTGpzSUZHR1ZLZDNENgpEdWkrMTBENkozOGEwbUdqRDdFQ0F3RUFBYU5DTUVBd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZCeWJPVS8ybit5Y1p2WUp3UXhickxIUE5Ra1VNQTBHQ1NxR1NJYjMKRFFFQkN3VUFBNElCQVFBNFNvclR3VDUyS1pxdmVZZzZZS24vaHk0L1lXTlh5a1VRY0dFZU9LK2FDNEk1cVYrcQpLMGx6Vk1SdFNFQS92eUtyOWxWSkpEeXdvUURMellkRGlndW1NaEF5Y2c0cGF6Ui94V1U4aXQ2aFlTYUNid09sCmI4b2c1SGdiSkRWY0xJcmg5Q3B4Um1JR2tld0wxaXhTNHVLZDkvc09kcktXTHkreDhHMVIzUmhDSjA2R1VpSmcKR3ZlUUhyQ1RRb2h4UVZVayt4bWp1TXI4c1hwYTRBd0E5eFo4MFg1L1g5ZFZOL3lUUERMOFI4MzBrM2tCa0JWZgpMWWFwSktRM25laU1EZFNNeDVJUWUwUTEweS93NTU2Nk85SjNUTTl6UWZZZDA5Qm1xbGdZSFlLSkNvUXZucjJpCnpMV0hKeHhwSSsrUjVzUmZMMStVRzBXN2M1SHhXNk1iSWlQMwotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    server: https://AFF9E22E65B2F8F7264F14346E54BF58.yl4.ap-northeast-2.eks.amazonaws.com
  name: arn:aws:eks:ap-northeast-2:846732235403:cluster/eks-mlops
contexts:
- context:
    cluster: eks-mlops.ap-northeast-2.eksctl.io
    user: i-0c3b27677650997bd@eks-mlops.ap-northeast-2.eksctl.io
  name: i-0c3b27677650997bd@eks-mlops.ap-northeast-2.eksctl.io
- context:
    cluster: arn:aws:eks:ap-northeast-2:846732235403:cluster/eks-mlops
    user: arn:aws:eks:ap-northeast-2:846732235403:cluster/eks-mlops
  name: arn:aws:eks:ap-northeast-2:846732235403:cluster/eks-mlops
current-context: arn:aws:eks:ap-northeast-2:846732235403:cluster/eks-mlops
kind: Config
preferences: {}
users:
- name: i-0c3b27677650997bd@eks-demo.ap-northeast-2.eksctl.io
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      args:
      - token
      - -i
      - eks-demo
      command: aws-iam-authenticator
      env:
      - name: AWS_STS_REGIONAL_ENDPOINTS
        value: regional
      - name: AWS_DEFAULT_REGION
        value: ap-northeast-2
      provideClusterInfo: false
- name: i-0c3b27677650997bd@eks-mlops.ap-northeast-2.eksctl.io
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      args:
      - token
      - -i
      - eks-mlops
      command: aws-iam-authenticator
      env:
      - name: AWS_STS_REGIONAL_ENDPOINTS
        value: regional
      - name: AWS_DEFAULT_REGION
        value: ap-northeast-2
      provideClusterInfo: false
- name: arn:aws:eks:ap-northeast-2:846732235403:cluster/eks-mlops
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      args:
      - --region
      - ap-northeast-2
      - eks
      - get-token
      - --cluster-name
      - eks-mlops
      command: aws
EoF
```

만약에 KUBECONFIG 환경변수가 잡혀 있지 않다면

**export KUBECONFIG=$KUBECONFIG:~/.kube/config**