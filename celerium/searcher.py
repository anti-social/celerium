from datetime import datetime

from solar import CommonSearcher
from solar.document import Document

from celery.events.state import Worker as _Worker, Task
from celery.utils.timeutils import maybe_iso8601

from .app import app


def try_fromtimestamp(timestamp):
    if timestamp:
       return datetime.fromtimestamp(timestamp)

class Worker(_Worker):
    # increase expire_window cause 200 is too small
    # Solr doesnt have time to do commit
    # 400 means freq * 4
    # if freq == 5 then
    # worker evaluates as alive during 20 seconds after last heartbeat
    expire_window = 400
    
class WorkerDocument(Document):
    @property
    def instance(self):
        if not hasattr(self, '_instance'):
            self._instance = Worker(**self.to_solr())
            for timestamp in self.heartbeats:
                self._instance.on_heartbeat(timestamp=timestamp)
        return self._instance
    
class WorkerSearcher(CommonSearcher):
    type_value = 'Worker'
    document_cls = WorkerDocument
    
    @classmethod
    def generate_indexing_doc(cls, worker, project):
        doc = dict(worker)
        doc['id'] = u'%s:%s' % (project, worker.hostname)
        doc['name'] = worker.hostname
        doc['project'] = project
        if worker.heartbeats:
            doc['last_heartbeat'] = try_fromtimestamp(worker.heartbeats[-1])
        return doc


class TaskSearcher(CommonSearcher):
    type_value = 'Task'

    iso8601_fields = ('eta', 'expires')
    timestamp_fields = (
        'timestamp', 'sent', 'received', 'started', 'succeeded',
        'failed', 'retried', 'revoked', 'expires',
        )
    
    @classmethod
    def generate_indexing_doc(cls, task, project):
        doc = dict(task)
        doc['id'] = doc.pop('uuid')
        doc['project'] = project
        if doc['name'].find('.') != -1:
            doc['module'] = '.'.join(doc['name'].split('.')[:-1])
        for field in cls.timestamp_fields:
            doc[field] = try_fromtimestamp(doc[field])
        for field in cls.iso8601_fields:
            doc[field] = maybe_iso8601(doc[field])
        if doc['worker']:
            doc['worker'] = doc['worker'].hostname
        return doc


worker_searcher = WorkerSearcher(app.config['CELERIUM_SOLR_URL'])
task_searcher = TaskSearcher(app.config['CELERIUM_SOLR_URL'])
