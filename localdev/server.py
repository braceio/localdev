import quickproxy
import os
import fnmatch
import devdns
from tornado import ioloop

from copy import copy

__all__ = ['run', 'configure']

routes = []

def split_host(host):

    name = ''
    port = None
    parts = host.split(':')

    if len(parts) > 1:
        name = parts[0]

    try:
        port = int(parts[-1])
    except ValueError:
        name = parts[-1]

    return name, port


def make_callbacks(routes):

    def req_callback(req):

        host = ''
        port = None

        # req.headers['Host']=req.host

        for src, dst in routes:
            if src[0] and fnmatch.fnmatch(req.host, src[0]):
                if src[1] and req.port != src[1]:
                    continue
                host = dst[0] or '127.0.0.1'
                port = dst[1] or 80 
                break

        if not host:
            body = 'No route for %s:%d' % (req.host, req.port)
            return quickproxy.ResponseObj(body=body, headers={'Content-Type': 'text/plain'})
        else:
            req.host, req.port = host, port

        # todo: deal with chunked transfer encoding headers

        return req


    def ssl_callback(req):
        req.port = 80
        req.protocol = 'http'
        req.headers.update({'x-forwarded-proto': 'https'})
        return req_callback(req)

    return req_callback, ssl_callback


def run(port, routes, sslport=None, dnsport=53, tld='dev', ip='127.0.0.1', verbose=False):

    req_callback, ssl_callback = make_callbacks(routes)

    dnsc = devdns.connect(port=dnsport)
    print 'devDNS :: *.%s. 60 IN A %s' % (tld, ip)

    mainloop = ioloop.IOLoop.instance()
    periodic = ioloop.PeriodicCallback(lambda : devdns.get_data(dnsc, tld, ip, verbose), 
                                       50.0, 
                                       io_loop=mainloop)
    periodic.start()

    all_methods = ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE', 'HEAD']
    quickproxy.run_proxy(port=port,
                         methods=all_methods, 
                         req_callback=req_callback,
                         debug_level=1 if verbose else 0,
                         start_ioloop=False)

    if sslport:
        # for ssl testing, run a second instance of the proxy on the ssl port
        quickproxy.run_proxy(port=sslport,
                             test_ssl=True,
                             methods=all_methods, 
                             req_callback=ssl_callback,
                             debug_level=1 if verbose else 0,
                             start_ioloop=False)

    try:
        print ("Starting HTTP proxy on port %d" % port)
        mainloop.start()
    except KeyboardInterrupt:
        dnsc.close()


def configure(routes=None, filename=None, watch=False):

    def load_routes():
        newroutes = []
        f = open(filename)
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                newroutes.append(map(split_host, parts))
            else:
                if parts:
                    print "Error, invalid route: %s" % line
        f.close()
        return newroutes

    if filename:
        routes = load_routes()
    elif routes:
        routes = [map(split_host, route) for route in routes]

    print "loaded %d routes" % len(routes)

    if watch and filename:
        from watchdog.observers import Observer
        from watchdog.events import PatternMatchingEventHandler

        class AliasWatcher(PatternMatchingEventHandler):
            def on_modified(self, event):
                routes[:] = load_routes()

        filename = os.path.normpath(os.path.abspath(filename))
        event_handler = AliasWatcher(patterns = [copy(filename)])
        observer = Observer()
        if not os.path.splitext(filename)[1]:
            filename = filename.rstrip('/') + '/'
        folder = os.path.split(filename)[0]
        observer.schedule(event_handler, path=folder, recursive=True)
        observer.start()

    return routes

