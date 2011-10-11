"""
REST+Json protocol implementation.
"""
import base64
import datetime
import decimal

from simplegeneric import generic

from wsme.rest import RestProtocol
from wsme.controller import register_protocol
import wsme.types

try:
    import simplejson as json
except ImportError:
    import json


@generic
def tojson(datatype, value):
    """
    A generic converter from python to jsonify-able datatypes.

    If a non-complex user specific type is to be used in the api,
    a specific tojson should be added::

        from wsme.protocol.restjson import tojson

        myspecialtype = object()

        @tojson.when_object(myspecialtype)
        def myspecialtype_tojson(datatype, value):
            return str(value)
    """
    if wsme.types.iscomplex(datatype):
        d = dict()
        for name, attr in wsme.types.list_attributes(datatype):
            d[name] = tojson(attr.datatype, getattr(value, name))
        return d
    return value


@tojson.when_type(list)
def array_tojson(datatype, value):
    return [tojson(datatype[0], item) for item in value]


@tojson.when_object(decimal.Decimal)
def decimal_tojson(datatype, value):
    return str(value)


@tojson.when_object(datetime.date)
def date_tojson(datatype, value):
    return value.isoformat()


@tojson.when_object(datetime.time)
def time_tojson(datatype, value):
    return value.isoformat()


@tojson.when_object(datetime.datetime)
def datetime_tojson(datatype, value):
    return value.isoformat()


@tojson.when_object(wsme.types.binary)
def datetime_tojson(datatype, value):
    return base64.encodestring(value)


@generic
def fromjson(datatype, value):
    """
    A generic converter from json base types to python datatype.

    If a non-complex user specific type is to be used in the api,
    a specific fromjson should be added::

        from wsme.protocol.restjson import fromjson

        class MySpecialType(object):
            pass

        @fromjson.when_object(MySpecialType)
        def myspecialtype_fromjson(datatype, value):
            return MySpecialType(value)
    """
    if value is None:
        return None
    if wsme.types.iscomplex(datatype):
        obj = datatype()
        for name, attrdef in wsme.types.list_attributes(datatype):
            if name in value:
                setattr(obj, name, fromjson(attrdef.datatype, value[name]))
        return obj
    return value


@fromjson.when_type(list)
def array_fromjson(datatype, value):
    return [fromjson(datatype[0], item) for item in value]


@fromjson.when_object(decimal.Decimal)
def decimal_fromjson(datatype, value):
    return decimal.Decimal(value)


@fromjson.when_object(datetime.date)
def date_fromjson(datatype, value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


@fromjson.when_object(datetime.time)
def time_fromjson(datatype, value):
    return datetime.datetime.strptime(value, '%H:%M:%S').time()


@fromjson.when_object(datetime.datetime)
def time_fromjson(datatype, value):
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')


@fromjson.when_object(wsme.types.binary)
def binary_fromjson(datatype, value):
    return base64.decodestring(value)


class RestJsonProtocol(RestProtocol):
    """
    REST+Json protocol.

    .. autoattribute:: name
    .. autoattribute:: dataformat
    .. autoattribute:: content_types
    """

    name = 'REST+Json'
    dataformat = 'json'
    content_types = [
        'application/json',
        'application/javascript',
        'text/javascript',
         '']

    def decode_arg(self, value, arg):
        return fromjson(arg.datatype, value)

    def parse_arg(self, name, value):
        return json.loads(value)

    def parse_args(self, body):
        raw_args = json.loads(body)
        return raw_args

    def encode_result(self, funcdef, result):
        r = tojson(funcdef.return_type, result)
        return json.dumps({'result': r}, ensure_ascii=False).encode('utf8')

    def encode_error(self, errordetail):
        return json.dumps(errordetail, encoding='utf-8')

register_protocol(RestJsonProtocol)
