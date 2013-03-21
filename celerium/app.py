import sys
import logging


from flask import Flask
app = Flask('celerium')

from . import config
app.config.from_object(config)
app.config.from_envvar('CELERIUM_SETTINGS', silent=True)

default_loglevel = getattr(
    logging, app.config.get('CELERIUM_DEFAULT_LOGLEVEL', 'INFO'))
logging.basicConfig(stream=sys.stdout, level=default_loglevel)
app.logger.addHandler(logging.StreamHandler(stream=sys.stdout))
app.logger.setLevel(default_loglevel)

from .util import current_url
app.jinja_env.globals['current_url'] = current_url
from functools import partial
app.jinja_env.globals['partial'] = partial


from . import views
