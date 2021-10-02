#!/usr/bin/env python

"""Use brace-style string formatting in log messages"""

import functools
import logging
import types

try:
    from collections.abc import Mapping
except ImportError:  # pragma: no cover
    from collections import Mapping


def _get_message(record):
    """Implement logging.LogRecord.getMessage using brace-style string formatting"""
    msg = str(record.msg)
    args = record.args
    if isinstance(args, Mapping):
        # The logging module has a special case where if a LogRecord is
        # constructed with a single dict as the arg it sets it as the args.
        # This enables using key-based templating. For example:
        # `logging.info("a:%(a)s, b:%(b)s", {"a": 1, "b": 2})`.
        #
        # For the moment this style of formatting is not supported by this
        # module. It may be supported in the future by only doing it in cases
        # where the message template also supports kwarg-based templating.
        args = (args,)

    if args:
        msg = msg.format(*args)
    return msg


def _handle_wrap(fcn):
    """Wrap logging.Handler.handle to use _getMessage"""

    @functools.wraps(fcn)
    def handle(record):
        record.getMessage = types.MethodType(_get_message, record)
        return fcn(record)

    return handle


def get_logger(name=None):
    """Get a logger instance that uses brace-style string formatting"""
    log = logging.getLogger(name)
    if not hasattr(log, "_bracelogger"):
        log.handle = _handle_wrap(log.handle)
    log._bracelogger = True

    return log
