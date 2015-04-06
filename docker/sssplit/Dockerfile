from base/archlinux:latest 

MAINTAINER James Ravenscroft <ravenscroft@papro.org.uk>

#add sapienta source
ADD ./sssplit /build/sssplit
ADD ./sssplit.properties /build/sssplit/sssplit.properties

#install dependencies
RUN pacman -Sy --noconfirm jdk7-openjdk apache-ant 

#run server
ENTRYPOINT cd /build/sssplit/ && ./split_server.sh
