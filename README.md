# [Work in Progress]
# Dolibarr MCP Tool

A Gradio-based interface and toolkit for interacting with the Dolibarr ERP system via its API. This project provides user-friendly web interfaces to perform various Dolibarr operations, such as managing third parties, invoices, products, and more, without manual API calls or data entry.

## Features

- **Gradio Web UI**: Easily interact with Dolibarr ERP through a modern web interface.
- **API Operations**: Supports GET, POST, PUT, DELETE requests to Dolibarr endpoints.
- **Prebuilt Operations**: Quickly fetch third parties, invoices, and stock information.
- **Custom Payloads**: Send custom data to Dolibarr endpoints.
- **Demo Utility**: Includes a sample app for letter counting to demonstrate Gradio integration.

## Getting Started

### Prerequisites
- Python 3.8+
- [Gradio](https://gradio.app/)
- [Requests](https://docs.python-requests.org/)

Install dependencies:
```bash
pip install gradio requests
```

### Dolibarr Setup
- Ensure your Dolibarr ERP instance is running and accessible.
- Obtain your Dolibarr API key from your user profile in Dolibarr.
- Update the API base URL in the scripts if your Dolibarr instance is not at `http://localhost/dolibarr/api/index.php`.

## Usage

### 1. Run the Main Interface

To launch the Dolibarr API tool:
```bash
python doli-mk1.py
```
### 2. visit the gradio on your localhost port(default: 7860), click on the view as api/mcp and copy the mcp configuration for the tool

### 3. add the mcp config on cursor/cline,etc and you are free to use this as a mcp tool


The Gradio interface will open in your browser. Enter your API key and select the desired operation.

## File Descriptions

- `doli-mk1.py`: Advanced Gradio interface for Dolibarr API. Supports all HTTP methods and endpoints with payloads.
- `doli.py`: Simple Gradio interface for fetching third parties, invoices, and stock.
- `README.md`: Project documentation.

## Contributing
Pull requests and suggestions are welcome! Please open an issue to discuss your ideas or report bugs.


---

*This project is not affiliated with Dolibarr. It is an independent tool to make Dolibarr API usage easier for developers and end-users.*
