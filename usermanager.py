#!/usr/bin/python

def main():
    while True:
        command=raw_input('Type a command(h for help):')
        if command=='h':
            print("l:list users and port\n")
            print("a:add a user\n")
            print("d:delete a user\n")
            print("q:quit\n")
        elif command=='l':
            f=open("user",'r')
            for line in f:
                if line[0]!='#':
                    print line.split('\t')[0:2]  
            f.close()
        elif command=='q':
            break
        elif command=='a':
            userinfo=[]
            userinfo.append(raw_input('name:'))
            userinfo.append(raw_input('port:'))
            userinfo.append(raw_input('password:'))
            userinfo.append(raw_input('bd_limit:'))
            userstr='\t'.join(userinfo)
            f=open('user','a')
            f.write(userstr)
            f.close
        elif command=='d':
            username=raw_input('Type a username:')
            f=open('user','r+')
            flist=f.readlines()
            a=0
            for line in flist:
                if line.split('\t')[0]==username:
                    del flist[a]
                a+=1
            f=open('user','w+')
            f.writelines(flist)
            f.close
        else:
            print("No such command!")

if __name__=="__main__":
    main()
