#  coding: utf-8 
from fileinput import filename
import socketserver
from os import path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Nasif Hossain
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.user_input = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.user_input)

        # parse the user input and store as variables after parsing
        self.data = self.parse_data()
        file_name = self.data['filename']
        http_protocol = self.data['http-ver']
        http_method = self.data['http-request']

        # starting with 404 as default response code
        self.http_response = self.getStatusResponse(404)

        # if the data checks the input specs return as requested
        corrected_path = self.check_path()
        if corrected_path:        
            print("The path given is", corrected_path)

            if not corrected_path[-1] == "/":
                self.http_response = self.getStatusResponse(301).format(file_name + '/')
                print("Getting a 301")
            elif path.isfile(file_name):
                print("Not Getting a 301")
                file = open(corrected_path + "/index.html" , 'r')
                file_content = file.read()
                print("File content" , file_content)
                file.close()
                self.http_response = self.getStatusResponse(200).format("text/html" , file_content)

        else:
            self.http_response = self.getStatusResponse(404)  
        self.request.sendall(self.http_response.encode('utf-8'))


    def parse_data(self):
        # dividing up the input
        inp = self.user_input.decode('utf-8').split('\r\n')[0].split(" ")
        data = {
            'http-request': inp[0],
            'path': path.abspath("www") + inp[1],
            'filename': inp[1],
            'http-ver': inp[2]
        }
        return data


    def check_path(self):
        """
            function for checking if the data constitutes of the correct 
             file path and returns True or False depending on the check
        """
        file_path = self.data['path']
        if path.exists(file_path):
            return file_path
        else:
            return False

    def getStatusResponse(self, statusCode):
        self.responses = {
            200: 'HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n{}\r\n',
            301: 'HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\n\r\n',
            404: 'HTTP/1.1 404 Not Found\r\n\r\n404 Error! File not found!\r\n',
            405: 'HTTP/1.1 405 Method Not Allowed\r\n\r\nThe specific request method is not allowed\r\n',
            505: 'HTTP/1.1 505 HTTP Version Not Support\r\n\r\nThe specific HTTP version is not supported\r\n'
        }

        return str(statusCode) + " " + self.responses[statusCode]

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    print("Connected to server")

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
