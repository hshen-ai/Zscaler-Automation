# Zscaler Automation with AWS Bedrock

## Overview

This repository contains two powerful automation agents for Zscaler:

1. **Cloud NSS Agent** (`cloud_nss_agent.py`) - Automates setup of Zscaler Cloud NSS to stream logs to AWS S3
2. **Bedrock AI Agent** (`bedrock_agent.py`) - AWS Bedrock-powered agent with Zscaler MCP server integration for AI-driven Zscaler automation

# Core dependencies
python-dotenv==1.1.1
boto3==1.35.0

# For Cloud NSS agent
# (boto3 is already listed above)


### Cloud NSS Agent

Automates the setup of **Zscaler Cloud NSS (Nanolog Streaming Service)** to stream logs to an AWS S3 bucket. It follows the Zscaler-AWS deployment guide to configure the necessary AWS infrastructure and prepare for log streaming.

The agent handles all AWS S3 configuration steps including bucket creation, versioning, encryption, bucket policies, and lifecycle management.

### Bedrock AI Agent

An intelligent agent powered by **AWS Bedrock's Claude 3.5 Sonnet** model that integrates with the **Zscaler MCP server** to provide natural language automation of Zscaler operations. The agent can:

- Execute Zscaler operations using natural language commands
- Leverage 100+ Zscaler MCP tools (ZPA, ZIA, ZDX, etc.)
- Perform complex multi-step operations autonomously
- Provide intelligent insights and recommendations

## What Does This Agent Do?

The Cloud NSS Agent automatically:

1. **Creates an S3 bucket** (or verifies it exists) in your specified AWS region
2. **Enables versioning** on the bucket for data protection
3. **Configures bucket policies** to allow Zscaler to write logs
4. **Enables server-side encryption** (SSE-S3) for data security
5. **Sets up lifecycle policies** (optional) for cost optimization:
   - Transitions logs to Glacier after 30 days
   - Expires logs after 90 days
6. **Generates configuration** for Zscaler portal setup

After running the agent, you'll receive clear instructions for completing the setup in the Zscaler Admin Portal.

## Prerequisites

### 1. AWS CLI Configuration

Install and configure the AWS CLI with your credentials:

```bash
# Install AWS CLI (if not already installed)
# macOS
brew install awscli

# Ubuntu/Debian
sudo apt-get install awscli

# Configure AWS credentials
aws configure
```

### 2. Zscaler Certificate Configuration (IMPORTANT)

If you're behind a Zscaler proxy that performs SSL inspection, you must configure the AWS CLI to trust the Zscaler root certificate. This prevents SSL verification errors when communicating with AWS services.

**Configure AWS CLI to use Zscaler certificate:**

```bash
aws configure set default.ca_bundle ZscalerRootCert.pem
```

This command sets the AWS CLI to use the Zscaler root certificate for SSL verification. Make sure `ZscalerRootCert.pem` is in your current directory, or provide the full path to the certificate file.

**Reference:** [Zscaler Help - Adding Custom Certificate to Application-Specific Trust Store (AWS CLI)](https://help.zscaler.com/zia/adding-custom-certificate-application-specific-trust-store#aws-cli-ubuntu)

**Alternative:** The agent also includes `--no-verify-ssl` flag in AWS CLI commands as a fallback, but using the certificate bundle is the recommended approach.

### 3. Python Environment

- Python 3.6 or higher
- Required Python packages: `python-dotenv`

```bash
pip install python-dotenv
```

### 4. Zscaler MCP Server (Optional)

For advanced integrations, you can connect the Zscaler MCP server, though it's not required for the basic setup.

## Installation

1. **Clone or download** the agent files to your local machine
2. **Ensure you have the Zscaler root certificate** (`ZscalerRootCert.pem`) in the project directory
3. **Install dependencies:**

```bash
pip install python-dotenv
```

## Configuration

### Environment Variables

Create a `.env` file in the same directory as the agent with the following configuration:

```bash
# AWS Configuration
S3_BUCKET_NAME=your-cloudnss-bucket-name
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Zscaler Configuration
ZSCALER_CUSTOMER_ID=your-customer-id

# Log Types (comma-separated: web, firewall, dns, tunnel, ipsec)
LOG_TYPES=web,firewall,dns
```

### Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `S3_BUCKET_NAME` | Name for your S3 bucket (must be globally unique) | `mycompany-zscaler-logs` |
| `AWS_REGION` | AWS region for the bucket | `us-east-1`, `eu-west-1` |
| `AWS_ACCOUNT_ID` | Your AWS account ID (12 digits) | `123456789012` |
| `ZSCALER_CUSTOMER_ID` | Your Zscaler customer/tenant ID | Found in Zscaler portal |
| `LOG_TYPES` | Types of logs to stream (comma-separated) | `web,firewall,dns` |
| `ZSCALER_AWS_ACCOUNT` | Zscaler's AWS account for NSS (default: 902912350113) | `902912350113` |
| `AUTO_CONFIGURE_ZSCALER` | Enable automatic Zscaler configuration via Bedrock AI | `true` or `false` |

### Supported Log Types

- `web` - Web traffic logs
- `firewall` - Firewall activity logs
- `dns` - DNS query logs
- `tunnel` - VPN tunnel logs
- `ipsec` - IPsec tunnel logs

## Usage

### Basic Usage

1. **Configure your environment:**
   - Set up the `.env` file with your configuration
   - Ensure AWS CLI is configured with credentials
   - Configure AWS CLI to use Zscaler certificate (see Prerequisites)

2. **Run the agent:**

```bash
python3 cloud_nss_agent.py
```

3. **Review the output:**
   - The agent will execute each setup step and display progress
   - If successful, you'll receive configuration details and next steps
   - A JSON configuration file will be saved (e.g., `cloud_nss_config_20251116_215930.json`)

### What Happens During Execution

```
================================================================================
ZSCALER CLOUD NSS TO AWS S3 SETUP
================================================================================

Configuration:
  - Bucket: mycompany-zscaler-logs
  - Region: us-east-1
  - Log Types: web, firewall, dns
  - Customer ID: ABC123
  - AWS Account: 123456789012

================================================================================

[STEP 1] Checking if bucket 'mycompany-zscaler-logs' exists...
[STEP 2] Creating S3 bucket 'mycompany-zscaler-logs' in us-east-1...
[STEP 3] Enabling versioning on bucket 'mycompany-zscaler-logs'...
[STEP 4] Applying bucket policy for Zscaler Cloud NSS access...
[STEP 5] Enabling server-side encryption (SSE-S3)...
[STEP 6] Configuring lifecycle policy (optional)...

[SUCCESS] Cloud NSS setup completed successfully!
```

### After Agent Completes

The agent will display detailed instructions for completing the setup in the Zscaler Admin Portal:

```
================================================================================
NEXT STEPS: Configure Cloud NSS in Zscaler Portal
================================================================================

1. Log in to Zscaler Admin Portal (https://admin.zscaler.net)

2. Navigate to: Administration > Nanolog Streaming Service

3. Click 'Add Cloud NSS Feed'

4. Configure the feed:
   - Name: AWS-S3-mycompany-zscaler-logs
   - NSS Type: Amazon S3
   - S3 Bucket Name: mycompany-zscaler-logs
   - AWS Region: us-east-1
   - Log Type: web, firewall, dns

5. Click 'Test Connection' to verify

6. Click 'Save' to activate the feed
```

## Verification

After configuring the feed in Zscaler portal, verify that logs are being delivered:

```bash
# List objects in your S3 bucket
aws s3 ls s3://your-bucket-name/ --region your-region

# View recent log files
aws s3 ls s3://your-bucket-name/ --region your-region --recursive
```

Logs should appear within **5-10 minutes** after activation.

## Security Features

The agent implements several security best practices:

- ✅ **Bucket Versioning** - Protects against accidental deletion
- ✅ **Server-Side Encryption** - All data encrypted at rest (AES-256)
- ✅ **Least Privilege Policies** - Bucket policies grant only necessary permissions
- ✅ **SSL/TLS** - All data in transit is encrypted
- ✅ **Certificate Validation** - Proper SSL certificate handling with Zscaler

## Troubleshooting

### SSL Certificate Errors

**Problem:** `SSL validation failed` or `certificate verify failed` errors

**Solution:**
```bash
# Configure AWS CLI to use Zscaler certificate
aws configure set default.ca_bundle ZscalerRootCert.pem

# Verify the configuration
aws configure get default.ca_bundle
```

### Bucket Already Exists

**Problem:** Bucket name is already taken globally

**Solution:** Choose a different, unique bucket name in your `.env` file. S3 bucket names must be globally unique across all AWS accounts.

### Permission Denied Errors

**Problem:** AWS CLI returns permission denied errors

**Solution:** 
- Verify your AWS credentials have appropriate S3 permissions
- Check that your IAM user/role has: `s3:CreateBucket`, `s3:PutObject`, `s3:PutBucketPolicy`, etc.

### No Logs Appearing

**Problem:** Logs don't appear in S3 after configuration

**Solution:**
- Verify the Cloud NSS feed is activated in Zscaler portal
- Check the feed status shows "Active"
- Wait 10-15 minutes for initial logs to appear
- Verify bucket policy is correctly applied

## Files Generated

- `cloud_nss_config_YYYYMMDD_HHMMSS.json` - Configuration snapshot with timestamp
- Contains bucket details, region, log types, and creation timestamp

## Architecture

```
┌─────────────────┐
│   Zscaler       │
│   Cloud NSS     │
└────────┬────────┘
         │
         │ Streams Logs
         │ (HTTPS)
         ▼
┌─────────────────┐
│   AWS S3        │
│   Bucket        │
│   ├─ web/       │
│   ├─ firewall/  │
│   └─ dns/       │
└─────────────────┘
         │
         │ (Optional)
         ▼
┌─────────────────┐
│   AWS Glacier   │
│   (30+ days)    │
└─────────────────┘
```

## Cost Considerations

- **S3 Storage:** ~$0.023/GB per month (Standard tier)
- **S3 Requests:** PUT requests ~$0.005 per 1,000 requests
- **Data Transfer:** No charge for data transfer into S3
- **Glacier:** ~$0.004/GB per month (after 30-day transition)

**Estimated Cost Example:** 1TB of logs/month ≈ $20-30/month

## Support & References

- [Zscaler Cloud NSS Documentation](https://help.zscaler.com/zia/about-nanolog-streaming-service)
- [Zscaler-AWS Deployment Guide](https://help.zscaler.com/zia/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Zscaler Certificate Configuration](https://help.zscaler.com/zia/adding-custom-certificate-application-specific-trust-store)

---

# AWS Bedrock AI Agent

## Overview

The Bedrock AI Agent is an intelligent automation system that combines AWS Bedrock's Claude 3.5 Sonnet model with the Zscaler MCP server to enable natural language control of Zscaler services.

## Features

- 🤖 **Natural Language Interface** - Control Zscaler using conversational commands
- 🛠️ **100+ Zscaler Tools** - Access to ZPA, ZIA, ZDX, ZCC, and other Zscaler services
- 🔄 **Multi-Step Operations** - Agent can autonomously execute complex workflows
- 💡 **Intelligent Insights** - AI-powered analysis and recommendations
- 🔗 **MCP Integration** - Direct integration with Zscaler MCP server

## Prerequisites

1. **AWS Bedrock Access**
   - AWS account with Bedrock access enabled
   - Claude 3.5 Sonnet model enabled in your region
   - AWS credentials configured

2. **Zscaler MCP Server**
   - MCP server installed and configured
   - Zscaler API credentials configured in `.env`

3. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Add the following to your `.env` file:

```bash
# AWS Bedrock Configuration
BEDROCK_MODEL_ID=your_bedrock_model_id
BEDROCK_MAX_TOKENS=4096
BEDROCK_TEMPERATURE=0.7

# Zscaler MCP Server Configuration
MCP_SERVER_PATH=/path/to/zscaler-mcp-server/.venv/bin/python
MCP_SERVER_MODULE=zscaler_mcp.server

# Zscaler Credentials (required for MCP server)
ZSCALER_CLIENT_ID=your_client_id
ZSCALER_CLIENT_SECRET=your_client_secret
ZSCALER_CUSTOMER_ID=your_customer_id
ZSCALER_VANITY_DOMAIN=your_vanity_domain
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `BEDROCK_MODEL_ID` | Bedrock model identifier | Claude 3.5 Sonnet |
| `AWS_REGION` | AWS region for Bedrock | From AWS config |
| `BEDROCK_MAX_TOKENS` | Maximum response tokens | 4096 |
| `BEDROCK_TEMPERATURE` | Model creativity (0-1) | 0.7 |
| `MCP_SERVER_PATH` | Path to MCP Python interpreter | Required |
| `MCP_SERVER_MODULE` | MCP server module name | zscaler_mcp.server |

## Usage

### Starting the Agent

```bash
python3 bedrock_agent.py
```

### Interactive Session

Once started, you can interact with the agent using natural language:

```
[YOU] > List all ZPA application segments

[AGENT] Let me retrieve that information for you...
[MCP] Calling tool: zpa_list_application_segments

[AGENT] I found 15 application segments in your ZPA tenant:
1. Corporate-Apps-Segment
2. Dev-Environment-Apps
3. Production-Web-Services
...
```

### Example Commands

**Query Information:**
```
- "List all ZPA application segments"
- "Show me the firewall rules in ZIA"
- "What are the current ZDX alerts?"
- "Get details about the application segment named 'Corporate-Apps'"
```

**Complex Operations:**
```
- "Create a new ZPA application segment for the HR portal"
- "Analyze the health of my ZPA connectors"
- "Find all application segments using port 443"
- "Show me which users have accessed the Finance app today"
```

**Insights and Analysis:**
```
- "What's the status of my Zscaler infrastructure?"
- "Are there any security issues I should be aware of?"
- "Which applications have the most traffic?"
- "Recommend optimizations for my ZPA configuration"
```

## How It Works

```
┌─────────────┐
│    User     │
│  (Natural   │
│  Language)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│   AWS Bedrock           │
│   Claude 3.5 Sonnet     │
│   ├─ Understands query │
│   ├─ Plans actions     │
│   └─ Calls tools       │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│   Zscaler MCP Server    │
│   ├─ ZPA Tools (40+)    │
│   ├─ ZIA Tools (30+)    │
│   ├─ ZDX Tools (15+)    │
│   └─ Other Services     │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│   Zscaler APIs          │
│   ├─ ZPA API            │
│   ├─ ZIA API            │
│   ├─ ZDX API            │
│   └─ Other APIs         │
└─────────────────────────┘
```

## Available Tool Categories

### ZPA (Zscaler Private Access)
- Application Segments
- App Connector Groups
- Server Groups
- Service Edge Groups
- Access Policies
- Segment Groups
- Provisioning Keys
- And more...

### ZIA (Zscaler Internet Access)
- Firewall Rules
- URL Filtering Rules
- DLP Rules
- Cloud Applications
- Locations
- VPN Credentials
- And more...

### ZDX (Zscaler Digital Experience)
- Device Health
- Application Performance
- User Experience Metrics
- Alerts and Monitoring
- And more...

## Security Considerations

1. **Read-Only by Default** - MCP server operates in read-only mode unless explicitly enabled
2. **AWS Credentials** - Uses standard AWS credential chain (IAM roles, profiles, etc.)
3. **Zscaler API Access** - Limited by your API client permissions
4. **Audit Logging** - All operations are logged for tracking

## Troubleshooting

### Bedrock Access Issues

**Problem:** Cannot access Bedrock model

**Solution:**
```bash
# Check if Claude model is available in your region
aws bedrock list-foundation-models --region your-aws-region

# Request model access in AWS Console if needed
# AWS Console > Bedrock > Model Access
```

### MCP Server Connection Issues

**Problem:** Failed to start MCP server

**Solution:**
- Verify `MCP_SERVER_PATH` points to correct Python interpreter
- Check Zscaler credentials are valid in `.env`
- Ensure MCP server dependencies are installed

### No Tools Available

**Problem:** Agent starts but shows 0 tools available

**Solution:**
- Check MCP server logs for errors
- Verify Zscaler API credentials
- Ensure write operations are enabled if needed

## Cost Estimation

### AWS Bedrock Costs

- **Input tokens:** ~$0.003 per 1K tokens
- **Output tokens:** ~$0.015 per 1K tokens

**Example:** 100 queries/day ≈ $10-20/month

### Optimization Tips

- Use lower temperature (0.5) for deterministic queries
- Reduce `BEDROCK_MAX_TOKENS` if responses are verbose
- Cache frequent queries when possible

## Advanced Usage

### Programmatic Usage

```python
from bedrock_agent import BedrockAgent

# Create agent
agent = BedrockAgent(
    model_id="your_bedrock_model_id",
    region="your_aws_region",
    max_tokens=4096,
    temperature=0.7
)

# Start agent
agent.start()

# Send queries
response = agent.chat("List ZPA application segments")

# Cleanup
agent.stop()
```

## License

This agent is provided as-is for Zscaler customers to automate operations.

## Version

- **Version:** 2.0
- **Last Updated:** November 2025
- **Python:** 3.9+
- **AWS CLI:** 2.x recommended
- **AWS Bedrock:** Claude 3.5 Sonnet
