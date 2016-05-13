import collections
import datetime
import decimal
import json
import sys


def _resolve_name(name, package, level):
    """Return the absolute name of the module to be imported."""
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in range(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level "
                             "package")
    return "%s.%s" % (package[:dot], name)


def import_module(name, package=None):
    """Import a module.

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.

    """
    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)
    __import__(name)
    return sys.modules[name]


def import_attribute(import_path, exception_handler=None):
    module_name, object_name = import_path.rsplit('.', 1)
    try:
        module = import_module(module_name)
    except:  # pragma: no cover
        if callable(exception_handler):
            exctype, excvalue, tb = sys.exc_info()
            return exception_handler(import_path, exctype, excvalue, tb)
        else:
            raise
    try:
        return getattr(module, object_name)
    except:  # pragma: no cover
        if callable(exception_handler):
            exctype, excvalue, tb = sys.exc_info()
            return exception_handler(import_path, exctype, excvalue, tb)
        else:
            raise


def is_aware(value):
    """
    Determines if a given datetime.datetime is aware.

    The logic is described in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    """
    return (value.tzinfo is not None and
            value.tzinfo.utcoffset(value) is not None)


class TimeAwareJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(TimeAwareJSONEncoder, self).default(o)


class KeyDefaultDict(collections.defaultdict):
    """
    A defaultdict where the default_factory can get the key as an arg.
    """

    def __missing__(self, key):
        """Attempt calling the factory with the key.

        If the normal methods don't work, try calling the
        ``default_factory`` with the key as an arg.
        """
        try:
            return super(KeyDefaultDict, self).__missing__(key)
        except TypeError:
            value = self.default_factory(key)
            self[key] = value
            return value
