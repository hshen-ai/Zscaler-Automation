# AWS Access Key Setup for Bedrock API Access

This guide will help you create AWS access keys for 3rd party applications to use the Bedrock endpoint.

## Prerequisites
- AWS Account with administrative access
- AWS CLI installed (optional but recommended)

---

## Method 1: Using AWS Console (Recommended for Beginners)

### Step 1: Create IAM User

1. **Sign in to AWS Console**
   - Go to https://console.aws.amazon.com
   - Navigate to IAM service (search "IAM" in the services)

2. **Create New IAM User**
   - Click **Users** in the left sidebar
   - Click **Create user** button
   - Enter username (e.g., `bedrock-api-user`)
   - Click **Next**

3. **Set Permissions**
   - Select **Attach policies directly**
   - Search and select: `AmazonBedrockFullAccess`
   - (Optional) For stricter access, create a custom policy (see Step 2)
   - Click **Next**

4. **Review and Create**
   - Review the settings
   - Click **Create user**

### Step 2: Create Access Keys

1. **Open User Details**
   - Click on the newly created user
   - Go to **Security credentials** tab

2. **Create Access Key**
   - Scroll down to **Access keys** section
   - Click **Create access key**
   - Select use case: **Third-party service** or **Application running outside AWS**
   - Click **Next**

3. **Download Credentials**
   - **IMPORTANT**: Download the `.csv` file or copy both:
     - Access Key ID
     - Secret Access Key
   - **WARNING**: This is the ONLY time you can view the Secret Access Key
   - Click **Done**

---

## Method 2: Using AWS CLI (For Advanced Users)

### Step 1: Create IAM User
```bash
# Create IAM user
aws iam create-user --user-name bedrock-api-user

# Create and attach policy
aws iam attach-user-policy \
    --user-name bedrock-api-user \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### Step 2: Create Access Keys
```bash
# Create access key
aws iam create-access-key --user-name bedrock-api-user

# Output will contain:
# - AccessKeyId
# - SecretAccessKey
```

---

## Custom IAM Policy (Recommended for Production)

Instead of `AmazonBedrockFullAccess`, use this minimal policy for better security:

### Create Custom Policy in Console

1. Go to **IAM** → **Policies** → **Create policy**
2. Click **JSON** tab
3. Paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockInvokeModel",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
            ]
        },
        {
            "Sid": "BedrockListModels",
            "Effect": "Allow",
            "Action": [
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": "*"
        }
    ]
}
```

4. Name it: `BedrockClaudeInvokeOnly`
5. Click **Create policy**
6. Attach this policy to your IAM user instead of `AmazonBedrockFullAccess`

### Using CLI to Create Custom Policy

```bash
# Create policy file
cat > bedrock-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockInvokeModel",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
            ]
        },
        {
            "Sid": "BedrockListModels",
            "Effect": "Allow",
            "Action": [
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create the policy
aws iam create-policy \
    --policy-name BedrockClaudeInvokeOnly \
    --policy-document file://bedrock-policy.json

# Attach to user (replace ACCOUNT_ID with your AWS account ID)
aws iam attach-user-policy \
    --user-name bedrock-api-user \
    --policy-arn arn:aws:iam::ACCOUNT_ID:policy/BedrockClaudeInvokeOnly
```

---

## Configuration for 3rd Party Applications

### For Python Applications (boto3)

```python
import boto3

# Method 1: Using environment variables
import os
os.environ['AWS_ACCESS_KEY_ID'] = 'YOUR_ACCESS_KEY_ID'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'YOUR_SECRET_ACCESS_KEY'
os.environ['AWS_DEFAULT_REGION'] = 'eu-central-1'

# Method 2: Direct credentials
client = boto3.client(
    'bedrock-runtime',
    region_name='eu-central-1',
    aws_access_key_id='YOUR_ACCESS_KEY_ID',
    aws_secret_access_key='YOUR_SECRET_ACCESS_KEY'
)

# Invoke model
response = client.invoke_model(
    modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
    body='{"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hello"}]}'
)
```

### For REST API (curl)

```bash
# Install AWS CLI and configure
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: eu-central-1
# - Output format: json

# Use aws bedrock-runtime invoke-model command
aws bedrock-runtime invoke-model \
    --model-id anthropic.claude-3-5-sonnet-20240620-v1:0 \
    --body '{"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hello"}]}' \
    --region eu-central-1 \
    output.json
```

### Environment Variables (.env file)

```bash
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
AWS_REGION=eu-central-1
AWS_ACCOUNT_ID=409073339454
```

---

## Security Best Practices

### ✅ DO

1. **Use IAM Roles when possible** (for EC2, Lambda, ECS)
2. **Create separate users** for different applications
3. **Use custom policies** with minimal permissions
4. **Rotate access keys regularly** (every 90 days)
5. **Enable MFA** for IAM users with console access
6. **Store credentials securely** (AWS Secrets Manager, environment variables)
7. **Never commit credentials** to version control (.gitignore them)
8. **Use AWS CloudTrail** to monitor API usage
9. **Set up billing alerts** to catch unexpected usage

### ❌ DON'T

1. **Don't use root account credentials**
2. **Don't share access keys** between applications
3. **Don't hardcode credentials** in source code
4. **Don't commit credentials** to Git
5. **Don't grant more permissions** than needed
6. **Don't disable CloudTrail logging**

---

## Testing the Access Keys

### Using Python
```python
import boto3

# Test connection
try:
    client = boto3.client(
        'bedrock-runtime',
        region_name='eu-central-1',
        aws_access_key_id='YOUR_ACCESS_KEY_ID',
        aws_secret_access_key='YOUR_SECRET_ACCESS_KEY'
    )
    
    # Test with a simple request
    response = client.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
        body='{"anthropic_version": "bedrock-2023-05-31", "max_tokens": 100, "messages": [{"role": "user", "content": "Say hello"}]}'
    )
    
    print("✅ Access keys are working!")
    print(f"Response: {response['body'].read()}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
```

### Using AWS CLI
```bash
# Test access
aws bedrock list-foundation-models \
    --region eu-central-1 \
    --query 'modelSummaries[?contains(modelId, `claude-3-5-sonnet`)].{ModelID:modelId,Name:modelName}' \
    --output table
```

---

## Troubleshooting

### Error: "Access Denied"
- Verify IAM policy is attached correctly
- Check if Bedrock service is available in your region
- Ensure model access is enabled in Bedrock console

### Error: "Invalid Access Key"
- Verify access key ID and secret are correct
- Check if access key is still active (not deleted)
- Ensure no extra spaces or characters in credentials

### Error: "Model Not Found"
- Verify model ID is correct: `anthropic.claude-3-5-sonnet-20240620-v1:0`
- Check if model access is requested in Bedrock console
- Confirm region is correct: `eu-central-1`

### Enable Model Access
1. Go to AWS Console → Bedrock
2. Click **Model access** in left sidebar
3. Click **Manage model access**
4. Enable: **Anthropic Claude 3.5 Sonnet**
5. Click **Save changes**

---

## Revoking Access Keys

### If Credentials Are Compromised

**Immediate Actions:**

1. **Deactivate Access Key**
   ```bash
   aws iam update-access-key \
       --user-name bedrock-api-user \
       --access-key-id ACCESS_KEY_ID \
       --status Inactive
   ```

2. **Delete Access Key**
   ```bash
   aws iam delete-access-key \
       --user-name bedrock-api-user \
       --access-key-id ACCESS_KEY_ID
   ```

3. **Create New Access Key**
   - Follow the creation steps again
   - Update all applications with new credentials

---

## Cost Monitoring

### Set Up Billing Alerts

1. Go to **AWS Billing Console**
2. Click **Budgets** → **Create budget**
3. Set threshold (e.g., $50/month)
4. Configure email notifications

### Monitor Bedrock Usage

```bash
# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Bedrock \
    --metric-name InvocationCount \
    --dimensions Name=ModelId,Value=anthropic.claude-3-5-sonnet-20240620-v1:0 \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-31T23:59:59Z \
    --period 86400 \
    --statistics Sum
```

---

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Boto3 Bedrock Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)

---

## Quick Reference

**Endpoint Details:**
- Service: `bedrock-runtime`
- Region: `eu-central-1`
- Endpoint: `https://bedrock-runtime.eu-central-1.amazonaws.com`
- Model ID: `anthropic.claude-3-5-sonnet-20240620-v1:0`

**Required IAM Permissions:**
```
bedrock:InvokeModel
bedrock:InvokeModelWithResponseStream
```

**AWS Account ID:** `409073339454`
