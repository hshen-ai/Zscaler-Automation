# Multiple API Calls to AI Guard - Explanation and Fix

## Problem Identified

**YES**, the agent was sending multiple prompts to AI Guard, but this is **by design** for agentic workflows using tool use (function calling).

## Why Multiple API Calls Happen

The agent uses an **agentic loop** pattern that requires multiple API calls:

### Example Flow:
```
1. User asks: "List all ZPA application segments"
   ↓
2. [API CALL #1] Send user message to AI Guard/Bedrock
   ↓
3. Model responds: "I need to use the zpa_list_application_segments tool"
   ↓
4. Agent executes the tool locally (calls MCP server)
   ↓
5. [API CALL #2] Send tool results back to AI Guard/Bedrock
   ↓
6. Model responds: "Here are the results: [formatted response]"
   ↓
7. Return final answer to user
```

**Result**: 2 API calls to AI Guard for a single user query that requires tool use.

### Breakdown:
- **API Call #1**: User message → Model decides to use tool
- **API Call #2**: Tool results → Model formats final response
- Each tool use iteration adds another API call

## What Was Fixed

The code now includes **enhanced visibility** to make these multiple calls transparent:

### 1. **API Call Counter**
```python
self.api_call_count = 0  # Track API calls to ZGuard
```

### 2. **Clear Call Logging**
```
================================================================================
[ZGUARD] API Call #1 to AI Guard
================================================================================
[ZGUARD] Sending request to: https://your-gateway/model/...
[ZGUARD] ✓ API Call #1 successful (status: 200)
```

### 3. **Iteration Tracking**
```
[INFO] Starting agentic loop (max 5 iterations)
[INFO] Each iteration may make an API call to ZGuard if tools are used

[AGENT] Starting iteration 1/5
[AGENT] Model requested tool use - will need another API call after processing tools
[AGENT] Tool results added to history. Continuing to iteration 2...
```

### 4. **Summary Report**
```
================================================================================
[SUMMARY] Completed in 2 API call(s) to ZGuard
================================================================================
```

## This Behavior is Normal and Expected

### Why it's necessary:
- **Agentic AI** requires a back-and-forth between the model and tools
- The model needs to see tool results before it can formulate a final response
- This is how Claude's function calling / tool use works
- Alternative would be to NOT use tools and directly call APIs from Python (but then you lose AI intelligence)

### Cost implications:
- Simple queries without tools: **1 API call**
- Queries requiring 1 tool: **2 API calls** (tool request + final response)
- Complex queries with multiple tools: **3-5 API calls** (depending on tools needed)

## How to Optimize

If you want to reduce API calls:

### Option 1: Reduce max_iterations (not recommended)
```python
max_iterations = 2  # Down from 5
```
⚠️ **Warning**: May prevent complex multi-step operations

### Option 2: Use streaming (future enhancement)
- Not currently implemented
- Would allow real-time updates but same number of calls

### Option 3: Disable tools for simple queries
```python
# In chat method, check if query needs tools
if is_simple_query(user_message):
    tools = None  # Skip tool use
```

### Option 4: Batch operations (recommended)
Instead of asking multiple separate questions:
```
User: "List ZPA segments"      [2 API calls]
User: "List ZIA rules"         [2 API calls]
Total: 4 API calls
```

Batch them:
```
User: "List both ZPA segments and ZIA rules"  [3 API calls]
- Call #1: Model plans to use 2 tools
- Call #2: After first tool result
- Call #3: After second tool result → final response
```

## Monitoring API Usage

The updated code now provides full visibility:

```bash
# Run the agent
python bedrock_agent_with_ZGuard.py

# You'll see output like:
[USER] List my ZPA application segments

[INFO] Starting agentic loop (max 5 iterations)
[INFO] Each iteration may make an API call to ZGuard if tools are used

[AGENT] Starting iteration 1/5

================================================================================
[ZGUARD] API Call #1 to AI Guard
================================================================================
[ZGUARD] ✓ API Call #1 successful (status: 200)

[AGENT] Model requested tool use - will need another API call after processing tools
[MCP] Calling tool: zpa_list_application_segments
[MCP] Tool executed successfully
[AGENT] Tool results added to history. Continuing to iteration 2...

[AGENT] Starting iteration 2/5

================================================================================
[ZGUARD] API Call #2 to AI Guard
================================================================================
[ZGUARD] ✓ API Call #2 successful (status: 200)

================================================================================
[SUMMARY] Completed in 2 API call(s) to ZGuard
================================================================================

[AGENT] [Final formatted response with the segments]
```

## Comparison with Other AI Services

This multi-call behavior is **standard** for agentic AI:

| Service | Tool Use Pattern | API Calls per Query |
|---------|-----------------|---------------------|
| **AWS Bedrock (via ZGuard)** | Multi-turn | 2-5 calls |
| OpenAI Function Calling | Multi-turn | 2-5 calls |
| Anthropic Claude API | Multi-turn | 2-5 calls |
| Google Vertex AI | Multi-turn | 2-5 calls |
| Azure OpenAI | Multi-turn | 2-5 calls |

**All major AI providers work this way** when using function/tool calling.

## Recommendations

✅ **Normal Usage**: Accept that 2-5 API calls per complex query is expected and normal

✅ **Monitor Costs**: Use the new logging to track actual API call counts

✅ **Batch Requests**: Combine multiple related queries into one when possible

✅ **Cache Results**: Store frequently requested data locally

❌ **Don't Reduce max_iterations**: This will break complex operations

❌ **Don't Disable Tools**: You'll lose the AI's ability to interact with Zscaler

## Summary

The "multiple prompts to AI Guard" issue is:
- ✅ **Identified and documented**
- ✅ **Now visible with enhanced logging**
- ✅ **Expected behavior for agentic AI**
- ✅ **Cannot be eliminated without losing functionality**
- ✅ **Consistent with industry standards**

The fix provides **transparency** so you can monitor and optimize your usage accordingly.
