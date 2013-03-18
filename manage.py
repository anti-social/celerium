from flask.ext.script import Manager, Server

from celerium.app import app


manager = Manager(app)

@manager.command
def events(project=None, frequency=5):
    from functools import partial
    from celery.app.base import Celery
    from celery.bin.celeryev import EvCommand
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
def clean_old_events():
    from datetime import datetime, timedelta
    from celerium.searcher import task_searcher

    task_searcher.delete(timestamp__lte=datetime.now() - timedelta(days=7))

if __name__ == "__main__":
    manager.run()
