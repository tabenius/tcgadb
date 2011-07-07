#!/usr/bin/python
import sys
import os
import os.path
import pickle
import time
sdir = os.path.dirname(sys.argv[0])+'/../tickets/'+sys.argv[1]+'/'
d = pickle.load(open(sdir+'meta.p'))
if not 'jobstart' in d.keys():
  d['jobstart'] = time.gmtime()
  pickle.dump(d, open(sdir+'meta.p','wb'))
  priv = os.path.dirname(sys.argv[0])+'/'
  os.system('''export TCGAticketdir=%s
export TCGAcancer=%s
export TCGAmrna=%d
export TCGAcna=%d
R --vanilla < %s/creatematrix.R > %s''' %(sdir,d['cancer'],d['mrna'],d['cna'],priv,sdir+'/R.out') )
  success = False
  try:
    os.stat(sdir+'cancer.mat')
    success = True
  except OSError:
    d['jobfailed'] = time.gmtime()
  if success:
    d['jobfinish'] = time.gmtime()
  pickle.dump(d, open(sdir+'meta.p','wb'))
else:
  print "job already started"

