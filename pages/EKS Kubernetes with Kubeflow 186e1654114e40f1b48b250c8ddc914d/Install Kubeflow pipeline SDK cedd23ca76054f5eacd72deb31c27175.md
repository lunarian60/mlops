# Install Kubeflow pipeline SDK

## Install the SDK

Run the following command to install the SDK:

```bash
pip3 install kfp --upgrade
export PATH=$PATH:~/.local/bin
```

## Set up IAM permissions

To use AWS KFP Components the KFP component pods need access to AWS SageMaker.

Enable OIDC support on EKS cluster

```bash
eksctl utils associate-iam-oidc-provider --cluster ${AWS_CLUSTER_NAME} --region ${AWS_REGION} --approve
aws eks describe-cluster --name ${AWS_CLUSTER_NAME} --query "cluster.identity.oidc.issuer" --output text
```

This will result in as below OIDC inclusive:

![Screen Shot 2021-11-07 at 6.41.26 PM.png](Install%20Kubeflow%20pipeline%20SDK%20cedd23ca76054f5eacd72deb31c27175/Screen_Shot_2021-11-07_at_6.41.26_PM.png)

Take note of the OIDC issuer URL. This URL is in the form `oidc.eks.<region>.amazonaws.com/id/<OIDC_ID>` . Note down the URL.

You can check your account number using aws cli and feed it into jq:

```bash
aws sts get-caller-identity|jq -r ".Account"
```

Create a file named trust.json with the following content:

```bash
cat <<EOF > trust.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::$AWS_ACC_NUM:oidc-provider/$OIDC_URL"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "$OIDC_URL:aud": "sts.amazonaws.com",
          "$OIDC_URL:sub": "system:serviceaccount:kubeflow:pipeline-runner"
        }
      }
    }
  ]
}
EOF
```

Create an IAM role using trust.json. Make a note of the ARN returned in the output.

```bash
aws iam create-role --role-name kfp-example-pod-role --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name kfp-example-pod-role --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
aws iam get-role --role-name kfp-example-pod-role --output text --query 'Role.Arn'
```

Create an IAM role using trust.json. Make a note of the ARN returned in the output.

```bash
aws iam create-role --role-name kfp-example-pod-role --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name kfp-example-pod-role --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
aws iam get-role --role-name kfp-example-pod-role --output text --query 'Role.Arn'
```

arn:aws:iam::846732235403:role/kfp-example-pod-role

Edit your pipeline-runner service account.

```bash
kubectl edit -n kubeflow serviceaccount pipeline-runner
```

Add `eks.amazonaws.com/role-arn: <role_arn>` to annotations at the top of the section, then save the file which may look like below:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::xxxxxxxxx:role/eks-kfp-role
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"annotations":{},"labels":{"app.kubernetes.io/component":"ml-pipeline","app.kubernetes.io/name":"kubeflow-pipelines"},"name":"pipeline-runner","namespace":"kubeflow"}}
  creationTimestamp: "2021-11-07T09:11:15Z"
  labels:
    app.kubernetes.io/component: ml-pipeline
    app.kubernetes.io/name: kubeflow-pipelines
  name: pipeline-runner
  namespace: kubeflow
  ownerReferences:
  - apiVersion: app.k8s.io/v1beta1
    blockOwnerDeletion: true
    controller: false
    kind: Application
    name: kubeflow-pipelines
    uid: d1357f49-7fb3-4d4c-9a3a-1219e81752bc
  resourceVersion: "48261"
  uid: 899adaba-fdf1-44fb-81b8-5f03f0a05de7
secrets:
- name: pipeline-runner-token-9kl7j
```

arn:aws:iam::846732235403:role/kfp-example-sagemaker-execution-role

Ref.

[https://github.com/kubeflow/pipelines/blob/master/samples/contrib/aws-samples/README.md](https://github.com/kubeflow/pipelines/blob/master/samples/contrib/aws-samples/README.md)

---

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: aws-secret
  namespace: kubeflow
type: Opaque
data:
  AWS_ACCESS_KEY_ID: AKIA4KJJMSKFZ2A3X45K
  AWS_SECRET_ACCESS_KEY: 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
EOF
```

Lastly, let’s assign sagemaker:InvokeEndpoint permission to Worker node IAM role

```bash
cat <<EOF > ~/environment/sagemaker-invoke.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sagemaker:CreateTrainingJob"
            ],
            "Resource": "*"
        }
    ]
}
EOF
aws iam put-role-policy --role-name $ROLE_NAME --policy-name sagemaker-invoke-for-worker --policy-document file://~/environment/sagemaker-invoke.json

aws iam attach-role-policy --role-name eks-kfp-role  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
```