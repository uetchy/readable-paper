import os
import bottle
import pymongo
import redis
from rq import Queue
from worker import arxiv_worker

host = '0.0.0.0'
port = os.environ.get('PORT', 8080)
redis_url = os.environ.get('REDIS_URL', 'redis://queue:6379')
mongodb_url = os.environ.get('MONGODB_URL', 'mongodb://db:27017/db')
is_production = os.environ.get('DEBUG', False)

print('is_production:', is_production)

# setup database
mongo_client = pymongo.MongoClient(mongodb_url)
db = mongo_client.get_default_database()
papers = db.papers

# setup job queue
print('redis_url:', redis_url)
redis_conn = redis.from_url(redis_url)
queue = Queue(connection=redis_conn)


@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(
        filepath,
        root=os.path.join(
            os.path.dirname(os.path.realpath(__file__)), './static'))


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
            <p>Supports <a href="https://arxiv.org">arXiv</a> papers.</p>
            <p>Put arXiv ID into textarea to convert (e.g. <b>1612.04811v1</b>)</p>
        </form>
    """)


@bottle.get('/arxiv/<id>')
def arxiv_get(id):
    if redis_conn.exists(id):
        job = queue.fetch_job(redis_conn.get(id).decode('utf-8'))
        if job is None:
            redis_conn.delete(id)
        elif job.result is None:
            return bottle.template("""
                % rebase('template/base.tpl', title='Readable Paper')
                <p>Converting now! Wait for a sec and refresh this page</p>
            """)

    paper = papers.find_one({"arxiv_id": id})
    if paper:
        return bottle.template(
            """
            % rebase('template/base.tpl', title='Readable Paper')
            <div class="paper">
            <blockquote>
                <a href="https://arxiv.org/abs/{{arxiv_id}}">Original source</a>
            </blockquote>
            {{!content}}
            </div>
        """,
            content=paper['content'],
            arxiv_id=id)
    else:
        # enqueue job and push job id to DB
        job = queue.enqueue(arxiv_worker.fetch_and_convert_tex, id)
        redis_conn.set(id, job.id.encode('utf-8'))
        return bottle.template("""
            % rebase('template/base.tpl', title='Readable Paper')
            <p>Process has been started! Refresh this page later</p>
        """)


bottle.run(host=host, port=port, server='paste', debug=(not is_production))
