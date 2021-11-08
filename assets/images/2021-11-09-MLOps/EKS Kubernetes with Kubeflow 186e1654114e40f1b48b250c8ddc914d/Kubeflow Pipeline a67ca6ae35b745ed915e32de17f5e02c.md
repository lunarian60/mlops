# Kubeflow Pipeline

![Untitled](Kubeflow%20Pipeline%20a67ca6ae35b745ed915e32de17f5e02c/Untitled.png)

## Components

컴포넌트는 ML 워크플로우의 한 단계를 수행하는 코드 집합입니다. 인풋, 아웃풋, 이름, 상세구현 등 함수와 유사합니다. 파이프라인 DSL로 작성된 파이썬 코드가 YAML 파일로 컴파일되는데 쿠베플로우 파이프라인의 컨테이너 컴포넌트 데이터 모델 형식으로 변환됩니다. Metadata, Interface, Implentation이라는 필드들로 구성되며, 여기에는 파이프라인의 이름, 인풋/아웃풋 타입 등이 기재됩니다.

## **SageMaker Components for Kubeflow Pipelines**

With Amazon SageMaker Components for Kubeflow Pipelines (KFP), you can create and monitor training, tuning, endpoint deployment, and batch transform jobs in Amazon SageMaker. By running Kubeflow Pipeline jobs on Amazon SageMaker, you move data processing and training jobs from the Kubernetes cluster to Amazon SageMaker’s machine learning-optimized managed service. The job parameters, status, logs, and outputs from Amazon SageMaker are still accessible from the Kubeflow Pipelines UI.

### **Training components**

- **Training**
    
    The Training component allows you to submit Amazon SageMaker Training jobs directly from a Kubeflow Pipelines workflow.
    
- **RLEstimator**
- **Hyperparameter Optimization**
    
    The Hyperparameter Optimization component enables you to submit hyperparameter tuning jobs to Amazon SageMaker directly from a Kubeflow Pipelines workflow.
    
- **Processing**

### **Inference components**

- **Hosting Deploy**
    
    The Deploy component enables you to deploy a model in Amazon SageMaker Hosting from a Kubeflow Pipelines workflow.
    
- **Batch Transform component**

**Code Sample:**

```python
@dsl.pipeline(
    name='XGBoost Trainer',
    description='A trainer that does end-to-end distributed training for XGBoost models.'
)
def xgb_train_pipeline(
    output='s://your-s3-bucket',
    project='your-aws-project',
    cluster_name='xgb-%s' % dsl.RUN_ID_PLACEHOLDER,
    region='ap-northeast-2',
    train_data='s3://ml-pipeline-playground/sfpd/train.csv',
    eval_data='s3://ml-pipeline-playground/sfpd/eval.csv',
    schema='gs://ml-pipeline-playground/sfpd/schema.json',
    target='resolution',
    rounds=200,
    workers=2,
    true_label='ACTION',
):
	_train_op = dataproc_train_op(
            project=project,
            region=region,
            cluster_name=cluster_name,
            train_data=transform_output_train,
            eval_data=transform_output_eval,
            target=target,
            analysis=analyze_output,
            workers=workers,
            rounds=rounds,
            output=train_output
        ).after(_transform_op).set_display_name('Trainer')

...
```

**Now, we'll build a Kubeflow pipeline where every component call a different Amazon SageMaker feature. Our simple pipeline will perform:**

1. Hyperparameter optimization
2. Select best hyperparameters and increase epochs
3. Training model on the best hyperparameters
4. Create an Amazon SageMaker model
5. Deploy model