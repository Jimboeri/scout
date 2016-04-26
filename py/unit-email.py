#!/usr/bin/python2

import os
import getopt
import sys
#import pg
#import string
import dbobj
#from procs import *
#import time
#import datetime
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
 

##############################################################################
def main():
  """This program is intended to be called from office.py
Obtains the following parameters:
  ou_id
  subject
  msg_body
  user_id - person who sent the message

  """
  
  error_file = open('/tmp/jim.log', 'w')
  testing = 1
  try:
    opts, args = getopt.getopt(sys.argv[1:], "")

    param = dbobj.paramrec()
    db = dbobj.dbinstance(param.dbname)

    ou_id = int(args[0])
    subject = args[1]
    msg_body = args[2]
    user_id = args[3]

    if testing:
      error_file.write("OU id = %d, subject = '%s', msg_body = '%s', user_id = %s\n" % (ou_id, subject, msg_body, user_id))

    ourec = dbobj.ourec(db, ou_id)
    if not ourec.found:
      if testing:
        error_file.write('Error: OU not found - OU id = %d\n' % ou_id)
      return
 
    maillist = []

    # get email addresses of members of ou
    mail_by_ou(ourec, maillist, db, error_file)
    error_file.write('No of Email addr = %d\n' % len(maillist))

    #Get children ous
    children = ourec.child_list()
    for ch in children:
      mail_by_ou(ch, maillist, db, error_file)

    #if testing:
    error_file.write('No of Email addr = %d\n' % len(maillist))


 
    # Get details of the logged in user
    user = dbobj.adultrec(db, user_id)  
    if not user.found:
      error_file.write('Error: User not found - User id = %d\n' % user_id)
      return
 
    maillist.append(user.email)
 
    # Open link to mail server
    mailserver = smtplib.SMTP(param.smtpserver)


    #Get the html header
    htmlfile = param.template_dir + '/' + param.email_header
    mf = open(htmlfile)
    html_header = mf.read()
    mf.close()

    error_file.write('html opened = %s\n' % htmlfile)

    #Get the footer of the email
    footerfile = param.template_dir + '/' + param.email_footer
    mf = open(footerfile)
    html_footer = mf.read()
    mf.close()
    error_file.write('footer opened = %s\n' % footerfile)

    msg_footer = '<HR><A HREF="%s%s/scout.py?jw_action=ouf_disp&ou_id=%d" CLASS=footer>%s</A>' % (param.baseurl, param.pythondir, ourec.ou_id, ourec.name)

    error_file.write('Set up mailserver and body\n')


    #Cycle through the mail list
    for em in maillist:
      #error_file.write(em)
      # Create the mail message
      outer = MIMEMultipart()
  
      # Mail headers
      outer['Subject'] = subject
      #outer['From'] = user.email + "<%s %s>" % (user.forename, user.surname)
      outer['From'] = user.email
      outer['To'] = em
      outer.preamble = 'Scout unit mail message'
      outer.epilogue = ''
  
      # Attach the created file to the e-mail.
      msgfile = MIMEText(html_header + msg_body + msg_footer + html_footer, 'html')
      outer.attach(msgfile)
  
      #mailserver.set_debuglevel(1)
      mailserver.sendmail(user.email, em, outer.as_string())
      error_file.write('Send email to %s\n' % em)

    # Send me a copy
    # Create the mail message
    outer = MIMEMultipart()
 
    # Mail headers
    outer['Subject'] = 'Copy of email to ' + ourec.name
    #outer['From'] = user.email + "<%s %s>" % (user.forename, user.surname)
    outer['From'] = user.email
    outer['To'] = 'scout@west.net.nz'
    outer.preamble = 'Scout unit mail message'
    outer.epilogue = ''

    html_body = html_header + 'Subject : %s<BR>Sent by : %s %s<BR>Message body :<BR>%s' %(subject, user.forename, user.surname, msg_body) + html_footer

    # Attach the created file to the e-mail.
    msgfile = MIMEText(html_body, 'html')
    outer.attach(msgfile)

    #mailserver.set_debuglevel(1)
    mailserver.sendmail(user.email, em, outer.as_string())


    error_file.write('Finished sending email\n')

    # Finished the loop, close connection to mail server
    mailserver.quit()

    error_file.close()
  except:
    error_file = open('/tmp/email_error.log', 'w')
    error_file.write('Error occured')
    error_file.close()
  return

##############################################################################
def mail_by_ou(ourec, maillist, db, ef):
  """Populates maillist parameter (which must be an array) with unique email addresses of members and parents.
Receives two parameters
  ourec - the OU being processed
  maillist - the array for email addresses
"""
  ef.write('Entered mail_by_ou, ou_id = %d\n' % ourec.ou_id)
  membs = ourec.member_list(status = 'C')

  for s in membs:
    pers = dbobj.scoutrec(db, s.scout_id)
    if pers.found:
      if pers.email is not None and pers.email != '':
        if maillist.count(pers.email) == 0:
          maillist.append(pers.email)
      p1 = dbobj.adultrec(db, pers.parent1)
      if p1.found != 0 and p1.email is not None and p1.email != '':
        if maillist.count(p1.email) == 0:
          maillist.append(p1.email)
      p2 = dbobj.adultrec(db, pers.parent2)
      if p2.found != 0 and p2.email is not None and p2.email != '':
        if maillist.count(p2.email) == 0:
          maillist.append(p2.email)


if __name__ == '__main__':
  main()
