FROM base/archlinux:latest


MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>

ADD models/ /models
ADD candc-1.00/ /candc
#ADD candc.patch /candc/candc.patch
ADD run_server.sh /candc/bin/run_server.sh

#make sure pacman keys are up to date
#RUN pacman-key --refresh-keys

#RUN pacman -Sy --noconfirm libstdc++5 base-devel libunistring wget

#build gsoap because the latest in the repo doesn't work
#RUN wget -O  gsoap.tar.gz http://sourceforge.net/projects/gsoap2/files/gSOAP/gSOAP%202.7.9f%20stable/gsoap_2.7.9f.tar.gz/download &&\
#    tar xf gsoap.tar.gz &&\
#    cd gsoap-2.7 &&\
#    export CXXFLAGS='-fpermissive' &&\
#    ./configure &&\
#    make &&\
#    make install

#RUN cd /candc && patch -p1 -i candc.patch

#RUN cd /candc && mv Makefile.unix Makefile && make && make soap

EXPOSE 9004

ENTRYPOINT cd /candc/bin && ./run_server.sh
