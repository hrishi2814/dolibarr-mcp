import gradio as gr
import requests
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
import anthropic
import openai
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

def dolibarr_interface(method: str, endpoint: str, api_key="9nUQANz1xD61s5c8E8sNMlzZu15KgcF5", payload_str: str = "") -> str:
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

class OpenAIDolibarrAgent:
    def __init__(self, openai_api_key: str, dolibarr_api_key: str, base_url: str = None):
        self.client = openai.OpenAI(api_key=openai_api_key, base_url=base_url)
        self.dolibarr_api_key = dolibarr_api_key
        
        # System prompt with Dolibarr context
        self.system_prompt = """You are a helpful ERP assistant that can interact with a Dolibarr system via API calls. 
CRITICAL RULES:
1. ALWAYS show ALL data returned by API calls - never truncate, limit, or summarize unless explicitly asked
2. When listing items (customers, invoices, products), display EVERY record returned
3. Present data in clean tables or structured format showing key fields
4. If API returns 100+ records, show all unless user asks for specific filtering
5. NEVER make assumptions about what the user wants to see - show everything
        
DOLIBARR API ENDPOINTS:
- /thirdparties - GET: list all, GET /{id}: specific customer, POST: create
- /invoices - GET: list all invoices, GET /{id}: specific invoice
- /products - GET: list all products, POST: create product
- /contacts - Contact management
- /users - System users  
- /proposals - Commercial proposals/quotes
- /orders - Sales orders
- /bills - Supplier bills
- /projects - Project management
- /stocks - Inventory management


RESPONSE FORMAT RULES:
- For lists: Show ID, Name, Status, and other key fields in table format
- For single items: Show all relevant details clearly organized
- Always extract and display the most important information from API responses
- If API returns error, explain clearly what went wrong
- Include record counts: "Found X customers:" or "Total invoices: Y"

BEHAVIOR RULES:
- Be proactive - if user asks for "customers", get ALL customers
- Don't ask "would you like to see more?" - just show everything
- For specific IDs, show complete details
- When creating records, confirm success with details
- Always make the API call needed - don't hesitate or ask for clarification

Common operations:
- GET /thirdparties - List all customers/suppliers
- GET /thirdparties/{id} - Get specific customer details
- POST /thirdparties - Create new customer
- GET /invoices - List all invoices
- GET /products - List all products
- POST /products - Create new product

When users ask for information, determine the appropriate API call needed and use the dolibarr_api function.
Always format responses in a user-friendly way, extracting key information from the API responses.
If an API call fails, explain the error clearly and suggest alternatives.

Current date: """ + datetime.now().strftime("%Y-%m-%d")

        # Function definition for OpenAI format
        self.functions = [
            {
                "name": "dolibarr_api",
                "description": "Execute API calls to the Dolibarr ERP system",
                "parameters": {
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
            # Convert Gradio history to OpenAI format
            messages = [{"role": "system", "content": self.system_prompt}]
            
            for human_msg, assistant_msg in history:
                if human_msg:
                    messages.append({"role": "user", "content": human_msg})
                if assistant_msg:
                    messages.append({"role": "assistant", "content": assistant_msg})
            
            # Add current message
            messages.append({"role": "user", "content": message})

            # Call OpenAI API with functions
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # or gpt-4
                messages=messages,
                functions=self.functions,
                function_call="auto",
                max_tokens=1500
            )

            # Process the response
            message = response.choices[0].message
            
            if message.function_call:
                # Execute the Dolibarr API call
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                
                if function_name == "dolibarr_api":
                    api_result = self.execute_dolibarr_call(
                        method=function_args.get("method", "GET"),
                        endpoint=function_args.get("endpoint", ""),
                        payload=function_args.get("payload", "")
                    )
                    
                    # Send function result back to OpenAI
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "function_call": message.function_call
                    })
                    messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": api_result
                    })
                    
                    # Get final response
                    final_response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        max_tokens=1500
                    )
                    
                    return final_response.choices[0].message.content
            
            return message.content if message.content else "I couldn't process that request."
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

def create_openai_agent_interface():
    """Create the Gradio interface for the OpenAI-powered Dolibarr agent"""
    
    # Set your API keys here
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Replace with your key
    NEBIUS_BASE_URL = "https://api.studio.nebius.ai/v1"  # For Nebius (optional)
    DOLIBARR_API_KEY = "9nUQANz1xD61s5c8E8sNMlzZu15KgcF5"
    
    # Initialize the agent (use base_url for Nebius)
    agent = OpenAIDolibarrAgent(OPENAI_API_KEY, DOLIBARR_API_KEY)
    # For Nebius: agent = OpenAIDolibarrAgent(NEBIUS_API_KEY, DOLIBARR_API_KEY, NEBIUS_BASE_URL)
    
    # Create Gradio ChatInterface
    demo = gr.ChatInterface(
        fn=agent.chat,
        title="🤖 OpenAI-Powered Dolibarr ERP Assistant",
        description="""
        Ask me anything about your Dolibarr ERP system! I can help you:
        
        📋 **Get Information**: "Show me all customers", "List recent invoices"
        👥 **Manage Contacts**: "Find customer details for ABC Corp"  
        📦 **Products**: "What products do we have?", "Create a new product"
        💰 **Invoicing**: "Show unpaid invoices", "Get invoice details"
        
        ### You can mess around with a test instance of dolibarr here : https://valiant-trust-production.up.railway.app/ 
        - username : admin , password : admin123
        - This demo will by default make all the changes in this dolibarr instance, have fun!

        - Just ask in natural language - and the agent will respond to you right away!
        """,
        examples=[
            "Show me all customers",
            "List all invoices", 
            "What products do we have?",
            "Get details for customer ID 1",
            "Show me recent proposals"
        ],
        cache_examples=False,
        theme=gr.themes.Soft()
    )
    
    return demo

# Main execution
if __name__ == '__main__':
    try:
        print("🚀 Starting OpenAI-Powered Dolibarr Agent...")
        
        # Create and launch the interface
        demo = create_openai_agent_interface()
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
