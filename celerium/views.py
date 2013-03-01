from datetime import datetime

from flask import request, render_template, url_for, abort

from solar import X
from solar.queryfilter import QueryFilter, FacetFilter, \
    FacetQueryFilter, FacetQueryFilterValue, \
    OrderingFilter, OrderingValue
from solar.contrib.flask.pagination import Pagination

from .app import app
from .util import current_url
from .searcher import TaskSearcher

@app.route('/')
def index():
    searcher = TaskSearcher(app.config['CELERIUM_SOLR_URL'])
    search_fail = (
        searcher.search()
        .filter(state='FAILURE')
        .group('project', limit=4)
        .order_by('-timestamp')
        .limit(len(app.config['CELERIUM_PROJECTS'])))
    search_long = (
        searcher.search()
        .filter(state='SUCCESS')
        .group('project', limit=4)
        .order_by('-runtime')
        .limit(len(app.config['CELERIUM_PROJECTS'])))
    return render_template('index.html',
                           failed_tasks=search_fail,
                           long_tasks=search_long)

@app.route('/tasks/<project>')
def tasks(project):
    if project not in app.config['CELERIUM_PROJECTS']:
        abort(404)

    try:
        page = int(request.args.get('page', '1'))
    except ValueError:
        page = 1

    searcher = TaskSearcher(app.config['CELERIUM_SOLR_URL'])
    search_query = (
        searcher.search()
        .filter(project=project))

    fixed_dt = request.args.get('fixed_dt')
    if fixed_dt:
        try:
            fixed_dt = datetime.strptime(fixed_dt, "%Y-%m-%d %H:%M:%S.%f")
            search_query = search_query.filter(timestamp__lte=fixed_dt)
        except ValueError:
            fixed_dt = None

    qf = QueryFilter()
    qf.add_filter(FacetFilter('state', mincount=0))
    qf.add_filter(FacetFilter('module', mincount=1))
    if 'module' in request.args:
        qf.add_filter(FacetFilter('name', mincount=1))
    qf.add_filter(
        FacetQueryFilter(
            'timestamp',
            FacetQueryFilterValue('last_hour', X(timestamp__gte='NOW-1HOUR'), title='Last Hour'),
            FacetQueryFilterValue('today', X(timestamp__gte='NOW/DAY'), title='Today'),
            FacetQueryFilterValue('last_day', X(timestamp__gte='NOW-1DAY'), title='Last Day')))
    qf.add_filter(
        FacetQueryFilter(
            'runtime',
            FacetQueryFilterValue('1m', X(runtime__gte=60), title='Minute'),
            FacetQueryFilterValue('10m', X(runtime__gte=60 * 10), title='10 Minutes'),
            FacetQueryFilterValue('1h', X(runtime__gte=60 * 60), title='Hour')))
    qf.add_ordering(
        OrderingFilter(
            'sort',
            OrderingValue(
                'timestamp', 'timestamp',
            ),
            OrderingValue(
                '-timestamp', '-timestamp',
            ),
            OrderingValue(
                'runtime', 'runtime',
            ),
            OrderingValue(
                '-runtime', '-runtime',
            ),
            default='-timestamp'))
        
    search_query = qf.apply(search_query, request.args)
    pagination = Pagination(search_query, page=page, per_page=20)
    qf.process_results(pagination.query.results)

    return render_template('tasks.html',
                           project=project,
                           pagination=pagination,
                           query_filter=qf,
                           fixed_dt=fixed_dt,
                           current_dt=datetime.now())

@app.route('/view/<task_id>')
def view(task_id):
    searcher = TaskSearcher(app.config['CELERIUM_SOLR_URL'])
    task = searcher.get(id=task_id)
    return render_template('view.html', project=task.project, task=task)
