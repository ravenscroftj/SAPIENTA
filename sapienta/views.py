import xmlrpclib
import os
import uuid
import mimetypes
import zlib
import pika

from flask import render_template,request, redirect, url_for, Response

from sapienta import app


ALLOWED_EXTENSIONS = ['.xml','.pdf']


@app.route('/')
def index():
    return render_template("index.html")


def submit():
    """This view allows users to submit papers for annotation by our servers."""

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
        r.mimetype=mimetypes.guess_type(outfile)[0]
        return f.read()


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
    
    COORD_URI = "http://%s:%d/" % (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])

    coordinator = xmlrpclib.ServerProxy(COORD_URI)

    stats = coordinator.get_stats()

    return render_template("stats.html",**stats)

