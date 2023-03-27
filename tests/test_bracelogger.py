#!/usr/bin/env python

import logging
import pickle
import sys

import bracelogger

import pytest


class _Obj:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __repr__(self):
        return "<Obj {}>".format(self.name)


def test_simple_message(caplog):
    """Test a reasonable approximation of the example in the readme"""
    caplog.set_level(logging.WARNING)

    __log__ = bracelogger.get_logger("logger1")
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

    l = bracelogger.get_logger("logger2")
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
    l = bracelogger.get_logger("logger4")
    sub_l = logging.getLogger("logger4.sublogger")

    std_l.info("%s %s", 1, 2)
    l.info("{} {}", 1, 2)
    sub_l.info("%s %s", 1, 2)

    assert len(caplog.records) == 3
    std_record, record, sub_record = (
        next(x for x in caplog.records if x.name == n)
        for n in ("logger3", "logger4", "logger4.sublogger")
    )

    assert std_record.args == record.args == sub_record.args
    assert isinstance(record.args, tuple)
    assert len(record.args) == 2

    assert std_record.msg == sub_record.msg == "%s %s"
    assert record.msg == "{} {}"
    assert std_record.message == record.message == sub_record.message == "1 2"


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_all_levels(caplog):
    """Test logging at all documented levels"""

    LEVELS = ["debug", "info", "warn", "warning", "error", "exception", "critical", "fatal"]
    if sys.version_info >= (3, 13):
        LEVELS.remove("warn")  # has been deprecated since 3.1, finally removed in v3.13

    TEMPLATE = "This is a {}-level log"

    caplog.set_level(1)  # capture everything
    l = bracelogger.get_logger("logger5")

    for level in LEVELS:
        getattr(l, level)(TEMPLATE, level)

    assert len(caplog.records) == len(LEVELS)
    for x in caplog.records:
        assert x.name == "logger5"
        assert isinstance(x.args, tuple)
        assert len(x.args) == 1

    for level in LEVELS:
        record = next(x for x in caplog.records if x.args[0] == level)
        assert record.msg == TEMPLATE
        assert record.message == TEMPLATE.format(*record.args)


def test_wrapped_not_modified(caplog):
    """Test that the same logger access from std and bracelogger use different formatting"""
    caplog.set_level(logging.DEBUG)

    l = bracelogger.get_logger("logger6")
    std_l = logging.getLogger("logger6")

    std_l.info("%s %s", 1, 2)
    l.info("{} {}", 1, 2)

    assert len(caplog.records) == 2
    record1, record2 = caplog.records
    assert record1.name == record2.name == "logger6"
    assert record1.args == record2.args
    assert record1.msg != record2.msg
    assert record1.message == record2.message == "1 2"


def test_instance():
    """Test loggers are the proper class (and child loggers are as well)"""

    std_l = logging.getLogger("logger7")
    std_l_child = std_l.getChild("child")

    l = bracelogger.get_logger("logger7")
    l_child = l.getChild("child")

    assert isinstance(std_l, logging.Logger)
    assert not isinstance(std_l, bracelogger.BraceloggerMixin)
    assert isinstance(l, logging.Logger)
    assert isinstance(l, bracelogger.BraceloggerMixin)

    assert isinstance(std_l_child, logging.Logger)
    assert not isinstance(std_l_child, bracelogger.BraceloggerMixin)
    assert isinstance(l_child, logging.Logger)
    assert isinstance(l_child, bracelogger.BraceloggerMixin)


def test_preserve_subclasses(caplog, monkeypatch):
    """Test that braceloggers preserve the original class of the loggers/logrecords"""

    class MyLogRecord(logging.LogRecord):
        pass

    class MyLogger(logging.Logger):
        pass

    monkeypatch.setattr("logging._loggerClass", MyLogger)
    if sys.version_info >= (3, 2):
        # doesn't exist until 3.2
        monkeypatch.setattr("logging._logRecordFactory", MyLogRecord)

    l = bracelogger.get_logger("logger8")
    assert isinstance(l, MyLogger)
    assert isinstance(l, logging.Logger)
    assert isinstance(l, bracelogger.BraceloggerMixin)

    std_l = logging.getLogger("logger8")
    assert isinstance(std_l, logging.Logger)
    assert isinstance(std_l, MyLogger)
    assert not isinstance(std_l, bracelogger.BraceloggerMixin)

    caplog.set_level(logging.INFO)
    std_l.info("%s %s", 1, 2)
    l.info("{} {}", 1, 2)

    assert len(caplog.records) == 2
    record_std, record_brace = caplog.records
    if record_std.msg == "{} {}":
        record_std, record_brace = record_brace, record_std

    assert isinstance(record_std, logging.LogRecord)
    if sys.version_info >= (3, 2):
        assert isinstance(record_std, MyLogRecord)
    assert not isinstance(record_std, bracelogger.BracelogRecordMixin)

    assert isinstance(record_brace, logging.LogRecord)
    if sys.version_info >= (3, 2):
        assert isinstance(record_brace, MyLogRecord)
    assert isinstance(record_brace, bracelogger.BracelogRecordMixin)


def test_no_extra_attribute(caplog):

    std_l = logging.getLogger("logger9")
    l = bracelogger.get_logger("logger9")

    caplog.set_level(logging.INFO)
    std_l.info("%s %s", 1, 2)
    l.info("{} {}", 1, 2)

    assert len(caplog.records) == 2
    record1, record2 = caplog.records

    assert "getMessage" not in record1.__dict__
    assert "getMessage" not in record2.__dict__

    assert record1.name == record2.name == "logger9"
    assert record1.msg != record2.msg
    assert record1.message == record2.message == "1 2"


@pytest.mark.xfail(reason="Pickling not supported with dynamically-created classes")
def test_pickle_logrecord(caplog):
    """Test that the modified LogRecords can be [de]serialized using the pickle module"""
    caplog.set_level(logging.INFO)

    bl = bracelogger.get_logger("logger10")
    sl = logging.getLogger("logger10")

    data = {"a": 1, "b": 2}
    TEMPLATES = ("a:{0[a]}, b:{0[b]}", "a:{a}, b:{b}", "a:%(a)s, b:%(b)s")

    bl.info(TEMPLATES[0], data)
    bl.info(TEMPLATES[1], data)
    sl.info(TEMPLATES[2], data)

    for r, tmpl in zip(caplog.records, TEMPLATES):
        new = pickle.loads(pickle.dumps(r))
        assert new.levelno == r.levelno == logging.INFO
        assert new.args == r.args == data
        assert new.msg == r.msg == tmpl
        assert new.getMessage() == new.message == r.getMessage() == r.message == "a:1, b:2"
