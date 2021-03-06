# -*- coding: utf-8 -*-

import sys
import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    field_name = 'a'
    form_html = \
        '''
        <html>
        <body>
        <form method='post' enctype='multipart/form-data'>
        <input type='text' name='%s'>
        <input type='submit'>
        </form>
        </body>
        </html>
        ''' % field_name

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        try:
            file = open("."+self.path, "rb")
        except FileNotFoundError as e:
            print(e)
            self.wfile.write(self.form_html.encode())
        else:
            content = file.read()
            self.wfile.write(content)

    def do_POST(self):
        grades='OK'
        flag=0
        form_data = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': self.headers['Content-Type'],
            })
        fields = form_data.keys()
        print(fields)
        if self.field_name in fields:
            input_data = form_data[self.field_name].value
            file = open("."+self.path, "wb")
            file.write(input_data.encode())
            flag=0
        
        elif 'grades' in fields:   #录入成绩
            course_id, student_id, grades = form_data['course_id'].value,\
                                            form_data['student_id'].value, \
                                            form_data['grades'].value
            conn = sqlite3.connect('edu.db')
            c = conn.cursor()
            sql = "insert into stuinfo values (%s, %s, %s)"%(course_id, student_id, grades)
            c.execute(sql)
            conn.commit()
            conn.close()
            flag=1

        else:                       #查询成绩
            course_id, student_id = form_data['course_id'].value, form_data['student_id'].value
            conn = sqlite3.connect('edu.db')
            c = conn.cursor()
            sql = "select grades from stuinfo where course_id=%s and student_id=%s"%(course_id, student_id)
            c.execute(sql)
            grades = "%s 同学 %s 课程的成绩为:  " % (student_id, course_id) + str(c.fetchone()[0])
            conn.close()
            flag=2
    

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if flag==0:
            self.wfile.write(b"<html><body>OK</body></html>")
        elif flag==1:
            self.wfile.write(b"<html><head><meta charset='utf-8'></head><body>Insert ok!</body></html>")
        else: 
            self.wfile.write(bytes(str("<html><head><meta charset='utf-8'></head><body>%s</body></html>"%(grades)),'utf-8'))

class MyHTTPServer(HTTPServer):
    def __init__(self, host, port):
        print("run app server by python!")
        HTTPServer.__init__(self,  (host, port), MyHTTPRequestHandler)


if '__main__' == __name__:
    server_ip = "0.0.0.0"
    server_port = 8080
    if len(sys.argv) == 2:
        server_port = int(sys.argv[1])
    if len(sys.argv) == 3:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
    print("App server is running on http://%s:%s " % (server_ip, server_port))

    server = MyHTTPServer(server_ip, server_port)
    server.serve_forever()