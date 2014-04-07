#!/usr/bin/env python
'''
Created on 31-May-2013

@author: Anil Kumar (anilkumar.s@paxterrasolutions.com)


    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.        


RamCloudCliDriver is the basic driver which will handle the RamCloud server functions
'''

import pexpect
import struct
import fcntl
import os
import signal
import re
import sys
import core.teston
import time

sys.path.append("../")
from drivers.common.clidriver import CLI

class RamCloudCliDriver(CLI):
    '''
RamCloudCliDriver is the basic driver which will handle the RamCloud server functions
    '''
    def __init__(self):
        super(CLI, self).__init__()
        self.handle = self
        self.wrapped = sys.modules[__name__]

    def connect(self, **connectargs):
        # Here the main is the TestON instance after creating all the log handles.
        self.port = None
        for key in connectargs:
            vars(self)[key] = connectargs[key]       
        self.home = "~/ONOS"
        for key in self.options:
           if key == "ONOShome":
               self.home = self.options['ONOShome']
               break

        
        self.name = self.options['name']
        self.handle = super(RamCloudCliDriver, self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd, home = self.home)
        
        self.ssh_handle = self.handle
        if self.handle :
            return main.TRUE
        else :
            main.log.error(self.name+": Connection failed to the host "+self.user_name+"@"+self.ip_address) 
            main.log.error(self.name+": Failed to connect to the Onos system")
            return main.FALSE
   
 
    def start_serv(self):
        '''
        This Function will start RamCloud Servers
        '''
        main.log.info(self.name+": Starting RAMCloud Server" )
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline(self.home + "/onos.sh rc-server start")
        self.handle.expect("onos.sh rc-server start")
        self.handle.expect("\$")
        response = self.handle.before + self.handle.after
        print ("RESPONSE IS: "+response)
        time.sleep(5)
        if re.search("Killed\sexisting\process", response):
            main.log.info(self.name + ": Previous RAMCloud killed. ")
            if re.search("Starting\sRAMCloud\sserver",response):
                main.log.info(self.name + ": RAMCloud Server Started")
                return main.TRUE
            else:
                main.log.info(self.name + ": Failed to start RAMCloud Server"+response)
                return main.FALSE
        if re.search("Starting\sRAMCloud\sserver",response):
             main.log.info(self.name + ": RAMCloud Server Started")
             return main.TRUE
         else:
            main.log.info(self.name + ": Failed to start RAMCloud Server"+response)
            return main.FALSE

 
    def start_coor(self):
        '''
        This Function will start RamCloud
        '''
        main.log.info(self.name+": Starting RAMCloud Coordinator" )
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline(self.home + "/onos.sh rc-coord start")
        self.handle.expect("onos.sh rc-coord start")
        self.handle.expect("\$")
        response = self.handle.before + self.handle.after
        if re.search("Starting\sRAMCloud\scoordinator\s", response):
            if re.search("Killed\sexisting\sprocess", response):
                main.log.warn(self.name+": Process was already running, killing existing process")
            main.log.info(self.name+": RAMCloud Coordinator Started ")
            return main.TRUE
        else:
            main.log.error(self.name+": Failed to start RAMCloud Coordinator"+ response)
            return main.FALSE

    def status_serv(self):
        '''
        This Function will return the Status of the RAMCloud
        '''
        time.sleep(5)
        self.execute(cmd="\n",prompt="\$",timeout=10)
        response = self.execute(cmd=self.home + "/onos.sh rc-server status ",prompt="\d+\sramcloud\sserver\srunning(.*)",timeout=10)
        

        self.execute(cmd="\n",prompt="\$",timeout=10)
        return response
        
        if re.search("0\sRAMCloud\sserver\srunning(.*)") :
            main.log.info(self.name+": RAMCloud not running")
            return main.TRUE
        elif re.search("1\sRAMCloud\sserver\srunning(.*)"):
            main.log.warn(self.name+": RAMCloud Running")
            return main.TRUE
        else:
            main.log.info( self.name+":  WARNING: status recieved unknown response")
            return main.FALSE
            
    def status_coor(self):
        '''
        This Function will return the Status of the RAMCloud
        '''
        self.execute(cmd="\n",prompt="\$",timeout=10)
        response = self.execute(cmd=self.home + "/onos.sh rc-coord status ",prompt="\d+\sRAMCloud\scoordinator\srunning",timeout=10)
        self.execute(cmd="\n",prompt="\$",timeout=10)
        #return response
        
        if re.search("0\sRAMCloud\scoordinator\srunning", response) :
            main.log.warn(self.name+": RAMCloud Coordinator not running")
            return main.TRUE
        elif re.search("1\sRAMCloud\scoordinator\srunning", response):
            main.log.info(self.name+": RAMCloud Coordinator Running")
            return main.TRUE
        else:
            main.log.warn( self.name+": coordinator status recieved unknown response")
            return main.FALSE

    def stop_serv(self):
        '''
        This Function will stop the RAMCloud if it is Running
        ''' 
        self.execute(cmd="\n",prompt="\$",timeout=10)
        time.sleep(5)
        response = self.execute(cmd=slef.home + "/onos.sh rc-server stop ",prompt="Killed\sexisting\sprocess(.*)",timeout=10)
        self.execute(cmd="\n",prompt="\$",timeout=10)
        if re.search("Killed\sexisting\sprocess(.*)",response):
            main.log.info("RAMCloud Server Stopped")
            return main.TRUE
        else:
            main.log.warn(self.name+": RAMCloud is not Running")
            return main.FALSE
           

    def stop_coor(self):
        '''
        This Function will stop the RAMCloud if it is Running
        ''' 
        self.execute(cmd="\n",prompt="\$",timeout=10)
        time.sleep(5)
        response = self.execute(cmd=self.home + "/onos.sh rc-coord stop ",prompt="Killed\sexisting\sprocess",timeout=10)
        self.execute(cmd="\n",prompt="\$",timeout=10)
        if re.search("Killed\sexisting\sprocess",response):
            main.log.info(self.name+": RAMCloud Coordinator Stopped")
            return main.TRUE
        else:
            main.log.warn(self.name+": RAMCloud was not Running")
 
    def disconnect(self):
        ''' 
        Called at the end of the test to disconnect the ssh handle. 
        ''' 
        response = ''
        if self.handle:
            self.handle.sendline("exit")
            self.handle.expect("closed")
        else :
            main.log.error("Connection failed to the host when trying to disconnect from RAMCloud component")
            response = main.FALSE
        return response 
