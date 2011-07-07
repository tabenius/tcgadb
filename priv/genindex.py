#!/usr/bin/python
import MySQLdb
import pickle
db = MySQLdb.connect(user='www',passwd='mahametta',host='localhost', db='TCGA')
sql = """select cancer.name as cancer,cancer.id,count(distinct a1.patid) as patienter,p1.name as cnaplatform,p1.id, p2.name as mRNAplatform,p2.id from aliquot as
a1, aliquot as a2, cancer, platform as p1, platform as p2 where
a1.datatid = 10 and a2.datatid = 1 and
a1.patid=a2.patid and a2.cancid=a1.cancid and cancer.id=a1.cancid and
p1.id = a1.platfid and p2.id=a2.platfid group by a1.cancid, a1.platfid,
a2.platfid order by cancer,patienter desc
"""
c=db.cursor()
c.execute(sql)
res = c.fetchall()
pickle.dump(res,open('/var/www/TCGA/datatypes.p','wb'))
