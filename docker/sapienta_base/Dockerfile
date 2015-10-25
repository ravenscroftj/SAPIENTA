from base/archlinux:latest

MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>

##add sapienta models
ADD https://www.dropbox.com/s/ghasw5691jxi9zl/all_papers.model?dl=1 /models/all_papers.model
ADD https://www.dropbox.com/s/powx8lpjwkjlm3e/ngrams.pickle?dl=1    /models/ngrams.pickle
ADD https://www.dropbox.com/s/6u5yd6nh0j45yfg/written.num.o5?dl=1   /models/written.num.o5

#make sure pacman keys are up to date
RUN pacman-key --refresh-keys

#install dependencies
RUN pacman -Syu --noconfirm libstdc++5 git base-devel python2 python2-pip python2-setuptools libunistring

#check out and build liblbfgs
RUN git clone https://github.com/chokkan/liblbfgs.git

RUN cd liblbfgs && ./autogen.sh && ./configure --prefix=/usr && make && make install

#check out and build crfsuite
ADD https://github.com/downloads/chokkan/crfsuite/crfsuite-0.12.tar.gz ./

RUN tar xf crfsuite-0.12.tar.gz

RUN cd ./crfsuite-0.12 && ./configure --prefix=/usr && make && make install

RUN cd /crfsuite-0.12/swig/python && cp ../crfsuite.cpp . && python2 setup.py install

#add sapienta source
ADD ./sapienta /build/sapienta
ADD ./setup.py /build/
ADD ./sapienta.cfg /sapienta.cfg

#install sapienta client
RUN cd /build/ && python2 setup.py develop
