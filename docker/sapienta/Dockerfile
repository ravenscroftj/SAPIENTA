from base/archlinux:latest 

MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>

#add sapienta source
ADD ./sapienta /build/sapienta
ADD ./setup.py /build/
ADD ./sapienta.cfg ~/.config/sapienta.cfg

##add sapienta models
ADD ./all_papers.model /models/all_papers.model
ADD ./ngrams.pickle    /models/ngrams.pickle
ADD ./written.num.o5   /models/written.num.o5

#install dependencies
RUN pacman -Sy --noconfirm libstdc++5 git base-devel python2 python2-pip python2-setuptools libunistring 

#check out and build liblbfgs
RUN git clone https://github.com/chokkan/liblbfgs.git

RUN cd liblbfgs && ./autogen.sh && ./configure --prefix=/usr && make && make install

#check out and build crfsuite
ADD https://github.com/downloads/chokkan/crfsuite/crfsuite-0.12.tar.gz ./

RUN tar xf crfsuite-0.12.tar.gz 

RUN cd ./crfsuite-0.12 && ./configure --prefix=/usr && make && make install

#install sapienta client
RUN cd /build/ && python2 setup.py develop

RUN python2 /build/sapienta/processing/base.py
