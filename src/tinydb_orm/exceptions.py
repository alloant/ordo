class ORMError(Exception):
    pass


class DuplicateError(ORMError):
    pass


class FieldValueNotSet(ORMError):
    pass
