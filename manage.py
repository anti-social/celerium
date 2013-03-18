from datetime import datetime, timedelta

from flask.ext.script import Manager, Server

from celerium.app import app
from celerium.searcher import TaskSearcher


manager = Manager(app)

@manager.command
def clean_old_events():
    searcher = TaskSearcher(app.config['CELERIUM_SOLR_URL'])
    searcher.delete(timestamp__lte=datetime.now() - timedelta(days=7))

if __name__ == "__main__":
    manager.run()
