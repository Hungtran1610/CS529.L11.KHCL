import json
import datetime
import uuid
import enum

from datetime import datetime, date, timedelta

from sqlalchemy import MetaData, func, desc, asc
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy_utils.primitives.currency import Currency
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask_sqlalchemy import Model, SQLAlchemy, BaseQuery

from enum import Enum

from system.exceptions import NotFound


class JsonSerializer(object):
    """
    Reference: https://github.com/mattupstate/overholt/blob/master/overholt/helpers.py#L45

    A mixin that can be used to mark a SQLAlchemy model class which
    implements a :func:`to_json` method. The :func:`to_json` method is used
    in conjuction with the custom :class:`JSONEncoder` class. By default this
    mixin will assume all properties of the SQLAlchemy model are to be visible
    in the JSON output. Extend this class to customize which properties are
    public, hidden or modified before being being passed to the JSON serializer.
    """

    __json_public__ = None
    __json_hidden__ = None
    __json_modifiers__ = None

    def get_field_names(self):
        for p in self.__mapper__.iterate_properties:
            yield p.key
        for p in sa_inspect(self.__class__).all_orm_descriptors:
            if type(p) == hybrid_property:
                yield p.__name__

    def to_json(self):
        field_names = self.get_field_names()

        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []
        modifiers = self.__json_modifiers__ or dict()

        rv = dict()
        for key in public:
            rv[key] = getattr(self, key)
        for key, modifier in modifiers.items():
            value = getattr(self, key)
            rv[key] = modifier(value, self)
        for key in hidden:
            rv.pop(key, None)

        for item in rv:
            if hasattr(rv[item], "to_json"):
                rv[item] = rv[item].to_json()
            elif isinstance(rv[item], datetime):
                rv[item] = rv[item].isoformat()
            elif isinstance(rv[item], uuid.UUID):
                rv[item] = str(rv[item])
            elif isinstance(rv[item], (int, float, bool, dict, list)):
                rv[item] = rv[item]
            elif isinstance(rv[item], enum.Enum) and hasattr(rv[item], "name"):
                rv[item] = rv[item].name
            elif rv[item] is None:
                continue
            else:
                rv[item] = str(rv[item])
        return rv


class ModelGeneralTasks(object):
    __update_field__ = None

    def save(self, session, is_commit=True):
        try:
            session.add(self)
            if is_commit:
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        return self

    def delete(self, session, is_commit=True):
        try:
            session.delete(self)
            if is_commit:
                session.commit()
        except Exception as error:
            session.rollback()
            raise error

    def update(self, data_update, session, is_commit=True):
        fields_can_update = self.__update_field__ or list()
        for k, v in data_update.items():
            if k in fields_can_update:
                setattr(self, k, v)
        try:
            if is_commit:
                session.commit()
        except Exception as error:
            session.rollback()
            raise error


class PowerPaintQuery(BaseQuery):
    def find_by_id(self, id):
        return self.get(id)

    def find_by_filter(self, model, filter, get_all=False):
        query = self
        for k, v in filter.items():
            query = query.filter(model.__table__.columns[k] == v)

        if get_all is False:
            return query.first()
        return query.all()

    def find_all(self, offset=0, limit=10, order=None):
        offset, limit = self.validate_offset_limit(offset, limit)
        return self.order_by(order).offset(offset).limit(limit).all()

    def find_all_with_attributes(self, model, attributes):
        cmd_query = self
        field_can_filter = model.__filter_field__ or list()
        offset = attributes.pop('offset', 0)
        limit = attributes.pop('limit', 10)
        offset, limit = self.validate_offset_limit(offset, limit)
        order_by = attributes.pop('order_by', 'created_at')
        order_by_type = attributes.get('order_by_type', 'desc')
        for k, v in attributes.items():
            if k in field_can_filter:
                if isinstance(v, list):
                    cmd_query = cmd_query.filter(
                        model.__table__.columns[k].in_(v))
                else:
                    cmd_query = cmd_query.filter(
                        model.__table__.columns[k] == v)
        if order_by_type == 'desc':
            cmd_query = cmd_query.order_by(desc(order_by))
        else:
            cmd_query = cmd_query.order_by(asc(order_by))
        items = cmd_query.offset(offset).limit(limit).all()
        count = cmd_query.count()
        return items, count

    @staticmethod
    def find_all_and_count_with_cmd_query_and_model(
        model, cmd_query, attributes):
        field_can_filter = model.__filter_field__ or list()
        for k, v in attributes.items():
            if k in field_can_filter:
                if isinstance(v, list):
                    cmd_query = cmd_query.filter(
                        model.__table__.columns[k].in_(v))
                else:
                    cmd_query = cmd_query.filter(
                        model.__table__.columns[k] == v)
        return cmd_query

    def find_all_by_filter_and_count(self, filter, offset=0, limit=10, order=None):
        offset, limit = self.validate_offset_limit(offset, limit)
        return self.filter(filter).order_by(order).offset(offset).limit(limit).all()

    def get_or_404(self, id, custom_message=None):
        data = self.get(id)
        if data is None:
            if custom_message is not None:
                raise NotFound('{custom_message}: {id}'.format(
                    custom_message=custom_message, id=str(id)))
            raise NotFound('Object does not exist: {id}'.format(id=str(id)))
        return data

    def filter_or_404(self, model, filter, custom_message=None):
        message_error = 'Object does not exist'
        if custom_message is not None and isinstance(custom_message, str):
            message_error = custom_message
        rv = self.find_by_filter(model, filter)
        if len(rv) == 0:
            raise NotFound(message_error)
        return rv[0]

    def max(self, column, filter):
        # type: (object, object) -> int
        return self.session.query(func.max(column)).filter(filter)

    def min(self, column, filter):
        # type: (object, object) -> int
        return self.session.query(func.min(column)).filter(filter)

    @staticmethod
    def validate_offset_limit(offset, limit):
        if offset < 0:
            offset = 0
        if limit < 0:
            limit = 10
        return offset, limit


class PowerPaintModel(Model, JsonSerializer, ModelGeneralTasks):
    pass


convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata, model_class=PowerPaintModel,
                query_class=PowerPaintQuery)
