import os

def getLineElements(line, report):
    line = line.strip("\n")
    line = line.replace(",", " ")
    line = line.split()

    # Parse MAC addresses
    report["SourceMAC"].append(line[2])
    report["DestinationMAC"].append(line[4])

    # Parse source IP and source port
    rawIP = line[10]
    rawIP = rawIP.split(".")
    formatedIP = ""
    for i in range(0, len(rawIP) - 1):
        formatedIP += rawIP[i]
        formatedIP += "."
    formatedIP = formatedIP[:-1]
    port = rawIP[-1]
    report["SourceIP"].append(formatedIP)
    report["SourcePort"].append(port)

    # Parse destination IP and port
    rawIP = line[12][:-1]
    rawIP = rawIP.split(".")
    formatedIP = ""
    for i in range(0, len(rawIP) - 1):
        formatedIP += rawIP[i]
        formatedIP += "."
    formatedIP = formatedIP[:-1]
    port = rawIP[-1]
    report["DestinationIP"].append(formatedIP)
    report["DestinationPort"].append(port)

    # Parse time and date
    report["CurrentDate"].append(line[0])
    report["CurrentTime"].append(line[1])
    report["Ethertype"].append(line[6])
    report["IPLength"].append(line[9][:-1])

    # Parse flags and options
    flags_options = ""
    for i in range(13, len(line)):
        if line[i] == "length":
            i += 1
            break
        else:
            flags_options += line[i]
            flags_options += " "
    report["FlagsAndOptions"].append(flags_options)

    # Parse packet length and content
    if line[i][-1] == ":":
        report["PacketLength"].append(line[i][:-1])
        content = ""
        for j in range(i + 1, len(line)):
            content += line[j]
            content += " "
        report["ContentType"].append(content)
    else:
        report["PacketLength"].append(line[i])
        report["ContentType"].append(None)

def readLogFile(options):
    report = {
    "SourceMAC" : [],
    "DestinationMAC" : [],
    "SourceIP": [],
    "SourcePort": [],
    "DestinationIP": [],
    "DestinationPort": [],
    "CurrentDate" : [],
    "CurrentTime" : [],
    "Ethertype" : [],
    "IPLength": [],
    "PacketLength": [],
    "FlagsAndOptions": [],
    "ContentType": []
    }

    with open(options["log-path"], "r") as f:
        content = f.readlines()
    for line in content:
        getLineElements(line, report)

    """for i in range(0, len(report["SourceMAC"])):
        for key in report.keys():
            print ("%s : %s" % (key, report[key][i]))
        print ('--------------------------------------\n')"""

    return report

def generateHTMLReport(options, report, name):
    HTMLContent = """\
<!DOCTYPE html>\n \
<html>\n \
<body>\n \
<table border=\"1\" style=\"width:100%\">\n \
    """

    table_first_row = ["ID", "Date", "Time", "Source MAC", "Destination MAC",
                        "Source IP", "Source Port", "Destination IP",
                        "Destination Port", "Ethertype", "IP Length",
                        "Flags And Options", "Content Length", "Content Type"]

    HTMLContent += "\t<tr>\n"
    for elem in table_first_row:
        HTMLContent += "\t\t<td>%s</td>\n" % elem
    HTMLContent += "\t</tr>\n"

    report_order = ["CurrentDate", "CurrentTime", "SourceMAC", "DestinationMAC",
                    "SourceIP", "SourcePort", "DestinationIP",
                    "DestinationPort", "Ethertype", "IPLength",
                    "FlagsAndOptions", "PacketLength", "ContentType"]

    for i in range(0, len(report["SourceMAC"])):
        HTMLContent += "\t<tr>\n"
        HTMLContent += "\t\t<td>%s</td>\n" % i
        for key in report_order:
            HTMLContent += "\t\t<td>%s</td>\n" % report[key][i]
        HTMLContent += "\t</tr>\n"

    HTMLContent += "</table>\n</body>\n</html>\n"
    with open(name, "w") as f:
        f.write(HTMLContent)

def generateIndexFile(options, file_list):
    HTMLContent = """\
<!DOCTYPE html>\n \
<html>\n \
<body>\n \
    """

    HTMLContent += "\t<center><h1>------TCPDUMP REPORT------</h1></center><br/><br/>\n"
    for f in file_list:
        HTMLContent += "<h3><a href=\"%s\">%s</a></h3><br/>" % ("./" + f, f.replace(".html", ""))
        os.system("sudo cp \"%s\" \"%s\"" % (f, options["apache-path"]))

    HTMLContent += "</body>\n</html>\n"
    with open(options["apache-path"] + "/index.html", "w") as f:
        f.write(HTMLContent)
