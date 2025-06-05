import gradio as gr
import requests
from typing import Dict, List, Any, Optional

class DolibarrAPI:
    base_url = "http://localhost/dolibarr/api/index.php"
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'DOLAPIKEY': api_key,
            'Content-Type': 'application/json'
        }

    def get_third_parties(self) -> List[Dict]:
        """Get list of third parties"""
        response = requests.get(f"{self.base_url}/thirdparties", headers=self.headers)
        return response.json()

    def get_invoices(self) -> List[Dict]:
        """Get list of invoices"""
        response = requests.get(f"{self.base_url}/invoices", headers=self.headers)
        return response.json()

    def get_stock(self) -> List[Dict]:
        """Get stock information"""
        response = requests.get(f"{self.base_url}/products/stock", headers=self.headers)
        return response.json()

def dolibarr_interface(operation: str, api_key: str, mcp_session=None) -> str:
    """
    Interface for Dolibarr operations
    
    Args:
        operation (str): The operation to perform (thirdparties, invoices, stock)
        api_key (str): Dolibarr API key
    """
    try:
        api = DolibarrAPI(api_key, base_url="http://localhost/dolibarr/api/index.php")
        
        if operation == "thirdparties":
            result = api.get_third_parties()
        elif operation == "invoices":
            result = api.get_invoices()
        elif operation == "stock":
            result = api.get_stock()
        else:
            return "Invalid operation selected"
            
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
demo = gr.Interface(
    fn=dolibarr_interface,
    inputs=[
        gr.Dropdown(["thirdparties", "invoices", "stock"], label="Operation"),
        gr.Textbox(label="API Key")
        #gr.Textbox(label="Base URL (e.g., http://localhost/dolibarr/api/index.php)")
    ],
    outputs=gr.Textbox(label="Result"),
    title="Dolibarr ERP Interface",
    description="Interact with your Dolibarr ERP system through this interface."
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)