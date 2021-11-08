# Create a cloud9 workspace

### Launch Cloud9

![Screen Shot 2021-10-28 at 11.32.55 AM.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-10-28_at_11.32.55_AM.png)

- Environment type : Create a new EC2 instance for environment (direct access)
- Instance type : t3.small (2 GiB RAM + 2 vCPU)
- Platform : Amazon Linux 2 (recommended)
- Cost-saving setting : Never

### Create an IAM role for your workspace

![Untitled](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Untitled.png)

![Screen Shot 2021-11-02 at 9.08.06 PM.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.08.06_PM.png)

### Attach the IAM role to your workspace

![Screen Shot 2021-11-02 at 9.09.38 PM.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.09.38_PM.png)

![Screen Shot 2021-11-02 at 9.10.59 PM.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.10.59_PM.png)

### Update IAM settings for your workspace

Return to your Cloud9 workspace and click the gear icon.

- Select **AWS SETTINGS**
- Turn off **AWS managed temporary credentials**
- Close the Preferences tab

![Screen Shot 2021-11-02 at 9.13.08 PM.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.13.08_PM.png)

To ensure temporary credentials aren’t already in place we will also remove any existing credentials file:

```bash
rm -vf ${HOME}/.aws/credentials
```

We should configure our aws cli with our current region as default.

```bash
export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
export AZS=($(aws ec2 describe-availability-zones --query 'AvailabilityZones[].ZoneName' --output text --region $AWS_REGION))
```