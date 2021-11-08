# Kubeflow Dashboard

## Kubeflow Dashboard

Check if istio-ingress is running

```yaml
kubectl get ingress -n istio-system
```

Use **port-forward** to access Kubeflow dashboard

```yaml
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

- note: Don't use an secret mode/incognito mode in the browser

In your Cloud9 environment, click **Tools / Preview / Preview Running Application** to access dashboard. You can click on Pop out window button to maximize browser into new tab.

![Screen Shot 2021-11-04 at 9.21.29 PM.png](Kubeflow%20Dashboard%2084bdb065d028457d835500b77fa12c6c/Screen_Shot_2021-11-04_at_9.21.29_PM.png)

## Create a kubeflow namespace

A namespace is used for the other settings, hence, "kubeflow" shall be used.

![Screen Shot 2021-11-07 at 9.37.39 PM.png](Kubeflow%20Dashboard%2084bdb065d028457d835500b77fa12c6c/Screen_Shot_2021-11-07_at_9.37.39_PM.png)

![Screen Shot 2021-11-07 at 9.38.34 PM.png](Kubeflow%20Dashboard%2084bdb065d028457d835500b77fa12c6c/Screen_Shot_2021-11-07_at_9.38.34_PM.png)

### kubectl을 통해 생성하는 방법

v0.6 버전 이전에는 다중 사용자에 대한 지원이 없었습니다. v0.6 버전 이후로 프로파일이라는 쿠베플로우 오브젝트를 제공하여 다중 사용자에 대한 지원을 시작했습니다. 프로파일이란 프로파일명과 같은 네임스페이스 리소스와 쿠버네티스 리소스의 모음입니다.

```yaml
apiVersion: kubeflow.org/v1beta1
kind: Profile
metadata:
  name: kubeflow
spec:
  owner:
    kind: User
    name: admin@kubeflow.org
```