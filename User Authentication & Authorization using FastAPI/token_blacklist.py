blacklisted_tokens = set()


def blacklist_token(token: str):

    """
    Add token to blacklist.
    """

    blacklisted_tokens.add(token)


def is_token_blacklisted(token: str) -> bool:

    """
    Returns True if token is blacklisted.
    """

    return token in blacklisted_tokens

def remove_token(token: str):

    """
    Remove token from blacklist.
    """

    blacklisted_tokens.discard(token)