'''
Author: your name
Date: 2022-02-27 11:15:55
LastEditTime: 2022-03-05 20:32:42
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/log.py
'''

import sys
import json
import logging
import logging.handlers
import logging.config
from json.tool import main
from cmath import log

try:
    import curses
except ImportError:
    curses = None


DEFAULT_COLORS = {
    logging.DEBUG: 4,
    logging.INFO: 2,
    logging.WARNING: 3,
    logging.ERROR: 1
}


def _stderr_supports_color():
    color = False
    if curses and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                color = True
        except Exception:
            pass
    return color


class LogFormatter(logging.Formatter):
    """Log formatter used in Tornado.
    Key features of this formatter are:
    * Color support when logging to a terminal that supports it.
    * Timestamps on every log line.
    * Robust against str/bytes encoding problems.
    This formatter is enabled automatically by
    `tornado.options.parse_command_line` or `tornado.options.parse_config_file`
    (unless ``--logging=none`` is used).
    """

    def __init__(self, format, datefmt, colors=DEFAULT_COLORS):
        r"""
        :arg bool color: Enables color support.
        :arg string fmt: Log message format.
          It will be applied to the attributes dict of log records. The
          text between ``%(color)s`` and ``%(end_color)s`` will be colored
          depending on the level if color support is on.
        :arg dict colors: color mappings from logging level to terminal color
          code
        :arg string datefmt: Datetime format.
          Used for formatting ``(asctime)`` placeholder in ``prefix_fmt``.
        .. versionchanged:: 3.2
           Added ``fmt`` and ``datefmt`` arguments.
        """
        logging.Formatter.__init__(self, datefmt=datefmt)
        self._fmt = format

        self._colors = {}
        if _stderr_supports_color():
            # The curses module has some str/bytes confusion in
            # python3.  Until version 3.2.3, most methods return
            # bytes, but only accept strings.  In addition, we want to
            # output these strings with the logging module, which
            # works with unicode strings.  The explicit calls to
            # unicode() below are harmless in python2 but will do the
            # right conversion in python 3.

            colors = {
                logging.DEBUG: 4,
                logging.INFO: 2,
                logging.WARNING: 3,
                logging.ERROR: 1
            }
            fg_color = (curses.tigetstr("setaf") or
                        curses.tigetstr("setf") or "")
            if (3, 0) < sys.version_info < (3, 2, 3):
                fg_color = str(fg_color, "ascii")
        
            for levelno, code in colors.items():
                self._colors[levelno] = str(curses.tparm(fg_color, code), "ascii")
            self._normal = str(curses.tigetstr("sgr0"), "ascii")
        else:
            self._colors = {
                logging.DEBUG: '\033[94m',   # Blue
                logging.INFO: '\033[92m',     # Green
                logging.WARNING: '\033[93m',  # Yellow
                logging.ERROR: '\033[91m',  # Red
            }
            self._normal = '\033[0m'

    def format(self, record):
        try:
            message = record.getMessage()
            assert isinstance(message, str)  # guaranteed by logging
            record.message = message
        except Exception as e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)
        record.asctime = self.formatTime(record, self.datefmt)
        if record.levelno in self._colors:
            record.color = self._colors[record.levelno]
            record.end_color = self._normal
        else:
            record.color = record.end_color = ''

        formatted = self._fmt % record.__dict__
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            # exc_text contains multiple lines.  We need to _safe_unicode
            # each line separately so that non-utf8 bytes don't cause
            # all the newlines to turn into '\n'.
            lines = [formatted.rstrip()]
            lines.extend(ln for ln in record.exc_text.split('\n'))
            formatted = '\n'.join(lines)
        return formatted.replace("\n", "\n    ")

wlog = logging.getLogger("ml.widget.logger")
mlog = logging.getLogger("ml.logger")
dlog = logging.getLogger("ml.data.logger")


def init_loggers(config_path="./log_config.json"):
    with open(config_path, 'r') as f:
        config = json.load(f)
        logging.config.dictConfig(config)
        
    
if __name__ == '__main__':
    init_loggers()
    wlog.debug("debug")
    wlog.info("info")
    wlog.error("error")