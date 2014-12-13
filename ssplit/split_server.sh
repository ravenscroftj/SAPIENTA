#!/bin/bash
PWD=`pwd`
JARS=$( ls $PWD/jar/*.jar )
CP=$PWD/dist/lib/SSSplit2.jar
for jar in $JARS
    do
        CP=$CP:$jar
done

echo "running java -cp $CP uk.ac.aber.sssplit.SplitServer"

java -cp "$CP" uk.ac.aber.sssplit.SplitServer 
