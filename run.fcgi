#!venv/bin/python

from flup.server.fcgi import WSGIServer
import app
#from app import app

if __name__ == '__main__':
    WSGIServer(app.create_app('default')).run()
