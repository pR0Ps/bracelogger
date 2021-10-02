bracelogger
===========
[![Status](https://github.com/pR0Ps/bracelogger/workflows/tests/badge.svg)](https://github.com/pR0Ps/bracelogger/actions/workflows/tests.yml)
[![Version](https://img.shields.io/pypi/v/bracelogger.svg)](https://pypi.org/project/bracelogger/)
![Python](https://img.shields.io/pypi/pyversions/bracelogger.svg)

A Python library that enables using the brace-style string formatting in log messages.

Features:
 - Supports a wide range of Python versions (v2.7 - v3.10)
 - No dependencies
 - Easy to use - no special syntax required
 - Easy to transition to from stdlib logging - just change the `logging.getLogger` calls and message
   templates.
 - Only enables brace-style formatting for loggers created by the library. This allows for gradually
   transitioning to brace-style formatting without breaking existing loggers or third party
   packages.
 - The formatting of the message is delayed until it is output (or not at all if the log message is
   filtered).
 - The args passed into the log call are stored on the `logging.LogRecord` objects as usual.

Installation
------------
```
pip install bracelogger
```

Usage example
-------------
```python
# import the library
from bracelogger import get_logger

# set up the logger
__log__ = get_logger(__name__)

# use brace-style formatting in log messages
try:
    process(some_obj)
except Exception:
    __log__.warning(
        "Failed to process object '{0!r}' with name '{0.name}' and path '{0.path}'",
        some_obj,
        exc_info=True
    )
```

Note that the above example is very basic. The real power of this module comes from being able to
use the more advanced operations that the brace-style formatting can provide. See
[the docs on the format string syntax](https://docs.python.org/library/string.html#format-string-syntax)
for more details.


Compatibility with existing code and loggers
--------------------------------------------
This library will only enable brace-style formatting for loggers created by this module's
`get_logger()` function. Loggers created via the stdlib `logging.getLogger()` function will still
use the normal %-based formatting.

This opt-in style means that codebases can gradually transition to brace-style logging without
having to convert everything over all at once. It also means that the logs from any third-party code
like libraries will continue to work as normal.

In addition to being compatible with existing code, it should also be compatible with most other
stdlib-compatible logging packages and modifications. As when using the stdlib logger, the message
arguments are still stored on the log record and the message is only formatted when it is handled
(and not at all if the message is filtered).


Converting existing code
------------------------
Because there is no special syntax required, migrating existing logs to brace-style formatting is
easy:
1. Replace `logging.getLogger(name)` with `bracelogger.get_logger(name)`
2. Change the log messages for the logger to use brace-style formatting (ex: change `%s` to `{}`)

### Special case
The logger from the standard library has a special case (introduced in [Python
2.4](https://github.com/python/cpython/blob/2.4/Lib/logging/__init__.py#L214-L227)) where key-based
formatting is used when a single dictionary is passed into the log message.
```python
logging.info("a:%(a)s, b:%(b)s", {"a": 1, "b": 2})
```
This library does not currently support this special case but there is an easy workaround - use
brace-style formatting to access the keys like so:
```python
logging.info("a:{0[a]}, b:{0[b]}", {"a": 1, "b": 2})
```


Tests
-----
This package contains basic tests. To run them, install `pytest` (`pip install pytest`) and run
`py.test` in the project directory.


License
-------
Licensed under the [GNU LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.html).
