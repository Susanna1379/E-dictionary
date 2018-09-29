import pymysql
import re

db = pymysql.connect("localhost","root","123456","Dict")
cursor = db.cursor()

f = open('dict.txt')


for line in f:
    l= re.split(r'\s+',line)
    word=l[0]
    interpret=' '.join(l[1:])
    sql="insert into word (word,interpret) values ('%s','%s')" % (word,interpret)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

# db.commit()
# cursor.close()
# db.close()
f.close()