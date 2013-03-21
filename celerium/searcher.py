from datetime import datetime

from solar import CommonSearcher
from solar.document import Document

from celery.events.state import Worker as _Worker, Task
from celery.utils.timeutils import maybe_iso8601

from .app import app


SEP = ':'

def try_fromtimestamp(timestamp):
    if timestamp:
       return datetime.fromtimestamp(timestamp)

def get_project_and_name(worker, project=None):
    if worker:
        if SEP in worker.hostname:
            return worker.hostname.split(SEP, 1)
        return worker.hostname, project
    return None, project

def get_worker_id(project, name):
    return u'%s%s%s' % (project, SEP, name)

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
    def generate_indexing_docs(cls, workers, project=None):
        docs = []
        for worker in workers:
            project, name = get_project_and_name(worker, project=project)
            if project not in app.config['CELERIUM_PROJECTS']:
                continue
            doc = dict(worker)
            doc['id'] = get_worker_id(project, name)
            doc['project'] = project
            doc['name'] = name
            if worker.heartbeats:
                doc['last_heartbeat'] = try_fromtimestamp(worker.heartbeats[-1])
            docs.append(doc)
        return docs


class TaskSearcher(CommonSearcher):
    type_value = 'Task'

    iso8601_fields = ('eta', 'expires')
    timestamp_fields = (
        'timestamp', 'sent', 'received', 'started', 'succeeded',
        'failed', 'retried', 'revoked', 'expires',
        )
    
    @classmethod
    def generate_indexing_docs(cls, tasks, project=None):
        docs = []
        for task in tasks:
            worker = task.worker
            project, worker_name = get_project_and_name(worker, project=project)
            if project not in app.config['CELERIUM_PROJECTS']:
                continue
            doc = dict(task)
            doc.pop('worker', None)
            doc['id'] = doc.pop('uuid')
            doc['project'] = project
            if doc['name'].find('.') != -1:
                doc['module'] = '.'.join(doc['name'].split('.')[:-1])
            for field in cls.timestamp_fields:
                doc[field] = try_fromtimestamp(doc[field])
            for field in cls.iso8601_fields:
                doc[field] = maybe_iso8601(doc[field])
            if worker:
                doc['worker_id'] = get_worker_id(project, worker_name)
                doc['worker_name'] = worker_name
            docs.append(doc)
        return docs


worker_searcher = WorkerSearcher(app.config['CELERIUM_SOLR_URL'])
task_searcher = TaskSearcher(app.config['CELERIUM_SOLR_URL'])
