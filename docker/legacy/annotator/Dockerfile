from sapienta/base

MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>

ENV PARTRIDGE_CONF /sapienta.cfg

ADD ./ccg_binding.wsdl /build/ccg_binding.wsdl

#run server
ENTRYPOINT cd /build/ && python2 sapienta/service/annotate.py
