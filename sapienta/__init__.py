"""This is the main entrypoint for SAPIENTA server and configuration"""
import os
from flask import Flask

app = Flask(__name__)

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
