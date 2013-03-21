import os
from functools import partial

from celery import states
from celery.app.base import Celery
from celery.loaders.base import BaseLoader
from celery.events.snapshot import Polaroid
from celery.utils.timeutils import maybe_iso8601

from .app import app
from .searcher import worker_searcher, task_searcher


class CeleryLoader(BaseLoader):
    def read_configuration(self):
        project = os.environ.get('CELERIUM_PROJECT')
        return app.config['CELERIUM_PROJECT_CELERY_CONFIG'][project]

celery_app = Celery(loader=CeleryLoader)

class Camera(Polaroid):
    clear_after = True

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', os.environ.get('CELERIUM_PROJECT'))
        super(Camera, self).__init__(*args, **kwargs)

    def on_shutter(self, state):
        if not state.event_count:
            # No new events since last snapshot
            return

        if state.workers:
            worker_searcher.add(
                worker_searcher.generate_indexing_docs(state.workers.values(),
                                                       project=self.project),
                commit=False)

        if state.tasks:
            task_searcher.add(
                task_searcher.generate_indexing_docs(state.tasks.values(),
                                                     project=self.project),
                commit=False)
