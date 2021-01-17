# Makefile for docker environment

.PHONY : clean sapienta_base candc all

all : sapienta_base candc


clean :
	rm -rf sapienta_base/sapienta/
	rm sapienta_base/setup.py

sapienta_base : sapienta_base/Dockerfile
	cp -r ../sapienta sapienta_base
	cp ../setup.py sapienta_base/setup.py
	docker build -t sapienta/base sapienta_base/ 


candc: candc/Dockerfile
	docker build -t sapienta/candc candc
