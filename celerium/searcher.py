from datetime import datetime

from solar import CommonSearcher

from celery.utils.timeutils import maybe_iso8601


def try_fromtimestamp(timestamp):
    if timestamp:
       return datetime.fromtimestamp(timestamp)

class WorkerSearcher(CommonSearcher):
    type_value = 'Worker'
    
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
    
    datetime_fields = (
        'timestamp', 'sent', 'received', 'started', 'succeeded', 'expires')
    
    @classmethod
    def generate_indexing_doc(cls, task, project):
        doc = dict(task)
        doc['id'] = doc.pop('uuid')
        doc['project'] = project
        if doc['name'].find('.') != -1:
            doc['module'] = '.'.join(doc['name'].split('.')[:-1])
        for field in cls.datetime_fields:
            doc[field] = try_fromtimestamp(doc[field])
        doc["eta"] = maybe_iso8601(doc["eta"])
        if doc['worker']:
            doc['worker'] = doc['worker'].hostname
        return doc
