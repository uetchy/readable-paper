from bottle import get, post, route, request, run, template, static_file
import arxiv.fetch
import os

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
    print(filepath)
    return static_file(filepath, root=os.path.join(os.path.dirname(os.path.realpath(__file__)), './static'))

@get('/')
def welcome():
    return layout_header() + """
        <h1>Readable Paper</h1>
    """ + layout_footer()

@get('/arxiv/<id>/tex')
def arxiv_tex(id):
    html_data = arxiv.fetch.extract_html(id)
    return layout_header() + html_data + layout_footer()


run(host='0.0.0.0', port=8080, debug=True)