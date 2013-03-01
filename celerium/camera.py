import os
from functools import partial

from celery import states
from celery.app.base import Celery
from celery.loaders.base import BaseLoader
from celery.events.snapshot import Polaroid
from celery.utils.timeutils import maybe_iso8601

from .app import app
from .searcher import TaskSearcher


class CeleryLoader(BaseLoader):
    def read_configuration(self):
        project = os.environ.get('CELERIUM_PROJECT')
        return app.config['CELERIUM_PROJECT_CELERY_CONFIG'][project]

celery_app = Celery(loader=CeleryLoader)

class Camera(Polaroid):
    clear_after = True

    def __init__(self, *args, **kwargs):
        super(Camera, self).__init__(*args, **kwargs)
        self._workers_cache = {}

        self.task_searcher = TaskSearcher('http://localhost:8983/solr/celery')
        self.project = os.environ.get('CELERIUM_PROJECT')

    def get_worker(self, hostname):
        if hostname not in self._workers_cache:
            self._workers_cache[hostname] = WorkerState.objects.get(
                hostname=hostname)
        return self._workers_cache[hostname]
    
    def on_shutter(self, state):
        if not state.event_count:
            # No new events since last snapshot
            return

        from pprint import pformat
        print "Workers: %s" % (pformat(state.workers, indent=4), )
        print "Tasks: %s" % (pformat(state.tasks, indent=4), )
        print "Total: %s events, %s tasks" % (
            state.event_count, state.task_count)

        if state.tasks:
            self.task_searcher.add(
                map(partial(TaskSearcher.generate_indexing_doc, project=self.project),
                    state.tasks.values()),
                commit=False)
