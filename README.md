#SAPIENTA for Python

This package contains all of the utilities and tools necessary to run a
SAPIENTA annotation server in Python. It currently relies upon the Perl version
of SAPIENTA but it is intended that a Python version of the annotation system
will be implemented imminently.

## Requirements

This package runs in Python 2.7 and requires the following Python libraries:

    *  Flask (version 0.9 or newer)
    *  pycurl (version 7.19 or newer)
    *  text-sentence (version 0.14 or newer)

These packages and their dependencies can be automatically installed as part of
the installation process illustrated below.


## Installation

Installation of SAPIENTA is simple although if you want to use it with the Perl
annotator it does require some extra configuration. There are two possible installation routes:


### Installation inside virtualenv (recommended)

It is recommended that you build SAPIENTA inside a
[virtualenv](http://www.virtualenv.org/en/latest/) environment. This avoids
conflicting dependencies between Python applications and allows you to install
the necessary dependency packages without superuser access on the machine in
question.

It is recommended that a virtualenv is set up in the top level of the project directory.
An example installation procedure with virtualenv is as follows:
    
    ~ $ git clone git@github.com:ravenscroftj/SAPIENTA.git
    ~ $ cd SAPIENTA
    ~/SAPIENTA $ virtualenv env
    ~/SAPIENTA $ source env/bin/activate
    (env) ~/SAPIENTA $ python setup.py install
    
Remember that you will need to run the `source env/bin/activate` command each
time you wish to interact with an instance of SAPIENTA installed inside a
virtualenv each time you open a new terminal.

### Installation with superuser access

If you wish to install SAPIENTA and its dependencies as system-wide site
packages, you can run the following command (as root):

    # git clone git@github.com:ravenscroftj/SAPIENTA.git
    # python setup.py install

This should set up SAPIENTA in your default python installation path.

## Configuration

SAPIENTA can be used as a web server, annotation worker or just as a
commandline tool for annotating papers. Regardless of how you intend to use it,
you need to set a few values in the configuration file. 

By default, SAPIENTA will look for a file named `sapienta.cfg` in the current working directory, then the user config directory (`~/.config/sapienta.cfg`) and finally a system-wide configuration file (`/etc/sapienta.cfg`). It will stop looking and use the first file it finds conforming to this pattern.

You should use the sample config file for reference when setting up your SAPIENTA installation:

    ~/SAPIENTA $ cp sapienta.cfg.sample ~/.config/
    $ [vim or gedit or kate] ~/.config/sapienta.cfg

## Usage


### pdfxconv - commandline paper annotation
The most common usage for SAPIENTA is expected to be for commandline processing
of papers. Once you've installed SAPIENTA, you should have access to the
commandline application `pdfxconv`. This is a 'swiss-army-knife' program which
provides pdf conversion, sentence splitting and annotation of papers. It also
supports batch processing. Depending on your configuration, `pdfxconv` can be
used as a thin client that offloads work to a remote SAPIENTA instance or make
use of local processing.

Typical usage of pdfxconv to convert a PDF to an annotated PubMed DTD paper
might look like the following:

    $ pdfconv -a myarticle.pdf

You can also batch process a set of files:

    $ pdfxconv -a *.pdf *.xml

### Web server and computation node

SAPIENTA also offers a web frontend/REST API for paper annotation with a
distributed backend to allow parallel annotation processes. This is considered an abnormal case and is not discussed in this document. You can read about how to use SAPIENTA as a server [here](https://github.com/ravenscroftj/SAPIENTA/wiki/ServerConfiguration)

