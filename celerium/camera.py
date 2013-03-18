import os
from functools import partial

from celery import states
from celery.app.base import Celery
from celery.loaders.base import BaseLoader
from celery.events.snapshot import Polaroid
from celery.utils.timeutils import maybe_iso8601

from .app import app
from .searcher import WorkerSearcher, TaskSearcher


class CeleryLoader(BaseLoader):
    def read_configuration(self):
        project = os.environ.get('CELERIUM_PROJECT')
        return app.config['CELERIUM_PROJECT_CELERY_CONFIG'][project]

celery_app = Celery(loader=CeleryLoader)

class Camera(Polaroid):
    clear_after = True

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', os.environ.get('CELERIUM_PROJECT'))
        self.worker_searcher = WorkerSearcher(app.config['CELERIUM_SOLR_URL'])
        self.task_searcher = TaskSearcher(app.config['CELERIUM_SOLR_URL'])
        super(Camera, self).__init__(*args, **kwargs)

    def on_shutter(self, state):
        if not state.event_count:
            # No new events since last snapshot
            return

        # import pprint
        # print "Workers: %s" % (pprint.pformat(state.workers, indent=4), )
        # print "Tasks: %s" % (pprint.pformat(state.tasks, indent=4), )
        # print "Total: %s events, %s tasks" % (
        #     state.event_count, state.task_count)
        # for worker in state.workers.values():
        #     pprint.pprint(dict(worker))
        # for task in state.tasks.values():
        #     pprint.pprint(dict(task))

        if state.workers:
            self.worker_searcher.add(
                map(partial(WorkerSearcher.generate_indexing_doc, project=self.project),
                    state.workers.values()),
                commit=False)

        if state.tasks:
            self.task_searcher.add(
                map(partial(TaskSearcher.generate_indexing_doc, project=self.project),
                    state.tasks.values()),
                commit=False)
