#!/usr/bin/env python3
"""
AWS Bedrock Agent with Zscaler MCP Server Integration (Direct Connection)

This agent uses AWS Bedrock's Claude 3.5 Sonnet model directly (without ZGuard)
and integrates with the Zscaler MCP server to provide AI-powered Zscaler 
automation capabilities.

The agent can:
- Use natural language to interact with Zscaler services
- Leverage all Zscaler MCP tools (ZPA, ZIA, ZDX, etc.)
- Perform complex multi-step operations
- Provide intelligent insights and automation
"""

import os
import json
import subprocess
import sys
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ZscalerMCPClient:
    """Client to interact with Zscaler MCP server."""
    
    def __init__(self, server_path: str, server_module: str):
        """
        Initialize MCP client.
        
        Args:
            server_path: Path to Python interpreter with MCP server
            server_module: Python module name for MCP server
        """
        self.server_path = server_path
        self.server_module = server_module
        self.process = None
        self.tools = []
        
    def start_server(self):
        """Start the MCP server process."""
        print("[MCP] Starting Zscaler MCP server...")
        
        # Set environment variables for MCP server
        env = os.environ.copy()
        
        try:
            self.process = subprocess.Popen(
                [self.server_path, "-m", self.server_module],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1
            )
            print("[MCP] Server started successfully")
            
            # Initialize the MCP connection
            print("[MCP] Initializing connection...")
            init_response = self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "bedrock-agent",
                    "version": "1.0.0"
                }
            })
            
            if "result" in init_response:
                print("[MCP] Connection initialized successfully")
                
                # Send initialized notification
                self.send_request("notifications/initialized")
                return True
            else:
                print(f"[MCP ERROR] Failed to initialize: {init_response}")
                return False
                
        except Exception as e:
            print(f"[MCP ERROR] Failed to start server: {str(e)}")
            return False
    
    def send_request(self, method: str, params: Dict = None) -> Dict:
        """
        Send JSON-RPC request to MCP server.
        
        Args:
            method: JSON-RPC method name
            params: Method parameters
            
        Returns:
            Response from server
        """
        if not self.process:
            raise RuntimeError("MCP server not started")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method
        }
        
        # Only include params if provided (MCP protocol requires this)
        if params is not None:
            request["params"] = params
        
        request_json = json.dumps(request) + "\n"
        
        try:
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line)
            else:
                return {"error": "No response from server"}
        except Exception as e:
            return {"error": str(e)}
    
    def list_tools(self) -> List[Dict]:
        """
        Get list of available tools from MCP server.
        
        Returns:
            List of tool definitions
        """
        print("[MCP] Fetching available tools...")
        response = self.send_request("tools/list")
        
        if "result" in response and "tools" in response["result"]:
            self.tools = response["result"]["tools"]
            print(f"[MCP] Found {len(self.tools)} available tools")
            return self.tools
        else:
            print(f"[MCP ERROR] Failed to list tools: {response}")
            return []
    
    def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        print(f"[MCP] Calling tool: {tool_name}")
        print(f"[MCP] Arguments: {json.dumps(arguments, indent=2)}")
        
        response = self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "result" in response:
            print(f"[MCP] Tool executed successfully")
            return response["result"]
        else:
            print(f"[MCP ERROR] Tool execution failed: {response}")
            return response
    
    def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            print("[MCP] Stopping server...")
            self.process.terminate()
            self.process.wait(timeout=5)
            print("[MCP] Server stopped")


class BedrockMCPAgent:
    """AWS Bedrock agent with direct connection and MCP integration."""
    
    def __init__(
        self,
        model_id: str,
        aws_region: str,
        max_tokens: int,
        temperature: float
    ):
        """
        Initialize Bedrock agent with direct AWS connection.
        
        Args:
            model_id: Bedrock model ID
            aws_region: AWS region for Bedrock
            max_tokens: Maximum tokens for response
            temperature: Model temperature
        """
        self.model_id = model_id
        self.aws_region = aws_region
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize Bedrock client
        print(f"[BEDROCK] Initializing boto3 client for region: {aws_region}")
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region
        )
        
        # Initialize MCP client
        mcp_path = os.getenv("MCP_SERVER_PATH")
        mcp_module = os.getenv("MCP_SERVER_MODULE")
        
        if not mcp_path or not mcp_module:
            raise ValueError("MCP server configuration missing in .env")
        
        self.mcp_client = ZscalerMCPClient(mcp_path, mcp_module)
        self.conversation_history = []
        self.available_tools = []
        self.api_call_count = 0  # Track API calls to Bedrock
        
    def start(self):
        """Start the agent and MCP server."""
        print("\n" + "="*80)
        print("AWS BEDROCK DIRECT + MCP INTEGRATION")
        print("="*80)
        print(f"\nModel: {self.model_id}")
        print(f"Region: {self.aws_region}")
        print(f"Connection: Direct to AWS Bedrock (no proxy)")
        print("\n" + "="*80 + "\n")
        
        # Start MCP server
        if not self.mcp_client.start_server():
            raise RuntimeError("Failed to start MCP server")
        
        # Get available tools
        self.available_tools = self.mcp_client.list_tools()
        
        if not self.available_tools:
            print("[WARNING] No tools available from MCP server")
            print("[INFO] Proceeding without tools...")
        else:
            print(f"\n[INFO] Agent has access to {len(self.available_tools)} Zscaler tools")
    
    def format_tools_for_bedrock(self) -> List[Dict]:
        """
        Format MCP tools for Bedrock's tool use format.
        
        Returns:
            Tools in Bedrock format
        """
        bedrock_tools = []
        
        for tool in self.available_tools:
            # Claude 3.5 Sonnet uses direct format
            bedrock_tool = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get("inputSchema", {})
            }
            bedrock_tools.append(bedrock_tool)
        
        return bedrock_tools
    
    def invoke_bedrock(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """
        Invoke Bedrock model directly using boto3.
        
        Args:
            messages: Conversation messages
            tools: Available tools
            
        Returns:
            Model response
        """
        # Increment API call counter
        self.api_call_count += 1
        
        # Print API call header
        print(f"\n{'='*80}")
        print(f"[BEDROCK] API Call #{self.api_call_count} to AWS Bedrock")
        print(f"{'='*80}")
        
        # Build request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages
        }
        
        if tools:
            request_body["tools"] = tools
        
        # Print detailed request information
        print(f"\n[DEBUG] Request Details:")
        print(f"  Model ID: {self.model_id}")
        print(f"  Region: {self.aws_region}")
        print(f"  anthropic_version: {request_body['anthropic_version']}")
        print(f"  max_tokens: {request_body['max_tokens']}")
        print(f"  temperature: {request_body['temperature']}")
        print(f"  messages: {len(messages)} message(s)")
        
        # Print message details
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', [])
            print(f"    Message {i+1}: role={role}, content_blocks={len(content) if isinstance(content, list) else 1}")
            
            # Show content types for debugging
            if isinstance(content, list):
                content_types = [block.get('type', 'unknown') for block in content]
                if content_types:
                    print(f"      Content types: {', '.join(content_types)}")
        
        if tools:
            print(f"  tools: {len(tools)} tool(s) available")
            print(f"    Tool names: {', '.join([t['name'] for t in tools])}")
        else:
            print(f"  tools: None")
        
        print(f"\n{'='*80}\n")
        
        # Retry logic for transient errors
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"[BEDROCK] Retry attempt {attempt + 1}/{max_retries} after {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
                print(f"[BEDROCK] Sending request to AWS...")
                
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                
                print(f"[BEDROCK] ✓ API Call #{self.api_call_count} successful")
                return response_body
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                
                # Handle retryable errors
                if error_code in ['ServiceUnavailableException', 'ThrottlingException']:
                    if attempt < max_retries - 1:
                        print(f"[BEDROCK] Transient error ({error_code}), retrying...")
                        continue
                    else:
                        error_msg = f"{error_code}: {error_message}. Max retries reached."
                        print(f"[BEDROCK ERROR] {error_msg}")
                        return {"error": error_msg}
                
                # Handle non-retryable errors immediately
                if error_code == 'ValidationException':
                    error_msg = f"Validation Error: {error_message}"
                elif error_code == 'AccessDeniedException':
                    error_msg = f"Access Denied: Check your AWS credentials and IAM permissions. {error_message}"
                elif error_code == 'ResourceNotFoundException':
                    error_msg = f"Model Not Found: The model '{self.model_id}' is not available in region '{self.aws_region}'. {error_message}"
                else:
                    error_msg = f"AWS Error ({error_code}): {error_message}"
                
                print(f"[BEDROCK ERROR] {error_msg}")
                return {"error": error_msg}
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                print(f"[BEDROCK ERROR] {error_msg}")
                return {"error": error_msg}
    
    def process_tool_use(self, tool_use_block: Dict) -> Dict:
        """
        Process tool use request from model.
        
        Args:
            tool_use_block: Tool use block from model response
            
        Returns:
            Tool execution result
        """
        tool_name = tool_use_block.get("name")
        tool_input = tool_use_block.get("input", {})
        
        print(f"\n[AGENT] Model wants to use tool: {tool_name}")
        
        # Call MCP tool
        result = self.mcp_client.call_tool(tool_name, tool_input)
        
        # Format result as text for Claude
        result_text = json.dumps(result, indent=2)
        
        return {
            "tool_use_id": tool_use_block.get("id"),
            "content": [{"type": "text", "text": result_text}]
        }
    
    def chat(self, user_message: str) -> str:
        """
        Send a message and get response.
        
        Args:
            user_message: User's message
            
        Returns:
            Agent's response
        """
        print(f"\n[USER] {user_message}")
        
        # Reset API call counter for this chat turn
        self.api_call_count = 0
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": [{"type": "text", "text": user_message}]
        })
        
        # Prepare tools
        tools = self.format_tools_for_bedrock() if self.available_tools else None
        
        # Conversation loop to handle tool use
        max_iterations = 5
        iteration = 0
        
        print(f"\n[INFO] Starting agentic loop (max {max_iterations} iterations)")
        print(f"[INFO] Each iteration may make an API call to Bedrock if tools are used\n")
        
        while iteration < max_iterations:
            iteration += 1
            print(f"[AGENT] Starting iteration {iteration}/{max_iterations}")
            
            # Invoke model - THIS MAKES AN API CALL TO BEDROCK
            response = self.invoke_bedrock(self.conversation_history, tools)
            
            if "error" in response:
                error_msg = response['error']
                print(f"\n[ERROR] API call failed: {error_msg}")
                
                # If we have tool results to show, display them
                if iteration > 1 and len(self.conversation_history) > 2:
                    print("\n[INFO] Showing partial results from successful tool calls:")
                    for msg in self.conversation_history:
                        if msg.get("role") == "user" and any(
                            block.get("type") == "tool_result" 
                            for block in msg.get("content", [])
                        ):
                            for block in msg.get("content", []):
                                if block.get("type") == "tool_result":
                                    tool_content = block.get("content", [])
                                    if tool_content:
                                        result_text = tool_content[0].get("text", "")
                                        print(f"\n{result_text}\n")
                
                return f"Error during API call: {error_msg}"
            
            # Get stop reason
            stop_reason = response.get("stop_reason")
            content = response.get("content", [])
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": content
            })
            
            # Check if tool use is needed
            if stop_reason == "tool_use":
                print(f"\n[AGENT] Model requested tool use - will need another API call after processing tools")
                
                # Collect tool results
                tool_results = []
                
                for block in content:
                    if block.get("type") == "tool_use":
                        result = self.process_tool_use(block)
                        tool_results.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": result["tool_use_id"],
                                "content": result["content"]
                            }]
                        })
                
                # Add tool results to history
                self.conversation_history.extend(tool_results)
                
                # Continue conversation with tool results
                print(f"[AGENT] Tool results added to history. Continuing to iteration {iteration + 1}...")
                continue
            
            elif stop_reason == "end_turn":
                # Extract text response
                response_text = ""
                for block in content:
                    if block.get("type") == "text":
                        response_text += block.get("text", "")
                
                print(f"\n{'='*80}")
                print(f"[SUMMARY] Completed in {self.api_call_count} API call(s) to Bedrock")
                print(f"{'='*80}")
                print(f"\n[AGENT] {response_text}")
                return response_text
            
            else:
                return f"Unexpected stop reason: {stop_reason}"
        
        return "Max iterations reached"
    
    def run_interactive(self):
        """Run interactive chat session."""
        print("\n[INFO] Starting interactive session...")
        print("[INFO] Type 'exit' or 'quit' to end the session\n")
        
        try:
            while True:
                user_input = input("\n[YOU] > ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n[INFO] Ending session...")
                    break
                
                if not user_input:
                    continue
                
                response = self.chat(user_input)
                
        except KeyboardInterrupt:
            print("\n\n[INFO] Session interrupted by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the agent and cleanup."""
        print("\n[INFO] Cleaning up...")
        self.mcp_client.stop_server()
        print("[INFO] Agent stopped")


def main():
    """Main entry point."""
    # Load configuration
    model_id = os.getenv("BEDROCK_MODEL_ID")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    max_tokens_str = os.getenv("BEDROCK_MAX_TOKENS")
    temperature_str = os.getenv("BEDROCK_TEMPERATURE")
    
    # Validate configuration
    if not all([model_id, max_tokens_str, temperature_str]):
        print("[ERROR] Missing required environment variables")
        print("Required: BEDROCK_MODEL_ID, AWS_REGION, BEDROCK_MAX_TOKENS, BEDROCK_TEMPERATURE")
        sys.exit(1)
    
    # Convert to appropriate types
    try:
        max_tokens = int(max_tokens_str)
        temperature = float(temperature_str)
    except ValueError as e:
        print(f"[ERROR] Invalid value for BEDROCK_MAX_TOKENS or BEDROCK_TEMPERATURE: {e}")
        sys.exit(1)
    
    # Check AWS credentials
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if not credentials:
            print("[ERROR] No AWS credentials found")
            print("Please configure AWS credentials using one of these methods:")
            print("  1. AWS CLI: aws configure")
            print("  2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
            print("  3. IAM role (if running on EC2/ECS)")
            sys.exit(1)
        print(f"[INFO] AWS credentials found (Access Key: {credentials.access_key[:8]}...)")
    except Exception as e:
        print(f"[ERROR] Failed to check AWS credentials: {e}")
        sys.exit(1)
    
    try:
        # Create and start agent
        agent = BedrockMCPAgent(
            model_id=model_id,
            aws_region=aws_region,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        agent.start()
        
        # Run interactive session
        agent.run_interactive()
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
