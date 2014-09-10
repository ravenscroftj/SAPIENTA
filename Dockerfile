FROM ubuntu:latest
MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>

#install necessary software 
RUN apt-get update && apt-get install -y python2 git gsoap build-essential


#download and install liblbfgs
RUN cd /home/ && wget https://github.com/downloads/chokkan/liblbfgs/liblbfgs-1.10.tar.gz && tar xf liblbfgs-1.10.tar.gz

RUN cd /home/liblbfgs-1.10 && ./configure --prefix=/usr && make && make install

#download and install crfsuite
RUN cd /home/ && wget https://github.com/chokkan/crfsuite/archive/master.zip && unzip master.zip

RUN cd /home/crfsuite-master && ./autogen.sh && ./configure --prefix=/usr && make && make install

RUN cd /home/crfsuite-master/swig/python && cp ../crfsuite.cpp . && python setup.py build && python setup.py install

#download CANDC tools
RUN cd /home/ && wget --http-user "ravenscroftj@gmail.com" --http-password lxArrHpJ http://svn.ask.it.usyd.edu.au/download/candc/candc-1.00.tbz2  && tar xf candc-1.00.tbz2

#download CANDC models
RUN cd /home/ && wget --http-user "ravenscroftj@gmail.com" --http-password lxArrHpJ http://svn.ask.it.usyd.edu.au/download/candc/models-1.02.tbz2  && tar xf models-1.02.tbz2

RUN cd /home/ && wget http://www.cl.cam.ac.uk/research/nl/nl-download/candc/pos_bio-1.00.tbz2 && tar xf pos_bio-1.00.tbz2 && mv pos_bio-1.00 /home/models

RUN cd /home/ && wget http://www.cl.cam.ac.uk/research/nl/nl-download/candc/pos_bio-1.00.tbz2 && tar xf pos_bio-1.00.tbz2 && mv pos_bio-1.00 /home/models

RUN cd /home/models/parser/cats && wget http://doku.jamesravenscroft.net/~james/sapienta_files/markedup_new
