localdev
==========

A command line tool that maps development domains (like *.myserver.dev) to a 
set of servers running on localhost. This tool was built to dramatically reduce 
the pain of setting up multi-domain local development. It takes the place of a 
DNS server like Bind or dnsmasq, and a webserver like Apache or Nginx. 

With localdev you can stop fussing with /etc/hosts and configuration files. 
Instead, hook-up your development servers with a single command.

## Use

    sudo localdev --rules "niftythings.dev=5000, api.niftythings.dev=5001, *.niftythings.dev=5002"

In the above example, three servers are running on localhost: a webserver on 
port 5000, an api server on 5001 and a proxy for customer apps on port 5002. 
Localdev routes web requests to the three servers using the specified domains.

Sudo is required if you use the default ports 53, 80 or 443 for handling DNS, 
HTTP or SSL traffic. 

## Installation

For non python developers, using a mac or linux:

    sudo easy_install localdev

For python people:

    pip install localdev

Also you'll want to add localhost (127.0.0.1) to the top of your DNS server 
list. I recommend adding google's DNS addresses (8.8.8.8 and 8.8.4.4) as backup 
servers.

![](http://raw.github.com/colevscode/devdns/master/dnsconfig.png)

## Under the hood

Localdev doesn't touch your system configuration. It's entirely contained 
within a single process.

When launched, localdev starts two services: a local DNS server that maps a TLD 
(like .dev) to localhost, and a reverse proxy that routes HTTP requests to your 
servers. 

The DNS is a lightweight server based on [devdns](https://github.com/colevscode/devdns). 
The reverse proxy is based on [quickproxy](https://github.com/colevscode/quickproxy), 
which is itself built on [Tornado](http://http://www.tornadoweb.org/).

## Usage Reference

    usage: localdev [-h] [-f CONFIG] [-r RULES] [-p PORT] [-t TLD] [-i IP]
                    [-S SSLPORT] [-D DNSPORT] [-v] [-w]

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
      -t TLD, --tld TLD     The TLD used for local development. Default: 'dev'.
      -i IP, --ip IP        The IP to which local domains will be routed. Default: 
                            '127.0.0.1'.
      -S SSLPORT, --sslport SSLPORT
                            If set, will enable SSL testing on specified port.
      -D DNSPORT, --dnsport DNSPORT
                            The port for DNS. (default 53)
      -v, --verbose         Print debug info to console.
      -w, --watch           Watch config file for changes. (requires 
                            watchdog to be installed)
