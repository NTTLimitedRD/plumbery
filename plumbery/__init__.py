"""
Are you looking for a cloud plumber? We hope this one will be useful to you
"""

# treat logs as event streams - http://12factor.net/logs
import logging
import sys
logging.basicConfig(
    format='%(message)s',
    level=logging.INFO,
    stream=sys.stdout)

__all__ = ['__version__']

__version__ = '0.2.4'
