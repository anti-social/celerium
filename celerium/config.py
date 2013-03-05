DEBUG = True

CELERIUM_SERVER_ADDRESS = '0.0.0.0'
# CELERIUM_SERVER_ADDRESS = '127.0.0.1'
CELERIUM_SERVER_PORT = 5500

CELERIUM_SOLR_URL = 'http://localhost:8983/solr/celery'

CELERIUM_PROJECTS = ['EXample.com', 'Prom.ua', 'Tiu.ru', 'Deal.by', 'Satu.kz']
CELERIUM_PROJECT_CELERY_CONFIG = {
    'EXample.com': {'BROKER_URL': 'redis://localhost:6379/11'},
    'Prom.ua': {'BROKER_URL': 'redis://localhost:6379/11'},
    'Tiu.ru': {'BROKER_URL': 'redis://localhost:6379/11'},
    'Deal.by': {'BROKER_URL': 'redis://localhost:6379/11'},
    'Satu.kz': {'BROKER_URL': 'redis://localhost:6379/11'},
}
