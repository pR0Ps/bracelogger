#!/usr/bin/env python

"""Use brace-style string formatting in log messages"""

import functools
import logging

try:
    from collections.abc import Mapping
except ImportError:  # pragma: no cover
    from collections import Mapping


def _get_message(record):
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


def _handle_wrap(fcn):
    """Wrap logging.Handler.handle to use _get_message"""

    @functools.wraps(fcn)
    def handle(record):
        record.getMessage = functools.partial(_get_message, record)
        return fcn(record)

    return handle


def get_logger(name=None):
    """Get a logger instance that uses brace-style string formatting"""
    log = logging.getLogger(name)
    if not hasattr(log, "_bracelogger"):
        log.handle = _handle_wrap(log.handle)
    log._bracelogger = True

    return log
