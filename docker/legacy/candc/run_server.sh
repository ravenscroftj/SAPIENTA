#!/bin/sh
./soap_server --models ../../models --candc-pos ../../models/pos_bio-1.00 --candc-pos-maxwords 900 --candc-parser ../../models/parser --candc-super ../../models/super_coresc/ --candc-parser-markedup ../../models/parser/cats/markedup_new --candc-super-maxwords 900 --candc-parser-maxwords 900 --server 0.0.0.0:9004
