import sys, os, time, atexit, subprocess
from signal import SIGTERM
import databaseWrapper
import htmlReport

class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """

        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as e:
            err = str(e)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print (str(err))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """

class Tcpdump(Daemon):
    command_type_1 = "sudo tcpdump -tttt -en -l -i %s \"src port %s and net not %s/16\""
    command_type_2 = "sudo tcpdump -tttt -en -l -i %s \"src port %s\""
    command_type_3 = "sudo tcpdump -tttt -en -l -i %s"
    command = None
    conn = None
    log = None
    options = None

    def run(self):
        while True:
            self.conn = databaseWrapper.connectDB(self.options)
            self.log = open(self.options["log-path"], "a")
            proc = subprocess.Popen(self.command, shell = True, stdout = subprocess.PIPE)

            info = ' '.join(str(i) for i in os.uname())
            self.log.write("--- TRAFFICDB LOG FILE ---\n")
            self.log.write("%s\n\n\n" % info)
            self.log.write("[INFO] Start monitoring on interface %s, port %s.\n" % (self.options["interface"], self.options["port"]))
            self.log.write("[INFO] Tcpdump command: %s\n" % self.command)
            while True:
                line = proc.stdout.readline()
                if line != "":
                    entry = None
                    line = str(line)

                    #print (line)
                    try:
                        entry = htmlReport.getLineElements(line)
                        #print (entry)
                    except Exception as e:
                        self.log.write("[ERROR] Crashed on line %s.\n" % line)
                        self.log.write("Error: %s\n" % e)

                    if entry == None:
                        continue

                    try:
                        print ("Write entry: %s" % entry)
                        databaseWrapper.writeEntry(self.conn, entry, self.options["table"])
                    except Exception as e:
                        self.log.write("[ERROR] Database crashed on entry %s.\n" % entry)
                        self.log.write("[ERROR] Error: %s\n" % e)
                else:
                    self.log.write("[INFO] Process finished.\n")
                    break
            databaseWrapper.disconnectDB(self.conn)
            self.log.close()

    def setOptions(self, options):
        self.options = options

        if options["port"] == None and options["ip-filter"] == None:
            self.command = self.command_type_3 % (options["interface"])
        elif options["ip-filter"] == None:
            self.command = self.command_type_2 % (options["interface"], options["port"])
        else:
            self.command = self.command_type_1 % (options["interface"], options["port"], options["ip-filter"])
        
        print (self.command)

def startService(service, options):
    service.setOptions(options)
    service.start()

def stopService(service, options):
    service.stop()
