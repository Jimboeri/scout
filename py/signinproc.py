#!/usr/bin/python2

import os
import string
import webproc
from webscout import *
import dbobj
import time
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from ou import home_page
 
##############################################################################
def profile (form, db, param, conn, message = ''):
  """This form displays options to manage a users personal settings"""
  
  nUser = conn.scout_id
  User = dbobj.adultrec(db, nUser)

  if nUser == 0 or not User.found:
    app_error(form, param, conn, message = 'Invalid user id')

  jw_header(param, conn)

  if message != '':
    print message

  table = webproc.table(cellpadding = "1", cellspacing = param.it_cellspc, width='100%', border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'Details of:'), align="center")
  row.items.append(item)
  table.rows.append(row)
  
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('B', User.forename + ' ' + User.initials + ' ' + User.surname))
  row.items.append(item)
  table.rows.append(row)

  disp_line(table, '<B>Address:<BR></B>' + User.addr1, '<BR><B>Tel (H):<B>' + User.telephone_h)
  disp_line(table, User.addr2, '<B>Tel (W):<B>' + User.telephone_w)
  disp_line(table, User.addr3 + ' ' + User.p_code, '<B>E Mail:<B>' + User.email)

  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('A', '<BR>Change password', "href=signin.py?jw_action=passwdf_edit&user_id=" + str(nUser)))
  row.items.append(item)
  table.rows.append(row)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('A', 'Modify personal details', "href=office.py?jw_action=persf_edit&user_id=" + str(nUser)))
  row.items.append(item)
  table.rows.append(row)

  # Display the details
  print table.pr_table()

  webproc.form_footer()
  return

##############################################################################
def passwdf_edit (form, db, param, conn, message=''):
  """This form displays a password change dialog"""

  old_pw = ''
  pw1 = ''
  pw2 = ''
  submit = form.getfirst('submitted', '')
  pw_hint = form.getfirst('pw_hint', '')

  nInp_user = int(form.getfirst('user_id', '0'))

  # Are we changing the password of the active user, or someone else
  if nInp_user != conn.scout_id:
    # Must have superuser rights to do this
    if not conn.superuser:
      app_error(form, param, conn, message = 'Invalid action, insufficient rights')
      return

  User = dbobj.adultrec(db, nInp_user)

  if nInp_user == 0 or not User.found:
    app_error(form, param, conn, message = 'Invalid user id = ' + str(nInp_user))
    return

  jw_header(param, conn)

  if message != '':
    print webproc.tag('H2', message)

  #print 'Superuser = ' + str(conn.superuser)

  table = webproc.table(cellpadding = '10', cellspacing = param.it_cellspc, width='100%', border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'Change the password of:'), align="center", colspan='3')
  row.items.append(item)
  table.rows.append(row)
  
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H4', User.forename + ' ' + User.initials + ' ' + User.surname), align="center", colspan='3')
  row.items.append(item)
  table.rows.append(row)

  if nInp_user == conn.scout_id:
    row = webproc.table_row()
    item = webproc.table_item('Old password', align = 'right', width='33%')
    row.items.append(item)
    item = webproc.table_item('<INPUT TYPE="PASSWORD" NAME="old_pw" SIZE="30" MAXLENGTH="60">', width='33%')
    row.items.append(item)
    item = webproc.table_item('', width='34%')
    row.items.append(item)
    table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item('New password', align = 'right')
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="PASSWORD" NAME="new_pw1" SIZE="30" MAXLENGTH="60">')
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item('Repeat new password', align = 'right')
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="PASSWORD" NAME="new_pw2" SIZE="30" MAXLENGTH="60">')
  row.items.append(item)
  table.rows.append(row)

  if nInp_user == conn.scout_id:
    row = webproc.table_row()
    item = webproc.table_item('Password hint', align = 'right')
    if submit == 'Y' and pw_hint == '':
      item.data += '<BR><SPAN CLASS="validation_message">Password hint must be entered</SPAN>'
    row.items.append(item)
    item = webproc.table_item('<INPUT TYPE="TEXT" NAME="pw_hint" SIZE="40" MAXLENGTH="40">')
    row.items.append(item)
    item = webproc.table_item('Please enter something that will help you to remember your password, but not the actual password.  This will be e-mailed to you if you forget your password.', width='34%')
    row.items.append(item)
    table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="passwdf_edit" VALUE="Submit">', align='right')
  item.data += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="passwdp_edit">'
  item.data += '<INPUT TYPE="HIDDEN" NAME="user_id" VALUE=' + str(nInp_user) + '>'
  item.data += '<INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', 'href=signin.py?jw_action=profile'))
  row.items.append(item)
  table.rows.append(row)

  # Display the details
  print webproc.tag('FORM', table.pr_table(), 'METHOD="POST", NAME="passwdf_edit" ACTION="signin.py"')

  webproc.form_footer()
  return

##############################################################################
def passwdp_edit (form, db, param, conn):
  """Process the change password page  """

  old_pw 	= form.getfirst('old_pw', '')
  pw1 		= form.getfirst('new_pw1', '')
  pw2 		= form.getfirst('new_pw2', '')
  nInp_user 	= int(form.getfirst('user_id', '0'))
  pw_hint	= form.getfirst('pw_hint', '')

  # Are we changing the password of the active user, or someone else
  superuser = 0
  if nInp_user != conn.scout_id:
    # Must have superuser rights to do this
    if not conn.superuser:
      app_error(form, param, conn, message = 'Invalid action, insufficient rights')
      return
    else:
      superuser = 1

  User = dbobj.adultrec(db, nInp_user)

  if nInp_user == 0 or not User.found:
    app_error(form, param, conn, message = 'Invalid user id = ' + str(nInp_user))
    return

  if pw1 != pw2:
    passwdf_edit(form, db, param, conn, message='New password must be entered twice identically each time') 
    return

  if nInp_user == conn.scout_id:
    if User.passwd is not None and User.passwd != '':
      if not User.check_pw(old_pw):
        passwdf_edit(form, db, param, conn, message='Current password must be entered correctly') 
        return
    if pw_hint == '':
      passwdf_edit(form, db, param, conn, message='Password hint must be entered') 
      return  

  ret = User.update_pw(pw1, old_pw, superuser)
  if ret == 1:
    message = 'Password update successfully'
    User.pw_hint = pw_hint
    User.update()
  else:
    message = 'Password not updated, return val = ' + str(ret)

  profile(form, db, param, conn, message = message)

  return

##############################################################################
def set_homef_edit (form, db, param, conn, message = ''):
  """This form displays options to change a users home page"""
  
  nUser = conn.scout_id
  User = dbobj.adultrec(db, nUser)

  if nUser == 0 or not User.found:
    app_error(form, param, conn, message = 'Invalid user id')
    return

  jw_header(param, conn)

  if message != '':
    print message

  if conn.last_level == 'N':
    nat = dbobj.nationalrec(db)
    if not nat.found:
      app_error(form, param, conn, message = 'Invalid parameter')
      return
    descr = 'National level'
    home_name = nat.name
    cancel_str = webproc.tag('A', 'Cancel', 'href=scout.py?jw_action=natf_disp')
  elif conn.last_level == 'A':
    area = dbobj.arearec(db, conn.last_level_id)
    if not area.found:
      app_error(form, param, conn, message = 'Invalid parameter')
      return
    descr = 'Area'
    home_name = area.name
    cancel_str = webproc.tag('A', 'Cancel', 'href=scout.py?jw_action=areaf_disp&area_id=' + str(conn.last_level_id))
  elif conn.last_level == 'D':
    dist = dbobj.districtrec(db, conn.last_level_id)
    if not dist.found:
      app_error(form, param, conn, message = 'Invalid parameter')
      return
    descr = 'District'
    home_name = dist.name
    cancel_str = webproc.tag('A', 'Cancel', 'href=scout.py?jw_action=distf_disp&dist_id=' + str(conn.last_level_id))
  elif conn.last_level == 'G':
    group = dbobj.grouprec(db, conn.last_level_id)
    if not group.found:
      app_error(form, param, conn, message = 'Invalid parameter')
      return
    descr = 'Area'
    home_name = group.name
    cancel_str = webproc.tag('A', 'Cancel', 'href=scout.py?jw_action=groupf_disp&group_id=' + str(conn.last_level_id))
  elif conn.last_level == 'U':
    unit = dbobj.unitrec(db, conn.last_level_id)
    if not unit.found:
      app_error(form, param, conn, message = 'Invalid parameter')
      return
    descr = 'Unit'
    home_name = unit.name
    cancel_str = webproc.tag('A', 'Cancel', 'href=scout.py?jw_action=unitf_disp&unit_id=' + str(conn.last_level_id))
  else:
    app_error(form, param, conn, message = 'Invalid parameter')

  print webproc.tag('CENTER', webproc.tag('H3', 'Set home page to:'))
  print webproc.tag('CENTER', webproc.tag('H4', descr + ': ' + home_name + '?'))
  Str = webproc.tag('A', 'Set home page', 'href=signin.py?jw_action=set_homep_edit') + '&nbsp;&nbsp;&nbsp;' + cancel_str
  print webproc.tag('CENTER', webproc.tag('H4', Str))

  webproc.form_footer()
  return

##############################################################################
def set_homep_edit (form, db, param, conn):
  
  user = dbobj.adultrec(db, conn.scout_id)
  if not user.found:
    app_error(form, param, conn, message = 'Invalid parameter')

  user.home_level = conn.last_level
  user.home_id = conn.last_level_id
  user.home_ou_id = conn.last_ou_id

  user.update()

  conn.home_level = conn.last_level
  conn.home_id = conn.last_level_id
  conn.home_ou_id = conn.last_ou_id

  home_page(form, db, param, conn)
  return


##############################################################################
def logout_form(form, db, param, conn):
  conn.scout_id = 0
  conn.logout()
  home_page(form, db, param, conn)
  return

##############################################################################
def login_form(form, db, param, conn, message = '', next_proc=''):
  """This procedure displays a form to allow a user to sign in
  """

  jw_header(param, conn, menu_item=30)

  if message != '':
    print webproc.tag('h4', message)

  table = webproc.table(cellpadding="10")
  table.add_row().add_item("Name", width = "25%", align = 'RIGHT')
  table.last_row().add_item('<INPUT TYPE="TEXT" NAME="li_name" size="20">')

  table.add_row().add_item("Password", width = "25%", align = 'RIGHT')
  table.last_row().add_item('<INPUT TYPE="PASSWORD" NAME="li_password" size="20">')

  table.add_row().add_item("&nbsp;", width = "25%")
  table.last_row().add_item('<A href=signin.py?jw_action=pwhint_f1>Need password help, click here</A>')

  table.add_row().add_item("&nbsp;")
  table.last_row().add_item('<INPUT TYPE="SUBMIT" VALUE="Sign in" NAME="li1">')

  table.add_row().add_item("&nbsp;")
  table.last_row().add_item('<INPUT TYPE="RESET" VALUE="Reset values" NAME="li2">')

  #for k in form.keys():
  #  table.add_row().add_item(k + " : " + form.getfirst(k))

  webform = webproc.form('signin.py', table.pr_table())
  webform.add_hidden('jw_action', 'login_proc')

  if next_proc is not None and next_proc != '':
    webform.add_hidden('next_proc', next_proc)
    for k in form.keys():
      if k != 'jw_action':
        webform.add_hidden(k, form.getfirst(k))


  print webform

  print '<br>'
  webproc.form_footer()
  return


##############################################################################
def pwhint_f1(form, db, param, conn, message = ''):
  jw_header(param, conn, menu_item=30)
  if message != '':
    print webproc.tag('h4', message)
  table = webproc.table()
  table.cellpadding="10"
  row = webproc.table_row()
  item = webproc.table_item("On line ID")
  item.width = "25%"
  item.align = 'RIGHT'
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="TEXT" NAME="li_name" size="20">')
  row.items.append(item)
  item = webproc.table_item('Enter your on-line ID if you know it')
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item("E-Mail address")
  item.width = "25%"
  item.align = 'RIGHT'
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="TEXT" NAME="li_email" size="20">')
  row.items.append(item)
  item = webproc.table_item("Enter your email address if you don't remember your on-line ID")
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item("&nbsp;")
  item.width = "25%"
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="SUBMIT" VALUE="Send help" NAME="pwh">')
  row.items.append(item)
  table.rows.append(row)

  cForm = table.pr_table()
  cForm += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="pwhint_p1">'
  print webproc.tag('FORM', cForm, 'METHOD="POST" NAME="pwhint_p1" action="signin.py"')

  print '<br>'
  webproc.form_footer()
  return

##############################################################################
def pwhint_p1(form, db, param, conn, message = ''):
  """Processes the input from the password hint form"""

  jw_header(param, conn, menu_item=30, js=['validate.js'])

  ol_id = form.getfirst('li_name', '')
  email = form.getfirst('li_email', '')

  send_email = 0
  adult = dbobj.adultrec(db, 0)

  if ol_id != '':
    adult = dbobj.adultrec(db, 0)
    # Look got the ID in tha database
    adult_ref = adult.find_on_line_id(ol_id)
    if adult_ref != 0:
      adult = dbobj.adultrec(db, adult_ref)

      if adult.pw_hint != '':
        send_email =1
  if not send_email:
    if email != '':
      adult_ref = adult.find_email(email)
      if adult_ref != 0:
        adult = dbobj.adultrec(db, adult_ref)
        send_email =1


  if send_email:

    # Email the password hint to the user
    # Create the mail message
    outer = MIMEMultipart()

    # Mail headers
    outer['Subject'] = 'Password hint from Scout membership database'
    outer['From'] = param.fromaddr
    outer['To'] = adult.email
    outer.preamble = 'Password hint'
    outer.epilogue = ''

    #Add the html header
    textfile = param.template_dir + '/' + param.email_header
    mf = open(textfile)
    msg_body = mf.read()
    mf.close()

    #Add the body of the email
    textfile = param.template_dir + '/' + param.email_pw_hint
    mf = open(textfile)
    msg_body += mf.read()
    mf.close()
 
    #Add the footer of the email
    textfile = param.template_dir + '/' + param.email_footer
    mf = open(textfile)
    msg_body += mf.read()
    mf.close()

    # Replace the placeholders 
    msg_body = string.replace(msg_body, '%onlineid%', str(adult.on_line_id))
    msg_body = string.replace(msg_body, '%passwordhint%', str(adult.pw_hint))

    # Finalise the message
    msgfile = MIMEText(msg_body, 'html')
    outer.attach(msgfile)

    # send the message
    mailserver = smtplib.SMTP(param.smtpserver)
    mailserver.sendmail(param.fromaddr, adult.email, outer.as_string())
    mailserver.quit()

    message = "Your accout details and password hint (if available) has been sent to your email address.  You may use these to sign on"
    print webproc.tag('H2', webproc.tag('CENTER', message))
    print " "

  else:
    # insert javascript submit validation script
    jscript = 'function submitform1(myform) {\n  if(validate_name(myform) && validate_email(myform)) {'
    jscript += '    return true\n  }\n  return false\n}\n'
    print webproc.jswrapper(jscript)
    message = "N0 sign on account could be found for the details you have provided."
    print webproc.tag('H2', webproc.tag('CENTER', message))
    print '<CENTER><H4>You may leave a message to the system administrator below. Please note that this database is maintained on a part time basis and it may be a while before you receive a reply.</H3></CENTER>'
    print " "

    table = webproc.table(cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, width='100%', border = param.it_brdr)
    row = webproc.table_row()
    item = webproc.table_item('Your name', width="20%")
    row.items.append(item)
    item = webproc.table_item('<INPUT TYPE="TEXT" NAME="name" size="40" maxsize="80">')
    row.items.append(item)
    table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('Your email address', width="20%")
    row.items.append(item)
    item = webproc.table_item('<INPUT TYPE="TEXT" NAME="email" size="40" maxsize="80">')
    row.items.append(item)
    table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('Your phone number', width="20%")
    row.items.append(item)
    item = webproc.table_item('<INPUT TYPE="TEXT" NAME="phone" size="40" maxsize="80">')
    row.items.append(item)
    table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('Subject', width="20%")
    row.items.append(item)
    item = webproc.table_item('<INPUT TYPE="TEXT" NAME="subject" size="40" maxsize="80">')
    row.items.append(item)
    table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('<TEXTAREA NAME="body" rows="10" cols="70"> </TEXTAREA>', colspan='2')
    row.items.append(item)
    table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item("&nbsp;", width="25%")
    row.items.append(item)
    item = webproc.table_item('<INPUT TYPE="SUBMIT" VALUE="Submit request" NAME="pwreq">')
    item.data += '&nbsp&nbsp' + webproc.jbutton('Login page', 'signin.py?jw_action=login_form')
    row.items.append(item)
    table.rows.append(row)

    cForm = table.pr_table()
    cForm += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="pwhint_p2">'

    print webproc.tag('FORM', cForm, 'METHOD="POST" NAME="pwhint_p1" action="signin.py" onsubmit="return submitform1(this)"')

  #dbobj.log_action(db, conn.scout_id, 301, scout.scout_id, parent.scout_id)

  webproc.form_footer()
  return

##############################################################################
def pwhint_p2(form, db, param, conn, message = ''):
  """Processes the second input from the password hint form"""

  name = form.getfirst('name', '')
  email = form.getfirst('email', '')
  phone = form.getfirst('phone', '')
  subject = form.getfirst('subject', '')
  body = form.getfirst('body', '')

  send_email = 0
  message = dbobj.messagerec(db, 0)

  if name != "":
    if email != '' or phone != '':
      if subject != '' or body != '':
        message.name = name
        message.email = email
        message.telephone = phone
        message.subject = subject
        message.body = body
        message.for_sysadmin = 1
        message.add()


  home_page(form, db, param, conn)
  return

##############################################################################
def olf_agree(form, db, param, conn, cScout_id, CPass):
  """Displays on line agreement and asks for acceptance """
  jw_header(param, conn, menu_item=30)

  #Add the explanatory text to the message
  textfile = param.template_dir + '/' + param.online_agreement
  mf = open(textfile)

  table = webproc.table(cellpadding="10")
  row = webproc.table_row()
  item = webproc.table_item(mf.read(), align = 'center')
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item(" ", align="center")
  item.data = webproc.jbutton('I agree', 'signin.py?jw_action=olp_agree&scout_id=%s'%cScout_id) + '&nbsp&nbsp&nbsp'
  item.data += webproc.jbutton("I don't agree", 'signin.py?jw_action=login_form')
  row.items.append(item)
  table.rows.append(row)

  print table.pr_table()

  print '<br>'
  webproc.form_footer()
  return

##############################################################################
def olp_agree(form, db, param, conn):
  """Processes the login agreement form"""

  # get login name & pw from the form
  nScout_id = int(form.getfirst("scout_id", ''))

  oScout = dbobj.adultrec(db, nScout_id)

  # Check password
  if not oScout.found:
    app_error(form, param, conn, message="Invalid input")
    return

  conn.scout_id = nScout_id
  conn.update()

  ol_dt = dbobj.dt_time(time.localtime())
  oScout.online_agree_dt = ol_dt.date
  oScout.update() 

  home_page(form, db, param, conn, menu_id=1)

  return

def login_proc(form, db, param, conn):
  """Processes the login form.
The module requires the username (li_name) and password (li_password) to be passed from the form.
Errors returned if:
  li_name not present
  user name not found in DB
  password invalid
If the user has not agreed to the online agreement, it is presented for acceptance (olf_agree() in signinproc.py)
The connection record is updated
Control passed to the following procedures based on 'next_proc' parameter:
	achievef_present()
	awardf_disp()
  else
        home_page()
"""

  if not form.has_key("li_name"):
    login_form(form, db, param, conn, "User not entered")
    return

  #if not form.has_key("li_password"):
  #  login_form(form, db, param, conn, "Password not entered")
  #  return
  
  # get login name & pw from the form
  cOn_line_id = form.getfirst("li_name", '')
  cPassword = form.getfirst('li_password', '')  

  # See if the user exists
  # Initialise object
  oScout = dbobj.scoutrec(db, 0)

  # search for on_line_id
  nScout_id = oScout.find_on_line_id(cOn_line_id)
  if nScout_id == 0:
    login_form(form, db, param, conn, "User not entered")
    return

  oScout = dbobj.adultrec(db, nScout_id)
  
  # Check password
  if not oScout.check_pw(cPassword):
    login_form(form, db, param, conn, "Password invalid")
    return

  if oScout.online_agree_dt == '' or oScout.online_agree_dt is None:
    olf_agree(form, db, param, conn, str(oScout.scout_id), cPassword)
    return

  conn.scout_id = nScout_id
  conn.update()

  if form.getfirst('next_proc', '') == 'achievef_present':
    achievef_present(form, db, param, conn)
  elif form.getfirst('next_proc', '') == 'awardf_disp':
    awardf_disp(form, db, param, conn)
  else:
    home_page(form, db, param, conn, menu_id=1)

  return



