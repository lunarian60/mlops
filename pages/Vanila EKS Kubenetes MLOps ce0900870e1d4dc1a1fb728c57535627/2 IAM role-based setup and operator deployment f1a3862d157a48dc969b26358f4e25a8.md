# 2. IAM role-based setup and operator deployment

refernece: [https://docs.aws.amazon.com/sagemaker/latest/dg/amazon-sagemaker-operators-for-kubernetes.html](https://docs.aws.amazon.com/sagemaker/latest/dg/amazon-sagemaker-operators-for-kubernetes.html)

## **Cluster-scoped deployment**

Before you can deploy your operator using an IAM role, associate an OpenID Connect (OIDC) provider with your role to authenticate with the IAM service.

### **Create an OpenID Connect Provider for Your Cluster**

The following instructions show how to create and associate an OIDC provider with your Amazon EKS cluster.

1. Set the local `CLUSTER_NAME` and `AWS_REGION` environment variables as follows:

```bash
# Set the Region and cluster
export CLUSTER_NAME="<your cluster name>"
export AWS_REGION="<your region>"
```

1. Use the following command to associate the OIDC provider with your cluster. For more information, see [Enabling IAM Roles for Service Accounts on your Cluster.](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html)

```bash
eksctl utils associate-iam-oidc-provider --cluster ${CLUSTER_NAME} \
    --region ${AWS_REGION} --approve
```

### **Get the OIDC ID**

OIDC could be retrieved from the console, however, the followings show another way to retrieve it.

To set up the ServiceAccount, obtain the OpenID Connect issuer URL using the following command:

```bash
aws eks describe-cluster --name ${CLUSTER_NAME} --region ${AWS_REGION} \
    --query cluster.identity.oidc.issuer --output text
```

The command returns a URL like the following:

```bash
https://oidc.eks.${AWS_REGION}.amazonaws.com/id/D48675832CA65BD10A532F597OIDCID
```

In this URL, the value `D48675832CA65BD10A532F597OIDCID` is the OIDC ID. The OIDC ID for your cluster is different. You need this OIDC ID value to create a role.

### **Create an IAM Role**

1. Create a file named `trust.json` and insert the following trust relationship code block into it. Be sure to replace all `<OIDC ID>`, `<AWS account number>`, and `<EKS Cluster region>` placeholders with values corresponding to your cluster.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS account number>:oidc-provider/oidc.eks.<EKS Cluster region>.amazonaws.com/id/<OIDC ID>"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc.eks.<EKS Cluster region>.amazonaws.com/id/<OIDC ID>:aud": "sts.amazonaws.com",
          "oidc.eks.<EKS Cluster region>.amazonaws.com/id/<OIDC ID>:sub": "system:serviceaccount:sagemaker-k8s-operator-system:sagemaker-k8s-operator-default"
        }
      }
    }
  ]
}
```

1. Run the following command to create a role with the trust relationship defined in `trust.json`. This role enables the Amazon EKS cluster to get and refresh credentials from IAM.

```bash
aws iam create-role --region ${AWS_REGION} --role-name <role name> --assume-role-policy-document file://trust.json --output=text
```

Take note of `ROLE ARN`; you pass this value to your operator. (deploy the operator)

### **Attach the AmazonSageMakerFullAccess Policy to the Role**

To give the role access to SageMaker, attach the [AmazonSageMakerFullAccess](https://console.aws.amazon.com/iam/home?#/policies/arn:aws:iam::aws:policy/AmazonSageMakerFullAccess) policy. If you want to limit permissions to the operator, you can create your own custom policy and attach it.

To attach AmazonSageMakerFullAccess, run the following command:

```bash
aws iam attach-role-policy --role-name <role name>  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
```

The Kubernetes ServiceAccount `sagemaker-k8s-operator-default` should have `AmazonSageMakerFullAccess` permissions. Confirm this when you install the operator.

## **Deploy the Operator**

### **Deploy the Operator Using YAML**

This is the simplest way to deploy your operators. The process is as follows:

1. Download the installer script using the following command:

```bash
wget https://raw.githubusercontent.com/aws/amazon-sagemaker-operator-for-k8s/master/release/rolebased/installer.yaml
```

1. Edit the `installer.yaml` file to replace `eks.amazonaws.com/role-arn`. Replace the ARN here with the Amazon Resource Name (ARN) for the OIDC-based role you’ve created.
2. Use the following command to deploy the cluster:

```bash
kubectl apply -f installer.yaml
```

### **Verify the operator deployment**

1. You should be able to see the SageMaker Custom Resource Definitions (CRDs) for each operator deployed to your cluster by running the following command:

```bash
kubectl get crd | grep sagemaker
```

Your output should look like the following:

```bash
batchtransformjobs.sagemaker.aws.amazon.com         2019-11-20T17:12:34Z
endpointconfigs.sagemaker.aws.amazon.com            2019-11-20T17:12:34Z
hostingdeployments.sagemaker.aws.amazon.com         2019-11-20T17:12:34Z
hyperparametertuningjobs.sagemaker.aws.amazon.com   2019-11-20T17:12:34Z
models.sagemaker.aws.amazon.com                     2019-11-20T17:12:34Z
trainingjobs.sagemaker.aws.amazon.com               2019-11-20T17:12:34Z
```

1. Ensure that the operator pod is running successfully. Use the following command to list all pods:

```bash
kubectl -n sagemaker-k8s-operator-system get pods
```

You should see a pod named `sagemaker-k8s-operator-controller-manager-*****` in the namespace `sagemaker-k8s-operator-system`