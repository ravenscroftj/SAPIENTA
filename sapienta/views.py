import xmlrpclib

from flask import render_template

from sapienta import app

@app.route('/')
def index():
    return render_template("index.html")


def submit():
    """This view allows users to submit papers for annotation by our servers."""

    
app.route("/status")
def service_status():
    """Get status of the work server"""
    
    addr = (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])
    uri = "http://%s:%d/" % addr

    self.logger.info("Trying to talk to XMLRPC server at %s", uri)

    coordinator = xmlrpclib.ServerProxy(uri)
