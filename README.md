# TrafficDB
TrafficDB is a console application that analyze output from `tcpdump` and
store it to a database.

## Installition and prerequisites
You can install TrafficDB by running following commands:
```
cd /usr/local/bin
sudo ln -s /full/path/to/trafficdb.py trafficdb
```
Now you can run `trafficdb` in your console.

Before using TrafficDB, you need to have installed on your computer
following software:
- Linux Distro
- Python 3.x
- Pip
- PyMySql

## Tehnical documentation
TrafficDB is formed of 3 modules:
- HTML Report Generator (htmlReport)
- System Wrapper (systemWrapper)
- Database Wrapper (databaseWrapper)

**HTML Report Generator**
It has 4 functions:
- readLogFile
- getLineElements
- generateHTMLReport
- generateIndexFile

`readLogFile` function opens log file and parse each output line of `tcpdump`
using `getLineElements`.
`generateHTMLReport` take as parameters a dictionary of `tcpdump` parsed output
and generate a HTML table in a file with name taken from parameters.
`generateIndexFile` takes a list of report files and create a index for them.
After, it place the index in the apache directory and you can see it at localhost.

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
It has 4 functions:
- connectDB
- disconnectDB
- writeReport
- readReport

`connectDB` and `disconnectDB` creates and destroys database connection object.

`writeReport` writes a report to database. (it checks each element if already 
exists using hashing)
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
mac-addr: *mac address to monitorize* (optional)
port: *port to monitorize* (optional)
```
Optional configuration can be omitted as it has a default value.

After you have a configuration file, you can start monitorizing by:
`sudo trafficdb -c /path/to/trafficdb.conf -s`
*It is recommanded to use sudo.*

You can stop service by:
`sudo trafficdb -c /path/to/trafficdb.conf -k`

If you want to register logs into database you could use:
`sudo trafficdb -c /path/to/trafficdb.conf -rg`

At last, if you need to generate a report:
`sudo trafficdb -c /path/to/trafficdb.conf -r`
*If log file isn't found, it will try to generate report from databse.*

**Configuration file is set by `-c` option.**
**You can omit it and set other options using command line arguments.**
**Other command line arguments can be found using `trafficdb --help`.**

## Bug report
If you find any bug or problem, mail me at anonimatanonimus@gmail.com.
