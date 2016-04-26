#!/usr/bin/python2

"""Run batch processing options for the scout development program

Usage scout-batch.py [options]

Options:
  --help
  -h
    Print this help message

"""

import os
#import pg
import string
import dbobj
from procs import *
import time
import datetime
import smtplib
import sys
from webproc import tag
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import getopt

##############################################################################
def usage(code, msg=''):
  if code:
    fd = sys.stderr
  else:
    fd = sys.stdout
  print >> fd, _(__doc__)
  if msg:
    print >> fd, msg
  sys_exit(code)

 
##############################################################################
def sys_adm_notify(db, param):
  """This program sends notifications of messages to sys admins"""
  
  new_messages = dbobj.sys_admin_msg_list(db, status='N')
  sysadmins = dbobj.sys_admin_list(db)

  for sa in sysadmins:
    send_mail = 0
    body = tag('H1', param.title)
    body += "<H4>The following messages have been received and await your attention</H4>"
    body = tag('A', body, 'href=' + param.baseurl + param.pythondir + '/office.py?jw_action=sys_admf_msg')
    for msg in new_messages.messagelist:
      send_mail = 1
      line = tag('A', msg.body, 'href=' + param.baseurl + param.pythondir + '/office.py?jw_action=sys_admf_disp&msg_id=' + str(msg.msg_id))
      line += ' From: ' + msg.name + '<BR>'
      body += line

    if send_mail:
      # Create the mail message
      outer = MIMEMultipart()

      # Mail headers
      outer['Subject'] = 'You have new messages from ' + param.title
      outer['From'] = param.fromaddr
      outer['To'] = sa.email
      outer.preamble = 'Notification of messages'
      outer.epilogue = ''

      #Add the html header
      textfile = param.template_dir + '/' + param.email_header
      mf = open(textfile)
      msg_body = mf.read()
      mf.close()

      #Add the body of the email
      msg_body += body

      #Add the footer of the email
      textfile = param.template_dir + '/' + param.email_footer
      mf = open(textfile)
      msg_body += mf.read()
      mf.close()

      msgfile = MIMEText(msg_body, 'html')
      outer.attach(msgfile)

      mailserver = smtplib.SMTP(param.smtpserver)
      #mailserver.set_debuglevel(1)
      mailserver.sendmail(param.fromaddr, sa.email, outer.as_string())
      mailserver.quit()


  return

##############################################################################
def unit_award_notification(db, param):
  """This program checks through all units in the database, checking for award
  that need to be presented
  """

  mailserver = smtplib.SMTP(param.smtpserver)

  #Get the html header
  mf = open(param.template_dir + '/' + param.email_header)
  email_header = mf.read()
  mf.close()

  #Get the footer of the email
  mf = open(param.template_dir + '/' + param.email_footer)
  email_footer = mf.read()
  mf.close()

  testfile = open('/tmp/testfile.log', 'a')

  top = dbobj.ourec(db, 1)
  if top.found:
    proc_ou_award_notify(top, mailserver, param, email_header, email_footer, testfile)

  mailserver.quit()
  testfile.close()
  return

##############################################################################
def proc_ou_award_notify(ourec, mailserver, param, em_head, em_foot, testfile):
  """Blah"""
  # Get list of members
  members = ourec.member_list()
  if len(members):
    # if some members exists, get the mngt ou members
    ourec.get_mngt()
    managers = ourec.mngt_ou.member_list()
    msg_body = '<H1>Awards to be presented for %s</H1>' % ourec.name
    table = webproc.table()
    num_to_award = 0
 
    for s in members:
      scout = dbobj.scoutrec(ourec.database, s.scout_id)
      scout_present = 0
      # lets look for awards to be presented
      scout.achieve_list()
      for ach in scout.achievelist:
        if not ach.awd_presented:
          num_to_award += 1
          item = table.add_row().add_item(' ')
          if not scout_present:
            scout_present += 1
            item.data = tag('A', '%s %s' % (s.forename, s.surname),\
              'href=%s%s/award.py?jw_action=awardf_disp&scout_id=%d' %\
              (param.baseurl, param.pythondir, s.scout_id))
          table.append_item(tag('A', ach.name,\
              'href=%s%s/award.py?jw_action=achievef_present&scout_id=%d&award_id=%d&ou_id=%d'\
              % (param.baseurl, param.pythondir, s.scout_id, ach.award_id, ourec.ou_id)))
    if num_to_award:
      msg_body += table.pr_table()
      msg_body += '<HR><A HREF="%s%s/ou_logic.py?jw_action=ouf_disp&ou_id=%d" CLASS=footer>%s</A>'\
          % (param.baseurl, param.pythondir, ourec.ou_id, ourec.name)
      for mngr in managers:
        # Create the mail message
        outer = MIMEMultipart()

        # Mail headers
        outer['Subject'] = 'Awards in %s that need to be presented' % ourec.name
        outer['From'] = param.fromaddr
        outer['To'] = mngr.email
        outer.preamble = 'Notification of messages'
        outer.epilogue = ''

        msgfile = MIMEText(em_head + msg_body + em_foot, 'html')
        outer.attach(msgfile)

        testfile.write(mngr.email + '\n')
        testfile.write(em_head + msg_body + em_foot + '\n')

        try:
          mailserver.sendmail(param.fromaddr, mngr.email, outer.as_string())
        except smtplib.SMTPRecipientsRefused:
          mngr.email_bounce += 1
          mngr.update()
        except:
          testfile.write('*** sendmail failed ***')

  # Get list of child ou's
  children_ous = ourec.child_list()

  # This make this procedure recursive
  for chld in children_ous:
    proc_ou_award_notify(chld, mailserver, param, em_head, em_foot, testfile)

  return

##############################################################################
# Main program logic, decides which progranms to run
def main():
  #try:
  #  opts, args = getopt.getopt(sys.argv[1:], 'vh', ['verbose', 'help'])
  #except getopt.error, msg:
  #  usage(1, msg)


  if len(sys.argv) > 1:
    param = dbobj.paramrec(sys.argv[1])
  else:
    param = dbobj.paramrec()

  today = datetime.date(2005,1,1)
  today = today.today()
  
  db = dbobj.dbinstance(param.dbname)
 
  sys_adm_notify(db, param)

  if today.weekday() == 6:
    # we only do thios on Sundays
    unit_award_notification(db, param)

  return

if __name__ == '__main__':
  main()
