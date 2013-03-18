DEBUG = True

CELERIUM_SOLR_URL = 'http://localhost:8983/solr/celery'

CELERIUM_PROJECTS = ['EXample.com']
CELERIUM_PROJECT_CELERY_CONFIG = {
    'EXample.com': {'BROKER_URL': 'redis://localhost:6379/0'},
}
