# Bedrock Agent with Zscaler AI Guard (ZGuard) Guide

This guide explains how to use the updated `bedrock_agent_with_ZGuard.py` that routes all requests through Zscaler AI Guard instead of directly to AWS Bedrock.

---

## What Changed

### Before (Direct AWS Bedrock)
```
Your App → boto3 → AWS Bedrock → Claude Response
```

### After (Via Zscaler AI Guard)
```
Your App → requests → Zscaler ZGuard → AWS Bedrock → Claude Response
                       ↓
                  Security/DLP/Audit
```

---

## Configuration

### Environment Variables Required

Add to your `.env` file:

```bash
# Required for ZGuard Agent
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
ZSCALER_GATEWAY_URL=https://proxy.zseclipse.net/
ZGUARDSECRET=your_zguard_api_key_here

# Required for MCP Server (Zscaler Tools)
MCP_SERVER_PATH=/path/to/your/mcp/server/.venv/bin/python
MCP_SERVER_MODULE=zscaler_mcp.server

# Zscaler API Credentials (for MCP tools)
ZSCALER_CLIENT_ID=your_client_id_here
ZSCALER_CLIENT_SECRET=your_client_secret_here
ZSCALER_CUSTOMER_ID=your_customer_id_here
```

---

## Usage

### Quick Start

```bash
# Install required package (if not already installed)
pip install requests

# Run the agent
python bedrock_agent_with_ZGuard.py
```

### Expected Output

```
================================================================================
AWS BEDROCK VIA Zscaler AI Guard + MCP INTEGRATION
================================================================================

Model: anthropic.claude-3-5-sonnet-20240620-v1:0
Gateway: https://proxy.zseclipse.net
Endpoint: https://proxy.zseclipse.net/model/anthropic.claude-3-5-sonnet-20240620-v1:0/invoke

================================================================================

[MCP] Starting Zscaler MCP server...
[MCP] Server started successfully
[MCP] Initializing connection...
[MCP] Connection initialized successfully
[MCP] Fetching available tools...
[MCP] Found 50+ available tools

[INFO] Agent has access to 50+ Zscaler tools
[INFO] Starting interactive session...
[INFO] Type 'exit' or 'quit' to end the session

[YOU] >
```

### Example Interaction

```
[YOU] > List all ZPA application segments

[ZGUARD] Sending request to: https://proxy.zseclipse.net/model/...
[ZGUARD] Request successful (status: 200)
[AGENT] Model wants to use tool: zpa_list_application_segments
[MCP] Calling tool: zpa_list_application_segments
[MCP] Tool executed successfully

[AGENT] I found 15 ZPA application segments in your environment:

1. HR Portal (enabled)
   - Domain: hr.company.com
   - App Connector Group: US-East-Connectors
   
2. Finance System (enabled)
   - Domain: finance.company.com
   - App Connector Group: US-West-Connectors
   
...
```

---

## Technical Details

### API Endpoint Format

The agent uses Zscaler's Bedrock-native endpoint format:

```
POST https://proxy.zseclipse.net/model/{model_id}/invoke

Headers:
  X-ApiKey: {your_zguard_secret}
  Content-Type: application/json

Body:
{
  "anthropic_version": "bedrock-2023-05-31",
  "max_tokens": 4096,
  "temperature": 0.7,
  "messages": [
    {
      "role": "user",
      "content": "Your message here"
    }
  ],
  "tools": [ ... ]  // Optional: for tool use
}
```

### Key Code Changes

#### 1. Replaced boto3 with requests

**Before:**
```python
import boto3

self.bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=region
)
```

**After:**
```python
import requests

self.endpoint_url = f"{zscaler_gateway_url}/model/{model_id}/invoke"
```

#### 2. Updated invoke_bedrock Method

**Before (Direct AWS):**
```python
response = self.bedrock.invoke_model(
    modelId=self.model_id,
    body=json.dumps(request_body)
)
response_body = json.loads(response['body'].read())
```

**After (Via Zscaler):**
```python
headers = {
    "X-ApiKey": self.zguard_api_key,
    "Content-Type": "application/json"
}

response = requests.post(
    self.endpoint_url,
    headers=headers,
    json=request_body,
    timeout=120
)

response_body = response.json()
```

#### 3. Updated Constructor

**Before:**
```python
def __init__(self, model_id: str, region: str, ...):
    self.region = region
    self.bedrock = boto3.client(...)
```

**After:**
```python
def __init__(self, model_id: str, zscaler_gateway_url: str, zguard_api_key: str, ...):
    self.zscaler_gateway_url = zscaler_gateway_url
    self.zguard_api_key = zguard_api_key
    self.endpoint_url = f"{zscaler_gateway_url}/model/{model_id}/invoke"
```

---

## Testing the Connection

### Test 1: Direct Curl Command

```bash
curl --location 'https://proxy.zseclipse.net/model/anthropic.claude-3-5-sonnet-20240620-v1:0/invoke' \
  --header 'X-ApiKey: your_zguard_api_key_here' \
  --header 'Content-Type: application/json' \
  --data '{
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 100,
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ]
  }'
```

### Test 2: Run the Agent

```bash
python bedrock_agent_with_ZGuard.py
```

---

## Error Handling & HTTP Status Codes

The agent includes comprehensive error handling with user-friendly messages for all scenarios.

### HTTP Status Code Reference

| Code | Meaning | User-Friendly Message |
|------|---------|----------------------|
| **200** | ✅ Success | Request successful |
| **400** | Bad Request | The request body was invalid. Please check your input format. |
| **401** | Unauthorized | Authentication failed. Check your API key (ZGUARDSECRET) or network access. |
| **403** | Forbidden | Request blocked by security policy (see details below) |
| **404** | Not Found | AI Gateway policy or endpoint not found. Verify configuration. |
| **429** | Rate Limit | Too many requests. Please wait and try again. |
| **500** | Server Error | Zscaler AI Guard error. Try again later. |
| **502** | Bad Gateway | Cannot connect to AWS Bedrock backend (not configured). |
| **503** | Unavailable | AI Gateway temporarily unavailable. Try again later. |
| **504** | Timeout | Request to AWS Bedrock timed out. Try again. |

### HTTP 403 - Policy Violations (Important!)

When your request is blocked by Zscaler security policies, you'll see:

```
[ZGUARD ERROR] HTTP 403: Policy blocked the request
[ZGUARD ERROR] Forbidden: Your request was blocked by Zscaler security policy. This may indicate:
  - Content policy violation (e.g., inappropriate content, hate speech)
  - DLP policy blocking sensitive data
  - Security policy restriction
Please review your input and try again with appropriate content.
```

**Common 403 Triggers:**
- 🚫 Hate speech or inappropriate content
- 🚫 Requests containing PII (Personal Identifiable Information)
- 🚫 Sensitive data like credit cards, SSNs, API keys
- 🚫 Malicious prompts or injection attempts
- 🚫 Custom policy violations configured by your organization

**Example:**
```
[YOU] > Give me a hate speech for a political campaign

[ZGUARD ERROR] HTTP 403: Policy blocked the request
[ZGUARD ERROR] Forbidden: Your request was blocked...

[AGENT] Error: Forbidden: Your request was blocked by Zscaler security policy...
```

### Other Common Errors

#### Connection Errors
```
[ZGUARD ERROR] Connection Error: Unable to connect to Zscaler AI Guard.
Please check your network connection.
```

**Solutions:**
- Verify internet connection
- Check if `proxy.us1.zseclipse.net` is reachable
- Check firewall settings
- Verify VPN connection if required

#### Timeout Errors
```
[ZGUARD ERROR] Request timeout (>120s): The request took too long to complete.
```

**Solutions:**
- Try a shorter prompt
- Check if AWS Bedrock is experiencing issues
- Reduce `max_tokens` value
- Try again later

## Troubleshooting

### Error: "Missing required environment variables"

**Symptom:**
```
[ERROR] Missing required environment variables
Required: BEDROCK_MODEL_ID, ZGUARDSECRET
```

**Solution:** Check your `.env` file has:
```bash
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
ZGUARDSECRET=your_zguard_api_key_here
```

### Error: "HTTP 502 Bad Gateway"

**Symptom:**
```
[ZGUARD ERROR] HTTP 502: Bad Gateway
Cannot connect to AWS Bedrock backend
```

**Cause:** AWS Bedrock backend not configured in Zscaler AI Guard

**Solution:** Contact your Zscaler administrator to:
1. Configure AWS Bedrock as a backend provider
2. Add AWS credentials (Access Key/Secret)
3. Enable the Claude model
4. Link to your API key

### Error: "HTTP 401 Unauthorized"

**Symptom:**
```
[ZGUARD ERROR] HTTP 401: Authentication failed
```

**Cause:** Invalid or expired API key

**Solution:** 
1. Verify `ZGUARDSECRET` in `.env` matches your Zscaler AI Guard API key
2. Check if API key has expired
3. Verify network access control policies

### Error: "HTTP 400 Bad Request"

**Symptom:**
```
[ZGUARD ERROR] HTTP 400: Malformed input request
```

**Cause:** Incorrect request format

**Solution:** 
- Ensure `anthropic_version` is at root level, not inside messages
- Verify JSON structure matches Bedrock API format
- Check for invalid characters in prompt

### Error: "HTTP 429 Rate Limit"

**Symptom:**
```
[ZGUARD ERROR] HTTP 429: Too many requests
```

**Cause:** Exceeded rate limits

**Solution:**
- Wait before sending next request
- Implement rate limiting in your application
- Contact admin to increase rate limits
- Use exponential backoff for retries

### Error: "Connection timeout"

**Symptom:**
```
[ZGUARD ERROR] Connection Error: Unable to connect
```

**Cause:** Network or firewall blocking Zscaler

**Solution:** 
- Check network connectivity to `proxy.us1.zseclipse.net`
- Verify firewall allows HTTPS to Zscaler
- Check if VPN is required
- Test with: `curl -I https://proxy.zseclipse.net`

---

## Best Practices

### 1. Use Environment-Specific Configs

```bash
# .env.development
ZSCALER_GATEWAY_URL=https://proxy-dev.us1.zseclipse.net
ZGUARDSECRET=dev_api_key

# .env.production
ZSCALER_GATEWAY_URL=https://proxy.zseclipse.net
ZGUARDSECRET=prod_api_key
```

### 2. Implement Retry Logic

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
```

### 3. Monitor API Key Usage

- Rotate keys every 90 days
- Use separate keys per environment
- Track usage per key
- Set up alerts for unusual activity

### 4. Cache Responses

For repeated queries:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(query: str) -> str:
    return agent.chat(query)
```

---

## Summary

✅ **Updated**: `bedrock_agent_with_ZGuard.py` now routes through Zscaler AI Guard
✅ **Added**: Request timeout handling (120s)
✅ **Added**: Better error messages
✅ **Added**: Logging of request/response status
✅ **Removed**: boto3 dependency (replaced with requests)
✅ **Configured**: `.env` file with Zscaler gateway settings

**Next Steps:**
1. Test the connection: `python bedrock_agent_with_ZGuard.py`
2. Verify in Zscaler AI Guard dashboard
3. Configure security policies as needed
4. Deploy to production when ready

**Remember:** All prompts are now going through Zscaler AI Guard, giving you full visibility, security, and control over AI usage! 🚀
