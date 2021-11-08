# IAM Role and credentials

### Create an IAM role for your workspace

![Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Untitled.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Untitled.png)

![Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.08.06_PM.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.08.06_PM.png)

### Attach the IAM role to your workspace

![Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.09.38_PM.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.09.38_PM.png)

![Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.10.59_PM.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.10.59_PM.png)

### Update IAM settings for your workspace 이거 왜함?

Return to your Cloud9 workspace and click the gear icon.

- Select **AWS SETTINGS**
- Turn off **AWS managed temporary credentials**
- Close the Preferences tab

![Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.13.08_PM.png](Create%20a%20cloud9%20workspace%2041b4c869fca6475d8ab3477bb28bc9b4/Screen_Shot_2021-11-02_at_9.13.08_PM.png)

To ensure temporary credentials aren’t already in place we will also remove any existing credentials file:

```
rm -vf ${HOME}/.aws/credentials

```

We should configure our aws cli with our current region as default.

```bash
export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
export AZS=($(aws ec2 describe-availability-zones --query 'AvailabilityZones[].ZoneName' --output text --region $AWS_REGION))

```

Let’s save these into bash_profile

```bash
aws configure set default.region ${AWS_REGION}
aws configure get default.region

```