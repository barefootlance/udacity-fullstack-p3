from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import re
from restaurants import *

class webServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                                 <h2>What would you like me to say?</h2>
                                 <input name="message" type="text" >
                                 <input type="submit" value="Submit">
                             </form>'''

                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += '''<form method='POST' enctype='multipart/form-data' action='/hola'>
                                 <h2>What would you like me to say?</h2>
                                 <input name="message" type="text" >
                                 <input type="submit" value="Submit">
                             </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = getRestaurantsHtml()
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = getRestaurantsNewHtml()
                self.wfile.write(output)
                return

            p = re.compile(r"/restaurants/(\d+)+/edit")
            m = p.match(self.path)
            if m:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = getRestaurantsEditHtml(int(m.group(1)))
                self.wfile.write(output)
                return

            p = re.compile(r"/restaurants/(\d+)+/delete")
            m = p.match(self.path)
            if m:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = getRestaurantsDeleteHtml(int(m.group(1)))
                self.wfile.write(output)
                return


        except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    name = fields.get('name')[0]
                    addRestaurant(name)
                return

            p = re.compile(r"/restaurants/(\d+)+/edit")
            m = p.match(self.path)
            if m:
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                editId = int(m.group(1))
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    newName = fields.get('name')[0]
                    for id, oldName in getRestaurants():
                        if id == editId:
                            changeRestaurant(oldName, newName)
                            break
                return

            p = re.compile(r"/restaurants/(\d+)+/delete")
            m = p.match(self.path)
            if m:
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                editId = int(m.group(1))
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    for id, name in getRestaurants():
                        if id == editId:
                            deleteRestaurant(name)
                            break
                return

            self.send_response(301)
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
            	fields=cgi.parse_multipart(self.rfile, pdict)
            	messagecontent = fields.get('message')

            output += " <h2> Okay, how about this: </h2>"
            output += "<h1> %s </h1>" % messagecontent[0]
            output += '''<form method='POST' enctype='multipart/form-data' action='http://127.0.0.1/'>
                             <h2>What would you like me to say?</h2>
                             <input name="message" type="text" >
                             <input type="submit" value="Submit">
                         </form>'''
            output += "</html></body>"

            self.wfile.write(output)
            print output

        except:
			pass

def getRestaurantsHtml():
    output = ""
    output += "<html><body>"
    output += "<h1>Restaurants</h1>"
    output += "<a href=/restaurants/new>Add new restaurant</a><br>"
    for id, name in getRestaurants():
        output += "<br>{Name} <a href='restaurants/{Id}/edit'>Edit</a> <a href='restaurants/{Id}/delete'>Delete</a><br>".format(Name=name, Id=id)
    output += "</body></html>"
    return output

def getRestaurantsNewHtml():
    output = ""
    output += "<html><body>"
    output += "<h1>Restaurants</h1>"
    output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
                     <h2>Add</h2>
                     <input name="name" type="text" >
                     <input type="submit" value="Submit">
                 </form>'''
    output += "</body></html>"
    return output

def getRestaurantsEditHtml(editId):
    for id, name in getRestaurants():
        if id == editId:
            output = ""
            output += "<html><body>"
            output += "<h1>Edit</h1>"
            output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/{Id}/edit'>
                             <h2>Edit</h2>
                             <input name="name" type="text" value="{Name}" >
                             <input type="submit" value="Submit">
                         </form>'''.format(Id=id, Name=name)
            output += "</body></html>"
            return output

def getRestaurantsDeleteHtml(deleteId):
    for id, name in getRestaurants():
        if id == deleteId:
            output = ""
            output += "<html><body>"
            output += "<h1>Delete</h1>"
            output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/{Id}/delete'>
                             <h2>Are you sure you want to delete {Name}?</h2>
                             <input type="submit" value="Delete">
                         </form>'''.format(Id=id, Name=name)
            output += "</body></html>"
            return output

def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webServerHandler)
		print "Web Server running on port %s"  % port
		server.serve_forever()
	except KeyboardInterrupt:
		print " ^C entered, stopping web server...."
		server.socket.close()

if __name__ == '__main__':
	main()
