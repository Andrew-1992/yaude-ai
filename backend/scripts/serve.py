"""
FastAPI inference server for Yaude AI -- streaming chat, user accounts
(signup/login), API key auth on inference endpoints, per-key rate
limiting, environment-driven CORS, structured logging, and a feedback
endpoint.

Usage (development):
    uvicorn scripts.serve:app --reload --port 8000

Usage (anything beyond your own machine):
    uvicorn scripts.serve:app --port 8000

Environment (.env file in backend/, or real environment variables):
    SANADI_CHECKPOINT        Path to a fine-tuned LoRA checkpoint directory.
    SANADI_API_KEY            Shared secret required in X-API-Key on /chat
                              and /feedback. If unset, those are OPEN.
    SANADI_ALLOWED_ORIGINS    Comma-separated CORS origins.
    SANADI_RATE_LIMIT         Requests/minute per key or IP.
    SANADI_JWT_SECRET         Signing secret for account session tokens.
                              REQUIRED for signup/login to work -- generate
                              a random string and set it before using
                              accounts. Without it, /auth/* endpoints
                              return a clear error rather than silently
                              issuing insecure tokens.

ACCOUNTS: user data lives in a small SQLite file (data/yaude.db) -- fine
for a phase-1 pilot's worth of users, not a production-scale store. See
src/yaude/db.py. Session tokens are bearer tokens (Authorization header),
not cookies -- the Next.js frontend is responsible for storing the token
in an httpOnly cookie scoped to its own origin; this server never sees or
sets browser cookies directly.

STREAMING: /chat streams token-by-token as plain text. See src/yaude/auth.py
and the StopOnEvent class below for how "stop generating" actually
interrupts generation server-side.

Known limitations at this stage (fine for a small pilot):
  - /chat and /feedback are still protected by the shared SANADI_API_KEY,
    NOT per-user auth -- accounts exist for identity/personalization right
    now, not yet for gating or per-user chat history on the backend (chat
    history still lives in browser localStorage). Moving chat history to
    per-account backend storage is a natural next step, not done here.
  - Single process, single model instance -- concurrent requests queue.
  - SQLite + in-memory rate limiting -- fine for a pilot, not a
    production-scale user base.
"""

import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Event, Thread

import torch
from dotenv import load_dotenv

load_dotenv()  # MUST run before importing yaude.auth, which reads
# SANADI_JWT_SECRET from the environment at import time.

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from yaude import db as yaude_db
from yaude import auth as yaude_auth
from fastapi import FastAPI, Request, HTTPException, Security, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer,
)
from peft import PeftModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("yaude.serve")

CHECKPOINT = os.environ.get("SANADI_CHECKPOINT", "checkpoints/yaude-coder-v0")
BASE_MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
API_KEY = os.environ.get("SANADI_API_KEY")
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("SANADI_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]
RATE_LIMIT = os.environ.get("SANADI_RATE_LIMIT", "10/minute")
FEEDBACK_LOG = Path("data/feedback.jsonl")

model_state = {}


class StopOnEvent(StoppingCriteria):
    def __init__(self, stop_event: Event):
        self.stop_event = stop_event

    def __call__(self, input_ids, scores, **kwargs) -> bool:
        return self.stop_event.is_set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yaude_db.init_db()
    logger.info(f"User database ready at {yaude_db.DB_PATH}")

    if not yaude_auth.JWT_SECRET:
        logger.warning(
            "SANADI_JWT_SECRET is not set -- /auth/signup and /auth/login "
            "will return a clear error instead of working. Set it in "
            "backend/.env before accounts can be used."
        )

    if not API_KEY:
        logger.warning(
            "SANADI_API_KEY is not set -- /chat and /feedback are OPEN. "
            "Fine for local development only."
        )
    else:
        logger.info("API key auth is ENABLED for /chat and /feedback.")

    logger.info(f"Allowed CORS origins: {ALLOWED_ORIGINS}")
    logger.info(f"Rate limit: {RATE_LIMIT} per key/IP")

    use_cuda = torch.cuda.is_available()
    dtype = torch.bfloat16 if use_cuda else torch.float32
    device_map = "auto" if use_cuda else "cpu"

    logger.info(f"Loading base model on {'GPU' if use_cuda else 'CPU'}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, dtype=dtype, device_map=device_map
    )

    checkpoint_path = Path(CHECKPOINT)
    adapter_config = checkpoint_path / "adapter_config.json"

    if adapter_config.exists():
        try:
            logger.info(f"Loading fine-tuned adapter from {CHECKPOINT}")
            model = PeftModel.from_pretrained(base_model, CHECKPOINT)
            model_state["mode"] = "fine-tuned"
        except Exception as e:
            logger.warning(f"Found {adapter_config} but failed to load it ({e}). Using base model.")
            model = base_model
            model_state["mode"] = "base-model-only"
    else:
        logger.warning(f"No checkpoint found at {CHECKPOINT} -- serving the BASE MODEL.")
        model = base_model
        model_state["mode"] = "base-model-only"

    model.eval()
    model_state["model"] = model
    model_state["tokenizer"] = tokenizer
    logger.info("Startup complete.")
    yield
    model_state.clear()


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Yaude AI Inference", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(provided_key: str = Security(api_key_header)) -> None:
    if not API_KEY:
        return
    if provided_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def get_current_user(authorization: str = Header(None)) -> dict:
    """Reads 'Authorization: Bearer <token>', verifies it, and returns the
    corresponding user row. Raises 401 on any failure -- missing header,
    bad token, expired token, or a token for a since-deleted user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ").strip()
    user_id = yaude_auth.decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    user = yaude_db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    return user


def _is_valid_email(email: str) -> bool:
    # Deliberately simple, not full RFC 5322 validation -- good enough to
    # catch typos without pulling in an extra dependency for a pilot.
    return "@" in email and "." in email.split("@")[-1] and len(email) <= 254


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    max_new_tokens: int = Field(512, ge=1, le=2048)
    temperature: float = Field(0.3, ge=0.0, le=2.0)


class FeedbackRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    response: str = Field(..., min_length=1, max_length=8000)
    rating: str = Field(..., pattern="^(up|down)$")


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=8, max_length=200)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _is_valid_email(v):
            raise ValueError("That doesn't look like a valid email address")
        return v


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1, max_length=200)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


@app.get("/health")
def health():
    return {
        "status": "ok",
        "checkpoint": CHECKPOINT,
        "mode": model_state.get("mode", "loading"),
    }


@app.post("/auth/signup", response_model=AuthResponse)
@limiter.limit("5/minute")
def signup(request: Request, req: SignupRequest):
    if not yaude_auth.JWT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Accounts aren't configured yet (SANADI_JWT_SECRET is unset).",
        )
    if yaude_db.get_user_by_email(req.email):
        raise HTTPException(status_code=409, detail="An account with that email already exists")

    password_hash = yaude_auth.hash_password(req.password)
    user = yaude_db.create_user(req.name.strip(), req.email, password_hash)
    token = yaude_auth.create_token(user["id"])
    logger.info(f"New account created: {user['email']}")
    return AuthResponse(token=token, user=UserResponse(**user))


@app.post("/auth/login", response_model=AuthResponse)
@limiter.limit("10/minute")
def login(request: Request, req: LoginRequest):
    if not yaude_auth.JWT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Accounts aren't configured yet (SANADI_JWT_SECRET is unset).",
        )
    user = yaude_db.get_user_by_email(req.email)
    if not user or not yaude_auth.verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = yaude_auth.create_token(user["id"])
    return AuthResponse(
        token=token, user=UserResponse(id=user["id"], name=user["name"], email=user["email"])
    )


@app.get("/auth/me", response_model=UserResponse)
def me(user: dict = Security(get_current_user)):
    return UserResponse(id=user["id"], name=user["name"], email=user["email"])


@app.post("/chat", dependencies=[Security(require_api_key)])
@limiter.limit(RATE_LIMIT)
async def chat(request: Request, req: ChatRequest):
    tokenizer = model_state.get("tokenizer")
    model = model_state.get("model")

    if tokenizer is None or model is None:
        raise HTTPException(status_code=503, detail="Model is still loading, try again shortly")

    messages = [{"role": "user", "content": req.message}]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    stop_event = Event()
    stopping_criteria = StoppingCriteriaList([StopOnEvent(stop_event)])

    generation_kwargs = dict(
        **inputs,
        max_new_tokens=req.max_new_tokens,
        temperature=req.temperature,
        do_sample=req.temperature > 0,
        pad_token_id=tokenizer.eos_token_id,
        streamer=streamer,
        stopping_criteria=stopping_criteria,
    )

    def _generate():
        try:
            model.generate(**generation_kwargs)
        except Exception:
            logger.exception("Generation failed")
            stop_event.set()

    thread = Thread(target=_generate, daemon=True)
    thread.start()

    async def token_stream():
        start = time.monotonic()
        char_count = 0
        try:
            for token_text in streamer:
                if await request.is_disconnected():
                    stop_event.set()
                    logger.info("Client disconnected -- stopping generation early")
                    break
                char_count += len(token_text)
                yield token_text
        finally:
            stop_event.set()
            thread.join(timeout=5)
            elapsed = time.monotonic() - start
            logger.info(
                f"chat stream done -- {len(req.message)} chars in, {char_count} chars out, "
                f"{elapsed:.1f}s, mode={model_state.get('mode')}"
            )

    return StreamingResponse(
        token_stream(),
        media_type="text/plain",
        headers={"X-Yaude-Mode": model_state.get("mode", "unknown")},
    )


@app.post("/feedback", dependencies=[Security(require_api_key)])
@limiter.limit("30/minute")
def feedback(request: Request, req: FeedbackRequest):
    FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "message": req.message,
        "response": req.response,
        "rating": req.rating,
        "timestamp": time.time(),
    }
    with open(FEEDBACK_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    logger.info(f"feedback recorded: {req.rating}")
    return {"status": "ok"}
