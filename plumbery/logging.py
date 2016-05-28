from __future__ import absolute_import
import logging
import colorlog

loggers = {}


class PlumberyLogFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """
    def filter(self, record):
        return True


def setup_logging(engine=None):
    global loggers
    if loggers.get('plumbery'):
        return loggers.get('plumbery')
    else:
        formatter = colorlog.ColoredFormatter(
            "%(asctime)-2s %(module)s %(funcName)-6s %(log_color)s%(message)s",
            datefmt='%H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )
        log = logging.getLogger('plumbery')
        log.setLevel(logging.DEBUG)
        if len(log.filters) == 0:
            f = PlumberyLogFilter()
            log.addFilter(f)
        if len(log.handlers) == 0:
            handler = colorlog.StreamHandler()
            handler.setFormatter(formatter)
            log.addHandler(handler)
        loggers.update(dict(name=log))
        return log