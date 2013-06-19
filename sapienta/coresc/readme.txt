#external python libraries
- SUDS - Suds is a lightweight SOAP python client for consuming Web Services.  https://fedorahosted.org/suds/
  Dwnload the tarball, extract and add folder to your PYTHONPATH enviroment variable.
  
- CRFsuite - A fast implementation of Conditional Random Fields (CRFs). http://www.chokkan.org/software/crfsuite/
  Download the source package, extract and follow the installation instructions ('INSTALL' file). Then change into swig/python folder and follow the instructions ('README' file) to build the python module.

  The last step created C and python libraries in /usr/local/lib, feel free to copy them somewhere else.
  set LD_LIBRARY_PATH to /usr/local/lib and add /usr/local/lib/python2.7/dist-packages to your PYTHONPATH.
  
#external services
- C&C tools - ... http://svn.ask.it.usyd.edu.au/trac/candc/wiki
  The site provides pre-compiled binaries, but the included SOAP server doesn't work.
  So off to compiling once again. Download the source code and follow the instructions: http://svn.ask.it.usyd.edu.au/trac/candc/wiki/Installation up to and including step 5.
  What we're really after are the (now working) binaries in the 'bin' folder, so feel free to copy them somewhere else. The only other thing we need is the WSDL file, found at src/api/soap/ccg/ccg_binding.wsdl
  
  Download the models from the download page and extract them.
  
  Python will interact with C&C via SOAP, so we need to start the server: bin/soap_server --models models --server localhost:9004
  /nfs/research2/textmining/grabmuel/aho/coresc/candc/candc-min/bin/soap_server --models /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models --candc-pos /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models/pos_bio-1.00 --candc-pos-maxwords 900 --candc-parser /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models/parser --candc-super /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models/super_coresc/ --candc-parser-markedup /nfs/research2/textmining/sapienta/software/softwares/candc-1.00/models/parser/cats/markedup_new --candc-super-maxwords 900 --candc-parser-maxwords 900 --server localhost:9004

export PYTHONPATH=/nfs/research2/textmining/grabmuel/aho/coresc/crfsuite/usr_local_lib/python2.7/dist-packages:/nfs/research2/textmining/grabmuel/aho/coresc/python-suds-0.4:/homes/grabmuel/avro/avro-1.6.3/src:/homes/grabmuel/eclipse/CoreSC
export LD_LIBRARY_PATH=/nfs/research2/textmining/grabmuel/aho/coresc/crfsuite/usr_local_lib
python /homes/grabmuel/eclipse/CoreSC/avro/start_coresc_server.py