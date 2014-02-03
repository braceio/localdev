localdev
==========

A command line tool that maps development domains (like *.myserver.dev) to a 
set of servers running on localhost. This tool was built to dramatically reduce 
[the pain](http://mikeferrier.com/2011/04/04/setting-up-wildcard-dns-on-localhost-domains-on-osx/) 
of setting up multi-domain local development. It takes the place of a DNS 
server like Bind or dnsmasq, and a reverse proxy like Apache or Nginx. 

With localdev you can stop fussing with /etc/hosts and configuration files. 
Instead, hook-up your development servers with a single command.

## Use

    sudo localdev --rules "niftythings.dev=5000, api.niftythings.dev=5001, *.niftythings.dev=5002"

In the above example, three servers are running on localhost: a webserver on 
port 5000, an api server on 5001 and a server hosting customer content on port 5002. 
Localdev routes web requests to the three servers by matching the hostname of 
each request to a rule, and proxying the request to the corresponding port.

By default requests are routed to localhost. You can also route traffic to a 
server running elsewhere, such as on your LAN:

    sudo localdev --rules "*.here.dev=5000, *.there.dev=192.168.1.10:5000"

Sudo is required if you use the default ports 53 and 80 for handling DNS and 
HTTP traffic. To run without sudo, you'd need to provide alternative ports, 
which is pretty normal for HTTP, but setting up DNS on a port other than 53 is
pretty weird. See the [reference](#ref) on option -D if this is important.

## Under the hood

Localdev doesn't touch your system configuration. It's entirely contained 
within a single process.

When launched, localdev starts two services: a local DNS server that maps a TLD 
(like .dev) to localhost, and a reverse proxy that routes HTTP requests to your 
servers based on the configuration rules.

The DNS is a lightweight server based on [devdns](https://github.com/colevscode/devdns). 
The reverse proxy is based on [quickproxy](https://github.com/colevscode/quickproxy), 
which is itself built on [Tornado](http://http://www.tornadoweb.org/).

## Installation

For non python developers, using a mac or linux:

    sudo easy_install localdev

For python people:

    pip install localdev

### Set localhost as your primary DNS server <a name="dnslist"></a>

In order for localdev to work, your browser needs to use it for DNS resolution.
This requires putting localhost (127.0.0.1) at the top of your system-wide DNS 
server list. I recommend also adding Google's DNS addresses (8.8.8.8 and 
8.8.4.4) as backup servers (since localdev isn't a general DNS server).

To do this on a Mac, open System Preferences and open the Network pane. On the 
left side, select the network adapter you use (most likely your wireless 
adapter), and then click Advanced. Under the DNS tab, click the + button under 
the DNS Servers list, and add 127.0.0.1, 8.8.8.8 and 8.8.4.4 in that order. 
Click OK, then click Apply.

![](http://raw.github.com/colevscode/devdns/master/dnsconfig.png)

## Troubleshooting (Mac)

If DNS was simple, this tool wouldn't be valuable. Unfortunately that also 
means that it's difficult to make a DNS tool that works out of the box for 
everyone. Here are some things you can check if localdev doesn't work on the  
first try:

- Use `dig` to see if localdev correctly resolves your domain name to 127.0.0.1
      
      dig mycoolsite.dev

  You should see something like:

      # dig mysite.dev
      ; <<>> DiG 9.8.3-P1 <<>> mysite.dev
      ;; global options: +cmd
      ;; Got answer:
      ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 55138
      ;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

      ;; QUESTION SECTION:
      ;mysite.dev.            IN  A

      ;; ANSWER SECTION:
      mysite.dev.     60  IN  A   127.0.0.1

      ;; Query time: 31 msec
      ;; SERVER: 127.0.0.1#53(127.0.0.1)
      ;; WHEN: Sun Feb  2 21:44:45 2014
      ;; MSG SIZE  rcvd: 44
  
  If there's no ANSWER SECTION, make sure you've correctly configured your 
  [dns server list](#dnslist).

- Use `curl -v mysite.dev` to see if there's an error. Depending on the error, 
  you can try a few things:

  - `curl: (6) Could not resolve host: mysite.dev`

    In this case, try flushing the dns cache and restarting mDNSResponder:

        dnscacheutil -flushcache
        sudo killall -HUP mDNSResponder

    If that doesn't work, unload and reload mDNSResponder:

        sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.mDNSResponder.plist
        sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.mDNSResponder.plist

    More discussion [here](http://apple.stackexchange.com/questions/26616/dns-not-resolving-on-mac-os).

  - `curl: (52) Empty reply from server`

    See the discussion below about previous installations.

- If you previously configured your mac with Bind or dnsmasq, you'll have to 
  disable those services. 

  Unload bind:

      sudo launchctl unload -w /System/Library/LaunchDaemons/org.isc.named.plist

  probably something similar for dnsmasq.

- If you're forwarding port 80 to a non restricted port, like 8080, with ipfw 
  or pf, that could also be a problem. Try running localdev using that port:

      localdev -r mysite.dev=5000 -p 8080

  Generally, check your firewall settings to ensure that HTTP traffic can get 
  to localdev.

## Usage Reference <a name="ref"></a>

    usage: localdev [-h] [-f CONFIG] [-r RULES] [-p PORT] [-t TLD] [-i IP]
                    [-S SSLPORT] [-D DNSPORT] [-v] [-w]

    Turn-key DNS server and proxy for multi-domain development.

    optional arguments:
      -h, --help            show this help message and exit
      -f CONFIG, --config CONFIG
                            The config file where proxy rules are stored. Format of
                            the file is each line contains a source followed by a
                            destination host:port. (localhost is the default 
                            destination host) ex:
                            
                            myserver.dev localhost:5000
                            *.myserver.dev 5001
                            
      -r RULES, --rules RULES
                            Comma separated list of SOURCE=DEST pairs where SOURCE is a
                            domain with optional wildcards, and DEST is a host:port. 
                            (localhost is the default destination host) ex:
                            
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
