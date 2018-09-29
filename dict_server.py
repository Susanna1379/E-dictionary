'''
name :  Tedu
date :  2018-10-1
email:  xxx
modules: pymongo
This is a dict project for AID
'''

from socket import *
import os,sys
import time
import pymysql
import signal

#定义需要的全局变量
DICT_TEXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 5000
ADDR = (HOST,PORT)

#流程控制
def main():
    #创建数据库连接
    db = pymysql.connect('localhost','root','123456','Dict')
    
    #创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)

    #处理子进程退出
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    print('listen the port 5000...')

    while True:
        try:
            c,addr = s.accept()
            print('已连接客户端：',addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务器退出')
        except Exception as e:
            print('服务器异常:',e)
            continue
        
    #创建子进程
        pid = os.fork()
        #子进程处理具体请求
        if pid == 0:
            s.close()
            do_child(c,db)
        else:
            c.close()
            continue

def do_child(c,db):
    #循环接收客户端请求
    while True:
        data = c.recv(1024).decode()
        if (not data) or data[0] == 'E':
            c.close()
            sys.exit(0)
        elif data[0] == 'R':
            do_register(c,db,data)
        elif data[0] == 'L':
            do_login(c,db,data)
        elif data[0] == 'Q':
            do_query(c,db,data)
        elif data[0] == 'H':
            do_hist(c,db,data)


def do_query(c,db,data):
    print('查词操作')
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cursor = db.cursor()
    def insert_history():
        tm = time.ctime()
        sql = "insert into hist (name,word,time) values('%s','%s'\
        ,'%s')" % (name,word,tm)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
    #文本查询
    try:
        f = open(DICT_TEXT)
    except:
        c.send(b'failed')
        return
    for line in f:
        tmp = line.split(' ')[0]
        if tmp > word:
            c.send(b'failed')
            f.close()
            return
        elif tmp == word:
            c.send(b'OK')
            time.sleep(0.1)
            c.send(line.encode())
            f.close()
            insert_history()
            return
    c.send(b'failed')
    f.close()


def do_login(c,db,data):
    print('登录操作')
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    sql = "select passwd from user where name='%s'" % name
    cursor.execute(sql)
    r = cursor.fetchone()
    if r[0] == passwd:
        c.send(b'OK')
    else:
        c.send(b'Failed')


def do_register(c,db,data):
    print('注册操作')
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    sql ="select * from user where name='%s'" % name
    cursor.execute(sql)
    r = cursor.fetchone()
    if r != None:
        c.send(b'EXISTS')
        return
    #用户不存在插入用户
    sql = "insert into user (name,passwd) values \
    ('%s','%s')"%(name,passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except:
        db.rollback()
        c.send(b'FAIL')
        return
    else:
        print('%s注册成功'%name)

def do_hist(c,db,data):
    print('历史记录')
    l = data.split(' ')
    name = l[1]
    cursor = db.cursor()
    sql = "select * from hist where name='%s'" % name
    cursor.execute(sql)
    r = cursor.fetchall()
    if not r:
        c.send(b'failed')
        return
    else:
        c.send(b'OK')
    for i in r:
        time.sleep(0.1)
        msg="%s   %s   %s" % (i[1],i[2],i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b'##')


if __name__=='__main__':
    main()