from uuid import UUID


def to_uuid(string):
    "Convert given string to UUID, return None if not possible"
    try:
        return UUID(string)
    except ValueError:
        return None
