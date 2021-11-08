# Assign IAM permissions

For the kubeflow to execute the pipeline, it is required to set three levels of IAM permissions. 

1. create Kubernetes secrets **aws-secret** with Sagemaker policies. This is used during pipeline execution to make calls to AWS API’s. 
2. create an IAM execution role for Sagemaker so that the job can assume this role in order to perform Sagemaker actions. Typically in a production environment, you would assign fine-grained permissions depending on the nature of actions you take and leverage tools like [IAM Role for Service Account](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html) for securing access to AWS resources but for simplicity we will assign AmazonSageMakerFullAccess IAM policy to both. You can read more about granular policies [here](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html). 
3. Assign sagemaker:InvokeEndpoint permission to Worker node IAM role so that we can use this to make predictions once Sagemaker creates the endpoint

Run the following command to create the permissions

```bash
aws iam create-user --user-name kubeflow-sagemaker-user
aws iam attach-user-policy --user-name kubeflow-sagemaker-user --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
aws iam create-access-key --user-name kubeflow-sagemaker-user > /tmp/create_output.json
```

Record the new user’s credentials into environment variables

```bash
export AWS_ACCESS_KEY_ID_VALUE=$(jq -j .AccessKey.AccessKeyId /tmp/create_output.json | base64)
export AWS_SECRET_ACCESS_KEY_VALUE=$(jq -j .AccessKey.SecretAccessKey /tmp/create_output.json | base64)
```

Now, apply this to the EKS cluster

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: aws-secret
  namespace: kubeflow
type: Opaque
data:
  AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID_VALUE
  AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY_VALUE
EOF
```

Run the following command to create a SageMaker execution role

```bash
TRUST="{ \"Version\": \"2012-10-17\", \"Statement\": [ { \"Effect\": \"Allow\", \"Principal\": { \"Service\": \"sagemaker.amazonaws.com\" }, \"Action\": \"sts:AssumeRole\" } ] }"
aws iam create-role --role-name sagemaker-kfp-role --assume-role-policy-document "$TRUST"
aws iam attach-role-policy --role-name sagemaker-kfp-role --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
aws iam attach-role-policy --role-name sagemaker-kfp-role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam get-role --role-name sagemaker-kfp-role --output text --query 'Role.Arn'
```