import gradio as gr
import requests
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional

# Set up logging to help debug issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DolibarrAPI:
    base_url = "https://valiant-trust-production.up.railway.app/api/index.php"
    
    def __init__(self, api_key: str):
        """
        Just a constructor, sets up the api key and some other stuff

        Args:
            api_key (str): Dolibarr user api key
        """
        self.api_key = "OKgV53jdbT1p1tKuZrB05eK9z0p9I2YX"
        self.headers = {
            'DOLAPIKEY': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _request(self, method: str, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None) -> Any:
        """
        basic method used for making http request to Dolibarr api

        Args:
            method (str): The type of HTTP  - GET, POST, PUT, DELETE,etc
            endpoint (str): api endpoint based on the request type - "/invoice" , "/thirdparties",etc
            data (Optional[dict]) : data to be sent in request body, dictionary
            params (Optional[dict]) :  dictionary of params to be sent with this request (for GET)
        """
        
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

    # --- GET REQUESTS ------
    def get_req(self, endpoint: str, params: Optional[dict] = None):
        return self._request('GET', endpoint, params=params)

    # --- POST requests -----
    def post_req(self, endpoint: str, params: dict):
        return self._request("POST", endpoint, data=params)

    # --- PUT requests ----
    def put_req(self, endpoint: str, params: dict):
        return self._request("PUT", endpoint, data=params)

    # --- DELETE requests ----
    def del_req(self, endpoint: str, params: Optional[dict] = None):
        return self._request("DELETE", endpoint, params=params)

def dolibarr_interface(method: str, endpoint: str, api_key="OKgV53jdbT1p1tKuZrB05eK9z0p9I2YX", payload_str: str = "") -> str:
    """
    To orchestrate the API call from start to finish based on simple string and dictionary inputs

    Args:
        method (str): http method type ( GET, POST, PUT, DELETE,etc)
        endpoint (str): api endpoint, basically which api to call (/invoices, /thirdparties,/products,etc)
        api_key : dolibarr api key
        payload_str (str): payload as JSON string to send as request body
    """
    
    try:
        api = DolibarrAPI(api_key)
        method = method.upper()
        
        # Parse payload if provided
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
        
        cleaned = clean_json_response(result)
        return json.dumps(cleaned, indent=2)
    
    except Exception as e:
        logger.error(f"Unexpected error in dolibarr_interface: {e}")
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

def clean_json_response(data: Any) -> Any:
    """
    Recursively clean JSON response by removing null values, empty strings, and empty collections.
    
    Args:
        data: The data to clean (can be dict, list, or primitive type)
    
    Returns:
        Cleaned data with null values and empty collections removed
    """
    if isinstance(data, dict):
        return {
            k: clean_json_response(v)
            for k, v in data.items()
            if v is not None and v != "" and clean_json_response(v) is not None
        }
    elif isinstance(data, list):
        cleaned = [clean_json_response(item) for item in data]
        return [item for item in cleaned if item is not None and item != ""]
    else:
        return data
    
# Create the Gradio interface with better error handling
def create_interface():
    """Create and return the Gradio interface"""
    
    demo = gr.Interface(
        fn=dolibarr_interface,
        inputs=[
            gr.Dropdown(
                choices=["GET", "POST", "PUT", "DELETE"],
                label="HTTP Method",
                value="GET"
            ),
            gr.Dropdown(
                choices=["/thirdparties", "/invoices", "/products", "/contacts", "/users"],
                label="API Endpoint",
                value="/thirdparties",
                allow_custom_value=True
            ),
            gr.Textbox(
                label="API Key", 
                value="OKgV53jdbT1p1tKuZrB05eK9z0p9I2YX"
            ),
            gr.Textbox(
                label="Payload (JSON format)",
                placeholder='{"ref": "PROD-001", "label": "Product Name", "price": "99.99"}'
            )
        ],
        outputs=gr.Textbox(
            label="API Response",
            #lines=10
        ),
        title="Dolibarr AI Agent/Personal ERP Assistant",
        description="Interact with your Dolibarr ERP system through API calls. Select method, endpoint, and provide JSON payload for POST/PUT requests.",
        
    )
    
    return demo

# Main execution with better MCP server handling
if __name__ == '__main__':
    try:
        demo = create_interface()
        
        # Launch with MCP server but with better error handling
        logger.info("Starting Gradio application with MCP server...")
        
        # Try launching with MCP server first
        try:
            demo.launch(
                mcp_server=True,
                server_name="127.0.0.1",
                server_port=7860,
                share=False,
                debug=True,
                show_error=True
            )
        except Exception as mcp_error:
            logger.error(f"Failed to start with MCP server: {mcp_error}")
            logger.info("Falling back to regular Gradio interface...")
            
            # Fallback to regular Gradio interface
            demo.launch(
                server_name="127.0.0.1",
                server_port=7861,  # Use different port
                share=False,
                debug=True,
                show_error=True
            )
            
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"Error starting application: {e}")

#----- Example usage ----
# Uncomment these lines to test the API functionality directly

# # Test basic API calling
# print("Testing API connection...")
# list_result = dolibarr_interface(method='GET', endpoint='/thirdparties')
# print("Thirdparties list:", list_result)

# # Test creating a product
# new_product_data = {
#     "ref": "PROD-007",
#     "label": "New AI-Powered Gadget", 
#     "price": "199.99",
#     "tva_tx": "20.0"
# }
# create_result = dolibarr_interface(
#     method='POST',
#     endpoint='/products',
#     payload_str=json.dumps(new_product_data)
# )
# print("Product creation result:", create_result)