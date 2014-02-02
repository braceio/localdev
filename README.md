localdev
==========

    usage: localdev [-h] [-f CONFIG] [-r RULES] [-p PORT] [-S SSLPORT] [-t TLD]
                    [-i IP] [-v] [-w]

    Turn-key DNS server and proxy for multi-domain development.

    optional arguments:
      -h, --help            show this help message and exit
      -f CONFIG, --config CONFIG
                            The config file where alias records are stored. Format of
                            the file is each line contains a source followed by a
                            destination. ex:
                            
                            myserver.dev 5000
                            *.myserver.dev 5001
                            
      -r RULES, --rules RULES
                            Comma separated list of SOURCE=DEST pairs where SOURCE is a
                            domain with optional wildcards, and DEST is a port. Wildcards
                            must be escaped if used on the command line. ex:
                            
                            localdev -r myserver.dev=5000,*.myserver.dev=5001
                            
      -p PORT, --port PORT  The port. (default 80)
      -S SSLPORT, --sslport SSLPORT
                            If set, will enable SSL testing on specified port.
      -t TLD, --tld TLD     The TLD used for local development. Default: 'dev'.
      -i IP, --ip IP        The IP to which local domains will be routed. Default: 
                            '127.0.0.1'.
      -v, --verbose         Print debug info to console.
      -w, --watch           Watch config file for changes.
      