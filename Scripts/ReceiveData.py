import mido
from ConfigurationSetup import *

#configuration Setup
cfgFile="config.cfg"
config=parse_cfg(cfgFile)

#receive Data
with mido.open_input(config["inPort"]) as inputPort:
    for msg in inputPort:
        print (msg)

