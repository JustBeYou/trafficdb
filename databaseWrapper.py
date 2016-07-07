import pymysql.cursors

report_columns = ["CurrentDate", "CurrentTime", "SourceMAC", "DestinationMAC",
                    "SourceIP", "SourcePort", "DestinationIP",
                    "DestinationPort", "Ethertype", "IPLength",
                    "FlagsAndOptions", "PacketLength", "ContentType",  "Hash"]

columns_names = []
for col in report_columns:
    col_as_list = list(col.lower())
    col_as_list.insert(0, "`")
    col_as_list.insert(len(col_as_list), "`")
    columns_names.append(''.join(col_as_list))

columns_names = ', '.join(columns_names)

def connectDB(options):
    return pymysql.connect(host = "localhost",
                            user = options["mysql-user"],
                            password = options["mysql-password"],
                            db = "trafficdb",
                            charset = "utf8mb4",
                            cursorclass = pymysql.cursors.DictCursor)

def disconnectDB(connectionToDB):
    connectionToDB.close()

def writeReport(connectionToDB, report):
    # Try to create table
    connectionToDB.cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS `traffic` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `currentdate` varchar(255) NOT NULL,
        `currenttime` varchar(255) NOT NULL,
        `sourcemac` varchar(255) NOT NULL,
        `destinationmac` varchar(255) NOT NULL,
        `sourceip` varchar(255) NOT NULL,
        `sourceport` varchar(255) NOT NULL,
        `destinationip` varchar(255) NOT NULL,
        `destinationport` varchar(255) NOT NULL,
        `ethertype` varchar(255) NOT NULL,
        `iplength` varchar(255) NOT NULL,
        `flagsandoptions` varchar(255) NOT NULL,
        `packetlength` varchar(255) NOT NULL,
        `contenttype` varchar(255),
        `hash` varchar(255) NOT NULL,
         PRIMARY KEY(`id`)
    );
    """
    )
    connectionToDB.commit()

    sqlstr = "INSERT INTO `traffic` (%s) VALUES (%s)"

    for i in range(0, len(report["SourceMAC"])):
        hashstr = report["Hash"][i]
        teststr = "SELECT `id` FROM `traffic` WHERE `hash`='%s'"
        curs = connectionToDB.cursor()
        curs.execute(teststr % hashstr)
        if curs.fetchone() != None:
            continue

        values = []
        for key in report_columns:
            val = list(report[key][i])
            if len(val) >= 255:
                val = val[:255]
            val.insert(0, '\'')
            val.insert(len(val), '\'')
            values.append(''.join(val))

        values = ', '.join(values)
        
        #print (columns_names)
        #print (values)
        #input()
        curs.execute(sqlstr % (columns_names, values))
    connectionToDB.commit()

def readReport(connectionToDB):
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
    "ContentType": [],
    "Hash" : []
    }

    curs = connectionToDB.cursor()
    curs.execute("SELECT %s FROM `traffic`" % columns_names)

    for row in curs:
        for row_key in row.keys():
            for col in report_columns:
                if col.lower() == row_key:
                    report[col].append(row[row_key])
    curs.close()

    return report