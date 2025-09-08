import bcrypt
from typing import Union, cast


def hash_password(password: Union[str, bytes]) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password as a string
    """
    if isinstance(password, str):
        password = password.encode("utf-8")

    salt: bytes = bcrypt.gensalt()
    hashed: bytes = bcrypt.hashpw(password, salt)
    return hashed.decode("utf-8")


def verify_password(
    password: Union[str, bytes], hashed_password: Union[str, bytes]
) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: The plain text password to verify
        hashed_password: The hashed password to check against

    Returns:
        True if the password matches the hash, False otherwise
    """
    if isinstance(password, str):
        password = password.encode("utf-8")

    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")

    result: bool = cast(bool, bcrypt.checkpw(password, hashed_password))
    return result
