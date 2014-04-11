#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
###
# Application: adb_controller
# File:        adb_controller.py
# Description: Android Debugging Bridge Controller
# Copyright (c) 2014 Wayne Moulden <http://www.mameau.com>
###
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
import os, sys
import cherrypy
import webbrowser
import subprocess
import re

# Doesn't work properly as Daemon yet
#from cherrypy.process.plugins import Daemonizer
#d = Daemonizer(cherrypy.engine)
#d.subscribe()

server_ip = '127.0.0.1'
server_port = 8237
sf = 'screen.png'
template_sub =  {
                '%title':'ADB Controller (w/Touch)',
                '%screenshot':sf,
                '%devices':'No Devices Found',
                }

adbcmd = 'adb'
adbshell = '%s shell' % adbcmd
adbdevices = '%s devices' % adbcmd
adb_reboot = '%s reboot' % adbcmd
adb_pull = '%s pull' % adbcmd
adb_inst = '%s install' % adbcmd
adbrun = '%s am start -n ' % adbshell
adb_ik = '%s input keyevent' % adbshell
adb_itext = '%s input text' % adbshell
adb_it = '%s input tap' % adbshell
adb_ss = '%s screencap -p' % adbshell

class Controller(object):

    def cmd(self, command, stdout=False, device=None):
        ''' execute the commands through Popen
        return the output of popen'''
        if device:
            command = "%s -s %s" % (command, device)
        proc=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        if stdout:
            return proc.stdout.read()
        else:
            return proc.communicate()[0]
        return

    def read_devices(self):
        ''' Build devices select box for all devices 
        connected to the adb server'''
        devices = []
        device = 'No Devices Found'        
        device_list = self.cmd(adbdevices)
        #devices_title = devices[0:24]
        dcmd_items = device_list.splitlines()
        for item in dcmd_items[1:]:
            print item
            if item:
                d_items = item.split('\t')
                devices.append('<option value="%s">%s (%s)</option>' % (d_items[0],d_items[0],d_items[1]))

        if len(devices) > 0:
            devices.insert(0,'<select>')
            devices.append('</select>')
            device = ''.join(devices)
        return device

    def match_id(self, buf):
        ''' Update the %id in a buffer if matched 
        to the values stored in template_sub dict'''
        output_buf = []
        for line in buf:
            for key, value in template_sub.items():
                if key in line:
                    if key == '%devices':
                        line = line.replace(key,self.read_devices())
                    else:
                        line = line.replace(key, value)
                else:
                    pass
            output_buf.append(line)
        return output_buf

    def proc_template(self, template):
        ''' read through template file and modify 
        for output in the browser '''
        if os.path.exists(template):
            t = open(template, 'r')
            buf = t.readlines()
            t.close()
            return self.match_id(buf)
        else:
            return template
        return
      
    def screenshot(self, direct=True):
        ''' Dump a screenshot from the device and
        upload it to the computer '''
        si = "%s/img/%s" % (current_dir,sf)
        sd = "/sdcard/%s" % sf

        if direct:
            # Dump direct from device, dumps in ASCII mode
            pngdump = self.cmd(adb_ss, True)
            f = open(si,'w')
            f.write(re.sub('\x0D\x0A','\x0A',pngdump))
            f.close
        else:
            # Take Screenshot, use this method as direct dump results in corrupt image
            self.cmd("%s %s" % (adb_ss, sd))
            self.cmd("%s %s %s" % (adb_pull, sd, si))
            self.cmd("%s rm %s" % (adbshell, sd))
        
    def index(self, device=None, adb_shell=None, adb_k=None, adb_ik_send=None, adb_it_send=None, adb_apk=None, apk_screen=None, x=None, y=None, zx=None, zy=None, device_reboot=None):
        ''' Expose index page '''
        # No-Touch Controls
        if adb_shell:
            self.cmd("%s %s" % (adbshell, adb_shell))
            adb_shell=None
        if adb_k:
            self.cmd("%s %s" % (adb_ik, adb_k))
            adb_k=None
        if adb_ik:
            self.cmd("%s %s" % (adb_ik, adb_ik_send))
            adb_ik_send=None
        if adb_it_send:
            self.cmd("%s %s" % (adb_itext, adb_it_send))
            adb_it_send=None
        if adb_apk:
            self.cmd("%s %s" % (adb_inst, adb_apk))
            adb_apk=None
        if apk_screen:
            self.cmd("%s %s" % (adbrun, apk_screen))
            apk_screen=None
        if device_reboot:
            os.system("%s %s" % (adb_reboot, device_reboot))
            device_reboot=None

        # Touch Control
        if x and y:
            y = int(y) - float(zy) #Modifier
            x = int(x) - float(zx) #Modifier
            os.system("%s %s %s" % (adb_it, x, y))
            self.screenshot()
        try:
            self.screenshot()
        except:
            pass

        return self.proc_template('template.html')
    index.exposed = True

    
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cherrypy.config.update({'server.socket_host': server_ip,
                            'server.socket_port': server_port,
                            'cherrypy._cplogging': True,
                            'log.access_file': 'logs/access.log',
                            'log.error_file': 'logs/error.log',
                            'open_browser': False,
                        })  
                        
    config = {
     '/': {
       'tools.staticdir.root': current_dir,
      },
     '/img': {
       'tools.staticdir.on': True,
       'tools.staticdir.dir': "img",
       },
     '/css': {
       'tools.staticdir.on': True,
       'tools.staticdir.dir': "css",
       },
     '/js': {
       'tools.staticdir.on': True,
       'tools.staticdir.dir': "js",
       },
       
    }


    app = cherrypy.tree.mount(Controller(), "/", config)
    cherrypy.engine.start()
    if cherrypy.config['open_browser']:
        webbrowser.open('http://%s:%s' % (cherrypy.config['server.socket_host'],cherrypy.config['server.socket_port']))
    cherrypy.engine.block()
