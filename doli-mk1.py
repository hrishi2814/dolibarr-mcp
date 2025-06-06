import gradio as gr
import requests
import json
from typing import Dict, List,Any,Optional

class DolibarrAPI:
    base_url = "http://localhost/dolibarr/api/index.php"
    
    def __init__(self, api_key:str):
        """
        Just a constAbsolutely! I understand the importance of getting the system prompt right for your local agent to handle the API requests properly. The system prompt needs to convey to the agent what actions need to be performed for each endpoint, the format of the JSON request, and how it should interact with your API interface. Here’s a **structured system prompt** that will help guide the agent in making the right decisions when calling the Dolibarr API for the given endpoints.

### System Prompt for Local Agent:

---

**System Prompt: Dolibarr API Interaction**

You are interacting with the Dolibarr ERP system using an API. The user can specify the type of action they want to perform, the endpoint (e.g., `/thirdparties`, `/invoices`, `/contacts`, `/orders`, `/products`), and any relevant data (payload). Your job is to understand the request and formulate the correct API call to be made to the Dolibarr system.

You will use the following **HTTP methods**:

* `GET` to retrieve data.
* `POST` to create new records.
* `PUT` to update existing records.
* `DELETE` to delete records.

Here is what you need to do for each of the provided **endpoints**:

---

### **1. `/thirdparties` (Customers, Suppliers, etc.)**

#### **GET** (Retrieve a list or details of a third party):

* **Endpoint**: `/thirdparties` or `/thirdparties/{id}`
* **Required parameters for GET**: No parameters for listing all, but you can use `id` in the endpoint for details of a specific third party.
* **Response**: A list of third parties or details of the specific one.

#### **POST** (Create a new third party):

* **Endpoint**: `/thirdparties`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "name": "John Doe",          // The name of the third party
    "address": "123 Main St",    // Street address
    "zip": "12345",              // Postal code
    "town": "Sample City",       // City or town
    "country_id": 1,             // Country ID (e.g., 1 for USA)
    "email": "johndoe@example.com", // Email address
    "phone": "+1234567890",      // Phone number
    "type": 1,                   // Type (1 for customer, 2 for supplier, etc.)
    "status": 1                  // Status (1 for active, 0 for inactive)
  }
  ```

#### **PUT** (Update an existing third party):

* **Endpoint**: `/thirdparties/{id}`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "name": "Updated Name",      // Update the name or other attributes as needed
    "email": "newemail@example.com", // Update email
    "phone": "+9876543210"       // Update phone number
  }
  ```

#### **DELETE** (Delete a third party):

* **Endpoint**: `/thirdparties/{id}`
* **No payload is needed**, just the `id` of the third party to be deleted.

---

### **2. `/invoices`**

#### **GET** (Retrieve a list or details of an invoice):

* **Endpoint**: `/invoices` or `/invoices/{id}`
* **Required parameters for GET**: None for listing all invoices, `id` for a specific invoice.
* **Response**: A list of invoices or details of the specific invoice.

#### **POST** (Create a new invoice):

* **Endpoint**: `/invoices`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "socid": 10,                 // Third-party ID (Customer ID)
    "lines": [                   // List of invoice lines
      {
        "desc": "Web Development Service", // Description of the service/product
        "subprice": 500,                // Unit price
        "qty": 1,                       // Quantity
        "total_ht": 500,                // Total excluding tax
        "vat": 18,                      // VAT percentage
        "total_ttc": 590                // Total including tax
      }
    ],
    "date": "2025-06-01",            // Invoice creation date (YYYY-MM-DD)
    "duedate": "2025-06-15"          // Due date (YYYY-MM-DD)
  }
  ```

#### **PUT** (Update an existing invoice):

* **Endpoint**: `/invoices/{id}`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "lines": [                      // Updated lines
      {
        "desc": "Updated Service",    // New or updated description
        "subprice": 550,              // New price
        "qty": 2,                     // Updated quantity
        "total_ht": 1100,             // Updated total excluding tax
        "vat": 18,                    // VAT
        "total_ttc": 1294             // Updated total including tax
      }
    ]
  }
  ```

#### **DELETE** (Delete an invoice):

* **Endpoint**: `/invoices/{id}`
* **No payload needed**, just the `id` of the invoice to delete.

---

### **3. `/contacts` (Contacts for Third Parties)**

#### **GET** (Retrieve a list or details of a contact):

* **Endpoint**: `/contacts` or `/contacts/{id}`
* **Required parameters for GET**: None for listing all contacts, `id` for a specific contact.
* **Response**: A list of contacts or details of a specific contact.

#### **POST** (Create a new contact):

* **Endpoint**: `/contacts`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "thirdparty_id": 1,              // Third-party ID (Customer or Supplier)
    "firstname": "Jane",             // Contact first name
    "lastname": "Doe",               // Contact last name
    "email": "janedoe@example.com",  // Email address
    "phone": "+1234567890",          // Phone number
    "position": "Sales Manager",     // Position of the contact
    "address": "1234 Office St"      // Address
  }
  ```

#### **PUT** (Update an existing contact):

* **Endpoint**: `/contacts/{id}`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "email": "newemail@example.com", // Update email
    "phone": "+9876543210"           // Update phone
  }
  ```

#### **DELETE** (Delete a contact):

* **Endpoint**: `/contacts/{id}`
* **No payload needed**, just the `id` of the contact to delete.

---

### **4. `/orders` (Customer/Supplier Orders)**

#### **GET** (Retrieve a list or details of an order):

* **Endpoint**: `/orders` or `/orders/{id}`
* **Required parameters for GET**: None for listing all orders, `id` for a specific order.
* **Response**: A list of orders or details of a specific order.

#### **POST** (Create a new order):

* **Endpoint**: `/orders`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "socid": 10,                    // Third-party ID (Customer ID)
    "lines": [                       // List of order lines
      {
        "desc": "Laptop",            // Description of product
        "subprice": 1000,            // Unit price
        "qty": 1,                    // Quantity
        "total_ht": 1000,            // Total excluding tax
        "vat": 18,                   // VAT
        "total_ttc": 1180            // Total including tax
      }
    ],
    "date": "2025-06-01",             // Order date
    "duedate": "2025-06-15"           // Due date
  }
  ```

#### **PUT** (Update an existing order):

* **Endpoint**: `/orders/{id}`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "lines": [                       // Updated lines
      {
        "desc": "Updated Laptop",     // Updated description
        "subprice": 1100,             // Updated price
        "qty": 2,                     // Updated quantity
        "total_ht": 2200,             // Updated total excluding tax
        "vat": 18,                    // VAT
        "total_ttc": 2600             // Updated total including tax
      }
    ]
  }
  ```

#### **DELETE** (Delete an order):

* **Endpoint**: `/orders/{id}`
* **No payload needed**, just the `id` of the order to delete.

---

### **5. `/products`**

#### **GET** (Retrieve a list or details of a product):

* **Endpoint**: `/products` or `/products/{id}`
* **Required parameters for GET**: None for listing all products, `id` for a specific product.
* **Response**: A list of products or details of a specific product.

#### **POST** (Create a new product):

* **Endpoint**: `/products`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "label": "Smartphone",           // Product
  ```


name
"price": 499.99,                 // Unit price
"stock": 100,                    // Quantity in stock
"description": "Latest model",   // Product description
"socid": 10                      // Supplier ID
}
\`\`\`

#### **PUT** (Update an existing product):

* **Endpoint**: `/products/{id}`
* **Required Parameters** (in `payload` JSON):

  ```json
  {
    "label": "Updated Smartphone",   // Updated product name
    "price": 549.99,                 // Updated price
    "stock": 120,                    // Updated stock
    "description": "Updated model"   // Updated description
  }
  ```

#### **DELETE** (Delete a product):

* **Endpoint**: `/products/{id}`
* **No payload needed**, just the `id` of the product to delete.

---

### Final Notes:

* Always ensure you have the **correct `api_key`**.
* **Format the data** according to the required fields (you can skip optional fields if not needed).
* When **sending requests**, make sure to properly format the **JSON data** to match the expected fields for each endpoint.

This is the complete system prompt for your local agent. When the user specifies the method (`GET`, `POST`, `PUT`, `DELETE`), the endpoint, and any relevant payload (or if it's just a simple request like `GET`), your agent can automatically create the proper API request.
ructor, sets up the api key and some other stuff

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