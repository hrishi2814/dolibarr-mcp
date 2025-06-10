import gradio as gr
import requests
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
import anthropic
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DolibarrAPI:
    """Your existing Dolibarr API class - keeping it unchanged"""
    base_url = "https://valiant-trust-production.up.railway.app/api/index.php"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'DOLAPIKEY': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _request(self, method: str, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None) -> Any:
        base_url = "https://valiant-trust-production.up.railway.app/api/index.php"
        url = f"{base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, headers=self.headers, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"error": f"API request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"error": f"Invalid JSON response: {str(e)}"}

    def get_req(self, endpoint: str, params: Optional[dict] = None):
        return self._request('GET', endpoint, params=params)

    def post_req(self, endpoint: str, params: dict):
        return self._request("POST", endpoint, data=params)

    def put_req(self, endpoint: str, params: dict):
        return self._request("PUT", endpoint, data=params)

    def del_req(self, endpoint: str, params: Optional[dict] = None):
        return self._request("DELETE", endpoint, params=params)

def dolibarr_interface(method: str, endpoint: str, api_key="OKgV53jdbT1p1tKuZrB05eK9z0p9I2YX", payload_str: str = "") -> str:
    """Your existing interface function - keeping it unchanged"""
    try:
        api = DolibarrAPI(api_key)
        method = method.upper()
        
        payload = None
        if payload_str and payload_str.strip():
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError as e:
                return json.dumps({"error": f"Invalid JSON payload: {str(e)}"}, indent=2)

        if method == 'GET':
            result = api.get_req(endpoint, payload)
        elif method == 'POST':
            if not payload:
                return json.dumps({"error": "POST requests require a payload"}, indent=2)
            result = api.post_req(endpoint, payload)
        elif method == 'PUT':
            if not payload:
                return json.dumps({"error": "PUT requests require a payload"}, indent=2)
            result = api.put_req(endpoint, payload)
        elif method == 'DELETE':
            result = api.del_req(endpoint, payload)
        else:
            return json.dumps({"error": f"Invalid HTTP method '{method}' selected."}, indent=2)
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        logger.error(f"Unexpected error in dolibarr_interface: {e}")
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

class ClaudeDolibarrAgent:
    def __init__(self, anthropic_api_key: str, dolibarr_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.dolibarr_api_key = dolibarr_api_key
        
        # System prompt with Dolibarr context
        self.system_prompt = """You are a helpful ERP assistant that can interact with a Dolibarr system via API calls. 

Available Dolibarr API endpoints:
- /thirdparties - Customers, suppliers, prospects
- /invoices - Sales invoices and billing
- /products - Product catalog management  
- /contacts - Contact information
- /users - System users
- /proposals - Commercial proposals/quotes
- /orders - Sales orders
- /bills - Supplier bills
- /projects - Project management
- /stocks - Inventory management

Common operations:
- GET /thirdparties - List all customers/suppliers
- GET /thirdparties/{id} - Get specific customer details
- POST /thirdparties - Create new customer
- GET /invoices - List all invoices
- GET /products - List all products
- POST /products - Create new product

When users ask for information, determine the appropriate API call needed and use the dolibarr_api tool.
Always format responses in a user-friendly way, extracting key information from the API responses.
If an API call fails, explain the error clearly and suggest alternatives.

Current date: """ + datetime.now().strftime("%Y-%m-%d")

        # Tool definition for Claude
        self.tools = [
            {
                "name": "dolibarr_api",
                "description": "Execute API calls to the Dolibarr ERP system",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE"],
                            "description": "HTTP method for the API call"
                        },
                        "endpoint": {
                            "type": "string", 
                            "description": "API endpoint (e.g., /thirdparties, /invoices)"
                        },
                        "payload": {
                            "type": "string",
                            "description": "JSON payload for POST/PUT requests (leave empty for GET)"
                        }
                    },
                    "required": ["method", "endpoint"]
                }
            }
        ]

    def execute_dolibarr_call(self, method: str, endpoint: str, payload: str = "") -> str:
        """Execute the actual Dolibarr API call"""
        return dolibarr_interface(method, endpoint, self.dolibarr_api_key, payload)

    def chat(self, message: str, history: List[List[str]]) -> str:
        """Main chat function that processes user messages"""
        try:
            # Convert Gradio history to Claude format
            messages = []
            for human_msg, assistant_msg in history:
                if human_msg:
                    messages.append({"role": "user", "content": human_msg})
                if assistant_msg:
                    messages.append({"role": "assistant", "content": assistant_msg})
            
            # Add current message
            messages.append({"role": "user", "content": message})

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=self.system_prompt,
                messages=messages,
                tools=self.tools
            )

            # Process the response
            response_text = ""
            
            for content in response.content:
                if content.type == "text":
                    response_text += content.text
                elif content.type == "tool_use":
                    # Execute the Dolibarr API call
                    tool_name = content.name
                    tool_input = content.input
                    
                    if tool_name == "dolibarr_api":
                        api_result = self.execute_dolibarr_call(
                            method=tool_input.get("method", "GET"),
                            endpoint=tool_input.get("endpoint", ""),
                            payload=tool_input.get("payload", "")
                        )
                        
                        # Send tool result back to Claude
                        follow_up_messages = messages + [
                            {"role": "assistant", "content": response.content},
                            {
                                "role": "user", 
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": content.id,
                                        "content": api_result
                                    }
                                ]
                            }
                        ]
                        
                        # Get Claude's interpretation of the results
                        final_response = self.client.messages.create(
                            model="claude-3-sonnet-20240229",
                            max_tokens=1000,
                            system=self.system_prompt,
                            messages=follow_up_messages
                        )
                        
                        return final_response.content[0].text
            
            return response_text if response_text else "I couldn't process that request. Please try again."
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

def create_claude_agent_interface():
    """Create the Gradio interface for the Claude-powered Dolibarr agent"""
    
    # You'll need to set your API keys here
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # Replace with your key
    DOLIBARR_API_KEY = "9nUQANz1xD61s5c8E8sNMlzZu15KgcF5"  # Your existing key
    
    # Initialize the agent
    agent = ClaudeDolibarrAgent(ANTHROPIC_API_KEY, DOLIBARR_API_KEY)
    
    # Create Gradio ChatInterface
    demo = gr.ChatInterface(
        fn=agent.chat,
        title="🤖 Claude-Powered Dolibarr ERP Assistant",
        description="""
        Ask me anything about your Dolibarr ERP system! I can help you:
        
        📋 **Get Information**: "Show me all customers", "List recent invoices"
        👥 **Manage Contacts**: "Find customer details for ABC Corp"  
        📦 **Products**: "What products do we have?", "Create a new product"
        💰 **Invoicing**: "Show unpaid invoices", "Get invoice details"
        
        Just ask in natural language - I'll figure out the right API calls!
        """,
        examples=[
            "Show me all customers",
            "List all invoices", 
            "What products do we have?",
            "Get details for customer ID 1",
            "Show me recent proposals"
        ],
        cache_examples=False,
        theme=gr.themes.Soft(),
        css="""
        .message-wrap.svelte-1lcyrx4.svelte-1lcyrx4.svelte-1lcyrx4 {
            max-width: 80%;
        }
        """
    )
    
    return demo

# Main execution
if __name__ == '__main__':
    try:
        print("🚀 Starting  Dolibarr Agent...")
        
        # Create and launch the interface
        demo = create_claude_agent_interface()
        demo.launch(
            server_name="127.0.0.1",
            server_port=7862,
            share=False,
            debug=True,
            show_error=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"❌ Error starting application: {e}")

# Example queries you can try:
"""
- "Show me all customers"
- "List all invoices"
- "Get me customer details for ID 1"  
- "What products do we have?"
- "Show me recent proposals"
- "Create a new customer named Test Corp"
- "Find all unpaid invoices"
"""
