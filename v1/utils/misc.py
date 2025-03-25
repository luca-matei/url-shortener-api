import secrets
import string
import hashlib

from v1.config import settings


def get_hash(text: str):
    """Return the SHA-256 hash of the input text."""
    return hashlib.sha256(text.encode()).hexdigest()


def generate_code(length: int = settings.code_length):
    """Generate a URL-safe code of specified length."""
    # Define the characters that can be used in the code
    characters = string.ascii_letters + string.digits
    # Securely generate a random string of the specified length
    return "".join(secrets.choice(characters) for _ in range(length))
