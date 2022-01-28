#  coding: utf-8 
from fileinput import filename
import socketserver
from os import path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2022 Nasif Hossain
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
        """
            Function which handles http requests from clients
            and returns the required requested information
        """
        self.user_input = self.request.recv(1024).strip()

        # in case of no http requests received
        if not self.user_input:
            return

        # some previous code
        # print ("Got a request of: %s\n" % self.user_input)   

        # parse the user input and store as variables after parsing
        user_inp = self.user_input.decode('utf-8').split('\r\n')[0].split(" ")
        if len(user_inp) == 0:
            return

        # parts of client input
        self.http_method = user_inp[0]
        self.file_name = user_inp[1]
        self.file_path = path.abspath("www") + user_inp[1]
        self.http_protocol = user_inp[2]

        # Dictionary containing all required status codes and their responses
        self.http_responses = {
            200: 'HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n{}\r\n',
            201: "Created\r\n\r\nConnection Closed\r\n",
            202: "Accepted\r\n\r\nConnection Closed\r\n",
            301: 'HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\n\r\nConnection Closed\r\n\r\n',
            302: "Found\r\n\r\nConnection Closed\r\n",
            404: 'HTTP/1.1 404 Not Found\r\n\r\nConnection Closed\r\n',
            405: 'HTTP/1.1 405 Method Not Allowed\r\n\r\nConnection Closed\r\n',
            505: 'HTTP/1.1 505 HTTP Version Not Support\r\n\r\nConnection Closed\r\n'
        }

        # variable for storing http responses
        self.http_response = None

        # variable storing the supporting file types
        self.file_type = self.getFileType()

        # preliminary tests for required http protocols and method
        if self.http_protocol != "HTTP/1.1":
            self.http_response = self.http_responses[505]

        # 405 method not allowed
        if self.http_method != "GET":
            self.http_response = self.http_responses[405]

        # if the data checks the input specs return http response as requested
        corrected_path = self.check_path()
        if corrected_path and self.http_response == None:                    
            if path.isfile(corrected_path):
                if "www" in path.abspath(corrected_path):
                    file = open(corrected_path, 'r')
                    file_content = file.read()
                    file.close()
                    self.http_response = self.http_responses[200].format(self.file_type , file_content)

            else:
                # 301 to correct paths
                if corrected_path[-1] != "/":
                    print("301 error")
                    self.http_response = self.http_responses[301].format(self.file_name + '/')
                    
                elif path.isfile(corrected_path + "index.html"):
                    file = open(corrected_path + "index.html" , 'r')
                    file_content = file.read()
                    file.close()
                    self.http_response = self.http_responses[200].format("text/html" , file_content)

        if self.http_response == None:
            self.http_response = self.http_responses[404] 

        self.request.sendall(self.http_response.encode('utf-8'))


    def check_path(self):
        """
            function for checking if the data constitutes of the correct 
            file path and returns True or False depending on the check
        """
        if path.exists(self.file_path):
            return self.file_path
        else:
            return False

    def getFileType(self):
        """
            function for getting the different filetypes
            supported and unsupported
        """
        filename = self.file_path.split()[-1]
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
