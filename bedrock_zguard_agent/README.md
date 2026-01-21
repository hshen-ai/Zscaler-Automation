# Zscaler Automation with AWS Bedrock

## Overview

This repository contains powerful AI-driven automation agents for Zscaler operations using AWS Bedrock:

1. **Bedrock MCP Agent** (`bedrock_mcp_agent.py`) - AWS Bedrock-powered agent with Zscaler MCP server integration for AI-driven Zscaler automation
2. **Bedrock ZGuard Agent** (`bedrock_zguard_agent/`) - Enhanced security with Zscaler AI Gateway (ZGuard) integration for prompt security and compliance

## Core Dependencies

```
python-dotenv==1.1.1
boto3==1.35.0
```

See `requirements.txt` for complete dependency list.

## What Can These Agents Do?

### Bedrock MCP Agent

An intelligent agent powered by **AWS Bedrock's Claude 3.5 Sonnet** model that integrates with the **Zscaler MCP server** to provide natural language automation of Zscaler operations. The agent can:

- Execute Zscaler operations using natural language commands
- Leverage 100+ Zscaler MCP tools (ZPA, ZIA, ZDX, etc.)
- Perform complex multi-step operations autonomously
- Provide intelligent insights and recommendations

**Key Features:**
- Direct AWS Bedrock integration (no proxy)
- Comprehensive error handling and retry logic
- API call tracking and detailed logging
- Interactive chat interface
- Support for complex multi-step operations

### Bedrock ZGuard Agent

Enhanced version with **Zscaler AI Gateway (ZGuard)** integration that adds:

- **Prompt Security** - Detects and blocks malicious prompts, jailbreak attempts, and injection attacks
- **PII Protection** - Identifies and redacts sensitive information (SSNs, credit cards, etc.)
- **Compliance Controls** - Enforces content policies and regulatory requirements
- **Audit Logging** - Complete visibility into AI interactions

## Prerequisites

### 1. AWS Configuration

- AWS account with Bedrock access enabled
- Claude 3.5 Sonnet model enabled in your region
- AWS credentials configured via AWS CLI or environment variables

```bash
# Install AWS CLI (if not already installed)
# macOS
brew install awscli

# Ubuntu/Debian
sudo apt-get install awscli

# Configure AWS credentials
aws configure
```

**Note:** For detailed AWS access key setup, see [AWS_ACCESS_KEY_SETUP.md](AWS_ACCESS_KEY_SETUP.md)

### 2. Python Environment

- Python 3.9 or higher
- Required Python packages

```bash
pip install -r requirements.txt
```

### 3. Zscaler MCP Server

Install and configure the Zscaler MCP server for full functionality.

**Note:** The Zscaler MCP server referenced in this project is available at: https://github.com/zscaler/zscaler-mcp-server

```bash
# Clone and set up Zscaler MCP server
git clone https://github.com/zscaler/zscaler-mcp-server.git
cd zscaler-mcp-server
# Follow the installation guide in the repository
```

### 4. Zscaler AI Gateway (Optional - for ZGuard Agent)

For enhanced security with prompt protection, configure Zscaler AI Gateway access.

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/hshen-ai/Zscaler-Automation.git
cd Zscaler-Automation
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables** (see Configuration section below)

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following configuration:

```bash
# AWS Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_REGION=us-east-1
BEDROCK_MAX_TOKENS=4096
BEDROCK_TEMPERATURE=0.7

# Zscaler MCP Server Configuration
MCP_SERVER_PATH=/path/to/zscaler-mcp-server/.venv/bin/python
MCP_SERVER_MODULE=zscaler_mcp.server

# Zscaler API Credentials (required for MCP server)
ZSCALER_CLIENT_ID=your_client_id
ZSCALER_CLIENT_SECRET=your_client_secret
ZSCALER_CUSTOMER_ID=your_customer_id

# ZIA Configuration (optional)
ZIA_CLOUD=zscaler.net
ZIA_USERNAME=your_zia_username
ZIA_PASSWORD=your_zia_password
ZIA_API_KEY=your_zia_api_key

# Zscaler AI Gateway (ZGuard) - Optional for enhanced security
ZGUARD_ENDPOINT=https://your-tenant.zpagw.net
ZGUARD_API_KEY=your_zguard_api_key
```

### Configuration Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `BEDROCK_MODEL_ID` | AWS Bedrock model identifier | Yes | Claude 3.5 Sonnet |
| `AWS_REGION` | AWS region for Bedrock | Yes | us-east-1 |
| `BEDROCK_MAX_TOKENS` | Maximum response tokens | No | 4096 |
| `BEDROCK_TEMPERATURE` | Model creativity (0-1) | No | 0.7 |
| `MCP_SERVER_PATH` | Path to MCP Python interpreter | Yes* | - |
| `MCP_SERVER_MODULE` | MCP server module name | Yes* | zscaler_mcp.server |
| `ZSCALER_CLIENT_ID` | Zscaler API client ID | Yes | - |
| `ZSCALER_CLIENT_SECRET` | Zscaler API client secret | Yes | - |
| `ZSCALER_CUSTOMER_ID` | Zscaler customer/tenant ID | Yes | - |
| `ZGUARD_ENDPOINT` | Zscaler AI Gateway endpoint | No** | - |
| `ZGUARD_API_KEY` | ZGuard API authentication key | No** | - |

\* Required for MCP agent functionality  
\*\* Required for ZGuard agent only

## Usage

### Bedrock MCP Agent

Start the MCP-integrated agent:

```bash
python3 bedrock_mcp_agent.py
```

**Example interactions:**

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

### Bedrock ZGuard Agent

For enhanced security with prompt protection:

```bash
cd bedrock_zguard_agent
python3 bedrock_agent_with_ZGuard.py
```

The ZGuard agent provides additional security layers including:
- Malicious prompt detection
- PII redaction
- Content policy enforcement
- Detailed audit logging

## Example Commands

### Query Information

```
- "List all ZPA application segments"
- "Show me the firewall rules in ZIA"
- "What are the current ZDX alerts?"
- "Get details about the application segment named 'Corporate-Apps'"
```

### Complex Operations

```
- "Create a new ZPA application segment for the HR portal"
- "Analyze the health of my ZPA connectors"
- "Find all application segments using port 443"
- "Show me which users have accessed the Finance app today"
```

### Insights and Analysis

```
- "What's the status of my Zscaler infrastructure?"
- "Are there any security issues I should be aware of?"
- "Which applications have the most traffic?"
- "Recommend optimizations for my ZPA configuration"
```

## Architecture

```
┌─────────────┐
│    User     │
│  (Natural   │
│  Language)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│   Zscaler AI Gateway    │  (Optional - ZGuard Agent)
│   ├─ Prompt Security    │
│   ├─ PII Protection     │
│   └─ Compliance Check   │
└──────┬──────────────────┘
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

## Security Features

- ✅ **Read-Only by Default** - MCP server operates in read-only mode unless explicitly enabled
- ✅ **AWS IAM Integration** - Uses standard AWS credential chain (IAM roles, profiles)
- ✅ **API Permission Control** - Limited by your Zscaler API client permissions
- ✅ **Audit Logging** - All operations are logged for tracking
- ✅ **Prompt Security** - ZGuard agent detects malicious prompts (when enabled)
- ✅ **PII Protection** - Automatic detection and redaction of sensitive data (ZGuard)
- ✅ **Compliance Controls** - Enforces content policies (ZGuard)

## Troubleshooting

### Bedrock Access Issues

**Problem:** Cannot access Bedrock model

**Solution:**
```bash
# Check if Claude model is available in your region
aws bedrock list-foundation-models --region your-region

# Request model access in AWS Console if needed
# AWS Console > Bedrock > Model Access
```

### MCP Server Connection Issues

**Problem:** Failed to start MCP server

**Solution:**
- Verify `MCP_SERVER_PATH` points to correct Python interpreter
- Check Zscaler credentials are valid in `.env`
- Ensure MCP server dependencies are installed

### AWS Credentials Issues

**Problem:** AWS authentication errors

**Solution:**
- Verify AWS credentials are configured: `aws sts get-caller-identity`
- Check IAM permissions for Bedrock access
- See [AWS_ACCESS_KEY_SETUP.md](AWS_ACCESS_KEY_SETUP.md) for detailed setup

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

## Documentation

- [Bedrock MCP Agent Guide](BEDROCK_MCP_AGENT_GUIDE.md) - Detailed setup and usage
- [Bedrock ZGuard Agent Guide](bedrock_zguard_agent/BEDROCK_ZGUARD_AGENT_GUIDE.md) - ZGuard integration details
- [API Testing Guide](API_TESTING_GUIDE.md) - API testing examples
- [AWS Access Key Setup](AWS_ACCESS_KEY_SETUP.md) - AWS credentials configuration
- [Zscaler AI Gateway Setup](ZSCALER_AI_GATEWAY_BEDROCK_SETUP.md) - ZGuard configuration

## Support & References

- [Zscaler Developer Portal](https://help.zscaler.com/developer)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Zscaler MCP Server](https://github.com/zscaler/zscaler-mcp-server)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## Version

- **Version:** 2.0
- **Last Updated:** January 2026
- **Python:** 3.9+
- **AWS Bedrock:** Claude 3.5 Sonnet
- **MCP Protocol:** Latest

---

## License

This project is provided as-is for Zscaler customers to automate operations.
