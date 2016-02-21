# Introduction

This document is essentially an installation guide for getting SAPIENTA installed on a UNIX-style system. To complete this guide, you will need:

* A UNIX/POSIX compatible operating system 
* Python 2.7 (Python 3+ is currently incompatible with SAPIENTA)
* The Python development files (usually separately installed in a package named
  python2.7-dev or similar)
* The GCC buildchain - specifically you'll need gcc, g++, make and
  automake/autoconfigure
* You will need libcurl and libcurl-dev since SAPIENTA relies upon pycurl which
  is build using these libraries.
* You'll need permission to install new libraries on the system (or you can use
  the `./configure --prefix=/path/to/fake/fsroot` syntax to install libraries
  into a custom path if you don't have root access).

# Installing Dependencies

## CandC Tools


### Acquiring the toolkit and models

CandC Tools is currently used by SAPIENTA for Part-of-Speech tagging and
lemmatizing. Specifically, the SOAP server is used, since it can be started in
the background and only loads the models into memory once (previously each
worker loaded a new instance of CandC, quickly exhausting system RAM).

Download the [C&C source bundle](https://www.dropbox.com/s/uoyu3jlr11wb9jd/candc-1.00.tbz2?dl=0). If you are running MacOSX or Windows you can download the binary files for C&C here ([Windows](https://www.dropbox.com/s/vxajm1870gf08za/candc-cygwin-1.00.tgz?dl=0) and ([Mac](https://www.dropbox.com/s/m7739wiaoxfl7lg/candc-macosxu-1.00.tgz?dl=0))
and therefore skip the compiling C&C tools step below. You will still need to download and extract the models.

You will also need to download:

 * [models_all from dropbox]() which contains all of the C&C annotation models. Extract the directory inside into the SAPIENTA folder.

The toolkit requires gSOAP2 in order to build the SOAP server which is used by
SAPIENTA. Your operating system should provide a package for this library, or
you can download and compile it yourself from
[here](http://sourceforge.net/project/showfiles.php?group_id=52781). Once
you've installed it, make sure `soapcpp2` is a valid command by running it. You
should get output similar to the following.

    **  The gSOAP code generator for C and C++, soapcpp2 release 2.8.15
    **  Copyright (C) 2000-2013, Robert van Engelen, Genivia Inc.
    **  All Rights Reserved. This product is provided "as is", without any warranty.
    **  The soapcpp2 tool is released under one of the following two licenses:
    **  GPL or the commercial license by Genivia Inc.

Hit CTRL + D to return back to the shell.

Some gsoap 2.7 and 2.8 versions give an IPV6 error when the CandC soap server is run. 
The last successful version of gsoap is 2.7.9f which can be obtained 
[here](http://sourceforge.net/projects/gsoap2/files/gSOAP/gSOAP%202.7.9f%20stable/). 
You may also need to export `CXXFLAGS='-fpermissive'` to get it to compile.

### Compiling C and C tools

**Note: You can skip this section if you are using the pre-compiled binaries**

Extract the source archive you downloaded from the CandC website and change
directory into the folder that is created (it should be called candc-1.00).

Next you'll need to apply the candc.patch file that I've written to correct a
couple of dependency problems in the original code. The patch called
opt/candc/candc.patch in the SAPIENTA repository. To apply it simply run (from
the candc-1.00 directory) :

    $ cp sapienta/opt/candc/candc.patch .
    $ patch -p1 -i candc.patch

There should be a number of Makefiles in this directory with operating system
names for file extensions. Rename the relevant one to Makefile for your
operating system environment. For example, on a Linux or UNIX system I'd run
`mv Makefile.unix Makefile` or if I was running a Mac system, I'd type `mv
Makefile.macosx Makefile`.

Now run `make` and `make soap`. You should now have a `bin` directory that contains
a bunch of binaries including `soap_server`. Run the `soap_server` file to
verify that compilation worked. You should an error message and usage
instructions for the server.

### Extracting C and C Models

The final step to configuring the server is to extract the models (downloaded from dropbox above) into the
same directory as `candc-1.00` as shown below:

    parent directory - SAPIENTA git repo probably
       --candc-1.00
       --models**


### Running C and C Server

Now, copy the file sapienta/opt/candc/run_server.sh to the candc-1.00/bin
directory, and execute it directly ./run_server.sh. If everything has been
properly configured, you should see `waiting for connections on
127.0.0.1:9004`. 


## CRFSuite

SAPIENTA currently uses CRFSuite for implementing Conditional Random Fields
Machine Learning models.

CRFSuite depends upon LibLBFGS. You'll need to download and install this first.
Get the source archive from
[here](https://github.com/downloads/chokkan/liblbfgs/liblbfgs-1.10.tar.gz).
Extract the archive and run:

    $ ./configure --prefix=/usr
    $ make
    $ sudo make install


Next, you'll need to download the CRFSuite source archive from
[here](https://github.com/chokkan/crfsuite/archive/master.zip) and extract it
to a convenient directory. 

The configure.in file provided doesn't work so copy the one from the SAPIENTA source directory over the top of it (opt/crfsuite/configure.in)

Next, enter the directory and run the following
commands:

    $ ./autogen.sh
    $ ./configure --prefix=/usr
    $ make
    $ sudo make install

Now we need to build the crfsuite Python extension. Drop into the swig/python
directory and run:

    $ cp ../crfsuite.cpp .
    $ python setup.py build

Hopefully this will build the extension and shouldn't produce any errors. We
can't install this python module yet, we'll come back to it later.

# Installing SAPIENTA virtualenv environment

It is recommended that you build SAPIENTA inside a
[virtualenv](http://www.virtualenv.org/en/latest/) environment. This avoids
conflicting dependencies between Python applications and allows you to install
the necessary dependency packages without superuser access on the machine in
question.

**Skip this bit if you are installing inside a Partridge virtualenv - just use the existing one rather than creating a new one**

It is recommended that a virtualenv is set up in the top level of the project directory.
An example installation procedure with virtualenv is as follows:
    
    ~ $ git clone git@bitbucket.org:partridge/sapienta.git
    ~ $ cd sapienta
    ~/sapienta $ virtualenv env
    ~/sapienta $ source env/bin/activate
    (env) ~/sapienta $ python setup.py develop
    
Remember that you will need to run the `source env/bin/activate` command each
time you wish to interact with an instance of SAPIENTA installed inside a
virtualenv each time you open a new terminal.

**Note: if the install fails due to dependencies (Specifically text-sentence as
is most often the case) you should try downloading the relevant library and
manually building and installing it ( python setup.py build && python setup.py
install from the source directory is the usuall convention). text-sentence can
be found [here](https://bitbucket.org/trebor74hr/text-sentence/).**

## Installing Python crfsuite wrapper into virtualenv

You now need to instruct Python to install crfsuite into the virtual
environment. From your virtualenv prompt (used above) run the following:

    (env) $ cd path/to/crfsuite/swig/python
    (env) $ python setup.py install

That's all there is to it, crfsuite should now be integrated into the virtual
environment.

# What next?

Now that you've installed everything, you will probably want to look [this
guide](https://bitbucket.org/partridge/sapienta/wiki/Configuration) on configuring SAPIENTA and if you want to try and retrain the model
you may want to [read
this](https://github.com/ravenscroftj/SAPIENTA/wiki/Training).
