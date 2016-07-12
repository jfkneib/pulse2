# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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


import netifaces
import json
import subprocess
import sys, os, platform
import logging
import ConfigParser
import random
import re
import traceback, types
from pprint import pprint
import hashlib
from functools import wraps
import base64
from importlib import import_module

pathbase = os.path.abspath(os.curdir)

pathseelfplugins = os.path.join(pathbase, "pluginmaster")

sys.path.append(pathseelfplugins)

#import PluginRecvMuctest
if sys.platform.startswith('win'):
    import wmi
    import pythoncom
    import _winreg as wr
    import win32net
    import win32netcon
    import socket

def load_plugin(name):
    mod = __import__("plugin_%s" % name)
    return mod

def call_plugin(name, *args, **kwargs):
    pluginaction = load_plugin(name)
    pluginaction.action(*args, **kwargs)


#def load_plugin_recv(name):
    #mod = __import__("pluginrecv_%s" % name)
    #return mod

#def call_pluginrecv(name, *args, **kwargs):
    #pluginob = load_plugin_recv(name)
    #pluginob.action(*args, **kwargs)


#def include(filename):
    #if os.path.exists(filename): 
        #execfile(filename)

##def plugingrecever(class,msg):
    ##for element in os.listdir("%s/plugins/xmppmaster/master/lib/"%os.getcwd()):
        ##if element.startswith( 'PluginRecvMuc' ) and element.endswith(".py"):
            ##include("%s/plugins/xmppmaster/master/lib/%s"%(os.getcwd(),element))


#def import_from(module, name):
    #module = __import__(module, fromlist=[name])
    #return getattr(module, name)

def pathbase():
    return os.path.abspath(os.getcwd())

def pathscript():
    return os.path.abspath(os.path.join(pathbase(),"script"))

def pathplugins():
    return os.path.abspath(os.path.join(pathbase(),"plugins"))

def pathlib():
    return os.path.abspath(os.path.join(pathbase(),"lib"))

def pathscriptperl(name):
    return os.path.abspath(os.path.join(pathbase(),"script","perl",name))

def leplusfrequent(L):
    """Retourne l'élément le plus fréquent de la liste"""
    L.sort()  # pour que les éléments identiques soient assemblés
    n0, e0 = 0, None  # pour conserver le plus fréquent
    ep = None  # stocke l'élément distinct de la boucle précédente
    for e in L:
        if e != ep:  # si l'élément e a déjà été rencontré, on ne fait rien
            n = L.count(e)
            if n > n0:
                n0, e0 = n, e  # on stocke le nouvel élément le plus fréquent
            ep = e  # on stocke l'élément courant pour la boucle suivante
    return e0, n0

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

#windows
def get_connection_name_from_guid(iface_guids):
    iface_names = ['(unknown)' for i in range(len(iface_guids))]
    reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
    reg_key = wr.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
    for i in range(len(iface_guids)):
        try:
            reg_subkey = wr.OpenKey(reg_key, iface_guids[i] + r'\Connection')
            iface_names[i] = wr.QueryValueEx(reg_subkey, 'Name')[0]
        except :
            pass
    return iface_names


#x = netifaces.interfaces()
#pprint(get_connection_name_from_guid(x))

def CreateWinUser(login,Password,Groups=['Users']):
    # Controle si l'utilisateur existe
    try:
        d = win32net.NetUserGetInfo(None,login, 1)
        return
    except:
        pass
    d = {}
    d['name'] = Login
    d['password'] = Password
    d['comment'] = ''
    d['flags'] = win32netcon.UF_NORMAL_ACCOUNT | win32netcon.UF_SCRIPT | win32netcon.UF_PASSWD_CANT_CHANGE | win32netcon.UF_DONT_EXPIRE_PASSWD
    d['priv'] = win32netcon.USER_PRIV_USER
    ##d['home_dir'] = str(objuser['Home'])
    win32net.NetUserAdd(None, 1, d)
    #d = win32net.NetUserGetInfo(None, 'TestUser', 10)
    #d['full_name'] = objuser['FullName']
    #d = win32net.NetUserSetInfo(None, 'TestUser', 10, d)
    domain = win32api.GetDomainName()

    d = [{"domainandname" : domain+"\\"+login}]
    for gr in Groups:
        win32net.NetLocalGroupAddMembers(None, gr, 3, d)


def create_Win_user(username, password, full_name=None, comment=None):
    """
    Create a system user account for Rattail.
    """
    try:
        d = win32net.NetUserGetInfo(None, username, 1)
        return
    except:
        pass
    if not full_name:
        full_name = "{0} User".format(username.capitalize())
    if not comment:
        comment = "System user account for Rattail applications"
    win32net.NetUserAdd(None, 2, {
            'name': username,
            'password': password,
            'priv': win32netcon.USER_PRIV_USER,
            'comment': comment,
            'flags': (win32netcon.UF_NORMAL_ACCOUNT
                      | win32netcon.UF_PASSWD_CANT_CHANGE
                      | win32netcon.UF_DONT_EXPIRE_PASSWD),
            'full_name': full_name,
            'acct_expires': win32netcon.TIMEQ_FOREVER,
            })

    win32net.NetLocalGroupAddMembers(None, 'Users', 3, [
            {'domainandname': r'{0}\{1}'.format(socket.gethostname(), username)}])
  
    hide_user_account(username)
    return True

def isWinUserAdmin():
    if os.name == 'nt':
        import ctypes
        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            print "Admin check failed, assuming not an admin."
            return False
    elif os.name == 'posix':
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise RuntimeError, "Unsupported operating system for this module: %s" % (os.name,)

#mac OS
def isMacOsUserAdmin():
    obj=simplecommande("cat /etc/master.passwd")#pour linux "cat /etc/shadow")
    if int(obj['code']) == 0:
        return True
    else:
        return False

#listplugins = ['.'.join(fn.split('.')[:-1]) for fn in os.listdir(pathplugins) if fn.endswith(".py") and fn != "__init__.py"]
def name_random(nb, pref=""):
    a="abcdefghijklnmopqrstuvwxyz0123456789"
    d=pref
    for t in range(nb):
        d=d+a[random.randint(0,35)]
    return d

def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()




def getIpListreduite():
    listmacadress={}
    for i in netifaces.interfaces():
        addrs = netifaces.ifaddresses(i)
        try:
            if_mac = reduction_mac(addrs[netifaces.AF_LINK][0]['addr'])
            if_ip = addrs[netifaces.AF_INET][0]['addr']
            adresse = int(if_mac,16)
            if adresse != 0:
                listmacadress[adresse]= if_mac
        except :
            pass
    return listmacadress


def name_jid():
    dd = getIpListreduite()
    cc = dd.keys()
    cc.sort()
    return dd[cc[0]]

   
def reduction_mac(mac):
    mac=mac.lower()
    mac = mac.replace(":","")
    mac = mac.replace("-","")
    mac = mac.replace(" ","")
    #mac = mac.replace("/","")
    return mac

def is_valid_ipv4(ip):
    """Validates IPv4 addresses.
    """
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(ip) is not None

def is_valid_ipv6(ip):
    """Validates IPv6 addresses.
    """
    pattern = re.compile(r"""
        ^
        \s*                         # Leading whitespace
        (?!.*::.*::)                # Only a single whildcard allowed
        (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
        (?:                         # Repeat 6 times:
            [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
        ){6}                        #
        (?:                         # Either
            [0-9a-f]{0,4}           #   Another group
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            [0-9a-f]{0,4}           #   Last group
            (?: (?<=::)             #   Colon iff preceeded by exacly one colon
             |  (?<!:)              #
             |  (?<=:) (?<!::) :    #
             )                      # OR
         |                          #   A v4 address with NO leading zeros 
            (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            (?: \.
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            ){3}
        )
        \s*                         # Trailing whitespace
        $
    """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
    return pattern.match(ip) is not None



#linux systemd ou init
def typelinux():
    p = subprocess.Popen('cat /proc/1/comm',
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    code_result= p.wait()
    system=result[0].rstrip('\n')    
    """renvoi la liste des ip gateway en fonction de l'interface linux"""
    return system

def isprogramme(name):
    obj={}
    p = subprocess.Popen("which %s"%(name),
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code']=p.wait()
    obj['result']=result
    print obj['code']
    print obj['result']
    print obj
    if obj['result'] != "":
        return True
    else:
        return False

def simplecommande(cmd):
    obj={}
    p = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code']=p.wait()
    obj['result']=result
    return obj

def simplecommandestr(cmd):
    obj={}
    p = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code']=p.wait()
    obj['result']="\n".join(result)
    return obj


    
    
def servicelinuxinit(name,action):
    obj={}
    p = subprocess.Popen("/etc/init.d/%s %s"%(name,action),
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code']=p.wait()
    obj['result']=result
    return obj

#restart service
def service(name, action): #start | stop | restart | reload
    obj={}
    if sys.platform.startswith('linux'):
        system=""
        p = subprocess.Popen('cat /proc/1/comm',
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        result = p.stdout.readlines()
        code_result = p.wait()
        system = result[0].rstrip('\n')
        if system == "init":
            p = subprocess.Popen("/etc/init.d/%s %s"%(name,action),
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
            result = p.stdout.readlines()
            obj['code']=p.wait()
            obj['result']=result
        elif system == "systemd":
            p = subprocess.Popen("systemctl %s %s"%(action, name),
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
            result = p.stdout.readlines()
            obj['code']=p.wait()
            obj['result']=result
    elif sys.platform.startswith('win'):
        pythoncom.CoInitialize ()
        try:
            wmi_obj = wmi.WMI()
            wmi_sql = "select * from Win32_Service Where Name ='%s'"%name
            wmi_out = wmi_obj.query( wmi_sql )
        finally:
            pythoncom.CoUninitialize ()    
        for dev in wmi_out:
            print dev.Caption
        pass
    elif sys.platform.startswith('darwin'):
        pass
    return obj
 
#listservice()
#FusionInventory Agent
def listservice():
    pythoncom.CoInitialize ()
    try:
        wmi_obj = wmi.WMI()
        wmi_sql = "select * from Win32_Service"# Where Name ='Alerter'"
        wmi_out = wmi_obj.query( wmi_sql )
    finally:
        pythoncom.CoUninitialize ()
    for dev in wmi_out:
        print dev.Caption
        print dev.DisplayName

def joint_compteAD():
    ##https://msdn.microsoft.com/en-us/library/windows/desktop/aa392154%28v=vs.85%29.aspx
    pythoncom.CoInitialize ()
    try:
        c = wmi.WMI()
        for computer in c.Win32_ComputerSystem():
            if computer.PartOfDomain:
                print computer.Domain #DOMCD
                print computer.SystemStartupOptions
                computer.JoinDomainOrWorkGroup(domaine,password,login,group,3  )
    finally:
        pythoncom.CoUninitialize ()        

def windowsservice(name, action):
    pythoncom.CoInitialize ()
    try:
        wmi_obj = wmi.WMI()
        wmi_sql = "select * from Win32_Service Where Name ='%s'"%name
        print wmi_sql
        wmi_out = wmi_obj.query( wmi_sql )
    finally:
      pythoncom.CoUninitialize ()
    print len(wmi_out)
    for dev in wmi_out:
        print dev.caption
        if action.lower() == "start":
            dev.StartService()
        elif action.lower() == "stop":
            print dev.Name
            dev.StopService()
        elif action.lower() == "restart":
            dev.StopService()
            dev.StartService()
        else:
            pass        
 
 
#windowsservice("FusionInventory-Agent", "Stop")

def methodservice():
    import pythoncom
    import wmi
    pythoncom.CoInitialize ()
    try:
        c = wmi.WMI ()
        for method in c.Win32_Service._methods:
            print method  
    finally:
        pythoncom.CoUninitialize ()
        
def file_get_content(path):
    inputFile = open(path, 'r')     #Open test.txt file in read mode
    content = inputFile.read()
    inputFile.close()        
    return content

def file_put_content(filename, contents,mode="w"):
    fh = open(filename, mode)
    fh.write(contents)  
    fh.close()  

##windows
#def listusergroup():
    #import wmi
    #c = wmi.WMI()
    #for group in c.Win32_Group():
    #print group.Caption
    #for user in group.associators("Win32_GroupUser"):
        #print "  ", user.Caption




#decorateur pour simplifier les plugins
def pulginprocess(func):
    def wrapper( objetxmpp, action, sessionid, data, message, dataerreur):
        resultaction = "result%s"%action
        result={}
        result['action'] = resultaction
        result['ret'] = 0
        result['sessionid'] = sessionid
        result['base64'] = False
        result['data'] = {}
        dataerreur['action']=resultaction
        dataerreur['data']['msg'] = "ERROR : %s"%action
        dataerreur['sessionid'] = sessionid
        try:
            response = func( objetxmpp, action, sessionid, data, message, dataerreur, result)
            #encode  result['data'] si besoin
            print result
            if result['base64'] == True:
                result['data'] = base64.b64encode(json.dumps(result['data']))
            objetxmpp.send_message( mto=message['from'],
                                    mbody=json.dumps(result),
                                    mtype='chat')
        except:
            objetxmpp.send_message( mto=message['from'],
                                    mbody=json.dumps(dataerreur),
                                    mtype='chat')
            return
        return response
    return wrapper

# decorateur pour simplifier les plugins
# verifie session existe.
# pas de session end 
def pulginmaster(func):
    def wrapper( objetxmpp, action, sessionid, data, message, ret ):
        if action.startswith("result"):
            action = action[:6]
        if objetxmpp.session.isexist(sessionid):
            objsessiondata = objetxmpp.session.sessionfromsessiondata(sessionid)
        else:
            objsessiondata = None
        response = func( objetxmpp, action, sessionid, data, message, ret, objsessiondata)
        return response
    return wrapper



def pulginmastersessionaction( sessionaction, timeminute = 10 ):
    def decorateur(func):
        def wrapper(objetxmpp, action, sessionid, data, message, ret, dataobj):
            #avant
            if action.startswith("result"):
                action = action[6:]
            if objetxmpp.session.isexist(sessionid):
                if sessionaction == "actualise":
                    objetxmpp.session.reactualisesession(sessionid, 10)
                objsessiondata = objetxmpp.session.sessionfromsessiondata(sessionid)
            else:
                objsessiondata = None
            response = func( objetxmpp, action, sessionid, data, message, ret, dataobj, objsessiondata)
            if sessionaction == "clear" and objsessiondata != None:
                objetxmpp.session.clear(sessionid)
            elif sessionaction == "actualise":
                objetxmpp.session.reactualisesession(sessionid, 10)
            return response
        return wrapper
    return decorateur


def searchippublic(site = 1):
    if site == 1:
        try:
            page = urllib.urlopen("http://ifconfig.co/json").read()
            objip = json.loads(page)
            return objip['ip']
        except:
            return searchippublic(2)
    else:
        page = urllib.urlopen("http://www.monip.org/").read()
        ip = page.split("IP : ")[1].split("<br>")[0]
        return ip


