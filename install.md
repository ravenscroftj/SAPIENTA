# Introduction

This document is essentially an installation guide for getting SAPIENTA installed on a UNIX-style system. To complete this guide, you will need:

* A UNIX/POSIX compatible operating system 
* Python 2.7 (Python 3+ is currently incompatible with SAPIENTA)
* The GCC buildchain - specifically you'll need gcc, g++, make and
  automake/autoconfigure
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

You'll need to go [here](http://svn.ask.it.usyd.edu.au/trac/candc) to register
and account in order to download [the
tools](http://svn.ask.it.usyd.edu.au/download/candc/candc-1.00.tbz2).
Registration is free and as soon as you log in you can access the files. It is
possible to download pre-compiled binaries for C and C, I recommend compiling
the system yourself rather than using these (unless you are trying to install
on Windows, in which case, using the prebuilt binaries is much easier).

You will also need to download:

 * [models](http://svn.ask.it.usyd.edu.au/download/candc/models-1.02.tbz2) (models trained on CCGbank 02-21 and MUC 7)
 * [pos_bio](http://www.cl.cam.ac.uk/research/nl/nl-download/candc/pos_bio-1.00.tbz2) (Models for biomedical parsing (for description see Biomedical
   Parsing) 
 * super_coresc (this is not provided by CandC tools, you can find it
   [here](http://doku.jamesravenscroft.net/~james/sapienta_files/super_coresc.tar.lzma)
 * CandC Markedup File (again this is privately hosted
   [here](http://doku.jamesravenscroft.net/~james/sapienta_files/markedup_new)

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

### Compiling the tools
