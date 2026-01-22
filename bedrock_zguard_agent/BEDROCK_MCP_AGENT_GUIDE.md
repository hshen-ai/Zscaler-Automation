# AWS Bedrock Direct MCP Agent Guide

## Overview

The `bedrock_mcp_agent.py` script provides a direct connection to AWS Bedrock's Claude 3.5 Sonnet model, integrated with the Zscaler MCP (Model Context Protocol) server. This agent bypasses Zscaler AI Gateway (ZGuard) and connects directly to AWS Bedrock using boto3.

## Key Features

- **Direct AWS Connection**: Uses boto3 to connect directly to AWS Bedrock
- **No Proxy Layer**: Bypasses Zscaler AI Gateway for direct model access
- **MCP Integration**: Full access to Zscaler MCP tools (ZPA, ZIA, ZDX, etc.)
- **Agentic Behavior**: Autonomous tool use and multi-step operations
- **Interactive Chat**: Real-time conversational interface

## Differences from ZGuard Agent

| Feature | ZGuard Agent | Direct Agent |
|---------|--------------|--------------|
| Connection | Via Zscaler AI Gateway | Direct to AWS Bedrock |
| Authentication | ZGuard API Key | AWS Credentials (IAM) |
| Library | requests (HTTP) | boto3 (AWS SDK) |
| Network | Through Zscaler proxy | Direct internet/VPN |
| Security Controls | ZGuard policies apply | AWS IAM only |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    bedrock_mcp_agent.py                      │
│                                                               │
│  ┌──────────────────┐           ┌────────────────────────┐  │
│  │  BedrockMCPAgent │           │  ZscalerMCPClient      │  │
│  │                  │           │                        │  │
│  │  - boto3 client  │           │  - JSON-RPC protocol   │  │
│  │  - conversation  │           │  - subprocess mgmt     │  │
│  │  - tool calling  │◄─────────►│  - tool invocation     │  │
│  └────────┬─────────┘           └───────────┬────────────┘  │
│           │                                  │                │
└───────────┼──────────────────────────────────┼───────────────┘
            │                                  │
            │ boto3                            │ stdio
            │ (AWS SDK)                        │
            ▼                                  ▼
   ┌────────────────────┐         ┌─────────────────────────┐
   │   AWS Bedrock      │         │  Zscaler MCP Server     │
   │                    │         │                         │
   │  Claude 3.5 Sonnet │         │  - ZPA tools            │
   │                    │         │  - ZIA tools            │
   │  (Direct)          │         │  - ZDX tools            │
   └────────────────────┘         │  - etc.                 │
                                  └─────────────────────────┘
```

## Prerequisites

### 1. AWS Access

- AWS account with Bedrock access
- IAM permissions for bedrock-runtime
- Model access enabled (Claude 3.5 Sonnet v2)

### 2. Python Environment

```bash
pip install boto3 python-dotenv
```

### 3. Zscaler MCP Server

The Zscaler MCP server must be installed and configured. See the main project README for setup instructions.

## Configuration

### Step 1: Create .env File

Copy the example configuration:

```bash
cp .env.example.direct .env
```

### Step 2: Configure AWS Credentials

Choose one of three methods:

#### Method 1: AWS CLI (Recommended)

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
```

This stores credentials in `~/.aws/credentials`

#### Method 2: Environment Variables

Add to `.env`:

```bash
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

#### Method 3: IAM Role

If running on EC2/ECS with an attached IAM role, no additional configuration is needed.

### Step 3: Configure Bedrock Settings

Edit `.env`:

```bash
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_REGION=us-east-1
BEDROCK_MAX_TOKENS=4096
BEDROCK_TEMPERATURE=0.0
```

### Step 4: Configure MCP Server

Update MCP server paths in `.env`:

```bash
MCP_SERVER_PATH=/path/to/zscaler-mcp-server/.venv/bin/python
MCP_SERVER_MODULE=zscaler_mcp.server
```

### Step 5: Configure Zscaler Credentials

Add your Zscaler API credentials to `.env`:

```bash
# ZPA
ZPA_CLIENT_ID=your_client_id
ZPA_CLIENT_SECRET=your_client_secret
ZPA_CUSTOMER_ID=your_customer_id
ZPA_CLOUD=your_cloud

# ZIA
ZIA_USERNAME=your_username
ZIA_PASSWORD=your_password
ZIA_API_KEY=your_api_key
ZIA_CLOUD=your_cloud
```

## Required IAM Permissions

Your AWS IAM user/role needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-*"
    }
  ]
}
```

## Usage

### Basic Usage

Run the agent interactively:

```bash
python bedrock_mcp_agent.py
```

The agent will:
1. Initialize boto3 Bedrock client
2. Start the Zscaler MCP server
3. Load available tools
4. Start interactive chat session

### Example Session

```
================================================================================
AWS BEDROCK DIRECT + MCP INTEGRATION
================================================================================

Model: anthropic.claude-3-5-sonnet-20241022-v2:0
Region: us-east-1
Connection: Direct to AWS Bedrock (no proxy)

================================================================================

[INFO] Starting interactive session...
[INFO] Type 'exit' or 'quit' to end the session

[YOU] > List all ZPA application segments

[USER] List all ZPA application segments

[INFO] Starting agentic loop (max 5 iterations)
[INFO] Each iteration may make an API call to Bedrock if tools are used

[AGENT] Starting iteration 1/5

================================================================================
[BEDROCK] API Call #1 to AWS Bedrock
================================================================================

[DEBUG] Request Details:
  Model ID: anthropic.claude-3-5-sonnet-20241022-v2:0
  Region: us-east-1
  ...

[BEDROCK] Sending request to AWS...
[BEDROCK] ✓ API Call #1 successful

[AGENT] Model requested tool use - will need another API call after processing tools

[MCP] Calling tool: zpa_list_application_segments
[MCP] Tool executed successfully
...
```

### Available Commands

In the interactive session:
- Type your question or command
- `exit`, `quit`, or `q` - End the session
- `Ctrl+C` - Interrupt the session

## Tool Use Flow

1. **User Input**: You send a natural language request
2. **Model Invocation**: Agent calls AWS Bedrock via boto3
3. **Tool Selection**: Model decides which Zscaler tools to use
4. **Tool Execution**: Agent calls MCP server to execute tools
5. **Result Processing**: Tool results are sent back to model
6. **Response Generation**: Model generates final response
7. **Display**: Response is shown to user

## Troubleshooting

### Error: "No AWS credentials found"

**Solution**: Configure AWS credentials using one of the three methods above.

```bash
# Quick fix with AWS CLI
aws configure
```

### Error: "AccessDeniedException"

**Solution**: Verify your IAM permissions include `bedrock:InvokeModel`.

```bash
# Check current IAM identity
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

### Error: "ResourceNotFoundException: Model not found"

**Solution**: 
1. Verify model ID is correct in `.env`
2. Check model is available in your region
3. Request model access in AWS Console:
   - Go to AWS Bedrock console
   - Click "Model access"
   - Request access to Claude 3.5 Sonnet v2

### Error: "MCP server not started"

**Solution**: Check MCP server configuration:
1. Verify `MCP_SERVER_PATH` points to correct Python interpreter
2. Verify `MCP_SERVER_MODULE` is correct
3. Ensure Zscaler credentials are configured
4. Check MCP server logs for errors

### Connection Issues

If you're having network connectivity issues:

1. **Check AWS region**: Ensure the region supports Bedrock
2. **VPN/Proxy**: boto3 respects system proxy settings
3. **Firewall**: Ensure outbound HTTPS is allowed to AWS

### Performance Issues

- **High latency**: Check network connection and AWS region proximity
- **Rate limits**: AWS has quota limits per model; request increase if needed
- **Token limits**: Adjust `BEDROCK_MAX_TOKENS` if responses are truncated

## Cost Considerations

AWS Bedrock charges per 1,000 input/output tokens. Current pricing for Claude 3.5 Sonnet v2:
- Input: ~$3 per 1M tokens
- Output: ~$15 per 1M tokens

Monitor usage:
```bash
# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name InvocationCount \
  --dimensions Name=ModelId,Value=anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

## Comparison: When to Use Which Agent

### Use Direct Agent (bedrock_mcp_agent.py) When:
- You want lowest latency
- You don't need ZGuard security controls
- You have direct AWS access
- You're in a development environment
- Cost optimization is priority

### Use ZGuard Agent (bedrock_agent_with_ZGuard.py) When:
- You need centralized security controls
- You want DLP/content filtering
- Your organization mandates AI gateway usage
- You need audit trails and compliance
- You're in a production environment

## Advanced Usage

### Custom System Prompts

Modify the agent initialization to add system prompts:

```python
# In bedrock_mcp_agent.py, modify the chat() method
self.conversation_history.insert(0, {
    "role": "system",
    "content": "You are a Zscaler automation expert..."
})
```

### Batch Processing

Create a script to process multiple queries:

```python
from bedrock_mcp_agent import BedrockMCPAgent

agent = BedrockMCPAgent(...)
agent.start()

queries = [
    "List all ZPA application segments",
    "Show ZIA firewall rules",
    "Get ZDX health metrics"
]

for query in queries:
    response = agent.chat(query)
    print(f"\nQuery: {query}\nResponse: {response}\n")

agent.stop()
```

## Security Best Practices

1. **Credentials**: Use IAM roles instead of access keys when possible
2. **Least Privilege**: Grant only necessary IAM permissions
3. **Rotation**: Rotate AWS credentials regularly
4. **Environment**: Never commit `.env` file to version control
5. **Network**: Use VPC endpoints for Bedrock when available
6. **Logging**: Enable AWS CloudTrail for audit logs

## Support

For issues or questions:
- Check AWS Bedrock documentation: https://docs.aws.amazon.com/bedrock/
- Review boto3 documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- Check Zscaler MCP server documentation

## License

This agent is part of the Zscaler Automation project.
