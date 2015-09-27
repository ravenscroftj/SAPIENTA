# Makefile for docker environment

.PHONY : clean sapienta_base all

all : fig

clean :
	rm -rf sapienta_base/sapienta/

sapienta_base : sapienta_base/Dockerfile
	cp -r ../sapienta sapienta_base
	docker build -t sapienta:base sapienta_base/ 

fig: sapienta_base fig.yml 
	fig up
