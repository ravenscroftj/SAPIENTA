import xmlrpclib
import os
import uuid
import mimetypes
import zlib
import pika
import logging
import docker

from base64 import b64decode

from flask import render_template,request, redirect, url_for, Response, make_response
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
            
            app.logger.info(app.config['SAPIENTA_MQ_HOST'])
            
            conn = pika.BlockingConnection(pika.ConnectionParameters(
                    host=app.config['SAPIENTA_MQ_HOST']))
            
            channel = conn.channel()
            
            result = channel.queue_declare()
            q = result.method.queue
            
            
            jobid = str(uuid.uuid4())
            
            headers = { 'docname' : os.path.basename(name) }

            props = pika.BasicProperties(headers=headers, 
                reply_to=q,
                correlation_id=jobid)

            
            if(ext == ".pdf"):
    
                app.logger.info("Converting %s", file.filename)
                inqueue = "sapienta.service.pdfx"
                
            elif( ext == ".xml"):
                app.logger.info("No conversion needed on %s" , file.filename)
                inqueue    = "sapienta.service.splitq"

            with open(os.path.join(destdir,fname),'rb') as f:
                body = f.read()
                
            channel.basic_publish(exchange=app.config['SAPIENTA_MQ_EXCHANGE'],
                routing_key=inqueue,
                properties=props,
                body = body)
            
            conn.close();


            return redirect(url_for('.view_status', jobid=jobid, q=q))
        else:
            return render_template("error.html", message="""You may upload only XML and PDF files. Other file types are not permitted.""")
    else:
        return render_template("error.html", message="""You must submit a file to be annotated. If you did and you are seeing thisd message, chances are the file was too big.""")


@app.route("/job/<string:jobid>/get")
def get_paper(jobid):

    outfile = os.path.join(app.config['OUTPUT_DIRECTORY'],
        "done", jobid+"_done.xml")
    
    with open(outfile, "rb") as f:

        r  = Response()
        r.headers['Content-Disposition'] = "attachment; filename=" + jobid+".xml"
        r.mimetype=mimetypes.guess_type(outfile)[0]
        r.set_data(f.read())
        return r

@app.route("/job/<string:jobid>/view")
def view_paper_stylesheet(jobid):
    import libxml2
    import libxslt


    outfile = os.path.join(app.config['OUTPUT_DIRECTORY'],
        "done", jobid+"_done.xml")
    
    stylefile = os.path.join(app.config['OUTPUT_DIRECTORY'],
        "done", jobid+"_pretty.html")

    styledoc = libxml2.parseFile("mode2.xsl")
    style = libxslt.parseStylesheetDoc(styledoc)
    doc = libxml2.parseFile(outfile)
    result = style.applyStylesheet(doc, None)
    style.saveResultToFilename(stylefile, result, 0)
    style.freeStylesheet()
    doc.freeDoc()
    result.freeDoc()
    
    with open(stylefile,'rb') as f:
        r = Response()
        r.set_data(f.read())
        return r
    


@app.route("/job/<string:jobid>/<string:q>")
def view_status(jobid,q):
    """Show the current status of a submitted job"""

    outfile = os.path.join(app.config['OUTPUT_DIRECTORY'],
                "done", jobid+"_done.xml")

    if(os.path.exists(outfile)):
        return render_template("job.html", job={
            "jobid" : jobid, 
            "status" : "DONE",
        })


    conn = pika.BlockingConnection(pika.ConnectionParameters(
        host=app.config['SAPIENTA_MQ_HOST']))
            
    channel = conn.channel()
    
    try:
        r = channel.basic_get(q)
    except pika.exceptions.ChannelClosed as exc:
        
        if exc.args[0] == 404:
            return render_template("error.html", 
                message="No such job with id %s" % jobid) 
        
        
    if(r == (None,None,None)):
        job = {"jobid" : jobid, "status" : "PENDING"}
        return render_template("job.html", job=job)
    else:
        method,properties,body = r
        
        if "error" in properties.headers:
            return render_template("error.html", message=body)
        else:
            job = {"jobid" : jobid, 
                   "status" : "DONE",
                   }
            
            
            
            with open(outfile, "wb") as f:
                f.write(body)
                
            channel.queue_delete(queue=q)
            
            
            return render_template("job.html", job=job)


    
@app.route("/status")
def service_status():
    """Get status of the work server"""
    
    #COORD_URI = "http://%s:%d/" % (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])

    #coordinator = xmlrpclib.ServerProxy(COORD_URI)

    #stats = coordinator.get_stats()


    return render_template("stats.html",**stats)

@app.route("/api")
def service_about():
    """API documentation page"""
    return render_template("api.html")

@app.route("/contact")
def service_contact():
    """Contact page"""
    return render_template("contact.html")
