from __future__ import print_function
import os
import time
import sys

if sys.version_info.major == 2:
    import BaseHTTPServer as server_module
else:
    import http.server as server_module


EXTRA_LINE = """
<style class="fallback">body{white-space:pre;font-family:monospace}</style>
<!-- <script src="markdeep.min.js"></script> -->
<script src="http://casual-effects.com/markdeep/latest/markdeep.min.js"></script>
"""

FILE_PATH = os.path.expanduser('~/context')
        

class HTTPRequestHandler(server_module.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    
    def do_GET(self):
        self.do_HEAD()        
        try:
            content = load_content(self.path)
        except Exception as e:
            with open('default.html') as f:
                content = f.read()
            raise e 
            print(e)
        self.wfile.write(content.encode('utf-8'))


def load_content(path):

    if '.' in path:
        head, tail = path.split(sep='.', maxsplit=1)
        edit = (tail == 'edit')
    else:
        edit = False

    if edit:
       content = get_edit(path=head)
    else:
        content = get_markdeep(path)

    return content


def get_markdeep(path):

    if path == '/':
        title = '**Table of Content**\n'
        file_list = os.listdir(FILE_PATH)
        file_list = ['* ['+name+']('+name+')' for name in file_list if not name.startswith('.')]
        content = '\n\n'.join(file_list)
    else:
        path = os.path.join(FILE_PATH, path[1:])
        with open(path) as f: content = f.read()

    return '\n'.join([content, EXTRA_LINE])


def get_edit(path):
    path = os.path.join(FILE_PATH, path[1:])
    with open(path) as f:
        content = f.read()

    with open('default.html') as f:
        head, tail = f.read().split('<!--splitline-->')

    return head + content + tail


def main():
    args = sys.argv[1:]
    if args:
        PORT_NUMBER = int(args[0])
    else:
        PORT_NUMBER = 8000

    HOST_NAME = ''
    
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
    
    httpd = server_module.HTTPServer(
        server_address=(HOST_NAME, PORT_NUMBER),
        RequestHandlerClass=HTTPRequestHandler
    )

    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))


if __name__ == '__main__':
    main()
