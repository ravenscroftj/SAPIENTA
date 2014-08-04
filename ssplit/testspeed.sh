#!/bin/bash
PWD=`pwd`
java -cp "$PWD/build:$PWD/jar/hamcrest-all-1.3.jar:$PWD/jar/junit-4.11.jar:$PWD/jar/xmlunit-1.5.jar:$PWD/jar/xom-1.2.6.jar" org.junit.runner.JUnitCore uk.ac.aber.sssplit.AverageTimeTest
