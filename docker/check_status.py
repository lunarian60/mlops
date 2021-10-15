import boto3


sagemaker = boto3.client('sagemaker',
                        aws_access_key_id='',
                        aws_secret_access_key='',
                        region_name='')


def describe_training_job(name):
    """ Describe SageMaker training job identified by input name.
    Args:
        name (string): Name of SageMaker training job to describe.
    Returns:
        (dict)
        Dictionary containing metadata and details about the status of the training job.
    """
    try:
        response = sagemaker.describe_training_job(
            TrainingJobName = name
        )
    except Exception as e:
        print(e)
        print('Unable to describe training job.')
        raise(e)
    
    return response
    

def get_job_status(training_job_name):
    
    training_details = describe_training_job(training_job_name)
    status = training_details['TrainingJobStatus']
    
    return training_details, status


if __name__ == '__main__':

    print('checking status')
    
    training_details, status = get_job_status('')
    
    if status == 'Completed':
        print(training_details['TrainingJobName'])
    elif status == 'Failed':
        print(training_details['FailureReason'])