#!/usr/bin/python

from sys import argv
import configparser
from datetime import date

import htmlReport
import systemWrapper

options = {
    "config-file" : "trafficdb.conf", # Default configuration file
    "enable" : False, # True if service is enabled on enable
    "apache-path" : "/srv/http", # Path of apache server http directory
    "generate-report" : False, # True if it is called to generate report
    "service" : False, # True if it is called to run as service
    "kill" : False, # True if is called to stop service
    "interface" : "eth0", # Network interface
    "port" : None, # Port
    "mac-addr" : None, # Mac address
    "log-path" : "/home/trafficdb.log" # Path of log
}

def main(options):
    # Parse command line arguments
    if "--help" in argv or "-h" in argv:
        print ("""\
--conf      or -c     Set configuration file.
--enable    or -en    Make service start at boot.
--disable   or -di    Stop service to start at boot.
--srv-path  or -sp    Set apache http directory.
--gen-rap   or -r     Generate report.
--service   or -s     Start service.
--kill      or -k     Kill service.
--interface or -i     Set network interface.
--port      or -p     Set port number.
--mac       or -m     Set mac addres.
--log       or -l     Set log path.
        """)
        return False

    ignore_arg = False
    use_file = False

    print ("[INFO] Parse arguments.")
    for i in range(1, len(argv)):
        arg = argv[i]

        if ignore_arg:
            ignore_arg = False
        elif arg == "--conf" or arg == "-c":
            try:
                options["config-file"] = argv[i + 1]
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
                options["apache-path"] = argv[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected path.")
                return True
        elif arg == "--gen-rap" or arg == "-r":
            options["generate-report"] = True
        elif arg == "--service" or arg == "-s":
            options["service"] = True
        elif arg == "--kill" or arg == "-k":
            options["kill"] = True
        elif arg == "--interface" or arg == "-i":
            try:
                options["interface"] = argv[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected interface name.")
                return True
        elif arg == "--port" or arg == "-p":
            try:
                options["port"] = argv[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected port number.")
                return True
        elif arg == "--mac" or arg == "-m":
            try:
                options["mac-addr"] = argv[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected mac address.")
                return True
        elif arg == "--log" or arg == "-l":
            try:
                options["log-path"] = argv[i + 1]
                ignore_arg = True
            except:
                print ("[ERROR] Expected path.")
                return True
        else:
            print("[ERROR] Unknown argument '%s'." % argv[i])
            return True

    if use_file:
        print ("[INFO] Read configuration file.")
        allowed_config = ["apache-path", "mac-addr", "port", "interface", "log-path"]

        config = configparser.RawConfigParser()
        config.read(options["config-file"])
        conf_options = config.options(config.sections()[0])
        for opt in conf_options:
            if opt not in allowed_config:
                print ("[ERROR] You used invalid config options.")
                return True
            else:
                options[opt] = config.get(config.sections()[0], opt)

    tcpdumpDaemon = systemWrapper.Tcpdump("/tmp/trafficdb.pid", stdout = options["log-path"])

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
    elif options["generate-report"]:
        print ("[INFO] Read log file...")
        report = htmlReport.readLogFile(options)
        print ("[INFO] Generate HTML files...")
        htmlReport.generateHTMLReport(options, report, "Full.html")

        for i in range(0, len(report["CurrentDate"])):
            year = int(report["CurrentDate"][i][:4])
            if date.today().year - year > 1:
                break
        for key in report.keys():
            report[key] = report[key][:i]
        htmlReport.generateHTMLReport(options, report, "Last year.html")

        for i in range(0, len(report["CurrentDate"])):
            month = report["CurrentDate"][i][5:7]
            if month[0] == "0":
                month = int(month[1])
            else:
                month = int(month)
            if date.today().month - month > 1:
                break
        for key in report.keys():
            report[key] = report[key][:i]
        htmlReport.generateHTMLReport(options, report, "Last month.html")

        for i in range(0, len(report["CurrentDate"])):
            day = report["CurrentDate"][i][8:]
            if day[0] == "0":
                day = int(day[1])
            else:
                day = int(day)
            if date.today().day - day > 1:
                break
        for key in report.keys():
            report[key] = report[key][:i]
        htmlReport.generateHTMLReport(options, report, "Last day.html")

        file_list = ["Full.html", "Last day.html",
                    "Last month.html", "Last year.html"]
        htmlReport.generateIndexFile(options, file_list)
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
