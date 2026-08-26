"""
Password hashing and JWT session tokens for Sanadi AI accounts.

Uses the `bcrypt` library directly rather than via passlib -- passlib is
largely unmaintained and its bcrypt version-detection code breaks against
modern bcrypt releases (bcrypt 4.1+ removed the `__about__` submodule
passlib reads). Calling bcrypt directly sidesteps that permanently.

Tokens are bearer tokens, not cookies -- the frontend's Next.js server is
responsible for storing the token in an httpOnly cookie scoped to its own
origin and forwarding it here as an Authorization header. This module
never touches cookies directly; it only issues and verifies tokens.
"""

import os
import time
from typing import Optional

import bcrypt
import jwt

JWT_SECRET = os.environ.get("SANADI_JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30  # 30 days

# bcrypt has a hard 72-byte input limit -- truncate defensively so a very
# long password hashes successfully (using its first 72 bytes) instead of
# crashing the request.
_MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        pw_bytes = password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
        return bcrypt.checkpw(pw_bytes, password_hash.encode("utf-8"))
    except ValueError:
        # Malformed stored hash (shouldn't happen with our own data, but
        # don't crash the request over it) -- treat as failed verification.
        return False


def create_token(user_id: str) -> str:
    if not JWT_SECRET:
        raise RuntimeError(
            "SANADI_JWT_SECRET is not set -- required for account sign-in. "
            "Generate one and add it to backend/.env."
        )
    payload = {"sub": user_id, "exp": time.time() + TOKEN_TTL_SECONDS}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """Returns the user id encoded in the token, or None if the token is
    missing, expired, malformed, or the secret isn't configured."""
    if not JWT_SECRET or not token:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
