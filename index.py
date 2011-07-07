def ticket(req,ticket=None):
  import os.path
  import pickle
  import time
  ddir = os.path.dirname(req.canonical_filename)
  if ticket.count('.') == 0 and ticket.count('/') == 0:
    rnd = ticket
  else:
    return '''<html><body>Invalid ticket!</body></html>'''
  sdir = ddir+'/tickets/'+rnd+'/'
  d = pickle.load(open(sdir+'meta.p'))
  res = ''
  if not 'request' in d.keys():
    d['request'] = time.gmtime()
    d['remotehost'] = req.get_remote_host()
    pickle.dump(d, open(sdir+'meta.p','wb'))
    os.system('echo '+ddir+'/priv/job.py '+rnd+'| batch')
  stat = '<i>%s</i>: Job requested.<br/>'%(time.strftime("%Y-%m-%d %T GMT",d['request']),)
  if 'jobstart' in d.keys():
    stat += '<i>%s</i>: Job started.<br/>'%(time.strftime("%Y-%m-%d %T GMT",d['jobstart']),)
  if 'jobfailed' in d.keys():
    stat += '<i>%s</i>: Job failed, output of job follows:<br/><pre>'%(time.strftime("%Y-%m-%d %T GMT",d['jobfailed']),)
    stat += open(sdir+'R.out').read()
    stat += '</pre>'
  if 'jobfinish' in d.keys():
    matlabdata = '/TCGA/tickets/'+rnd+'/cancer.mat'
    rdata = '/TCGA/tickets/'+rnd+'/cancer.Rdata'
    import datetime
    delt = datetime.datetime(*list(d['jobfinish'])[0:6]) - datetime.datetime(*list(d['jobstart'])[0:6])
    stat += '''<i>%s</i>: Job finished, here are your files:<br/>
    <ul>
    <li><a href="%s">R data</a><br/>
    <li><a href="%s">MATLAB data</a><br/>
    </ul>
    Duration of extraction: %s
   '''%(time.strftime("%Y-%m-%d %T GMT",d['jobfinish']),rdata,matlabdata,str(delt))
  return '''<html><body>Reload page to see updates<br/><br/>%s<br/></body></html>''' % (stat,)

def get(req,data=None):
  import os.path
  import string
  import pickle
  import random
  import time
  ddir = os.path.dirname(req.canonical_filename)
  rnd = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
  try:
    os.mkdir(ddir+'/tickets/')
  except OSError:
    pass
  sdir = ddir+'/tickets/'+rnd+'/'
  os.mkdir(sdir,0700)

  d = {}
  for kv in data.split(','): k,v = kv.split('='); d[k]=int(v)
  d['first'] = time.gmtime()
  pickle.dump(d, open(sdir+'meta.p','wb'))
 
  return '''<html>
  <body>Here is a ticket, <a href="../index.py/ticket?ticket=%s">show the ticket</a> to the job dispatcher to request start of processing.
  </body></html>''' %(rnd,)

def _cancerShortToLongInit(ddir):
  import csv
  reader = csv.reader(open(ddir+'diseaseStudy.csv'))
  c = list(reader)
  return c

def _cancerShortToLong(cmap,short):
  import string
  m = filter(lambda x: x[0]==string.upper(short),cmap)
  if len(m) < 1:
    return short
  else:
    return m[0][1]

def index(req):
  import os.path
  ddir = os.path.dirname(req.canonical_filename)+'/'
  import pickle
  d = pickle.load(open(ddir+'/datatypes.p'))
  cmap = _cancerShortToLongInit(ddir)
  html = """<html>
  <head>
    <style>
      table { border-collapse: collapse; border: 1px solid black;}
      th,td { 
        padding-right: 10px; 
	font-family: helvetica;
      }
      td {
//        border-bottom: 1px solid gray;
      }
      .odd { background-color: #ffc0c0; }
      .even { background-color: #ffc0f0; }
      .hi { background-color: #00ffff; }
    </style>
  </head>
  <body><table>
<tr><th>Cancer</th><th>no patients</th><th>CNA platform</th><th>mRNA platform</th></tr>
"""
  i = 0
  for row in d:
    if i % 2 == 0:
      html += "<tr class='even' id='tr%d'>\n" % (i,)
    else:
      html += "<tr class='odd' id='tr%d'>\n" % (i,)
    j = 0
    rowp = list(row)
    mrnaid = rowp.pop(6)
    cnaid = rowp.pop(4)
    cancer = rowp.pop(1)
    for col in rowp:
      if j == 0:
	col = _cancerShortToLong(cmap,col)
      html += "<td class='col%d'>" % (j,)
      html += str(col)
      html += "</td>"
      j += 1
    html += """
    <td><a href="index.py/get?data=%s"><img src="dl.png" border="0" width=16 onmouseover="document.getElementById('tr%d').className = 'hi';" onmouseout="document.getElementById('tr%d').className = '%s';"/></a></td>
    </tr>
    """ % (("cancer=%s,mrna=%d,cna=%d" % (cancer,mrnaid,cnaid)),i,i,['even','odd'][i%2])

    i += 1
  html += "</table>\n"
  html += "<!-- %d rows -->" %(len(d),)
  html += "</body></html>"
  return html

