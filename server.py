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

        # variable for storing http responses
        self.http_response = None

        # variable storing the supporting file types
        self.file_type = self.getFileType()

        # preliminary tests for required http protocol and method
        if http_protocol != "HTTP/1.1":
            self.http_response = self.getStatusResponse(505)

        if http_method != "GET":
            self.http_response = self.getStatusResponse(405)

        # if the data checks the input specs return as requested
        corrected_path = self.check_path()
        if corrected_path and self.http_response == None:        
            print("The path given is", corrected_path)
            
            if path.isfile(corrected_path):
                if "www" in path.abspath(corrected_path):
                    file = open(corrected_path, 'r')
                    file_content = file.read()
                    file.close()
                    self.http_response = self.getStatusResponse(200).format(self.file_type , file_content)

            else:
                if not corrected_path[-1] == "/":
                    self.http_response = self.getStatusResponse(301).format(file_name + '/')
                    
                elif path.isfile(corrected_path + "index.html"):
                    file = open(corrected_path + "index.html" , 'r')
                    file_content = file.read()
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
        """
            function for returning the http status response codes with
            their respective messages
        """
        self.responses = {
            200: 'HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n{}\r\n',
            301: 'HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\n\r\nConnection Closed\r\n\r\n',
            404: 'HTTP/1.1 404 Not Found\r\n\r\nConnection Closed\r\n',
            405: 'HTTP/1.1 405 Method Not Allowed\r\n\r\nConnection Closed\r\n',
            505: 'HTTP/1.1 505 HTTP Version Not Support\r\n\r\nThe specific HTTP version is not supported\r\n'
        }

        return str(statusCode) + " " + self.responses[statusCode]

    def getFileType(self):
        """
        function for getting the different filetypes
        supported and unsupported
        """
        filename = self.data['path'].split()[-1]
        splitted = filename.split(".")
        filename_extension = ''
        if len(splitted) != 1:
            filename_extension = splitted[-1]

        # file types
        content_type = "text/plain"             
        if filename_extension == "css":
            content_type = "text/css"
        elif filename_extension == "html":
            content_type = "text/html"
        else:
            content_type = "application/octet-stream"

        return content_type

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    print("Connected to server")

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
