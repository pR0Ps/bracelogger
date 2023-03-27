#!/usr/bin/env python

"""Use brace-style string formatting in log messages"""

import logging

try:
    from collections.abc import Mapping
except ImportError:  # pragma: no cover
    from collections import Mapping


_BLPROXY_LOCAL = {
    "_log", "_wrapped", "log", "makeRecord", "getChild",
    "debug", "info", "warn", "warning", "error", "exception", "critical", "fatal",
}


_class_cache = {}
def _make_class(name, mixin, type_):
    """Dynamically create a class or pull it from the cache"""
    if type_ not in _class_cache:
        _class_cache[type_] = type(name, (mixin,) + type_.__mro__, {})
    return _class_cache[type_]


class BracelogRecordMixin(object):

    def getMessage(record):
        """Implement logging.LogRecord.getMessage using brace-style string formatting"""
        msg = str(record.msg)
        args = record.args

        # The logging module has a special case where if a LogRecord is constructed
        # with a single non-empty dict to format into the message, that single dict
        # is treated as the args instead of the first in a tuple of args.
        # This is done to enable using key-based templating in log messages. Ex:
        #     logging.info("a:%(a)s, b:%(b)s", {"a": 1, "b": 2})
        #
        # This case is handled here by splatting the dict in as kwargs to allow
        # using key-based format strings, but also passing it as the first arg to
        # preserve compatibility with index-based format strings.
        if isinstance(args, Mapping):
            msg = msg.format(args, **args)
        elif args:
            msg = msg.format(*args)
        return msg


class BraceloggerMixin(object):
    """A proxy to a logging.Logger instance that causes all handled LogRecords
    to use brace-style message formatting"""

    def __init__(self, logger):
        self._wrapped = logger

    def __getattribute__(self, key):
        if key in _BLPROXY_LOCAL:
            return super(BraceloggerMixin, self).__getattribute__(key)
        return getattr(self._wrapped, key)

    def __setattr__(self, key, val):
        if key == "_wrapped":
            return super(BraceloggerMixin, self).__setattr__(key, val)
        return setattr(self._wrapped, key, val)

    def __delattr__(self, key):
        return delattr(self._wrapped, key)

    def makeRecord(self, *args, **kwargs):
        """Create a BracelogRecord"""
        record = self._wrapped.makeRecord(*args, **kwargs)
        record.__class__ = _make_class("BracelogRecord", BracelogRecordMixin, type(record))
        return record

    def getChild(self, suffix):
        """Get a Bracelogger which is a descendant to this one"""
        logger = self._wrapped.getChild(suffix)
        return _make_class("Bracelogger", BraceloggerMixin, type(logger))(logger)


def get_logger(name=None):
    """Get a proxy to a logger instance that uses brace-style string formatting"""
    logger = logging.getLogger(name)

    # Create a new subclass of the existing logger class so introspection works
    return _make_class("Bracelogger", BraceloggerMixin, type(logger))(logger)
