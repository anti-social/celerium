from flask import Flask
app = Flask('celerium')

from . import config
app.config.from_object(config)
app.config.from_envvar('CELERIUM_SETTINGS', silent=True)

from .util import current_url
app.jinja_env.globals['current_url'] = current_url
from functools import partial
app.jinja_env.globals['partial'] = partial


from . import views
