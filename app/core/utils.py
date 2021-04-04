import crypt
from random import choice
from typing import Optional, Tuple

from cryptography.fernet import Fernet

from .settings import get_settings


ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
KEY_DELIMITER = "#"

_fernet = Fernet(get_settings().secret_key)


def get_password_hash(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Get user password hash."""
    salt = salt or crypt.mksalt(crypt.METHOD_SHA256)
    return salt, crypt.crypt(password, salt)


def get_random_string(length: int = 64, alphabet: str = ALPHABET) -> str:
    """Generate random string of specified length and alphabet."""
    return "".join(choice(alphabet) for _ in range(length))


def encode_share_key(item_id: str, user_id: str) -> str:
    """Get encoded shared item ID."""
    return _fernet.encrypt(
        f"{str(item_id)}{KEY_DELIMITER}{str(user_id)}".encode()
    ).hex()


def decode_share_key(key: str) -> Tuple[str, str]:
    """Decode share key."""
    return tuple(_fernet.decrypt(bytes.fromhex(key)).decode().split(KEY_DELIMITER))
