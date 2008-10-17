# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from mmc.agent import PluginManager
from mmc.support.mmctools import shLaunch
import mmc.support.mmctools
import logging
import glob
import os
import re
import imp
import time
import datetime
import exceptions
from bool_equations import BoolRequest
from mmc.plugins.base.computers import ComputerManager
from mmc.support.mmctools import xmlrpcCleanup
from mmc.support.config import PluginConfig
from ConfigParser import NoOptionError

from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.support.mmctools import Singleton

class QueryManager(Singleton):
    """
    MMC Query manager.

    Query all plugins to know if they can query things.
    """
    
    def activate(self):
        self.logger = logging.getLogger()

        os.chdir(os.path.dirname(mmc.support.mmctools.__file__) + '/..')
        
        # hash{ pluginName:module }
        self.queryablePlugins = self._getQueryablePlugins()

        # list[ possibilities ]
        self.queryPossibilities = {}
        for pluginName in self.queryablePlugins:
            module = self.queryablePlugins[pluginName]
            self.queryPossibilities[pluginName] = self._getPluginQueryPossibilities(module)
    
    def _getQueryablePlugins(self):
        """
        Check in existing plugins which one support the query manager
        """
        pm = PluginManager()
        ret = {}

        for plugin in pm.getEnabledPluginNames():
            if os.path.exists(os.path.join('plugins/', plugin, 'querymanager', '__init__.py')):
                self.logger.debug("QueryManager is trying to load plugin "+plugin)
                f, p, d = imp.find_module('querymanager', [os.path.join('plugins/', plugin)])
                try:
                    mod = imp.load_module(plugin+'_querymanager', f, p, d)
                    func = getattr(mod, 'activate')
                    if func():
                        ret[plugin] = mod
                        self.logger.info('QueryManager plugin ' + plugin + ' loaded')
                    else:
                        self.logger.info('QueryManager plugin '+ plugin+ ' is disabled by configuration.')
                    
                except Exception,e:
                    self.logger.exception(e)
                    self.logger.error('QueryManager plugin '+ plugin+ " raise an exception.\n"+ plugin+ " not loaded.")
                    continue
        return ret

    def _getPluginQueryPossibilities(self, pluginModule):
        func = getattr(pluginModule, 'queryPossibilities')
        return func()

    def _getPluginReplyToQuery(self, ctx, pluginModule, query):
        func = getattr(pluginModule, 'query')
        return func(ctx, query[0], query[1])

    def getQueryPossibilities(self, ctx):
        return self.queryPossibilities

    def getPossiblesModules(self, ctx):
        return self.queryPossibilities.keys()
    
    def getPossiblesCriterionsInModule(self, ctx, moduleName):
        try:
            return self.queryPossibilities[moduleName].keys()
        except:
            self.logger.error("Dyngroup module %s don't exists"%(moduleName))
            return []

    def getTypeForCriterionInModule(self, ctx, moduleName, criterion):
        ret = self.queryPossibilities[moduleName][criterion]
        return ret[0]
        
    def getPossiblesValuesForCriterionInModule(self, ctx, moduleName, criterion, value = ''):
        ret = self.queryPossibilities[moduleName][criterion]
        if len(ret) == 3:
            if len(value) < ret[2]:
                return [ret[0], []]
        return [ret[0], ret[1](ctx, value)]

    def replyToQuery(self, ctx, query, bool = None, min = 0, max = 10):
        return self._replyToQuery(ctx, query, bool)[int(min):int(max)]

    def replyToQueryLen(self, ctx, query, bool = None):
        return len(self._replyToQuery(ctx, query, bool))
        
    def __recursive_query(self, ctx, query):
        op = query[0]
        ret = []
        for q in query[1]:
            if len(q) == 4:
                qid, module, criterion, value = q
                val, neg = self._getPluginReplyToQuery(
                        ctx,
                        self.queryablePlugins[module],
                        [criterion, value]
                )
            else:
                ret += [[mmc.plugins.dyngroup.replyToQuery(ctx, q, 0, -1), True]]
        return (self.__treat_query(op, ret))
    
    def _replyToQuery(self, ctx, query, bool = None):
        raise "DON'T USE _replyToQuery!!!"
        ret = self.__recursive_query(ctx, query)
        
        values = {}
        values_neg = {}

        # TODO does not seems to work...
        #['AND', [['1', 'dyngroup', 'groupname', 'test']]]
        for qid, module, criterion, value in query:
            val, neg = self._getPluginReplyToQuery(
                ctx,
                self.queryablePlugins[module],
                [criterion, value]
            )
            values[str(qid)] = [val, neg]
                
        self.logger.debug(values)

        br = BoolRequest()
        if bool == None or bool == '' or bool == 0 or bool == '0':
            bool = 'AND('+','.join(map(lambda a:a[0][0], values))+')'


        all = ComputerManager().getComputersList(ctx)
        #all = ComputerManager().getRestrictedComputersList(ctx, 0, 50)
        # for the moment everything is based on names... should be changed into uuids
        #all = map(lambda a: a[1]['cn'][0], all.values())
        all = all.keys()
        values['A'] = [all, True]

        bool = 'AND(A, '+bool+')'

        br.parse(bool)
        if bool == None or not br.isValid(): # no bool specified = only AND
            if len(values.keys()) > 0:
                retour = values.pop()
                for val in values:
                    neg = val[1]
                    val = val[0]
                    if neg:
                        retour = filter(lambda a,val=val:a in val, retour)
                    else:
                        retour = filter(lambda a,val=val:a not in val, retour)

                return retour
            else:
                return [] # TODO : when plugged on Machines : should return : Machine - values_neg
        else:
            retour = br.merge(values)
            return retour[0]

    def replyToQueryXML(self, ctx, query, bool = None, min = 0, max = 10):
        return self._replyToQueryXML(ctx, query, bool)[int(min):int(max)]
        
    def replyToQueryXMLLen(self, ctx, query, bool = None):
        return len(self._replyToQueryXML(ctx, query, bool))
        
    def _replyToQueryXML(self, ctx, query, bool = None):
        values = {}
        values_neg = {}
        for qid, module, criterion, value in query:
            val, neg = self._getPluginReplyToQuery(
                ctx,
                self.queryablePlugins[module],
                [criterion, value]
            )
            values[str(qid)] = [val, neg]
                
        self.logger.debug(values)

        br = BoolRequest()
        if bool == None or bool == '':
            bool = "<AND><p>"+('</p><p>'.join(map(lambda a:a[0][0], values)))+"</p></AND>"

        all = ComputerManager().getComputersList(ctx)
        # for the moment everything is based on names... should be changed into uuids
        all = map(lambda a: a[1]['cn'][0], all)
        values['A'] = [all, True]

        bool = '<AND><p>A</p><p>'+bool+'</p></AND>'

        br.parseXML(bool)
        if bool == None or not br.isValid(): # no bool specified = only AND
            if len(values.keys()) > 0:
                retour = values.pop()
                for val in values:
                    neg = val[1]
                    val = val[0]
                    if neg:
                        retour = filter(lambda a,val=val:a in val, retour)
                    else:
                        retour = filter(lambda a,val=val:a not in val, retour)

                return retour
            else:
                return [] # TODO : when plugged on Machines : should return : Machine - values_neg
        else:
            retour = br.merge(values)
            return retour[0]

    def getQueryTree(self, query, bool = None):
        if type(query) != list:
            query = self.parse(query)

        values = {}

        for qid, module, criterion, value in query:
            values[str(qid)] = [qid, module, criterion, value]
            
        br = BoolRequest()
        if bool == None or bool == '' or bool == 0 or bool == '0': # no bool specified = only AND
            bool = 'AND('+','.join(map(lambda a:a, values))+')'

        br.parse(bool)
        if not br.isValid(): # invalid bool specified = only AND
            bool = 'AND('+','.join(map(lambda a:a, values))+')'
            br.parse(bool)                                     
            
        return br.getTree(values)
            
    def parse(self, query):
        p1 = re.compile('\|\|')
        p2 = re.compile('::')
        p3 = re.compile('==')
        p4 = re.compile(', ')
        queries = p1.split(query)
        ret = []
        for q in queries:
            a = p2.split(q)
            b = p3.split(a[0])
            c = p3.split(a[1])
            val = p4.split(c[1])
            if len(val) == 1:
                val = val[0]
            ret.append([b[0], b[1], c[0], val])
        return ret
    
def getAvailablePlugins(path):
    """
    Fetch all available MMC plugin

    @param path: UNIX path where the plugins are located
    @type path: str

    @return: list of all .py in a path
    @rtype: list
    """
    ret = []
    for item in glob.glob(os.path.join(path, "*", "__init__.py")):
        ret.append(item.split("/")[1])
    return ret
 
