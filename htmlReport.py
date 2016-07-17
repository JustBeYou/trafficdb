import os
import hashlib
import databaseWrapper

def getLineElements(line):
    entry = {
    "SourceMAC" : "None",
    "DestinationMAC" : "None",
    "SourceIP": "None",
    "SourcePort": "None",
    "DestinationIP": "None",
    "DestinationPort": "None",
    "CurrentDate" : "None",
    "CurrentTime" : "None",
    "Ethertype" : "None",
    "IPLength": "None",
    "PacketLength": "None",
    "FlagsAndOptions": "None",
    "ContentType": "None",
    "Hash" : "None"
    }

    line = line.strip("\n")
    line = line.strip("b")
    line = line.strip("\'")
    line = line.replace("\\n", "")
    line = line.replace("(", "")
    line = line.replace(")", "")
    line = line.replace(",", " ")
    line = line.split()

    # Parse MAC addresses
    entry["SourceMAC"] = line[2]
    entry["DestinationMAC"] = line[4]

    # Parse source IP and source port
    rawIP = line[10]
    rawIP = rawIP.split(".")
    formatedIP = ""
    for i in range(0, len(rawIP) - 1):
        formatedIP += rawIP[i]
        formatedIP += "."
    formatedIP = formatedIP[:-1]
    port = rawIP[-1]
    entry["SourceIP"] = formatedIP
    entry["SourcePort"] = port

    # Parse destination IP and port
    rawIP = line[12][:-1]
    rawIP = rawIP.split(".")
    formatedIP = ""
    for i in range(0, len(rawIP) - 1):
        formatedIP += rawIP[i]
        formatedIP += "."
    formatedIP = formatedIP[:-1]
    port = rawIP[-1]
    entry["DestinationIP"] = formatedIP
    entry["DestinationPort"] = port

    # Parse time and date
    entry["CurrentDate"] = line[0]
    entry["CurrentTime"] = line[1]
    entry["Ethertype"] = line[6]
    entry["IPLength"] = line[9][:-1]

    # Parse flags and options
    flags_options = ""
    for i in range(13, len(line)):
        if line[i] == "length":
            i += 1
            break
        else:
            flags_options += line[i]
            flags_options += " "
    entry["FlagsAndOptions"] = flags_options

    # Parse packet length and content
    if line[i][-1] == ":":
        entry["PacketLength"] = line[i][:-1]
        content = ""
        for j in range(i + 1, len(line)):
            content += line[j]
            content += " "
        entry["ContentType"] = content
    else:
        entry["PacketLength"] = line[i]
        entry["ContentType"] = "None"

    # Create hash
    hashstring = entry["SourceMAC"] + entry["DestinationMAC"]
    hashstring += entry["SourceIP"] + entry["DestinationIP"]
    hashstring += entry["CurrentDate"] + entry["CurrentTime"]
    hashstring += entry["PacketLength"] + entry["ContentType"]
    packethash = str(hashlib.md5(hashstring.encode("utf-8")).hexdigest())
    entry["Hash"] = packethash

    return entry


def generatePHPindex(options):
    content = """ \
<!DOCTYPE html>
    <head>
        <title>TCPDUMP REPORT</title>
    </head>
    <body>
        <?php
            echo 'Connect to db';
            $dbh = new PDO("mysql:host=localhost;dbname=trafficdb;", "%s", "%s");
            
        ?>
        <table>
            <tr>
                <td>Id</td>
                <td>Date</td>
                <td>Time</td>
                <td>Source MAC</td>
                <td>Destination MAC</td>
                <td>Source IP</td>
                <td>Source Port</td>
                <td>Destination IP</td>
                <td>Destination Port</td>
                <td>Ethertype</td>
                <td>IP Length</td>
                <td>Flags</td>
                <td>Packet Length</td>
                <td>Content Type</td>
                <td>Hash</td>
            </tr>
            <?php
               echo 'LETS BUILD IT!';
               $stmt = $dbh->query("SELECT * FROM traffic");
               $stmt->execute();
               $result = $stmt->fetchall(PDO::FETCH_ASSOC);
               foreach($result as $line) {
                    echo $line;
                   echo "<tr>";
                   echo "<td>".$line[id]."</td>";
                   echo "<td>".$line[currentdate]."</td>";
                   echo "<td>".$line[currenttime]."</td>";
                   echo "<td>".$line[sourcemac]."</td>";
                   echo "<td>".$line[destinationmac]."</td>";
                   echo "<td>".$line[sourceip]."</td>";
                   echo "<td>".$line[sourceport]."</td>";
                   echo "<td>".$line[destinationip]."</td>";
                   echo "<td>".$line[destinationport]."</td>";
                   echo "<td>".$line[ethertype]."</td>";
                   echo "<td>".$line[iplength]."</td>";
                   echo "<td>".$line[flagsandoptions]."</td>";
                   echo "<td>".$line[packetlength]."</td>";
                   echo "<td>".$line[contenttype]."</td>";
                   echo "<td>".$line[hash]."</td>";
                   echo "</tr>";
               }

            ?>
        </table>
    </body>
</html>
    """
    print (content % (options["mysql-user"], options["mysql-password"]))
    f = open(options["apache-path"] + "/" + "index.php", "w")
    f.write(content % (options["mysql-user"], options["mysql-password"]))
    f.close()

#def readTcpdumpOutput(options):
#    report = {
#    "SourceMAC" : [],
#    "DestinationMAC" : [],
#    "SourceIP": [],
#    "SourcePort": [],
#    "DestinationIP": [],
#    "DestinationPort": [],
#    "CurrentDate" : [],
#    "CurrentTime" : [],
#    "Ethertype" : [],
#    "IPLength": [],
#    "PacketLength": [],
#    "FlagsAndOptions": [],
#    "ContentType": [],
#    "Hash" : []
#    }
#
#    with open(options["log-path"], "r") as f:
#        for line in f:
#           try:
#               getLineElements(line, report)
#          except:
#             print ("Unsupported line format: %s" % line)
#            print ("Register it manually or contact developer for update!")
#
#    return report

# OLD IMPLEMENTATION FOR REPORT GENERATION
#def generateHTMLReport(options, report, name):
#    HTMLContent = """\
#<!DOCTYPE html>\n \
#<html>\n \
#<body>\n \
#<table border=\"1\" style=\"width:100%\">\n \
#    """
#
#    table_first_row = ["ID", "Date", "Time", "Source MAC", "Destination MAC",
#                        "Source IP", "Source Port", "Destination IP",
#                        "Destination Port", "Ethertype", "IP Length",
#                        "Flags And Options", "Content Length", "Content Type", "Hash"]#
#
#    HTMLContent += "\t<tr>\n"
#    for elem in table_first_row:
#        HTMLContent += "\t\t<td>%s</td>\n" % elem
#    HTMLContent += "\t</tr>\n"
#
#    report_order = ["CurrentDate", "CurrentTime", "SourceMAC", "DestinationMAC",
#                    "SourceIP", "SourcePort", "DestinationIP",
#                    "DestinationPort", "Ethertype", "IPLength",
#                    "FlagsAndOptions", "PacketLength", "ContentType",  "Hash"]
#
#    for i in range(0, len(report["SourceMAC"])):
#        HTMLContent += "\t<tr>\n"
#        HTMLContent += "\t\t<td>%s</td>\n" % i
#        for key in report_order:
#            HTMLContent += "\t\t<td>%s</td>\n" % report[key][i]
#        HTMLContent += "\t</tr>\n"
#
#    HTMLContent += "</table>\n</body>\n</html>\n"
#    with open(name, "w") as f:
#        f.write(HTMLContent)
#
#def generateIndexFile(options, file_list):
#    HTMLContent = """\
#<!DOCTYPE html>\n \
#<html>\n \
#<body>\n \
#    """
#
#    HTMLContent += "\t<center><h1>------TCPDUMP REPORT------</h1></center><br/><br/>\n"
#    for f in file_list:
#        HTMLContent += "<h3><a href=\"%s\">%s</a></h3><br/>" % ("./" + f, f.replace(".html", ""))
#        os.system("sudo cp \"%s\" \"%s\"" % (f, options["apache-path"]))
#
#    HTMLContent += "</body>\n</html>\n"
#    with open(options["apache-path"] + "/index.html", "w") as f:
#        f.write(HTMLContent)
