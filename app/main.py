from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import os
from pathlib import Path
from datetime import datetime

app = FastAPI(title="E-commerce Support & Sales Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
MEMORY_FILE = DATA_DIR / "memory.json"


def load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {
        "products": [],
        "faqs": [],
        "policies": [],
        "custom_knowledge": [],
        "store_info": {
            "name": "My E-commerce Store",
            "description": "Welcome to our online store!",
            "contact_email": "support@store.com",
            "contact_phone": "",
        },
    }


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class Product(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    price: float
    category: Optional[str] = ""
    features: Optional[List[str]] = []
    in_stock: Optional[bool] = True


class FAQ(BaseModel):
    id: Optional[str] = None
    question: str
    answer: str
    category: Optional[str] = ""


class Policy(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    type: Optional[str] = "general"


class CustomKnowledge(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    keywords: Optional[List[str]] = []


class StoreInfo(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


def generate_id():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def search_knowledge(query: str, memory: dict) -> dict:
    """Search through all knowledge bases for relevant information."""
    import re
    # Clean query: lowercase and remove punctuation
    query_lower = query.lower()
    query_clean = re.sub(r'[^\w\s]', '', query_lower)
    results = {
        "products": [],
        "faqs": [],
        "policies": [],
        "custom_knowledge": [],
        "store_info": None,
    }

    query_words = set(query_clean.split())
    # Filter out common stop words for better matching
    stop_words = {"a", "an", "the", "is", "are", "do", "does", "what", "how", "can", "i", "you", "your", "my", "me", "we", "us", "to", "for", "of", "in", "on", "at", "with", "have", "has", "any", "some", "all", "this", "that", "these", "those"}
    meaningful_words = query_words - stop_words
    
    # Common greeting words
    greeting_words = {"hi", "hello", "hey", "greetings", "good", "morning", "afternoon", "evening"}
    
    # Check if it's a greeting
    is_greeting = bool(query_words & greeting_words)
    
    # Store info keywords
    store_keywords = {"store", "shop", "about", "contact", "email", "phone", "who", "company"}
    if query_words & store_keywords or is_greeting:
        results["store_info"] = memory.get("store_info")

    # Product-specific query detection
    product_query_keywords = {"product", "products", "item", "items", "buy", "sell", "selling", "offer", "catalog", "catalogue", "inventory", "merchandise"}
    is_product_query = bool(query_words & product_query_keywords)
    
    # If asking about products in general, return all products
    if is_product_query:
        # Check if there are specific product terms beyond just "products"
        specific_terms = meaningful_words - product_query_keywords
        if not specific_terms:
            results["products"] = memory.get("products", [])
        else:
            # Search for specific products
            for product in memory.get("products", []):
                product_text = f"{product['name']} {product['description']} {product.get('category', '')} {' '.join(product.get('features', []))}".lower()
                if any(word in product_text for word in specific_terms):
                    results["products"].append(product)
    else:
        # Search products by specific terms
        for product in memory.get("products", []):
            product_text = f"{product['name']} {product['description']} {product.get('category', '')} {' '.join(product.get('features', []))}".lower()
            # Check if any meaningful word matches
            if meaningful_words and any(word in product_text for word in meaningful_words):
                results["products"].append(product)
            # Also check for price-related queries
            elif query_words & {"price", "cost", "much", "expensive", "cheap"}:
                results["products"].append(product)

    # Search FAQs - be more specific
    faq_keywords = {"shipping", "ship", "delivery", "deliver", "return", "refund", "exchange", "warranty", "guarantee", "payment", "pay", "order", "track", "tracking"}
    for faq in memory.get("faqs", []):
        faq_text = f"{faq['question']} {faq['answer']} {faq.get('category', '')}".lower()
        # Match on meaningful words or FAQ-specific keywords
        if meaningful_words and any(word in faq_text for word in meaningful_words):
            results["faqs"].append(faq)
        elif query_words & faq_keywords and any(kw in faq_text for kw in query_words & faq_keywords):
            results["faqs"].append(faq)

    # Search policies
    policy_keywords = {"shipping", "return", "refund", "policy", "policies", "delivery", "exchange", "warranty", "guarantee", "terms", "privacy"}
    for policy in memory.get("policies", []):
        policy_text = f"{policy['title']} {policy['content']} {policy.get('type', '')}".lower()
        if meaningful_words and any(word in policy_text for word in meaningful_words):
            results["policies"].append(policy)
        elif query_words & policy_keywords and any(kw in policy_text for kw in query_words & policy_keywords):
            results["policies"].append(policy)

    # Search custom knowledge
    for knowledge in memory.get("custom_knowledge", []):
        knowledge_text = f"{knowledge['title']} {knowledge['content']} {' '.join(knowledge.get('keywords', []))}".lower()
        if meaningful_words and any(word in knowledge_text for word in meaningful_words):
            results["custom_knowledge"].append(knowledge)

    return results


def generate_response(query: str, search_results: dict, memory: dict) -> str:
    """Generate a helpful response based on search results."""
    import re
    query_lower = query.lower()
    query_clean = re.sub(r'[^\w\s]', '', query_lower)
    query_words = set(query_clean.split())
    response_parts = []

    # Check for greetings - only if it's primarily a greeting
    greeting_words = {"hi", "hello", "hey", "greetings"}
    non_greeting_keywords = {"shipping", "return", "product", "price", "policy", "order", "buy", "help", "support"}
    is_pure_greeting = bool(query_words & greeting_words) and not bool(query_words & non_greeting_keywords)
    
    if is_pure_greeting:
        store_name = memory.get("store_info", {}).get("name", "our store")
        response_parts.append(f"Hello! Welcome to {store_name}! 👋 How can I help you today? I can assist you with:")
        response_parts.append("• Product information and recommendations")
        response_parts.append("• Pricing and availability")
        response_parts.append("• Shipping and return policies")
        response_parts.append("• General questions about our store")
        return "\n".join(response_parts)

    # Check for product queries
    if search_results["products"]:
        if len(search_results["products"]) == 1:
            p = search_results["products"][0]
            response_parts.append(f"**{p['name']}**")
            response_parts.append(f"📝 {p['description']}")
            response_parts.append(f"💰 Price: R{p['price']:.2f}")
            if p.get("category"):
                response_parts.append(f"📁 Category: {p['category']}")
            if p.get("features"):
                response_parts.append("✨ Features:")
                for feature in p["features"]:
                    response_parts.append(f"  • {feature}")
            stock_status = "✅ In Stock" if p.get("in_stock", True) else "❌ Out of Stock"
            response_parts.append(stock_status)
        else:
            response_parts.append("Here are some products that might interest you:")
            for p in search_results["products"][:5]:
                stock_emoji = "✅" if p.get("in_stock", True) else "❌"
                response_parts.append(f"• **{p['name']}** - R{p['price']:.2f} {stock_emoji}")

    # Check for FAQ matches
    if search_results["faqs"]:
        if response_parts:
            response_parts.append("\n---\n")
        for faq in search_results["faqs"][:3]:
            response_parts.append(f"**Q: {faq['question']}**")
            response_parts.append(f"A: {faq['answer']}")

    # Check for policy matches
    if search_results["policies"]:
        if response_parts:
            response_parts.append("\n---\n")
        for policy in search_results["policies"][:2]:
            response_parts.append(f"**{policy['title']}**")
            response_parts.append(policy["content"])

    # Check for custom knowledge
    if search_results["custom_knowledge"]:
        if response_parts:
            response_parts.append("\n---\n")
        for knowledge in search_results["custom_knowledge"][:2]:
            response_parts.append(f"**{knowledge['title']}**")
            response_parts.append(knowledge["content"])

    # Include store info if relevant
    if search_results["store_info"] and not response_parts:
        info = search_results["store_info"]
        response_parts.append(f"**{info.get('name', 'Our Store')}**")
        if info.get("description"):
            response_parts.append(info["description"])
        if info.get("contact_email"):
            response_parts.append(f"📧 Email: {info['contact_email']}")
        if info.get("contact_phone"):
            response_parts.append(f"📞 Phone: {info['contact_phone']}")

    # Default response if nothing found
    if not response_parts:
        store_name = memory.get("store_info", {}).get("name", "our store")
        contact_email = memory.get("store_info", {}).get("contact_email", "support@store.com")
        response_parts.append(f"I'm sorry, I couldn't find specific information about that in my knowledge base.")
        response_parts.append(f"Here's what I can help you with:")
        response_parts.append("• Product information and pricing")
        response_parts.append("• Shipping and delivery questions")
        response_parts.append("• Return and refund policies")
        response_parts.append("• General store inquiries")
        response_parts.append(f"\nFor more specific questions, please contact us at {contact_email}")

    return "\n".join(response_parts)


# Chat endpoint
@app.post("/api/chat")
async def chat(message: ChatMessage):
    memory = load_memory()
    search_results = search_knowledge(message.message, memory)
    response = generate_response(message.message, search_results, memory)
    return {"response": response, "session_id": message.session_id}


# Product endpoints
@app.get("/api/products")
async def get_products():
    memory = load_memory()
    return memory.get("products", [])


@app.post("/api/products")
async def add_product(product: Product):
    memory = load_memory()
    product_dict = product.model_dump()
    product_dict["id"] = generate_id()
    memory["products"].append(product_dict)
    save_memory(memory)
    return product_dict


@app.put("/api/products/{product_id}")
async def update_product(product_id: str, product: Product):
    memory = load_memory()
    for i, p in enumerate(memory["products"]):
        if p["id"] == product_id:
            product_dict = product.model_dump()
            product_dict["id"] = product_id
            memory["products"][i] = product_dict
            save_memory(memory)
            return product_dict
    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str):
    memory = load_memory()
    memory["products"] = [p for p in memory["products"] if p["id"] != product_id]
    save_memory(memory)
    return {"message": "Product deleted"}


# FAQ endpoints
@app.get("/api/faqs")
async def get_faqs():
    memory = load_memory()
    return memory.get("faqs", [])


@app.post("/api/faqs")
async def add_faq(faq: FAQ):
    memory = load_memory()
    faq_dict = faq.model_dump()
    faq_dict["id"] = generate_id()
    memory["faqs"].append(faq_dict)
    save_memory(memory)
    return faq_dict


@app.put("/api/faqs/{faq_id}")
async def update_faq(faq_id: str, faq: FAQ):
    memory = load_memory()
    for i, f in enumerate(memory["faqs"]):
        if f["id"] == faq_id:
            faq_dict = faq.model_dump()
            faq_dict["id"] = faq_id
            memory["faqs"][i] = faq_dict
            save_memory(memory)
            return faq_dict
    raise HTTPException(status_code=404, detail="FAQ not found")


@app.delete("/api/faqs/{faq_id}")
async def delete_faq(faq_id: str):
    memory = load_memory()
    memory["faqs"] = [f for f in memory["faqs"] if f["id"] != faq_id]
    save_memory(memory)
    return {"message": "FAQ deleted"}


# Policy endpoints
@app.get("/api/policies")
async def get_policies():
    memory = load_memory()
    return memory.get("policies", [])


@app.post("/api/policies")
async def add_policy(policy: Policy):
    memory = load_memory()
    policy_dict = policy.model_dump()
    policy_dict["id"] = generate_id()
    memory["policies"].append(policy_dict)
    save_memory(memory)
    return policy_dict


@app.put("/api/policies/{policy_id}")
async def update_policy(policy_id: str, policy: Policy):
    memory = load_memory()
    for i, p in enumerate(memory["policies"]):
        if p["id"] == policy_id:
            policy_dict = policy.model_dump()
            policy_dict["id"] = policy_id
            memory["policies"][i] = policy_dict
            save_memory(memory)
            return policy_dict
    raise HTTPException(status_code=404, detail="Policy not found")


@app.delete("/api/policies/{policy_id}")
async def delete_policy(policy_id: str):
    memory = load_memory()
    memory["policies"] = [p for p in memory["policies"] if p["id"] != policy_id]
    save_memory(memory)
    return {"message": "Policy deleted"}


# Custom knowledge endpoints
@app.get("/api/knowledge")
async def get_knowledge():
    memory = load_memory()
    return memory.get("custom_knowledge", [])


@app.post("/api/knowledge")
async def add_knowledge(knowledge: CustomKnowledge):
    memory = load_memory()
    knowledge_dict = knowledge.model_dump()
    knowledge_dict["id"] = generate_id()
    memory["custom_knowledge"].append(knowledge_dict)
    save_memory(memory)
    return knowledge_dict


@app.put("/api/knowledge/{knowledge_id}")
async def update_knowledge(knowledge_id: str, knowledge: CustomKnowledge):
    memory = load_memory()
    for i, k in enumerate(memory["custom_knowledge"]):
        if k["id"] == knowledge_id:
            knowledge_dict = knowledge.model_dump()
            knowledge_dict["id"] = knowledge_id
            memory["custom_knowledge"][i] = knowledge_dict
            save_memory(memory)
            return knowledge_dict
    raise HTTPException(status_code=404, detail="Knowledge entry not found")


@app.delete("/api/knowledge/{knowledge_id}")
async def delete_knowledge(knowledge_id: str):
    memory = load_memory()
    memory["custom_knowledge"] = [k for k in memory["custom_knowledge"] if k["id"] != knowledge_id]
    save_memory(memory)
    return {"message": "Knowledge entry deleted"}


# Store info endpoints
@app.get("/api/store-info")
async def get_store_info():
    memory = load_memory()
    return memory.get("store_info", {})


@app.put("/api/store-info")
async def update_store_info(store_info: StoreInfo):
    memory = load_memory()
    current_info = memory.get("store_info", {})
    update_data = store_info.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            current_info[key] = value
    memory["store_info"] = current_info
    save_memory(memory)
    return current_info


# Export/Import memory
@app.get("/api/memory/export")
async def export_memory():
    return load_memory()


@app.post("/api/memory/import")
async def import_memory(data: dict):
    save_memory(data)
    return {"message": "Memory imported successfully"}


# Serve static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(static_dir / "index.html"))


@app.get("/admin")
async def admin():
    return FileResponse(str(static_dir / "admin.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=12000)
