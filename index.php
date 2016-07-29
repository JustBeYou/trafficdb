<!DOCTYPE html>
<head>
    <title>TrafficDB Report</title>
    <style>
        table, th, td {
            border: 1px solid black;
        }
    </style>
</head>

<?php
    // Change this line with your database username, password and IP
    $db = new PDO("mysql:host=localhost;dbname=trafficdb;charset=utf8", "root", "toor");
?>

<body>
    <a href="./index.php"><h3>Home</h3></a><br/>
    <center><h1>Traffic analysis report</h1></center><br/><br/>
    <?php
        if (isset($_GET['table'])) {
            $table_name = $_GET['table'];
             if (strpos($table_name, "traffic") !== false) {
                $columns = "id,currentdate,currenttime,sourcemac,destinationmac,sourceip,sourceport,destinationip,destinationport,iplength,ethertype,flagsandoptions,packetlength,contenttype,hash";

                if (isset($_GET['order'])) {
                    $result = $db->query("SELECT $columns FROM ".$table_name." ORDER BY ".$_GET['order']." ASC");
                } else {
                    $result = $db->query("SELECT $columns FROM ".$table_name);
                }

                if ($result->execute()) {
                    echo "<table>
    <tr>
        <th><a href=\"./index.php?table=".$table_name."&order=id\">ID</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=currentdate\">Date</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=currenttime\">Time</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=sourcemac\">Source MAC</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=destinationmac\">Destination MAC</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=sourceip\">Source IP</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=sourceport\">Source Port</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=destinationip\">Destination IP</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=destinationport\">Destination Port</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=iplength\">IP Length</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=ethertype\">Ethertype</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=flagsandoptions\">Flags and Options</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=packetlength\">Packet Length</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=contenttype\">Content Type</a></th>
        <th><a href=\"./index.php?table=".$table_name."&order=hash\">Hash</a></th>
    </tr>";

                    $rows = $result->fetchall(PDO::FETCH_ASSOC);
                    $col_names = explode(',', $columns);

                    foreach($rows as $row) {
                        echo "<tr>\n";
                        foreach($col_names as $col_name) {
                            echo "<td>".$row[$col_name]."</td>\n";
                        }
                        echo "</tr>";            
                    }
                    echo "</table>";
                } else {
                    echo '<tr><td>Crash!</td></tr>';
                }
             }
        } else {
            echo "<h3>Available reports are: </h3><br/>\n";
            echo "<ul>\n";
            $result = $db->query("show tables");
            while ($row = $result->fetch(PDO::FETCH_NUM)) {
                $table_name = $row[0];

                if (strpos($table_name, "traffic") !== false) {
                    $elems = explode("_", $table_name);

                    echo "<li><a href=\"./index.php?table=".$table_name."\">Report on interface ".$elems[1].", port ".$elems[2]." with IP filter ".$elems[3]."</a></li>\n";
                }
            }
            echo "</ul>\n";
        }
    ?>
</body>
</html>
