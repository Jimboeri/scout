#!/usr/bin/python

import os
import zipfile
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Utils, Encoders
import mimetypes
import smtplib

# set a flag to see if we need to archive mail
lNew = 0
arc_file = 'scoutdev.zip'


# Check for control file, if not found, create it
if not os.access(arc_file, os.F_OK):
  ctrl = file(arc_file, 'w')
  ctrl.close()
  lNew = 1

# First get a listing of the directory
ld = os.listdir('.')

newlist = []

for f in ld:
  if f.endswith('.py'):
    newlist.append(f)
  elif f == arc_file:
    last_time = os.stat(f)[8]
    print last_time

for f in newlist:
  if os.stat(f)[8] > last_time:
    print f
    lNew = 1
    break

if lNew:
  print "New files found"
else:
  print "NO new files found"

if lNew:
  prog_arc = zipfile.ZipFile(arc_file, 'w')

  for f in newlist:
    prog_arc.write(f)

  prog_arc.close()
  farc = file(arc_file, 'r')


  msg = MIMEMultipart()
  msg['To'] = 'jim@localhost'
  msg['From'] = 'jim@west.net.nz'
  msg['Subject'] = 'Program archive'
  msg['Date'] = Utils.formatdate(localtime=1)
  msg['Message-ID'] = Utils.make_msgid()

  bodytext = MIMEText('Python archive files', _subtype='plain')
  msg.attach(bodytext)

  attach = MIMEBase('application', 'zip')
  attach.set_payload(farc.read())
  Encoders.encode_base64(attach) 
  attach.add_header('Content-Disposition', 'Attachment', filename = arc_file)
  msg.attach(attach)
  farc.close()

  s = smtplib.SMTP('localhost')
  s.sendmail('jim@west.net.nz', 'jim@localhost', msg.as_string())


mimetype, mimeencoding = mimetypes.guess_type(arc_file)
print mimetype
print mimeencoding




