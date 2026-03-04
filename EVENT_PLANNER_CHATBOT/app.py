import os
import json
from uuid import uuid4
from datetime import datetime, timedelta
from typing import Optional

import jwt
from flask import Flask, request, jsonify, send_from_directory, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from agent import TravelAgent
from models import UserProfile, SavedItinerary, ChatMessage, ItineraryItem

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret")
JWT_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "4320"))  # default 3 days

# Database setup (MongoDB)
# Set MONGO_URI to your cluster string (e.g. mongodb+srv://user:pass@cluster1.zbkf6.mongodb.net) and MONGO_DB to the DB name.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "event_planner")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
users_col = db["users"]
itins_col = db["itineraries"]
convos_col = db["conversations"]

agent = TravelAgent()


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _create_jwt(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MIN),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def _decode_jwt(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except Exception:
        return None


def _auth_response(payload: dict, token: str):
    resp = jsonify(payload)
    resp.set_cookie("auth_token", token, httponly=True, samesite="Lax")
    return resp


def _get_user_from_token() -> Optional[dict]:
    auth_header = request.headers.get("Authorization", "")
    bearer = auth_header.split(" ")
    token = None
    if len(bearer) == 2 and bearer[0].lower() == "bearer":
        token = bearer[1]
    if not token:
        token = request.cookies.get("auth_token")
    if not token:
        return None
    user_id = _decode_jwt(token)
    if not user_id:
        return None
    return users_col.find_one({"_id": user_id})


def _public_profile(user: dict) -> dict:
    saved_count = itins_col.count_documents({"user_id": user["_id"]})
    convo = convos_col.find_one({"user_id": user["_id"]}, sort=[("updated_at", -1)]) or {}
    chat_history = convo.get("messages", [])[-20:]
    return {
        "id": user["_id"],
        "email": user["email"],
        "name": user["name"],
        "saved_itinerary_count": saved_count,
        "chat_history": chat_history,
    }


def _ensure_convo(user_id: str, convo_id: Optional[str] = None, title: Optional[str] = None) -> dict:
    if convo_id:
        convo = convos_col.find_one({"_id": convo_id, "user_id": user_id})
        if convo:
            return convo
    convo_doc = {
        "_id": convo_id or str(uuid4()),
        "user_id": user_id,
        "title": title or "New conversation",
        "messages": [],
        "itinerary": None,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    convos_col.insert_one(convo_doc)
    return convos_col.find_one({"_id": convo_doc["_id"], "user_id": user_id})

@app.route("/api/itinerary", methods=["POST"])
def api_itinerary():
    user = _get_user_from_token()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    location = (data.get("location") or "").strip()
    date = (data.get("date") or "").strip()
    prefs = data.get("preferences") or []
    start_time = (data.get("start_time") or "09:00").strip()
    end_time = (data.get("end_time") or "22:00").strip()
    convo_id = data.get("conversation_id") or None

    if not prompt:
        if not location or not date:
            return jsonify({"error": "Provide a prompt or both location and date."}), 400
        prefs_text = ", ".join(prefs) if prefs else "your interests"
        prompt = (
            f"Plan a day in {location} on {date}. Preferences: {prefs_text}. "
            f"Start at {start_time} and finish by {end_time}."
        )
    try:
        itinerary = agent.generate_itinerary(
            prompt,
            location=location or None,
            date=date or None,
            preferences=prefs,
            start_time=start_time,
            end_time=end_time,
        )
        title = data.get("title") or f"{location or 'Trip'} {date}".strip()
        convo = _ensure_convo(user["_id"], convo_id=convo_id, title=title)
        convos_col.update_one(
            {"_id": convo["_id"]},
            {"$set": {"messages": [], "updated_at": _now_iso(), "title": title, "itinerary": itinerary}},
        )
        return jsonify({"itinerary": itinerary, "meta": {"location": location, "date": date}, "conversation_id": convo["_id"]})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/itinerary/save", methods=["POST"])
def api_save_itinerary():
    user = _get_user_from_token()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    items_payload = data.get("itinerary") or []
    if not items_payload:
        return jsonify({"error": "Itinerary is required"}), 400

    try:
        items = [ItineraryItem(**item).model_dump() for item in items_payload]
    except Exception:
        return jsonify({"error": "Invalid itinerary format"}), 400

    saved = SavedItinerary(
        id=str(uuid4()),
        title=data.get("title") or "Trip Plan",
        prompt=data.get("prompt") or "",
        date=data.get("date") or "",
        location=data.get("location") or "",
        items=items,
        created_at=_now_iso(),
    ).model_dump()

    itins_col.insert_one({"_id": saved["id"], **saved, "user_id": user["_id"]})
    users_col.update_one({"_id": user["_id"]}, {"$set": {"last_itinerary": {"items": items, "meta": {"location": saved["location"], "date": saved["date"]}}}})
    return jsonify({"saved": saved})


@app.route("/api/itinerary/saved", methods=["GET"])
def api_saved_list():
    user = _get_user_from_token()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    items = list(itins_col.find({"user_id": user["_id"]}).sort("created_at", -1).limit(20))
    for item in items:
        item["id"] = item.get("id") or item.get("_id")
        item.pop("_id", None)
        item.pop("user_id", None)
    return jsonify({"saved": items})


@app.route("/api/itinerary/saved/<saved_id>", methods=["DELETE"])
def api_saved_delete(saved_id: str):
    user = _get_user_from_token()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    result = itins_col.delete_one({"_id": saved_id, "user_id": user["_id"]})
    if result.deleted_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"deleted": True})


@app.route("/api/itinerary/question", methods=["POST"])
def api_question():
    user = _get_user_from_token()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400

    convo_id = data.get("conversation_id") or None
    itinerary = data.get("itinerary") or []

    convo = None
    if convo_id:
        convo = convos_col.find_one({"_id": convo_id, "user_id": user["_id"]})
    if not convo:
        convo = convos_col.find_one({"user_id": user["_id"]}, sort=[("updated_at", -1)])
    if convo and not itinerary:
        itinerary = convo.get("itinerary") or []
    if not itinerary:
        return jsonify({"error": "Generate an itinerary first."}), 400

    try:
        answer = agent.answer_question(itinerary, question)
        if convo:
            messages = convo.get("messages", [])
            messages.extend([
                ChatMessage(role="user", content=question, timestamp=_now_iso()).model_dump(),
                ChatMessage(role="assistant", content=answer, timestamp=_now_iso()).model_dump(),
            ])
            convos_col.update_one(
                {"_id": convo["_id"]},
                {"$set": {"messages": messages[-200:], "updated_at": _now_iso(), "itinerary": itinerary}},
            )
        return jsonify({"answer": answer, "conversation_id": convo["_id"] if convo else None})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversations", methods=["GET", "POST"])
def api_conversations():
    user = _get_user_from_token()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    if request.method == "POST":
        data = request.get_json(force=True)
        title = (data.get("title") or "New conversation").strip() or "New conversation"
        convo = _ensure_convo(user["_id"], title=title)
        return jsonify({"conversation_id": convo["_id"], "title": title})

    convos = list(convos_col.find({"user_id": user["_id"]}, projection={"messages": 0}).sort("updated_at", -1).limit(50))
    for c in convos:
        c["id"] = c.get("_id")
        c.pop("_id", None)
    return jsonify({"conversations": convos})


@app.route("/api/conversations/<convo_id>", methods=["GET", "DELETE"])
def api_conversation_detail(convo_id: str):
    user = _get_user_from_token()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    if request.method == "DELETE":
        result = convos_col.delete_one({"_id": convo_id, "user_id": user["_id"]})
        if result.deleted_count == 0:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"deleted": True})

    convo = convos_col.find_one({"_id": convo_id, "user_id": user["_id"]})
    if not convo:
        return jsonify({"error": "Not found"}), 404
    convo["id"] = convo.get("_id")
    convo.pop("_id", None)
    return jsonify({"conversation": convo})


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json(force=True)
    email = (data.get("email") or "").lower().strip()
    password = (data.get("password") or "").strip()
    name = data.get("name") or email.split("@")[0]
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if users_col.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    profile = UserProfile(id=str(uuid4()), email=email, name=name)
    user_dict = profile.model_dump()
    user_dict["_id"] = user_dict.pop("id")
    user_dict["password"] = generate_password_hash(password)
    users_col.insert_one(user_dict)
    token = _create_jwt(user_dict["_id"])
    return _auth_response({"token": token, "profile": _public_profile(user_dict)}, token)


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").lower().strip()
    password = (data.get("password") or "").strip()
    user = users_col.find_one({"email": email})
    if not user or not check_password_hash(user.get("password", ""), password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = _create_jwt(user["_id"])
    return _auth_response({"token": token, "profile": _public_profile(user)}, token)


@app.route("/api/logout", methods=["POST"])
def api_logout():
    resp = jsonify({"ok": True})
    resp.set_cookie("auth_token", "", expires=0)
    return resp


@app.route("/api/profile", methods=["GET"])
def api_profile():
    user = _get_user_from_token()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    saved = list(itins_col.find({"user_id": user["_id"]}).sort("created_at", -1).limit(20))
    for item in saved:
        item["id"] = item.get("id") or item.get("_id")
        item.pop("_id", None)
        item.pop("user_id", None)
    return jsonify({"profile": _public_profile(user), "saved": saved})


@app.route("/api/history", methods=["GET"])
def api_history():
    user = _get_user_from_token()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    saved = list(itins_col.find({"user_id": user["_id"]}).sort("created_at", -1).limit(20))
    for item in saved:
        item["id"] = item.get("id") or item.get("_id")
        item.pop("_id", None)
        item.pop("user_id", None)

    convo = convos_col.find_one({"user_id": user["_id"]}) or {}
    history = convo.get("messages", [])[-50:]
    return jsonify({
        "saved_itineraries": saved,
        "chat_history": history,
    })


@app.route("/")
def root():
    if _get_user_from_token():
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/login")
def login_page():
    if _get_user_from_token():
        return redirect("/dashboard")
    return send_from_directory("static", "login.html")


@app.route("/dashboard")
def dashboard_page():
    if not _get_user_from_token():
        return redirect("/login")
    return send_from_directory("static", "dashboard.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
