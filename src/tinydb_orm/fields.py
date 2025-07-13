import uuid


class Missing:
    pass


_missing = Missing()


class Field:
    def __init__(self, *, default=_missing, is_primary=False):
        self.is_primary = is_primary
        self.default = default

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class Int(Field):
    def serialize(self, value):
        return int(value)

    def deserialize(self, value):
        return int(value)


class Str(Field):
    def serialize(self, value):
        return str(value)

    def deserialize(self, value):
        return str(value)


def uuid_hex():
    return uuid.uuid4().hex


class UUID(Str):
    def __init__(self, *args, default=uuid_hex, **kwargs):
        super().__init__(*args, default=default, **kwargs)


class PrimaryKey(Int):
    def __init__(self, *args, is_primary=True, **kwargs):
        super().__init__(*args, is_primary=is_primary, **kwargs)
