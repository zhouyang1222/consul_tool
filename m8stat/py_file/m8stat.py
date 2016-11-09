#encoding = utf8

import etcd
import time
import datetime
import commands
import ConfigParser

cf = ConfigParser.ConfigParser()
cf.read("/etc/sysconfig/m8stat.conf")
group = cf.sections()
group.remove("etcd_host")
host_name = commands.getoutput("hostname")
project_name = cf.get("etcd_host", 'project')
etcd_ip = cf.get("etcd_host", 'ip')
etcd_port = cf.get("etcd_host", 'port')

while(1):
    try:
        client = etcd.Client(host=etcd_ip, port=int(etcd_port), allow_redirect=True)
        for ser_lists in group:    
            values = cf.options(ser_lists)
            for value in values:
                ser_name = cf.get(ser_lists,value)
                num = commands.getoutput("ps -ef | grep %s | grep -v \"grep\" |wc -l" %ser_name)
                ser_status = "inactive" if num == '0' else "active"
                try:
                    etcd_value = eval(client.read(project_name+'/'+host_name+'/'+ser_lists+'/'+ser_name).value)
                except:
                    etcd_value = None
                if etcd_value == None:
                    ser_time = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
                    client.write(project_name+'/'+host_name+'/'+ser_lists+'/'+ser_name, {'status':ser_status,'start_time':ser_time,'stop_time':ser_time})
                else:
                    if etcd_value['status'] != ser_status:
                        if ser_status == 'active':
                            stop_time = etcd_value['stop_time']
                            start_time = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
                        else:
                            start_time = etcd_value['start_time']
                            stop_time = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
                        client.write(project_name+'/'+host_name+'/'+ser_lists+'/'+ser_name, {'status':ser_status,'start_time':start_time,'stop_time':stop_time})
    except:
        print "error"
        time.sleep(5)   
    time.sleep(5)

