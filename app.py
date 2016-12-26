import os
import logging
from bottle import get, post, route, request, run, template, static_file
from rq import Queue
from redis import Redis
from arxiv_worker import fetch_and_convert_tex

redis_conn = Redis(host='redis')
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

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=os.path.join(os.path.dirname(os.path.realpath(__file__)), './static'))

@get('/')
def welcome():
    return layout_header() + """
        <h1>Readable Paper</h1>
        <form onSubmit="location.pathname='/arxiv/'+document.querySelector('#field').value; return false">
            <input type="text" id="field" />
        </form>
    """ + layout_footer()

@get('/arxiv/<id>')
def arxiv_get(id):
    print(id)
    if redis_conn.exists(id):
        job = queue.fetch_job(redis_conn.get(id).decode('utf-8'))
        if job.result == None:
            return "Converting! Wait for a sec and refresh this page"
        else:
            return layout_header() + job.result + layout_footer()
    else:
        job = queue.enqueue(fetch_and_convert_tex, id)
        redis_conn.set(id, job.id.encode('utf-8'))
        return "Process has been started! Refresh this page later"

run(host='0.0.0.0', port=80, server='paste', debug=True)