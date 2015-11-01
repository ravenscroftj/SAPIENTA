import xmlrpclib
import os
import uuid
import mimetypes
import zlib
import pika
import logging

from base64 import b64decode

from flask import render_template,request, redirect, url_for, Response
from sapienta import app,socketio,mqclient
from flask.ext.socketio import emit, join_room, leave_room
from sapienta.service.mq import BaseMQService

ALLOWED_EXTENSIONS = ['.xml','.pdf']


logger = logging.getLogger(__name__)


@socketio.on('work')
def submit_job(message):
    #print "Got message: " + message['filename']

    inqueue = "sapienta.service.pdfx"
    exit_after = inqueue
    filename = message['filename']

    name,ext = os.path.splitext(filename)

    split    = "split" in message and message['split']
    annotate = "annotate" in message and message['annotate'] 
            
    if(ext == ".pdf"):

        logging.info("Converting %s", filename)
        
    elif( ext == ".xml"):
        logging.info("No conversion needed on %s" , filename)
        inqueue    = "sapienta.service.splitq"
    else:
        logging.info("Unrecognised format for file %s", filename)
        sys.exit(0)

    if(split):
        logging.info("Splitting sentences in %s", filename)
        exit_after = "sapienta.service.splitq"
        
    if(annotate):
        #build annotated filename
        logging.info("Annotating file %s", filename)
        exit_after = "sapienta.service.annotateq"

    body = b64decode(message['body'])

    jobid = mqclient.submit_job(inqueue, os.path.basename(filename), body, exit_after)

    join_room(jobid)

    emit("jobid", {"filename" : filename, "jobid" : jobid })


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/upload", methods=['GET'])
def upload_form():
    return render_template("upload_form.html")

@app.route("/upload", methods=['POST'])
def upload_act():

    if 'the_file' in request.files:
        file = request.files['the_file']

        destdir = app.config['OUTPUT_DIRECTORY']

        name,ext = os.path.splitext(file.filename)

        if ext in ALLOWED_EXTENSIONS:
            fname = str(uuid.uuid4()) + ext

            file.save(os.path.join(destdir, fname))

            COORD_URI = "http://%s:%d/" % (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])

            coordinator = xmlrpclib.ServerProxy(COORD_URI)

            with open(os.path.join(destdir,fname),'rb') as f:
                data = zlib.compress(f.read())
                

            jobid = coordinator.queue_job(fname, xmlrpclib.Binary(data))

            return redirect(url_for('.view_status', jobid=jobid))
        else:
            return render_template("error.html", message="""You may upload only XML and PDF files. Other file types are not permitted.""")
    else:
        return render_template("error.html", message="""You must submit a file to be annotated. If you did and you are seeing thisd message, chances are the file was too big.""")


@app.route("/job/<int:jobid>/get")
def get_paper(jobid):

    COORD_URI = "http://%s:%d/" % (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])

    coordinator = xmlrpclib.ServerProxy(COORD_URI)

    job = coordinator.get_status(jobid)
    blob = coordinator.get_result(jobid)


    r  = Response()
    r.mimetype=mimetypes.guess_type(job['filename'])[0]
    return zlib.decompress(blob.data)


@app.route("/job/<int:jobid>")
def view_status(jobid):
    """Show the current status of a submitted job"""

    COORD_URI = "http://%s:%d/" % (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])

    coordinator = xmlrpclib.ServerProxy(COORD_URI)

    job = coordinator.get_status(jobid)

    if job == None:
        return render_template("error.html", message="""Invalid jobid. Please enter a valid ID and try again""")
    else:
        return render_template("job.html", job=job)


    
@app.route("/status")
def service_status():
    """Get status of the work server"""
    
    COORD_URI = "http://%s:%d/" % (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])

    coordinator = xmlrpclib.ServerProxy(COORD_URI)

    stats = coordinator.get_stats()

    return render_template("stats.html",**stats)

