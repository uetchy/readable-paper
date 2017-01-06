import os
import bottle
import redis
from rq import Queue
from worker import arxiv_worker

port = os.environ.get('PORT', 80)
redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379')
is_production = os.environ.get('DEBUG', False)

print('is_production:', is_production)

# setup job queue
print('redis_url:', redis_url)
redis_conn = redis.from_url(redis_url)
queue = Queue(connection=redis_conn)

@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root=os.path.join(os.path.dirname(os.path.realpath(__file__)), './static'))

@bottle.get('/')
def welcome():
    return bottle.template("""
        % rebase('template/base.tpl', title='Readable Paper')
        <style>
            body {
                text-align: center;
            }
        </style>
        <form onSubmit="location.pathname='/arxiv/'+document.querySelector('#field').value; return false">
            <input type="text" id="field" placeholder="arXiv ID" />
            <button type="submit">Convert</button>
            <p>Currently supports arXiv papers.</p>
            <p>Put arXiv ID into textarea to convert (e.g. 1612.04811v1)</p>
        </form>
    """)

@bottle.get('/arxiv/<id>')
def arxiv_get(id):
    if redis_conn.exists(id):
        job = queue.fetch_job(redis_conn.get(id).decode('utf-8'))
        if job.result == None:
            return bottle.template("""
                % rebase('template/base.tpl', title='Readable Paper')
                <p>Converting now! Wait for a sec and refresh this page</p>
            """)
        else:
            return bottle.template("""
                % rebase('template/base.tpl', title='Readable Paper')
                {{!result}}
            """, result=job.result)
    else:
        # enqueue job and push job id to DB
        job = queue.enqueue(arxiv_worker.fetch_and_convert_tex, id)
        redis_conn.set(id, job.id.encode('utf-8'))
        return bottle.template("""
            % rebase('template/base.tpl', title='Readable Paper')
            <p>Process has been started! Refresh this page later</p>
        """)

bottle.run(host='0.0.0.0', port=port, server='paste', debug=not is_production)