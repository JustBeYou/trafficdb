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
    <center><h1>Traffic analysis report</h1></center><br/><br/>
    <?php
        if (isset($_GET['table'])) {
            $table_name = $_GET['table'];
             if (strpos($table_name, "traffic") !== false) {
                $columns = "id,currentdate,currenttime,sourcemac,destinationmac,sourceip,sourceport,destinationip,destinationport,iplength,ethertype,flagsandoptions,packetlength,contenttype,hash";

                $result = $db->query("SELECT $columns FROM ".$table_name);
        
                if ($result->execute()) {
                    echo "<table>
    <tr>
        <th>ID</th>
        <th>Date</th>
        <th>Time</th>
        <th>Source MAC</th>
        <th>Destination MAC</th>
        <th>Source IP</th>
        <th>Source Port</th>
        <th>Destination IP</th>
        <th>Destination Port</th>
        <th>IP Length</th>
        <th>Ethertype</th>
        <th>Flags and Options</th>
        <th>Packet Length</th>
        <th>Content Type</th>
        <th>Hash</th>
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
