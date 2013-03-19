# Fix runserver command with reloader
import os
import sys
sys.path[:0] = [os.path.split(os.path.dirname(__file__))[0]]

from flask.ext.script import Manager

from celerium.app import app


manager = Manager(app)


@manager.command
def events(project=None, frequency=10):
    from functools import partial
    from celery.app.base import Celery
    try:
        # celery 3.0
        from celery.bin.celeryev import EvCommand
    except ImportError:
        # celery 3.1
        from celery.bin.events import events as EvCommand
    from celerium.camera import Camera

    celery_app = Celery()
    celery_app.conf.add_defaults(
        app.config['CELERIUM_PROJECT_CELERY_CONFIG'][project])
    command = EvCommand(app=celery_app)
    pidfile = 'celeryev-%s.pid' % project
    command.run(camera=partial(Camera, project=project),
                frequency=frequency,
                pidfile=pidfile)


@manager.command
def clean_old_events(days=6):
    from celerium.searcher import task_searcher

    days = int(days)
    if days < 0:
        raise ValueError('Days must be great or equal zero')
    task_searcher.delete(timestamp__lte='NOW/DAY-%sDAYS' % int(days))


def main():
    manager.run()
    

if __name__ == '__main__':
    main()
