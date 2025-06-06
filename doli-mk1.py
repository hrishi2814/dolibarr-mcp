import gradio as gr
import requests
import json
from typing import Dict, List,Any,Optional

class DolibarrAPI:
    base_url = "http://localhost/dolibarr/api/index.php"
    
    def __init__(self, api_key:str):
        """
        Just a constructor, sets up the api key and some other stuff

        Args:
            api_key (str): Dolibarr user api key
        """
        self.api_key = api_key
        self.headers = {
            'DOLAPIKEY': api_key ,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _request(self,method: str, endpoint: str, data: Optional[dict]=None, params: Optional[dict]=None ) -> Any:
        """
        basic method used for making http request to Dolibarr api

        Args:
            method (str): The type of HTTP  - GET, POST, PUT, DELETE,etc
            endpoint (str): api endpoint based on the request type - "/invoice" , "/thirdparties",etc
            data (Optional[dict]) : data to be sent in request body, dictionary
            params (Optional[dict]) :  dictionary of params to be sent with this request (for GET)
        """
        
        base_url = "http://localhost/dolibarr/api/index.php"

        url = f"{base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data, params=params)
        response.raise_for_status()
        
        # Return the response data
        return response.json()

    # --- GET REQUESTS ------
    def get_req(self, endpoint: str, params: Optional[dict]=None):
        return self._request('GET', endpoint, params=params)

    # --- POST requests -----
    def post_req(self, endpoint: str, params: dict):
        return self._request("POST", endpoint, data=params)

    # --- PUT requests ----
    def put_req(self, endpoint : str, params: dict):
        return self._request("PUT", endpoint, data=params)

    # --- DELETE requests ----
    def del_req(self, endpoint :str, params :Optional[dict]=None):
        return self._request("DELETE", endpoint, params=params)

def dolibarr_interface(method: str, endpoint : str, api_key = "OKgV53jdbT1p1tKuZrB05eK9z0p9I2YX", payload: dict = None) -> str:
    """
    To orchestrate the API call from start to finish based on simple string and dictionary inputs

    Args:
        method (str): http method type ( GET, POST, PUT, DELETE,etc)
        endpoint (str): api endpoint, basically which api to call (/invoices, /thirdparties,/products,etc)
        api_key : dolibarr api key
        payload (dict): payload in json to send as request body - contains data/params to be passed to the api
    """
    
    api = DolibarrAPI(api_key)
    method = method.upper()

    if method=='GET':
        result=api.get_req(endpoint,payload)
    elif method=='POST':
        result=api.post_req(endpoint,payload)
    elif method=='PUT':
        result=api.put_req(endpoint,payload)
    elif method == 'DELETE':
        result=api.del_req(endpoint)
    else:
        return json.dumps({"error": f"Invalid HTTP method '{method}' selected."})
    
    return json.dumps(result,indent=2)

# ## Gradio interface
demo = gr.Interface(
    fn=dolibarr_interface,
    inputs=[
        gr.Dropdown(["GET","PUT","POST","DELETE"]),
        gr.Dropdown(["/thirdparties","/invoices","/products"]),
        gr.Textbox(label="API key", value="OKgV53jdbT1p1tKuZrB05eK9z0p9I2YX"),
        gr.Textbox(label="Payload")
    ],
    outputs=gr.Textbox(label="ze result"),
    title="Dolibarr AI Agent/Personal ERP Assistant",
    description="Interact with your dollybaby with ai agents and call the shots by typing in english, no more data entry(stupid(sick))"
)
if __name__=='__main__':
    demo.launch(mcp_server=True)


#----- basic api calling ----
# #trying basic calling of api, lets see
# # list_result = dolibarr_interface(method='GET', endpoint='/thirdparties')
# # print(list_result)

# # creating a product
# new_product_data = {
#     "ref": "PROD-007",
#     "label": "New AI-Powered Gadget",
#     "price": "199.99",
#     "tva_tx": "20.0"
# }
# create_result = dolibarr_interface(
#     method='POST',
#     endpoint='/products',
#     payload=new_product_data
# )
# print(create_result)