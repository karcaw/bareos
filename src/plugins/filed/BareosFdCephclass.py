#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Adapted from examples for ceph backup
#Copyright 2014 Battelle Memorial Institute
#Written by Evan Felix

from bareosfd import *
from bareos_fd_consts import *
import rados
from time import mktime,time
from  BareosFdPluginBaseclass import *
import BareosFdWrapper
import json
import cStringIO

_infopacketname = "----Ceph-Info-Packet----"

class BareosFdCephclass (BareosFdPluginBaseclass):
    '''
        Plugin for backing up all mysql databases found in a specific mysql server
    '''       
    def __init__(self, context, plugindef):
        DebugMessage(context, 100, "%s.__init__ called\n"%(self.__class__));
        BareosFdPluginBaseclass.__init__(self, context, plugindef)
        DebugMessage(context, 100, "%s.__init__ exiting: %s\n"%(self.__class__,self));

    def defopt(self,key,default):
        try:
            val = self.options[key]
        except KeyError:
            val = default
        return val

    def parse_plugin_definition(self,context, plugindef):
        '''
        '''
        BareosFdPluginBaseclass.parse_plugin_definition(self, context, plugindef)

        #connect to ceph and get an object iterator for the specified pool
        config = self.defopt("cephconf","/etc/ceph/ceph.conf")
        radosid = self.defopt("id","notbackup")
        self.pool = self.defopt("pool","data") 

        self.infos={}
        self.cluster = rados.Rados(conffile=config,rados_id=radosid)
        try:
            self.cluster.connect()
            self.ioctx = self.cluster.open_ioctx(self.pool)
            self.objects = self.ioctx.list_objects()
            #pre-load first object
            self.object = self.objects.next()
            return bRCs['bRC_OK'];
        except rados.PermissionError,msg:
            JobMessage(context, 10, "Permissions error during ceph connect:%s"%(msg));
            return bRCs['bRC_Error'] 

    def start_backup_file(self,context, savepkt):
        '''
        '''
        DebugMessage(context, 100, "start_backup called\n");
        if self.infos != self.object:
            ostat = self.object.stat()
            xattr = self.object.get_xattrs()
            otime = int(mktime(ostat[1]))
            size = ostat[0]
            DebugMessage(context, 100, "Object:"+str(self.object)+"\n")
            DebugMessage(context, 100, "Ostat:"+str(ostat)+"\n")
        
            objectinfo={}
            if xattr:
                xattrlist={}
                for xa in xattr:
                    xattrlist[xa[0]]=xa[1]
                    DebugMessage(context, 100, "XAttr:"+str(xa)+"\n")
                objectinfo["xattr"]=xattrlist
            self.infos[self.object.key]=objectinfo
            
            statp = StatPacket(mtime=otime,ctime=otime,atime=otime,size=size)
            savepkt.statp = statp
            savepkt.fname = "ceph:" + self.pool + ":" + self.object.key
            if self.since < otime:
                savepkt.type = bFileType['FT_REG']
            else:
                savepkt.type = bFileType['FT_NOCHG']
            DebugMessage(context, 100, "statp"+str(statp)+"\n");
            JobMessage(context, bJobMessageType['M_INFO'], "Starting backup of " + savepkt.fname + "\n");
        else:
            otime=int(time())
            self.object = cStringIO.StringIO(json.dumps(self.infos))
            statp = StatPacket(mtime=otime,ctime=otime,atime=otime,size=0)
            savepkt.statp = statp
            savepkt.fname = "ceph:" + self.pool + ":"+_infopacketname
            savepkt.type = bFileType['FT_REG']
            DebugMessage(context, 100, "writing info file"+str(statp)+"\n");
            self.infos={} # this terminates the backup
        return bRCs['bRC_OK'];

    def plugin_io(self, context, IOP):
        DebugMessage(context, 110, "plugin_io called with " + str(IOP) + "\n");

        if IOP.func == bIOPS['IO_OPEN']:
            return bRCs['bRC_OK']

        elif IOP.func == bIOPS['IO_READ']:
            IOP.buf = self.object.read(IOP.count)
            IOP.status = len(IOP.buf)
            IOP.io_errno = 0
            return bRCs['bRC_OK']
        
        elif IOP.func == bIOPS['IO_WRITE']:
            return bRCs['bRC_OK'];

        elif IOP.func == bIOPS['IO_CLOSE']:
            return bRCs['bRC_OK']
        
        elif IOP.func == bIOPS['IO_SEEK']:
            return bRCs['bRC_OK']
        
        else:
            DebugMessage(context,100,"plugin_io called with unsupported IOP:"+str(IOP.func)+"\n")
            return bRCs['bRC_OK']

    def end_backup_file(self, context):
        '''
        '''
        DebugMessage(context, 100, "end_backup_file() entry point in Python called\n")
        try:
            self.object = self.objects.next()
            return bRCs['bRC_More']
        except StopIteration:
            pass
        if self.infos:
            self.object = self.infos
            return bRCs['bRC_More']
        else:
            return bRCs['bRC_OK'];


# vim: ts=4 tabstop=4 expandtab shiftwidth=4 softtabstop=4
