#!/usr/bin/env python

import pytest

import logging
from bracelogger import get_logger


class _Obj:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __repr__(self):
        return "<Obj {}>".format(self.name)


def test_simple_message(caplog):
    """Test a reasonable approximation of the example in the readme"""
    caplog.set_level(logging.WARNING)

    __log__ = get_logger("logger1")
    some_obj = _Obj("testname", "/test/path")

    try:
        1 / 0
    except ZeroDivisionError:
        __log__.warning(
            "Failed to process object '{0!r}' with name '{0.name}' and path '{0.path}'",
            some_obj,
            exc_info=True,
        )

    assert len(caplog.records) == 1
    record = caplog.records[0]

    assert record.name == "logger1"
    assert isinstance(record.args, tuple)
    assert len(record.args) == 1
    assert record.args[0] == some_obj
    assert record.message == "Failed to process object '<Obj testname>' with name 'testname' and path '/test/path'"
    assert record.exc_info[0] == ZeroDivisionError


def test_dict_special_case(caplog):
    """Test the dict special case in the stdlib logger is handled properly"""
    caplog.set_level(logging.INFO)

    l = get_logger("logger2")
    data = {"a": 1, "b": 2}

    # test index-based and key-based formatting
    l.info("a:{0[a]}, b:{0[b]}", data)
    l.info("a:{a}, b:{b}", data)

    assert len(caplog.records) == 2
    record1 = caplog.records[0]
    record2 = caplog.records[1]

    assert record1.name == record2.name == "logger2"
    assert record1.args == record2.args == data
    assert isinstance(record1.args, dict)
    assert record1.message == record2.message == "a:1, b:2"


def test_no_other_loggers(caplog):
    """Test that only the loggers created by the module use brace formatting"""
    caplog.set_level(logging.INFO)

    std_l = logging.getLogger("logger3")
    l = get_logger("logger4")

    std_l.info("%s %s", 1, 2)
    l.info("{} {}", 1, 2)

    assert len(caplog.records) == 2
    std_record, record = caplog.records
    if std_record.name == "logger4":
        std_record, record = record, std_record

    assert std_record.name == "logger3"
    assert record.name == "logger4"

    assert std_record.args == record.args
    assert isinstance(record.args, tuple)
    assert len(record.args) == 2

    assert std_record.msg == "%s %s"
    assert record.msg == "{} {}"
    assert std_record.message == record.message == "1 2"
