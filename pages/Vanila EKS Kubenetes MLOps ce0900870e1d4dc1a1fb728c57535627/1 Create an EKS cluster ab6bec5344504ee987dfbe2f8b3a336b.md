# 1. Create an EKS cluster

This following process is for a cluster creation in EKS that could replicate/simulate a on-prem kubernetes in a site. 

## Create an EKS cluster

1. Create a key-pair

```bash
aws ec2 create-key-pair --region ap-northeast-2 --key-name mlopsKeyPair
```

1. Create an EKS cluster

```bash
eksctl create cluster
--name eks-mlops \
--region ap-northeast-2 \
--with-oidc \
--ssh-access \
--ssh-public-key mlopsKeyPair \
--managed
```

- 키페어 생성 / EKS 클러스터 생성 Ref
    
    [https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html](https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html)
    
1. Check the cluster info

```bash
kubectl cluster-info
```