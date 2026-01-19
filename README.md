# Madisha Coffee Agent 🛍️☕

An intelligent e-commerce support and sales agent for Madisha Coffee, built with FastAPI and vanilla JavaScript.

## Features

- **💬 Chat Interface**: Beautiful, responsive chat widget for customer interactions
- **🛍️ Product Information**: Answer questions about products, pricing, and availability
- **📋 Policy Management**: Handle shipping, returns, and other policy inquiries
- **❓ FAQ System**: Manage frequently asked questions
- **📚 Custom Knowledge**: Add any custom information to the agent's memory
- **🏪 Store Info**: Configure store details and contact information
- **📥 Export/Import**: Backup and restore your knowledge base

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Data Storage**: JSON-based knowledge base
- **Currency**: South African Rand (ZAR)

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/madisha-coffee-agent.git
cd madisha-coffee-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 12000
```

4. Open your browser:
   - **Chat Interface**: http://localhost:12000
   - **Admin Panel**: http://localhost:12000/admin

## Usage

### Admin Panel

Access the admin panel at `/admin` to manage:

- **Products**: Add, edit, and delete products with prices in Rands
- **FAQs**: Create frequently asked questions and answers
- **Policies**: Define shipping, return, and other policies
- **Custom Knowledge**: Add any additional information
- **Store Info**: Update store name, description, and contact details

### Chat Interface

Customers can interact with the agent at the root URL (`/`). The agent can:

- Greet customers and provide store information
- Answer questions about products and pricing
- Explain shipping and return policies
- Respond to FAQs
- Provide contact information

## API Endpoints

### Chat
- `POST /api/chat` - Send a message and get a response

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Add a new product
- `PUT /api/products/{id}` - Update a product
- `DELETE /api/products/{id}` - Delete a product

### FAQs
- `GET /api/faqs` - List all FAQs
- `POST /api/faqs` - Add a new FAQ
- `PUT /api/faqs/{id}` - Update a FAQ
- `DELETE /api/faqs/{id}` - Delete a FAQ

### Policies
- `GET /api/policies` - List all policies
- `POST /api/policies` - Add a new policy
- `PUT /api/policies/{id}` - Update a policy
- `DELETE /api/policies/{id}` - Delete a policy

### Custom Knowledge
- `GET /api/knowledge` - List all knowledge entries
- `POST /api/knowledge` - Add a new entry
- `PUT /api/knowledge/{id}` - Update an entry
- `DELETE /api/knowledge/{id}` - Delete an entry

### Store Info
- `GET /api/store-info` - Get store information
- `PUT /api/store-info` - Update store information

### Data Management
- `GET /api/memory/export` - Export entire knowledge base
- `POST /api/memory/import` - Import knowledge base

## Project Structure

```
madisha-coffee-agent/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── static/
│   ├── index.html       # Chat interface
│   └── admin.html       # Admin panel
├── data/
│   └── memory.json      # Knowledge base storage
├── requirements.txt
└── README.md
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
