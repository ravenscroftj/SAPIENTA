FROM base/archlinux:latest


MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>

ADD models/ /models
ADD candc-1.00/ /candc
ADD candc.patch /candc/candc.patch

RUN pacman -Sy --noconfirm libstdc++5 gsoap base-devel libunistring

#RUN cd /candc && patch -p1 -i candc.patch

RUN cd /candc && mv Makefile.unix Makefile && make && make soap

EXPOSE 9004

ENTRYPOINT cd /candc/bin && ./run_server.sh
