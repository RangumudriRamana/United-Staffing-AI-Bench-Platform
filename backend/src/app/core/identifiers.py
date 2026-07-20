from uuid import UUID, uuid4


def generate_public_id() -> UUID:
    """
    Generate a public identifier.

    This implementation currently uses UUID4.
    It can later be upgraded to UUID7 without
    changing any model definitions.
    """
    return uuid4()