from functools import reduce
from operator import and_

from tinydb import Query

from .exceptions import DuplicateError, FieldValueNotSet
from .fields import Field, PrimaryKey, _missing


class Meta:
    meta_keys = ['db', 'table_name', 'unique_together']

    def __init__(self, **kwargs):
        for key in self.meta_keys:
            setattr(self, key, None)
        for key, value in kwargs.items():
            if key in self.meta_keys:
                setattr(self, key, value)
        assert self.db is not None, 'db is required'
        assert self.table is not None, 'table is required'

    @property
    def table(self):
        return self.db.table(self.table_name)

    @classmethod
    def from_obj(cls, obj):
        kwargs = {}
        for key in cls.meta_keys:
            if not hasattr(obj, key):
                continue
            kwargs[key] = getattr(obj, key)
        return cls(**kwargs)


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        field_mapping = {}
        unique_keys = []
        for key, value in attrs.items():
            if not isinstance(value, Field):
                continue
            field_mapping[key] = value
        for key in field_mapping:
            attrs.pop(key)
        attrs['_field_mapping'] = field_mapping
        unique_fields = {}
        if 'Meta' in attrs:
            meta = Meta.from_obj(attrs.pop('Meta'))
            attrs['_meta'] = meta
            for field_name in meta.unique_together or []:
                field = field_mapping[field_name]
                unique_fields[field_name] = field
        attrs['_unique_fields'] = unique_fields
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=ModelMeta):
    def __init__(self, _id=None, **kwargs):
        self.__value_mapping = {}
        for key, value in kwargs.items():
            if self._is_field_key(key):
                self._set_field_value(key, value)
        self.id = _id

    @classmethod
    def _is_field_key(cls, key):
        return key in cls._field_mapping

    def _set_field_value(self, key, value):
        field = self._field_mapping[key]
        self.__value_mapping[key] = field.serialize(value)

    def __setattr__(self, key, value):
        if self._is_field_key(key):
            return self._set_field_value(key, value)
        return super().__setattr__(key, value)

    def __getattr__(self, key, *default):
        if self._is_field_key(key):
            return self.__value_mapping[key]
        model_name = self.__class__.__name__
        raise AttributeError(f'{model_name} has no attribute {key}')

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save(insert=True)
        return obj

    def _check_duplicate(self, insert=False):
        querys = {}
        for key in self._unique_fields:
            querys[key] = self.__value_mapping[key]
        if not querys:
            return
        existed = self.__class__.get(**querys)
        if existed:
            if insert or existed.id != self.id:
                raise DuplicateError()

    def save(self, insert=False):
        # make sure all field have value
        for key, field in self._field_mapping.items():
            if key in self.__value_mapping:
                continue
            default = field.default
            if default is _missing:
                raise FieldValueNotSet(f'field {key} has no value')
            if callable(default):
                default = default()
            self.__value_mapping[key] = default
        # check unique fields
        self._check_duplicate(insert=insert)
        if insert:
            self.id = self._meta.table.insert(self.__value_mapping)
        else:
            self._meta.table.update(self.__value_mapping, doc_ids=[self.id])

    @classmethod
    def filter(cls, **query):
        query_args = cls._construct_query(**query)
        lst = cls._meta.table.search(query_args)
        return [cls._from_tinydb_document(item) for item in lst]

    @staticmethod
    def _construct_query(**query):
        query_args = []
        q = Query()
        for key, value in query.items():
            query_impl = getattr(q, key) == value
            query_args.append(query_impl)
        return reduce(and_, query_args)

    @classmethod
    def _from_tinydb_document(cls, document):
        return cls(_id=document.doc_id, **document)

    @classmethod
    def all(cls):
        return [
            cls._from_tinydb_document(item) for item in cls._meta.table.all()
        ]

    @classmethod
    def get(cls, **query):
        records = cls.filter(**query)
        if records:
            return records[0]
        return None

    @classmethod
    def count(cls):
        return len(cls._meta.table.all())

    def __str__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
