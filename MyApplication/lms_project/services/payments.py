import uuid
import requests
from django.conf import settings

def initiate_zenopay_payment(institution, buyer_phone):
    order_id = str(uuid.uuid4())

    payload = {
        "order_id": order_id,
        "buyer_email": institution.owner_email,
        "buyer_name": institution.name,
        "buyer_phone": buyer_phone,  # placeholder
        "amount": 1000,
        "webhook_url": "http://localhost:8000/api/public/zenopay/webhook/",
        "metadata": {
            "schema_name": institution.schema_name
        }
    }

    headers = {
        "x-api-key": settings.ZENOPAY_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://zenoapi.com/api/payments/mobile_money_tanzania",
            json=payload,
            headers=headers,
            timeout=10
        )

        print("Zenopay status:", response.status_code)
        print("Zenopay response:", response.text)

        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()

            # Fallback payment_url if not provided
            payment_url = data.get("payment_url")
            if not payment_url and "order_id" in data:
                payment_url = f"https://zenoapi.com/track/{data['order_id']}"

            return {
                "status_code": response.status_code,
                "order_id": order_id,
                "payment_url": payment_url,
                "message": data.get("message"),
                "raw": data
            }

        else:
            return {
                "status_code": response.status_code,
                "order_id": order_id,
                "error": "Non-JSON response",
                "text": response.text
            }

    except requests.RequestException as e:
        print("Zenopay exception:", str(e))
        return {
            "status_code": 500,
            "order_id": order_id,
            "error": "Request failed",
            "details": str(e)
        }