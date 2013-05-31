# -*- coding: utf-8; -*-
#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import logging

import twisted.web.server
import twisted.internet.error
import twisted.web.xmlrpc
from twisted.internet import reactor

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http # pyflakes.ignore

import pulse2.scheduler.config
import pulse2.xmlrpc

class SchedulerHTTPChannel(http.HTTPChannel):
    """
    We inherit from http.HTTPChannel to log incoming connections when the
    scheduler is in DEBUG mode, and to log connection errors.
    """

    def connectionMade(self):
        logger = logging.getLogger()
        logger.debug("Connection from %s" % (self.transport.getPeer().host,))
        http.HTTPChannel.connectionMade(self)

    def connectionLost(self, reason):
        if not reason.check(twisted.internet.error.ConnectionDone):
            logger = logging.getLogger()
            logger.error(reason)
        http.HTTPChannel.connectionLost(self, reason)

class SchedulerSite(twisted.web.server.Site):
    protocol = SchedulerHTTPChannel

class SchedulerProxy(twisted.web.xmlrpc.Proxy):

    def __init__(self, url, user=None, password=None):
        twisted.web.xmlrpc.Proxy.__init__(self, url, user, password)
        self.SSLClientContext = None

    def setSSLClientContext(self, SSLClientContext):
        self.SSLClientContext = SSLClientContext

    def callRemote(self, method, *args):
        factory = self.queryFactory(
            self.path, self.host, method, self.user,
            self.password, self.allowNone, args)
        d = factory.deferred
        if self.secure:
            from twisted.internet import ssl
            if not self.SSLClientContext:
                self.SSLClientContext = ssl.ClientContextFactory()
            reactor.connectSSL(self.host, self.port or 443,
                               factory, self.SSLClientContext)
        else:
            reactor.connectTCP(self.host, self.port or 80, factory)
        return d

def getProxy(url):
    """
    Return a suitable SchedulerProxy object to communicate with launchers
    """
    if url.startswith("http://"):
        ret = twisted.web.xmlrpc.Proxy(url)
    else:
        config = pulse2.scheduler.config.SchedulerConfig()
        if config.verifypeer:
            # We have to build the SSL context to include scheduler
            # certificates
            ctx = pulse2.xmlrpc.OpenSSLContext().getContext()
            ret = SchedulerProxy(url)
            ret.setSSLClientContext(ctx)
        else:
            ret = twisted.web.xmlrpc.Proxy(url)
    return ret
