from sapienta/base

MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>


ENV PARTRIDGE_CONF /sapienta.cfg

#create output for "done" papers
RUN mkdir -p /tmp/done

#add mode2 transform to dir
ADD mode2.xsl /build/mode2.xsl

#run server
ENTRYPOINT cd /build/ && python2 -m "sapienta"
