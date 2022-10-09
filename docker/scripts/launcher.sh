#!/bin/sh
# PAPERS=$(ls -d ./papers/* |  xargs -i echo \"{}\")

# echo "running 'pdfxconv --candc-hosts="http://candc:9004/" -a $PAPERS' "
pdfxconv --candc-hosts="http://candc:9004/" -a $@

chmod 777 /app/papers/*