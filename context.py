from __future__ import print_function
import os
import time
import sys
import cgi

if sys.version_info.major == 2:
    import BaseHTTPServer as server_module
else:
    import http.server as server_module


EXTRA_LINE = """
<meta charset="utf-8" lang="en">
<style class="fallback">body{white-space:pre;font-family:monospace}</style>
<!-- <script src="markdeep.min.js"></script> -->
<script src="http://casual-effects.com/markdeep/latest/markdeep.min.js"></script>
"""

FILE_PATH = os.path.expanduser('~/context')

from pprint import pprint

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
            #with open('default.html') as f:
            #    content = f.read()
            raise e 
            content = str(e)

        self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        pdict['boundary'] = pdict['boundary'].encode('utf-8')
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        type_ = lob2str(postvars['type'])

        if type_ == 'save':
            save_file(
                filename=lob2str(postvars['filename']),
                content=lob2str(postvars['text']),)
        else:
            print('unkown type!!')

def save_file(filename, content):

    if filename.endswith('?edit'):
        filename = filename[:-len('?edit')]
    else:
        raise Exception('Not a valid filename!')

    path = os.path.join(FILE_PATH, filename)
    with open(path, 'w') as f:
        f.write(content)
    print('Content written to:', path)

def lob2str(lob, sep=''):
    """Converts list of bytes to single string."""
    return sep.join(b.decode('utf-8') for b in lob)

def load_content(path):

    sep = '?'

    if sep in path:
        head, tail = path.split(sep, 1)
        edit = (tail == 'edit')
    else:
        edit = False

    if path[1:] == "resume":
        content = get_raw(path)  

    elif edit:
       content = get_edit(path=head)
       print('get edit')
    else:
        content = get_markdeep(path)
        print('get markdeep')

    return content


def get_markdeep(path):

    if path == '/':
        title = '**Table of Content**\n'
        file_list = os.listdir(FILE_PATH)
        file_list = ['* ['+name+']('+name+')' for name in file_list if not name.startswith('.')]
        content = '\n\n'.join(file_list)
        
        content = ''
        
    else:
        path = os.path.join(FILE_PATH, path[1:])
        with open(path) as f: content = f.read()

    return '\n'.join([content, EXTRA_LINE])


def get_edit(path):
    path = os.path.join(FILE_PATH, path[1:])
    with open(path) as f:
        content = f.read()

    default_path = os.path.join(os.path.dirname(__file__), 'default.html')
    with open(default_path) as f:
        head, tail = f.read().split('<!--splitline-->')

    return head + content + tail

def get_raw(path):
    path = os.path.join(FILE_PATH, path[1:])
    with open(path, 'r') as f:
        content = f.read()
    
    return content #.decode('unicode_escape').encode('utf-8')

def main():
    args = sys.argv[1:]
    global FILE_PATH
    FILE_PATH = args[0]
    if len(args) == 1:
        PORT_NUMBER = 8000
    else:
        PORT_NUMBER = int(args[1])

    HOST_NAME = ''
    
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
    
    httpd = server_module.HTTPServer(
        server_address=(HOST_NAME, PORT_NUMBER),
        RequestHandlerClass=HTTPRequestHandler
    )

    print(time.asctime(), "Server Starts - %s:%s in %s" % (HOST_NAME, PORT_NUMBER, FILE_PATH))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))


if __name__ == '__main__':
    main()
