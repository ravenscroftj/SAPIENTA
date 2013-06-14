import xmlrpclib
import os
import uuid
import mimetypes

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

            COORD_URI = "http://%s:%d/" % (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])

            coordinator = xmlrpclib.ServerProxy(COORD_URI)

            jobid = coordinator.queue_job(os.path.join(destdir,fname))

            return redirect(url_for('.view_status', jobid=jobid))
        else:
            return render_template("error.html", message="""You may upload only XML and PDF files. Other file types are not permitted.""")
    else:
        return render_template("error.html", message="""You must submit a file to be annotated. If you did and you are seeing thisd message, chances are the file was too big.""")


@app.route("/job/<int:jobid>/get")
def get_paper(jobid):

    COORD_URI = "http://%s:%d/" % (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])

    coordinator = xmlrpclib.ServerProxy(COORD_URI)

    job = coordinator.get_result(jobid)

    r  = Response()
    r.mimetype=mimetypes.guess_type(job['filename'])[0]
    with open(job['filename'],'rb') as f:
        r.data = f.read()
    return r


@app.route("/job/<int:jobid>")
def view_status(jobid):
    """Show the current status of a submitted job"""

    COORD_URI = "http://%s:%d/" % (app.config['COORD_ADDRESS'], app.config['COORD_PORT'])

    coordinator = xmlrpclib.ServerProxy(COORD_URI)

    job = coordinator.get_result(jobid)

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

