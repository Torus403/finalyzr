import string
import random


def generate_random_string(length=12):
    """
    Generate a random string of specified length.

    Args:
        length (int): Length of the random string.

    Returns:
        str: Random string.
    """
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def generate_random_email():
    """
    Generate a random email address.

    Returns:
        str: Random email address.
    """
    return f"{generate_random_string(8)}@example.com"


def generate_random_password():
    """
    Generate a random password.

    Returns:
        str: Random password.
    """
    return generate_random_string(12)
