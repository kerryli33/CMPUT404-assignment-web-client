#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    

class HTTPClient(object):
    
    def get_host_port(self,url):
        info = urllib.parse.urlparse(url)
        port = info.port
        path = info.path
        host = info.hostname
        return (host,port,path)

    def connect(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
        except:
            self.close()

    def get_code(self, data):
        return data.split(" ")[1]

    def get_headers(self,data):
        endHeaders = False
        headers = ""
        for line in data.splitlines():
            if line == "":
                endHeaders = True
            if not endHeaders:
                headers += line+"\n"

        return headers

    def get_body(self, data):
        isBody = False
        body = ""
        for line in data.splitlines():
            if line == "":
                isBody = True

            if isBody:
                body += line+"\n"
         
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        try:
            while not done:
                part = sock.recv(1024)
                if (part):
                    buffer.extend(part)
                else:
                    done = not part
        except Exception as e:
            print(e)
            pass
        finally:
            self.close()

        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host,port,path = self.get_host_port(url)
        if port == None:
            port = 80
        if len(path) == 0:
            path= '/'
        #print("ARGS: "+ args)
        self.connect(host,port)
        ua = "Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0"
        payload = """GET {PATH} HTTP/1.1
User-Agent: {UA}
Host: {HOST}
Accept: */*
Connection: close



""".format(PATH=path,UA=ua,HOST=host)
        self.sendall(payload)
        data = self.recvall(self.socket)
        header = self.get_headers(data)
        code = self.get_code(header.splitlines()[0])
        body = self.get_body(data)
        resp = HTTPResponse(int(code), body)
        #print("CODE: "+code+ "FOR "+host)
        print(resp.body)
        return resp


    def POST(self, url, args=None):
        host,port,path = self.get_host_port(url)
        self.connect(host,port)
        content = "Hellooooo"
        if args!=None:
            content = urllib.parse.urlencode(args,True)
        length = len(content)
        payload = """POST {PATH} HTTP/1.1
Host: {HOST}
Content-Type: application/x-www-form-urlencoded
Content-Length: {LENGTH}
Connection: keep-alive

{CONTENT}
""".format(PATH=path,
            HOST=host,
            LENGTH=length,
            CONTENT=content)
        self.sendall(payload)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        resp = HTTPResponse(int(code), body)
        print(resp.body)
        return resp

    def command(self, url, command="GET", args=None):
        #print("URL: "+ str(url)+'\tcommand: ' + str(command)+"args: "+str(args))
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 2):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        args = []
        i=3
        for i in len(sys.argv):
            args.append(sys.arv[i])
        print(client.command( sys.argv[2], sys.argv[1], args ))
