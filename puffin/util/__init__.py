from uuid import UUID


def to_uuid(string):
    "Convert given string to UUID, return None if not possible"
    try:
        return UUID(string)
    except ValueError:
        return None

def truncate(string, length, suffix="..."):
    "Truncate string to a given length, preserving last word"
    if len(string) <= length:
        return string
    else:
        return string[:length].rsplit(' ', 1)[0] + suffix
