"""This is the main entrypoint for SAPIENTA server and configuration"""
import os
import sys
import logging
from flask import Flask


app = Flask("sapienta")

import sapienta.views

#try and load configuration
if( os.getenv("PARTRIDGE_CONF")):
    #try and load config from env directory
    app.config.from_envvar("PARTRIDGE_CONF")
else:
    for loc in (os.getcwd(), 
      os.path.expanduser("~/.config/"), 
      "/etc/"):
      
              try:
                    source = os.path.join(loc,"sapienta.cfg")
                    app.config.from_pyfile(source)
              except IOError:
                pass


def main():
    """Main sapienta web server entrypoint
    
    This entrypoint can be used on the commandline to run a flask test server for SAPIENTA"""

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("-d", "--debug", dest="debug", action="store_true",
            help="Provide more debug output and reload server on changes")

    parser.add_option("-p", "--port", dest="port", default="5000",
        help="Set the port that sapienta will server web pages on")

    opts,args = parser.parse_args(sys.argv)

    logLevel = logging.INFO

    if opts.debug:
        app.config['DEBUG'] = True
        logLevel = logging.DEBUG

    logging.basicConfig(level=logLevel, format="%(asctime)s - %(levelname)s - %(name)s:%(message)s")

    app.run(host="0.0.0.0", port=int(opts.port))


#----------------------------------------------------------------
if __name__ == "__main__":
    main()
