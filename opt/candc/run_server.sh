#!/bin/sh


if [ $# -lt 1 ]
then
    PORT=9004
else
    PORT=$1
fi

echo $PORT

ARGS="--models ../../models --candc-pos ../../models/pos_bio-1.00 --candc-pos-maxwords 900 --candc-parser ../../models/parser --candc-super ../../models/super_coresc/ --candc-parser-markedup ../../models/parser/cats/markedup_new --candc-super-maxwords 900 --candc-parser-maxwords 900 --server 127.0.0.1:$PORT"

until ./soap_server $ARGS; do
    echo "soap server crashed. Respawning..." >&2
    sleep 1
done
