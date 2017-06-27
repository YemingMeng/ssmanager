#!/usr/bin/python

import os
import json
import time
import socket

class user:
    def __init__(self,port,passwd,name,current_bd,bd_lim):
        self.port=port
        self.passwd=passwd
        self.name=name
        self.current_bd=current_bd
        self.bd_lim=bd_lim

def datasize(num):
    num=int(num)
    if num < 1024:
        return '%.2f'%(num) +'B'
    elif num < 1024**2:
        return '%.2f'%(num*1.0/1024) +'KB'
    elif num < 1024**3:
        return '%.2f'%(num*1.0/1024**2) +'MB'
    else:
        return '%.2f'%(num*1.0/1024**3) +'GB'

class userspace:
    def __init__(self):
        self.users=[]
    def loaduser(self):
        userfile=open("user")
        for line in userfile:
            if line[0]=='#':
                pass
            else:
                line=line.replace('\n','')
                a=line.split('\t')
                self.adduser(a[1],a[2],a[0],eval(a[3]))
        userfile.close()
    def adduser(self,port,passwd,name,bd_lim,current_bd=0):
        self.users.append(user(port,passwd,name,current_bd,bd_lim))
    def deluser(self,port):
        a=0
        for i in self.users:
            if i.port==port:
                del self.users[a]
                a+=1
        if a==len(self.users):
            print "Can't del port!"
    def writebd(self):
        bd={}
        for i in self.users:
            bd[i.name]=i.current_bd
        json.dump(bd,open("current_bd","w"))
    def loadbd(self):
        if os.path.exists('current_bd'):
            bd=json.load(open("current_bd","r"))
            a=0
            for user in self.users:
                if user.name in bd:
                    self.users[a].current_bd=bd[user.name]
                    a+=1
    def initbd(self):
        a=0
        for user in self.users:
            self.users[a].current_bd=0
            a+=1

def write_config(userspace):
    text={"port_password":{},
            "timeout":300,
            "method":"aes-256-cfb",
            "fast_open":True}
    for i in userspace.users:
        text["port_password"][i.port]=i.passwd
    json.dump(text,open("ss_config.json",'w'))

def run_server():
    try:
        os.system("killall ssserver")
    except:
        pass
    os.system("nohup ./runss.sh >/dev/null 2>&1 &")

def bd_cal():
    global users
    try:
        os.remove("/tmp/client.sock")
    except:
        pass
    cli = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    cli.bind('/tmp/client.sock')  # address of the client
    cli.connect('/tmp/shadowsocks-manager.sock')  # address of Shadowsocks manager
    cli.send(b'ping')
    cli.recv(1506)
    yesterday=time.strftime('%d',time.localtime(time.time()))
    while True:
        date=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        tmp=cli.recv(1506)
        port,data=tmp[8:12],int(tmp[14:-1])
        a=0
        for user in users.users:
            if user.port==port:
                #add bandwidth
                users.users[a].current_bd+=data
                text=time.strftime('%H:%M:%S',time.localtime(time.time()))+'\t'+users.users[a].name+'\t'+datasize(users.users[a].current_bd)
                print text
                #ban port
                if users.users[a].current_bd > users.users[a].bd_lim:
                    cli.send(b'remove:{"server_port":'+port+b'}')
                    cli.recv(1506)
                #write log imformation
                logfile=open('log/'+'log_'+date,'a')
                logfile.write(text+'\n')
                logfile.close()
                users.writebd()
            a+=1
        #clear bandwidth in new month
        if yesterday=='24' and time.strftime('%d',time.localtime(time.time()))=='25':
            os.remove('current_bd')
            user.initbd()
        yesterday=time.strftime('%d',time.localtime(time.time()))

def main():
    try:
        os.mkdir('log')
    except:
        pass
    global users
    users=userspace()
    users.loaduser()
    users.loadbd()
    write_config(users)
    run_server()
    time.sleep(5)
    bd_cal()

if __name__ == "__main__":
    main()
