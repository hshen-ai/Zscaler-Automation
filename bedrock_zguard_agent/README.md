## 📞 Support Disclaimer

- This script is not an officially supported feature of Zscaler
- It is created for learning and testing purposes only

# Bedrock Agent via Zscaler AI Guard (ZGuard)

A testing-only AWS Bedrock agent that routes all requests through Zscaler AI Guard for enhanced security, compliance, and monitoring.

## 📁 What's in This Folder

```
bedrock_zguard_agent/
├── README.md                           # This file
├── .env.example                        # Clean environment configuration template
├── bedrock_agent_with_ZGuard.py       # Main agent script
└── BEDROCK_ZGUARD_AGENT_GUIDE.md     # Complete documentation
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Navigate to this folder
cd bedrock_zguard_agent

# Copy the example .env file
cp .env.example .env

# Edit .env with your credentials
# Required: ZGUARDSECRET, ZSCALER_CLIENT_ID, ZSCALER_CLIENT_SECRET, ZSCALER_CUSTOMER_ID
```

### 2. Install Dependencies

```bash
pip install requests python-dotenv
```

### 3. Run the Agent

```bash
python bedrock_agent_with_ZGuard.py
```

## 🔑 Required Credentials

You need to configure the following in your `.env` file:

### Zscaler AI Guard
- `ZGUARDSECRET` - Your Zscaler AI Guard API key
- `ZSCALER_GATEWAY_URL` - Gateway URL (default: https://proxy.zseclipse.net)

### Zscaler API (for MCP tools)
- `ZSCALER_CLIENT_ID` - Zscaler API client ID
- `ZSCALER_CLIENT_SECRET` - Zscaler API client secret
- `ZSCALER_CUSTOMER_ID` - Zscaler customer ID

### MCP Server
- `MCP_SERVER_PATH` - Path to your Zscaler MCP server Python interpreter
- `MCP_SERVER_MODULE` - Module name (default: zscaler_mcp.server)

## 📊 What This Agent Does

### Architecture

```
Your Prompt → Zscaler AI Guard → AWS Bedrock → Claude Response
                     ↓
            Security/DLP/Audit/Monitoring
```

### Features

✅ **Security**
- blocking malicious URLs, invisible text, adversarial attacks;

✅ **Content moderation**
- filtering PII, secrets, off-topic inputs, and toxic content; 

✅ **Visibility**
- tracking prompts and responses with classification capabilities. 

✅ **Data Security**
- Provided with the combination of GEN AI DLP. 


### Policy Blocking (HTTP 403)

The agent includes smart error handling for policy violations:

```
[YOU] > Give me a hate speech for a political campaign

[ZGUARD ERROR] HTTP 403: Policy blocked the request
[ZGUARD ERROR] Forbidden: Your request was blocked by Zscaler security policy.
  - Content policy violation (e.g., inappropriate content, hate speech)
  - DLP policy blocking sensitive data
  - Security policy restriction
```

### e.g. What can be Blocked

- 🚫 Hate speech and inappropriate content
- 🚫 PII (Personal Identifiable Information)
- 🚫 Credit cards, SSNs, API keys
- 🚫 Malicious prompts
- 🚫 Custom policy violations
- 🚫 content matching certain topic that you can define in natural language
- 🚫 all above in prompts and responses

## 📖 Documentation

For complete documentation, see **BEDROCK_ZGUARD_AGENT_GUIDE.md** in this folder, which covers:

- Complete setup instructions
- API endpoint details
- Error handling reference
- Troubleshooting guide
- Security features
- Monitoring and analytics
- Best practices

## 🔍 Testing

### Test the Connection

```bash
# Basic functionality test
python bedrock_agent_with_ZGuard.py

# Then try a simple prompt
[YOU] > Hello, how are you?
```

### Test Policy Blocking

```bash
# Test content filtering (should get 403)
[YOU] > Give me inappropriate content

# Should see:
# [ZGUARD ERROR] HTTP 403: Policy blocked the request
```

## 🆚 Comparison with Direct AWS Access

### bedrock_agent.py (Direct AWS)
- ❌ No security policies
- ❌ No audit logging
- ❌ No DLP protection

### bedrock_agent_with_ZGuard.py (This Agent)
- ✅ Enterprise security
- ✅ Complete audit trail
- ✅ DLP and content filtering
- ✅ Centralized monitoring

## 🐛 Troubleshooting

### Error: Missing environment variables

```bash
# Check your .env file
cat .env

# Ensure these are set:
# - BEDROCK_MODEL_ID
# - ZGUARDSECRET
# - ZSCALER_CLIENT_ID
# - ZSCALER_CLIENT_SECRET
# - ZSCALER_CUSTOMER_ID
```

### Error: HTTP 502 Bad Gateway

AWS Bedrock backend not configured in Zscaler. Contact your Zscaler admin to:
1. Add AWS Bedrock as backend provider
2. Configure AWS credentials
3. Enable Claude 3.5 Sonnet model

### Error: HTTP 403 Forbidden

Your request was blocked by security policy. Review your prompt for:
- Inappropriate content
- Sensitive data (PII, credentials)
- Policy violations

## 📝 Example Session

```
================================================================================
AWS BEDROCK VIA Zscaler AI Guard + MCP INTEGRATION
================================================================================

Model: anthropic.claude-3-5-sonnet-20240620-v1:0
Gateway: https://proxy.zseclipse.net
Endpoint: https://proxy.zseclipse.net/model/.../invoke

[YOU] > List my ZPA application segments

[ZGUARD] Sending request to: https://proxy.zseclipse.net/model/...
[ZGUARD] Request successful (status: 200)
[AGENT] Model wants to use tool: zpa_list_application_segments
[MCP] Calling tool: zpa_list_application_segments
[MCP] Tool executed successfully

[AGENT] I found 15 ZPA application segments in your environment:

1. HR Portal (enabled)
   - Domain: hr.company.com
   ...
```

## 🔐 Security Best Practices

1. **Never commit .env file** - Use .env.example as template
2. **Rotate API keys** - Every 90 days minimum
3. **Use separate keys** - Different keys for dev/staging/prod
4. **Monitor usage** - Check Zscaler Analytics regularly
5. **Test policies** - Verify security policies work as expected

## 📦 Dependencies

```bash
pip install requests python-dotenv
```

Optional (for testing):
```bash
pip install boto3  # For comparing with direct AWS access
```

## 🚦 Status Indicators

| Indicator | Meaning |
|-----------|---------|
| `[ZGUARD]` | Zscaler AI Guard operation |
| `[MCP]` | Zscaler MCP tool operation |
| `[AGENT]` | Claude model response |
| `[ZGUARD ERROR]` | Error from Zscaler gateway |
| `[MCP ERROR]` | Error from MCP tool |

## 📊 Monitoring

View your usage in Zscaler Admin Portal:
1. Go to **ZSlogin** → **ZGuard**
2. Check dashboard, insights, usage
3. check the tab of AI Applications

---

**Ready to get started?** Run `python bedrock_agent_with_ZGuard.py` and start chatting! 🚀

For detailed documentation, see **BEDROCK_ZGUARD_AGENT_GUIDE.md** in this folder.
