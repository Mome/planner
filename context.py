#! /usr/bin/python2
import BaseHTTPServer
import os
import time

DEFAULT_CONTENT = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Mehrzeilige Eingabebereiche definieren</title>
  </head>
  <body>
    <h1>Ganz spontan</h1>
    <p>Welche HTML-Elemente fallen Ihnen ein, was bewirken sie?<p>
    <textarea>404 : File not found</textarea>
  </body>
</html>
"""

EXTRA_LINE = """
<style class="fallback">body{white-space:pre;font-family:monospace}</style><script src="markdeep.min.js"></script><script src="http://casual-effects.com/markdeep/latest/markdeep.min.js"></script>
"""

FILE_PATH = os.path.expanduser('~/context')

def prepare_content(text):
    defs = text.split('\n\n') 
    for i,d in enumerate(defs):
        if ' - ' not in d: continue
        head, tail = d.split(' - ',1)
        defs[i] = '__' + head + '__ - ' + tail
    return '\n\n'.join(defs)
        

class HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    
    def do_GET(self):
        self.do_HEAD()        
        try:
            content = self.load_content()
        except Exception as e:
            content = DEFAULT_CONTENT
            #raise e 
        self.wfile.write(content)

    def load_content(self):
        path = os.path.join(FILE_PATH, self.path[1:])
        if self.path == '/':
            title = '**Table of Content**\n'
            file_list = os.listdir(FILE_PATH)
            file_list = ['* ['+name+']('+name+')' for name in file_list if not name.startswith('.')]
            content = '\n\n'.join(file_list)
        else: 
            title = os.path.split(path)[1]
            title = title.replace('_',' ') 
            title = ''.join(['**',title,'**','\n'])
            with open(path) as f:
                text = f.read()
            content = prepare_content(text)

        return '\n'.join([title, content, EXTRA_LINE])


def main():
    import sys
    args = sys.argv[1:]
    if args:
        PORT_NUMBER = int(args[0])
    else:
        PORT_NUMBER = 8000

    FILE_PATH = os.path.expanduser('~/context')
    HOST_NAME = ''
    
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
    
    httpd = BaseHTTPServer.HTTPServer(
        server_address=(HOST_NAME, PORT_NUMBER),
        RequestHandlerClass=HTTPRequestHandler
    )

    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)


if __name__ == '__main__':
    main()
