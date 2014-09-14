FROM ubuntu:latest
MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>

#install necessary software 
RUN apt-get update && apt-get install -qy \
python\
autoconf\
automake\
libtool\
lzma\
libpython-dev\
python-pip\
python-pycurl\
python-flask\
git\
gsoap\
build-essential\
openssh-server\
supervisor\
unzip

RUN mkdir -p /var/run/sshd /var/log/supervisor

#download and install liblbfgs
RUN cd /home/ && wget https://github.com/downloads/chokkan/liblbfgs/liblbfgs-1.10.tar.gz && tar xf liblbfgs-1.10.tar.gz

RUN cd /home/liblbfgs-1.10 && ./configure --prefix=/usr && make && make install

#download crfsuite
RUN cd /home/ && wget https://github.com/chokkan/crfsuite/archive/master.zip && unzip master.zip

#download CANDC tools
RUN cd /home/ && wget --http-user "ravenscroftj@gmail.com" --http-password lxArrHpJ http://svn.ask.it.usyd.edu.au/download/candc/candc-1.00.tbz2  && tar xf candc-1.00.tbz2

#download CANDC models
RUN cd /home/ && wget --http-user "ravenscroftj@gmail.com" --http-password lxArrHpJ http://svn.ask.it.usyd.edu.au/download/candc/models-1.02.tbz2  && tar xf models-1.02.tbz2

RUN cd /home/ && wget http://www.cl.cam.ac.uk/research/nl/nl-download/candc/pos_bio-1.00.tbz2 && tar xf pos_bio-1.00.tbz2 && mv pos_bio-1.00 /home/models

RUN cd /home/models && wget http://doku.jamesravenscroft.net/~james/sapienta_files/super_coresc.tar.lzma && tar xf super_coresc.tar.lzma

RUN cd /home/models/parser/cats && wget http://doku.jamesravenscroft.net/~james/sapienta_files/markedup_new

#patch and build crfsuite
#COPY opt/crfsuite/crfsuite.patch /home/crfsuite-master/crfsuite.patch
COPY opt/crfsuite/configure.in /home/crfsuite-master/configure.in

RUN cd /home/crfsuite-master && patch -p1 crfsuite.patch

RUN cd /home/crfsuite-master && ./autogen.sh && ./configure --prefix=/usr && make && make install

RUN cd /home/crfsuite-master/swig/python && cp ../crfsuite.cpp . && python setup.py build && python setup.py install

#patch and build candc
COPY opt/candc/candc.patch /home/candc-1.00/candc.patch

RUN cd /home/candc-1.00 && \
patch -p1 -i candc.patch && \
mv Makefile.unix Makefile && \
make && \
make soap 

#copy C and C script
COPY opt/candc/run_server.sh /home/candc-1.00/bin/run_server.sh

#install text-sentence package
RUN cd /home/ && wget http://doku.jamesravenscroft.net/~james/sapienta_files/text-sentence.tar.gz && tar xf text-sentence.tar.gz
RUN cd /home/text-sentence && python setup.py build && python setup.py install

#copy sapienta source
COPY setup.py /home/sapienta/setup.py
COPY sapienta /home/sapienta/sapienta
COPY ccg_binding.wsdl /home/sapienta/ccg_binding.wsdl

#build and install sapienta
RUN cd /home/sapienta/ && python setup.py build && python setup.py install

#copy and install supervisor config
COPY opt/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 1234

CMD ["/usr/bin/supervisord"]
