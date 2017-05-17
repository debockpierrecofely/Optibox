import configparser
import os

Config = configparser.ConfigParser()
Config.read("../conf/config.ini")
#Config.read("C:\\Users\\Pierre\\Documents\\GitHub\\Nouveau dossier (2)\\Optimiz\\PulseImport\\conf\\config.ini")

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def GetVariable(section, vari):
    try:
        res=os.environ[vari]
    except Exception as e:
        print ('%s Environment variable not set.' %(vari))
        res=ConfigSectionMap(section)[vari.lower()];
    return res
