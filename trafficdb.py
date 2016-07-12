#!/usr/bin/python

from sys import argv
import configparser
from datetime import date

import htmlReport
import systemWrapper
import databaseWrapper

options = {
    "config-file" : "trafficdatabaseWrapper.conf", # Default configuration file
    "enable" : False, # True if service is enabled on enable
    "apache-path" : "/srv/http", # Path of apache server http directory
    "mysql-user" : "root", # Database user
    "mysql-password" : "toor", # Database password
    "database" : False, # True if read logs from database
    "generate-report" : False, # True if it is called to generate report
    "service" : False, # True if it is called to run as service
    "kill" : False, # True if is called to stop service
    "register" : False, # True if it is time to store log into database
    "interface" : "eth0", # Network interface
    "port" : None, # Port
    "ip-filter" : None, # IP address for filtering
    "log-path" : "/home/trafficdb.log" # Path of log
}

def parseArguments(arguments):
    if "--help" in arguments or "-h" in arguments:
        print ("""\
--conf           or -c     Set configuration file.
--enable         or -en    Make service start at boot.
--disable        or -di    Stop service to start at boot.
--srv-path       or -sp    Set apache http directory.
--database       or -db    Read logs from database.
--mysql-user     or -mu    Set mysql user.
--mysql-password or -mp    Set mysql password.
--service        or -s     Start service.
--kill           or -k     Kill service.
--interface      or -i     Set network interface.
--port           or -p     Set port number.
--ip-filer       or -f     Set IP address for filter.
--log            or -l     Set log path.
        """)
        return False

    ignore_arg = False
    use_file = False

    print ("[INFO] Parse arguments.")
    for i in range(1, len(arguments)):
        arg = arguments[i]

        if ignore_arg:
            ignore_arg = False
        elif arg == "--conf" or arg == "-c":
            try:
                options["config-file"] = arguments[i + 1]
                ignore_arg = True
                use_file = True
            except:
                print ("[ERROR] Expected filename.")
                return True
        elif arg == "--enable" or arg == "-en":
            options["enable"] = True
        elif arg == "--disable" or arg == "-di":
            options["enable"] = False
        elif arg == "--srv-path" or arg == "-sp":
            try:
                options["apache-path"] = arguments[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected path.")
                return True
        elif arg == "--database" or arg == "-db":
            options["database"] = True
        elif arg == "--mysql-user" or arg == "-mu":
            try:
                options["mysql-user"] = arguments[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected path.")
                return True
        elif arg == "--mysql-password" or arg == "-mp":
            try:
                options["mysql-password"] = arguments[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected path.")
                return True
        elif arg == "--service" or arg == "-s":
            options["service"] = True
        elif arg == "--kill" or arg == "-k":
            options["kill"] = True
        elif arg == "--interface" or arg == "-i":
            try:
                options["interface"] = arguments[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected interface name.")
                return True
        elif arg == "--port" or arg == "-p":
            try:
                options["port"] = arguments[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected port number.")
                return True
        elif arg == "--ip-filter" or arg == "-f":
            try:
                options["ip-filter"] = arguments[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected mac address.")
                return True
        elif arg == "--log" or arg == "-l":
            try:
                options["log-path"] = arguments[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected path.")
                return True
        else:
            print("[ERROR] Unknown argument '%s'." % arguments[i])
            return True

    if use_file:
        print ("[INFO] Read configuration file.")
        allowed_config = ["apache-path", "ip-filter", "port", "interface", "log-path", "mysql-password", "mysql-user"]

        config = configparser.RawConfigParser()
        config.read(options["config-file"])
        conf_options = config.options(config.sections()[0])
        for opt in conf_options:
            if opt not in allowed_config:
                print ("[ERROR] You used invalid config options.")
                return True
            else:
                options[opt] = config.get(config.sections()[0], opt)

def main(options):
    if parseArguments(argv):
        return True

    pidFileName = "/tmp/trafficdb_%s_%s_%s.pid" % (options["interface"], options["port"], options["ip-filter"])
    tcpdumpDaemon = systemWrapper.Tcpdump(pidFileName, stdout = options["log-path"])

    print ("[INFO] Options are the following:")
    for key in options.keys():
        print ("%s: %s" % (key, options[key]))
    choice = input("Run the program? [Y/n]? ")
    if choice.lower() != "y":
        print ("[INFO] Aborted!")
        return False

    if options["generate-report"] and options["service"]:
        print ("[ERROR] You cand use only one running mode.")
        return True
    elif options["service"] and options["kill"]:
        print ("[ERROR] You can't start and kill service in same time.")
        return True
    elif options["service"]:
        print ("[INFO] Start the service...")
        systemWrapper.startService(tcpdumpDaemon, options)
    elif options["kill"]:
        print ("[INFO] Stop the service...")
        systemWrapper.stopService(tcpdumpDaemon, options)

    return False

if __name__ == "__main__":
    ret = main(options)
    if ret:
        print ("[INFO] Program stopped.")
