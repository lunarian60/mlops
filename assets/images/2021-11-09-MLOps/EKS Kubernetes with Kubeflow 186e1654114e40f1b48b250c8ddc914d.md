# EKS/Kubernetes with Kubeflow

![Kubeflow.v.0.1.drawio.png](EKS%20Kubernetes%20with%20Kubeflow%20186e1654114e40f1b48b250c8ddc914d/Kubeflow.v.0.1.drawio.png)

## **Prerequisites**

- Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)
- (Optional) Install and configure the AWS Command Line Interface (AWS CLI) - this won't be needed if you use an AWS IDE such as Cloud9:
    - Install the [AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).
    - Configure the AWS CLI by running the following command: `aws configure`.
    - Enter your Access Keys ([Access Key ID and Secret Access Key](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)).
    - Enter your preferred AWS Region and default output options.
- Install [eksctl](https://github.com/weaveworks/eksctl) and the [aws-iam-authenticator](https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html).

## Kubeflow on EKS

[Install Kubeflow](EKS%20Kubernetes%20with%20Kubeflow%20186e1654114e40f1b48b250c8ddc914d/Install%20Kubeflow%20d5344c86fbc642f0894142615638c947.md)

[Kubeflow Dashboard](EKS%20Kubernetes%20with%20Kubeflow%20186e1654114e40f1b48b250c8ddc914d/Kubeflow%20Dashboard%2084bdb065d028457d835500b77fa12c6c.md)

[Assign IAM permissions](EKS%20Kubernetes%20with%20Kubeflow%20186e1654114e40f1b48b250c8ddc914d/Assign%20IAM%20permissions%20e91a4cf961a94df7a38dd5ab467ec456.md)

[Install Kubeflow pipeline SDK](EKS%20Kubernetes%20with%20Kubeflow%20186e1654114e40f1b48b250c8ddc914d/Install%20Kubeflow%20pipeline%20SDK%20cedd23ca76054f5eacd72deb31c27175.md)

[Kubeflow Pipeline](EKS%20Kubernetes%20with%20Kubeflow%20186e1654114e40f1b48b250c8ddc914d/Kubeflow%20Pipeline%20a67ca6ae35b745ed915e32de17f5e02c.md)