import os
import bottle
import redis
from rq import Queue
from worker import arxiv_worker
from pypandoc.pandoc_download import download_pandoc

port = os.environ.get('PORT', 80)
redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379')
is_production = os.environ.get('DEBUG', False)

print('is_production:', is_production)

# setup pandoc
download_pandoc()

# setup job queue
print('redis_url:', redis_url)
redis_conn = redis.from_url(redis_url)
queue = Queue(connection=redis_conn)

def layout_header():
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/5.0.0/normalize.min.css" />
            <style type="text/css">code{white-space: pre;}</style>
            <link rel="stylesheet" href="/static/pandoc.css">

            <!-- Include MathJax -->
            <script type="text/x-mathjax-config">
                MathJax.Hub.Config({
                    tex2jax: {
                        inlineMath: [['$','$'], ['\\(','\\)']],
                        displayMath: [['$$','$$'], ['\[','\]']],
                        processEscapes: true,
                        processEnvironments: true,
                        skipTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
                        TeX: { equationNumbers: { autoNumber: "AMS" },
                             extensions: ["AMSmath.js", "AMSsymbols.js"] }
                    }
                });
            </script>
            <script type="text/javascript" async src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML"></script>
        </head>
        <body>
    """

def layout_footer():
    return """
        </body>
        </html>
    """

@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root=os.path.join(os.path.dirname(os.path.realpath(__file__)), './static'))

@bottle.get('/')
def welcome():
    return layout_header() + """
        <style>
            body {
                text-align: center;
            }
        </style>
        <h1>Readable Paper</h1>
        <form onSubmit="location.pathname='/arxiv/'+document.querySelector('#field').value; return false">
            <input type="text" id="field" placeholder="arXiv ID" />
            <button type="submit">Convert</button>
            <p>Example: 1612.04811v1</p>
        </form>
    """ + layout_footer()

@bottle.get('/arxiv/<id>')
def arxiv_get(id):
    if redis_conn.exists(id):
        job = queue.fetch_job(redis_conn.get(id).decode('utf-8'))
        if job.result == None:
            return "Converting now! Wait for a sec and refresh this page"
        else:
            return layout_header() + job.result + layout_footer()
    else:
        # enqueue job and push job id to DB
        job = queue.enqueue(arxiv_worker.fetch_and_convert_tex, id)
        redis_conn.set(id, job.id.encode('utf-8'))
        return "Process has been started! Refresh this page later"

bottle.run(host='0.0.0.0', port=port, server='paste', debug=not is_production)