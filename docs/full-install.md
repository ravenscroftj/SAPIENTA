
## Requirements

This package runs in Python 2.7 and requires the following Python libraries:

    *  Flask (version 0.9 or newer)
    *  pycurl (version 7.19 or newer)
    *  text-sentence (version 0.14 or newer)

These packages and their dependencies can be automatically installed as part of
the installation process illustrated below.


## Installation

Please Read the [INSTALL](install.md) file for notes on how to compile and install SAPIENTA for your system.


## Configuration

SAPIENTA can be used as a web server, annotation worker or just as a
commandline tool for annotating papers. Regardless of how you intend to use it,
you need to set a few values in the configuration file. 

By default, SAPIENTA will look for a file named `sapienta.cfg` in the current working directory, then the user config directory (`~/.config/sapienta.cfg`) and finally a system-wide configuration file (`/etc/sapienta.cfg`). It will stop looking and use the first file it finds conforming to this pattern.

You should use the sample config file for reference when setting up your SAPIENTA installation:

    ~/SAPIENTA $ cp sapienta.cfg.sample ~/.config/
    $ [vim or gedit or kate] ~/.config/sapienta.cfg
    
For a more in depth look at configuring SAPIENTA. Read the [configuration](https://github.com/ravenscroftj/SAPIENTA/wiki/Configuration) guide or the [server configuration](https://github.com/ravenscroftj/SAPIENTA/wiki/ServerConfiguration) guide.

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

    $ pdfxconv -a myarticle.pdf

You can also batch process a set of files:

    $ pdfxconv -a *.pdf *.xml

### Web server and computation node

You can read about how to use SAPIENTA as a web service [here](https://github.com/ravenscroftj/SAPIENTA/wiki/ServerConfiguration)

