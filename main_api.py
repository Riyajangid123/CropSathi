import base64
import hashlib
import hmac
import io
import os
import httpx
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv
from PIL import Image
from Rag.db import SupabaseDB
from graph.workflow import Workflow

load_dotenv()

db = SupabaseDB()


app = FastAPI(title="Agrotech WhatsApp Bot")

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
META_APP_SECRET = os.getenv("META_APP_SECRET")

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"

workflow_app = Workflow().build_workflow()


# ---------- Webhook verification (Meta calls this once when you set up the webhook) ----------

@app.get("/webhook/whatsapp")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    print("mode:", mode)
    print("token received:", token)
    print("challenge:", challenge)
    print("token matches:", token == os.getenv("META_VERIFY_TOKEN"))

    if mode == "subscribe" and token == os.getenv("META_VERIFY_TOKEN"):
        return PlainTextResponse(challenge, status_code=200)

    raise HTTPException(status_code=403, detail="Verification failed")

# ---------- Signature validation (confirms the request really came from Meta) ----------

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    if not signature_header or not META_APP_SECRET:
        return False

    expected_signature = hmac.new(
        META_APP_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    received_signature = signature_header.replace("sha256=", "")
    return hmac.compare_digest(expected_signature, received_signature)


# ---------- Sending messages back to the farmer ----------

async def send_whatsapp_message(to: str, body: str):
    url = f"{GRAPH_API_BASE}/{META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Failed to send message: {response.status_code} {response.text}")


# ---------- Downloading incoming media (images) ----------

async def download_whatsapp_media(media_id: str):
    token = os.getenv("META_ACCESS_TOKEN")

    print("META_ACCESS_TOKEN exists:", token is not None)
    print("TOKEN length:", len(token) if token else 0)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient() as client:
        meta_response = await client.get(
            f"https://graph.facebook.com/v21.0/{media_id}",
            headers=headers
        )

        print("Meta status:", meta_response.status_code)
        print("Meta response:", meta_response.text)

        meta_response.raise_for_status()

        media_info = meta_response.json()
        media_url = media_info["url"]

        media_response = await client.get(
            media_url,
            headers=headers
        )

        media_response.raise_for_status()

        return media_response.content


# ---------- Background processing (keeps the webhook response fast) ----------

async def process_message(from_number: str, question: str, image_data_uri: str | None):
    farmer_id = db.get_or_create_farmer(from_number)
    recent = db.get_recent_conversations(farmer_id, limit=1)

    prior_crop = recent[0]["crop"] if recent else None
    prior_language = recent[0]["language"] if recent and "language" in recent[0] else None

    try:
        state_input = {
            "question": question or "What's affecting my crop?",
            "image": image_data_uri or "",
        }

        result = workflow_app.invoke(state_input)
        answer = result.get("answer")

        if not answer or not answer.strip():
            answer = "Sorry, I couldn't generate a clear answer for this. Please try again with a clearer photo or a more specific question."

        db.log_conversation(farmer_id, result)

    except Exception as e:
        print(f"Error processing message from {from_number}: {e}")
        answer = "Sorry, something went wrong while analyzing your crop. Please try again in a moment."

    await send_whatsapp_message(to=from_number, body=answer)

# ---------- Main webhook: receives incoming messages ----------

@app.post("/webhook/whatsapp")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    print("🔥🔥🔥 WHATSAPP WEBHOOK HIT 🔥🔥🔥")

    if not verify_signature(raw_body, signature):
        print("❌ INVALID SIGNATURE")
        raise HTTPException(status_code=403, detail="Invalid signature")

    print("✅ Signature verified")

    payload = await request.json()

    try:
        entry = payload["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            # Could be a status update (delivered/read) — ignore those
            return JSONResponse(content={"status": "ignored"}, status_code=200)

        message = value["messages"][0]
        from_number = message["from"]  # e.g. "91XXXXXXXXXX", no "whatsapp:" prefix here

        question = ""
        image_data_uri = None

        if message["type"] == "text":
            question = message["text"]["body"]

        elif message["type"] == "image":
            media_id = message["image"]["id"]
            question = message["image"].get("caption", "")
            image_data_uri = await download_whatsapp_media(media_id)

        if not question and not image_data_uri:
            await send_whatsapp_message(
                to=from_number,
                body="Hi! Please send a photo of your crop along with your question.",
            )
            return JSONResponse(content={"status": "ok"}, status_code=200)

        background_tasks.add_task(process_message, from_number, question, image_data_uri)

    except (KeyError, IndexError) as e:
        print(f"Unexpected payload structure: {e}")

    return JSONResponse(content={"status": "ok"}, status_code=200)


@app.get("/health")
async def health():
    return {"status": "ok"}
