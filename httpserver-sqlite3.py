from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import cgi

import sqlite3

'''
  DATE: Tue Jun  4 12:56:16 2024 
  Use the script to post JSON data
  
  DATE: Thu 20 Jun 13:59:58 2024 
  Update: todoApp table schema 

  /Users/aaa/myfile/bitbucket/python/postJson.py

  Sqlite3 database: '/Users/aaa/myfile/bitbucket/database/test_sqlite3.db'

   CREATE TABLE todoApp(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        uuid TEXT NOT NULL,
        key TEXT NOT NULL,
        item TEXT NOT NULL
    );

  Support three commands: add, list, deleteall
  {
    'cmd' : 'add',
    'uuid' : 'b',
    'key' : 'key1',
    'item' : 'Buy milk today'
  }
  {
    'cmd' : 'list',
    'uuid' : 'a',
    'key' : '',
    'item' : ''
  }
  {
    'cmd' : 'deleteall',
    'uuid' : 'c',
    'key' : '',
    'item' : ''
  }
  --------------------------------------------------------------------------------

  DATE: Mon Jun  3 19:51:44 2024 
  # How to run it 
  python3 httpserver-sqlite3.py 8000

  # GET
  curl http://localhost:8000

  # POST
  curl -X POST http://localhost:8000 -H 'Content-Type: application/json' -d '{"key1" : "From client"}' 

  Get json from client 
  {'key1' : 'Get JSON'}

  Reply json to client 
  {'key1' : 'Reply from Server'}

'''

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        response = json.dumps({'hello': 'world', 'received': 'OK'})
        byteResp = bytes(response, 'utf-8')
        self.wfile.write(byteResp)
        
    def return_post(self, cur, con, cmd):
        cur.execute('select uuid, key, item, important, time from todoApp')
        con.commit();
        listdict = []
        items = cur.fetchall()
        for item in items:
          print(item)
          d = {'uuid' : item[0],  'cmd' : cmd, 'key' : item[1], 'item' : item[2], 'important' : item[3], 'time' : item[4]}
          listdict.append(d)
        self._set_headers()
        self.wfile.write(bytes(json.dumps(listdict), 'utf-8'))

    # POST echoes the message adding a JSON field
    def do_POST(self):
        if self.path == '/todo':
          ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
          
          # refuse to receive non-json content
          if ctype != 'application/json':
              self.send_response(400)
              self.end_headers()
              return
              
          # read the message and convert it into a python dictionary
          length = int(self.headers.get('content-length'))
          payload_str = self.rfile.read(length).decode('utf-8') 
          jsonItem = json.loads(payload_str) 

          print('jsonItem=>', jsonItem)

          # mydb = '/Users/aaa/myfile/bitbucket/database/test_sqlite3.db'
          mydb = '/Users/aaa/myfile/bitbucket/database/mytest.db'
          con = sqlite3.connect(mydb)
          cur = con.cursor()

          exeStr = f'SELECT * FROM todoApp'
          cur.execute(exeStr)
          # cur.execute('select * from todoApp')
          users = cur.fetchall()

          ''' 
          for row in users:
            print(row)
          '''

          print(jsonItem)

          todoCmd = jsonItem['cmd']

          print("todoCmd cmd: len =>", len(todoCmd))
          print("todoCmd cmd: strip=>", todoCmd.strip())
          if todoCmd.strip() == 'add':
            cur.execute('''
              INSERT INTO todoApp (uuid, key, item, important, time) VALUES(?,?,?,?,?)
              ''', (jsonItem['uuid'], jsonItem['key'], jsonItem['item'], jsonItem['important'], jsonItem['time']))
            con.commit();
            self._set_headers()
            replyJson = {'reply' : 'OK', 'cmd' : 'add'}
            self.wfile.write(bytes(json.dumps(replyJson), 'utf-8'))
          elif todoCmd == 'deleteall':
            print("deleteall todo items")
            cur.execute('''
              DELETE FROM todoApp WHERE id > 0 
              ''')
            con.commit();
            
            self.return_post(cur, con, 'list')
            # replyJson = {'reply' : 'OK', 'cmd' : 'deleteall'}
            #  self._set_headers()
            # self.wfile.write(bytes(json.dumps(replyJson), 'utf-8'))
          elif todoCmd == 'deleteByUUID':
            print("deleteByUUID todoApp items")
            cur.execute('''
                        DELETE FROM todoApp WHERE uuid = ? ''', (jsonItem['uuid'], ))
            con.commit();
            self._set_headers()
            replyJson = {'reply' : 'OK', 'cmd' : 'deleteByUUID'}
            self.wfile.write(bytes(json.dumps(replyJson), 'utf-8'))
          elif todoCmd == 'list':
            self.return_post(cur, con, 'list')
            
          print("uuid:", jsonItem['uuid'])
          print("key:", jsonItem['key'])
          print("item:", jsonItem['item'])

          # send the message back
          # self._set_headers()
          # self.wfile.write(bytes(json.dumps(jsonItem), 'utf-8'))
        else: 
          print("Unsupported: route => ", self.path)
        
def run(server_class=HTTPServer, handler_class=Server, port=8000):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    
    print('Starting httpd on port %d...' % port)
    httpd.serve_forever()
    
if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
        
