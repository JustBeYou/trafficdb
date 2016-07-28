# TrafficDB
TrafficDB is a console application that analyze output from `tcpdump` and
store it to a database.

## Installition and prerequisites
You can install TrafficDB by running following commands:
```
chmod +x /full/path/to/trafficdb.py
cd /usr/local/bin
sudo ln -s /full/path/to/trafficdb.py trafficdb
```
Now you can run `trafficdb` in your console.

Before using TrafficDB, you need to have installed on your computer
following software:
- Linux Distro
- MySQL Server
- Apache Server
- PDO PHP Module
- Python 3.x
- Pip
- PyMySql

## Tehnical documentation
TrafficDB is formed of 3 modules:
- HTML Report Generator (htmlReport)
- System Wrapper (systemWrapper)
- Database Wrapper (databaseWrapper)

**HTML Report Generator**

It has 2 functions:
- getLineElements
- generatePHPindex

`getLineElements` split output lines from `tcpdump` and return a dictionary
with its content.
`generatePHPindex` generate report files into apache html folder.

**System Wrapper**

It has 2 classes:
- Daemon
- Tcpdump (child of Daemon)

And 2 functions:
- startService
- stopService

`Daemon` is a wrapper class for forking a process to background.
`Tcpdump` is a child of `Daemon` that forks `tcpdump` to background.

`startService` and `stopService` just starts and stops the service :)

**Database Wrapper**

It has 5 functions:
- connectDB
- disconnectDB
- writeReport
- readReport
- writeEntry

`connectDB` and `disconnectDB` creates and destroys database connection object.

`writeReport` writes a report to database. (it checks each element if already 
exists using hashing)
`writeEntry` writes a single row to the database.
`readReport` loads databse in a dictionary.

**TrafficDB main file**

Main file has just a main function that takes command line arguments and parse
them. After it loads configuration file if it needs.
It uses all modules to analyze and parse `tcpdump`, register into database and
generate reports using database and logfiles.

## How to use?
If you want to run TrafficDB, first you need to write a configuration file:

**trafficdb.conf**
```
apache-path: */path/to/http/folder/of/apache* (optional)
interface: *network interface name*
log-path: */full/path/to/log/file* (optional)
mysql-user: *username of database*
mysql-password: *password of database*
ip-filter: *ip to filter by* (optional)
port: *port to monitorize* (optional)
```
Optional configuration can be omitted as it has a default value.

After you have a configuration file, you can start monitorizing by:
`sudo trafficdb -c /path/to/trafficdb.conf -s`
*It is recommanded to use sudo.*

You can stop service by:
`sudo trafficdb -c /path/to/trafficdb.conf -k`

You can start multiple times `trafficdb` if you use different configurations
for it. For example, if you have two configuration files: `trafficdb_80.conf`
and `trafficdb_443.conf`, first is to monitorize port 80 and second for port
443, you can run two different processes of `trafficdb`:

`sudo trafficdb -c /path/to/trafficdb_80.conf -s`

`sudo trafficdb -c /path/to/trafficdb_443.conf -s`

If you want to kill them, you need to run `trafficdb` with same configurations, 
but with `-k` option, like `sudo trafficdb -c /path/to/trafficdb_80.conf -k`.

Reports can be found at http://localhost/. Here you will see a list of all
reports generated.

Debug informations can be found into the log you selected in configuration
(`/home/trafficdb.log` by default) and`/var/trafficdb_err.txt` for other errors.
**Configuration file is set by `-c` option.**
**You can omit it and set other options using command line arguments.**
**Other command line arguments can be found using `trafficdb --help`.**

## Bug report
If you find any bug or problem, mail me at anonimatanonimus@gmail.com.
