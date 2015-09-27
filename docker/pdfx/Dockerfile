from sapienta:base

MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>

RUN pacman-db-upgrade
RUN pacman -Syu --noconfirm python2-lxml

ENV PARTRIDGE_CONF /sapienta.cfg

#run server
ENTRYPOINT cd /build/ && python2 sapienta/service/pdf.py
