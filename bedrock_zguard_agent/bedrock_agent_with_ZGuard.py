#!/usr/bin/env python3
"""
AWS Bedrock Agent with Zscaler MCP Server Integration

This agent uses AWS Bedrock's Claude 3.5 Sonnet model and integrates with
the Zscaler MCP server to provide AI-powered Zscaler automation capabilities.

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
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
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


class BedrockAgent:
    """AWS Bedrock agent with Zscaler AI Guard (ZGuard) and MCP integration."""
    
    def __init__(
        self,
        model_id: str,
        zscaler_gateway_url: str,
        zguard_api_key: str,
        max_tokens: int,
        temperature: float
    ):
        """
        Initialize Bedrock agent via Zscaler AI Guard.
        
        Args:
            model_id: Bedrock model ID
            zscaler_gateway_url: Zscaler AI Guard base URL
            zguard_api_key: Zscaler AI Guard API key
            max_tokens: Maximum tokens for response
            temperature: Model temperature
        """
        self.model_id = model_id
        self.zscaler_gateway_url = zscaler_gateway_url
        self.zguard_api_key = zguard_api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Build the full endpoint URL
        self.endpoint_url = f"{zscaler_gateway_url}/model/{model_id}/invoke"
        
        # Initialize MCP client
        mcp_path = os.getenv("MCP_SERVER_PATH")
        mcp_module = os.getenv("MCP_SERVER_MODULE")
        
        if not mcp_path or not mcp_module:
            raise ValueError("MCP server configuration missing in .env")
        
        self.mcp_client = ZscalerMCPClient(mcp_path, mcp_module)
        self.conversation_history = []
        self.available_tools = []
        
    def start(self):
        """Start the agent and MCP server."""
        print("\n" + "="*80)
        print("AWS BEDROCK VIA Zscaler AI Guard + MCP INTEGRATION")
        print("="*80)
        print(f"\nModel: {self.model_id}")
        print(f"Gateway: {self.zscaler_gateway_url}")
        print(f"Endpoint: {self.endpoint_url}")
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
            # Claude 3.5 Sonnet uses direct format, not toolSpec wrapper
            bedrock_tool = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get("inputSchema", {})
            }
            bedrock_tools.append(bedrock_tool)
        
        return bedrock_tools
    
    def invoke_bedrock(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """
        Invoke Bedrock model via Zscaler AI Guard.
        
        Args:
            messages: Conversation messages
            tools: Available tools
            
        Returns:
            Model response
        """
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages
        }
        
        if tools:
            request_body["tools"] = tools
        
        headers = {
            "X-ApiKey": self.zguard_api_key,
            "Content-Type": "application/json"
        }
        
        try:
            print(f"[ZGUARD] Sending request to: {self.endpoint_url}")
            
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                json=request_body,
                timeout=120
            )
            
            # Handle different HTTP status codes with user-friendly messages
            if response.status_code == 200:
                response_body = response.json()
                print(f"[ZGUARD] Request successful (status: {response.status_code})")
                return response_body
            
            # Error handling with specific messages
            elif response.status_code == 400:
                error_msg = "Bad Request: The request body was invalid. Please check your input format."
                print(f"[ZGUARD ERROR] HTTP 400: {error_msg}")
                print(f"[ZGUARD ERROR] Response: {response.text}")
                return {"error": error_msg}
            
            elif response.status_code == 401:
                error_msg = "Unauthorized: Authentication failed. Please check your API key (ZGUARDSECRET) or network access permissions."
                print(f"[ZGUARD ERROR] HTTP 401: {error_msg}")
                return {"error": error_msg}
            
            elif response.status_code == 403:
                error_msg = "Forbidden: Your request was blocked by Zscaler security policy. This may indicate:\n"
                error_msg += "  - Content policy violation (e.g., inappropriate content, hate speech)\n"
                error_msg += "  - DLP policy blocking sensitive data\n"
                error_msg += "  - Security policy restriction\n"
                error_msg += "Please review your input and try again with appropriate content."
                print(f"[ZGUARD ERROR] HTTP 403: Policy blocked the request")
                print(f"[ZGUARD ERROR] {error_msg}")
                return {"error": error_msg}
            
            elif response.status_code == 404:
                error_msg = "Not Found: The AI Gateway policy or endpoint was not found. Please verify your configuration."
                print(f"[ZGUARD ERROR] HTTP 404: {error_msg}")
                return {"error": error_msg}
            
            elif response.status_code == 429:
                error_msg = "Rate Limit Exceeded: Too many requests. Please wait a moment and try again."
                print(f"[ZGUARD ERROR] HTTP 429: {error_msg}")
                return {"error": error_msg}
            
            elif response.status_code == 500:
                error_msg = "Internal Server Error: Zscaler AI Guard encountered an error. Please try again later."
                print(f"[ZGUARD ERROR] HTTP 500: {error_msg}")
                print(f"[ZGUARD ERROR] Response: {response.text}")
                return {"error": error_msg}
            
            elif response.status_code == 502:
                error_msg = "Bad Gateway: Cannot connect to AWS Bedrock backend. This usually means:\n"
                error_msg += "  - AWS Bedrock is not configured in Zscaler AI Guard\n"
                error_msg += "  - AWS credentials are incorrect\n"
                error_msg += "  - The model is not enabled\n"
                error_msg += "Please contact your Zscaler administrator to configure AWS Bedrock backend."
                print(f"[ZGUARD ERROR] HTTP 502: {error_msg}")
                return {"error": error_msg}
            
            elif response.status_code == 503:
                error_msg = "Service Unavailable: The AI Gateway is temporarily unavailable. Please try again later."
                print(f"[ZGUARD ERROR] HTTP 503: {error_msg}")
                return {"error": error_msg}
            
            elif response.status_code == 504:
                error_msg = "Gateway Timeout: The request to AWS Bedrock timed out. Please try again."
                print(f"[ZGUARD ERROR] HTTP 504: {error_msg}")
                return {"error": error_msg}
            
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"[ZGUARD ERROR] {error_msg}")
                return {"error": error_msg}
            
        except requests.exceptions.Timeout:
            error_msg = "Request timeout (>120s): The request took too long to complete. Please try again."
            print(f"[ZGUARD ERROR] {error_msg}")
            return {"error": error_msg}
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection Error: Unable to connect to Zscaler AI Guard. Please check your network connection."
            print(f"[ZGUARD ERROR] {error_msg}")
            print(f"[ZGUARD ERROR] Details: {str(e)}")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"[ZGUARD ERROR] {error_msg}")
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
        
        while iteration < max_iterations:
            iteration += 1
            
            # Invoke model
            response = self.invoke_bedrock(self.conversation_history, tools)
            
            if "error" in response:
                return f"Error: {response['error']}"
            
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
                print("\n[AGENT] Processing tool use requests...")
                
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
                continue
            
            elif stop_reason == "end_turn":
                # Extract text response
                response_text = ""
                for block in content:
                    if block.get("type") == "text":
                        response_text += block.get("text", "")
                
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
    zscaler_gateway_url = os.getenv("ZSCALER_GATEWAY_URL")
    zguard_api_key = os.getenv("ZGUARDSECRET")
    max_tokens_str = os.getenv("BEDROCK_MAX_TOKENS")
    temperature_str = os.getenv("BEDROCK_TEMPERATURE")
    
    # Validate configuration
    if not all([model_id, zscaler_gateway_url, zguard_api_key, max_tokens_str, temperature_str]):
        print("[ERROR] Missing required environment variables")
        print("Required: BEDROCK_MODEL_ID, ZSCALER_GATEWAY_URL, ZGUARDSECRET, BEDROCK_MAX_TOKENS, BEDROCK_TEMPERATURE")
        sys.exit(1)
    
    # Convert to appropriate types
    try:
        max_tokens = int(max_tokens_str)
        temperature = float(temperature_str)
    except ValueError as e:
        print(f"[ERROR] Invalid value for BEDROCK_MAX_TOKENS or BEDROCK_TEMPERATURE: {e}")
        sys.exit(1)
    
    try:
        # Create and start agent
        agent = BedrockAgent(
            model_id=model_id,
            zscaler_gateway_url=zscaler_gateway_url,
            zguard_api_key=zguard_api_key,
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
