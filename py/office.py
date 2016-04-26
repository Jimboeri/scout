#!/usr/bin/python2

import cgi
import os
import cgitb; cgitb.enable()
#import pg
import string
import webproc
from webscout import *
import dbobj
from procs import *
import time
import datetime
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import heir_disp
import threading
import ou
 

##############################################################################
def sys_admin (form, db, param, conn, message = ''):

  if not conn.superuser:
    app_error(form, param, conn, message = 'Invalid authority')
    return

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)
 
  table = webproc.table(cellpadding = '10', cellspacing = param.it_cellspc, width='100%', border = param.it_brdr)

  table.add_row().add_item(webproc.tag('A', 'Modify online details',\
      'href=office.py?jw_action=select_person1&next_prog=onlinef_edit&next_module=office.py'),\
      align="center", colspan='2')
  table.add_row().add_item(webproc.tag('A', 'Add adult', 'href=scout.py?jw_action=adultf_add'),\
      align="center", colspan='2')
  table.add_row().add_item(webproc.tag('A', 'Messages for Sysadmins', 'href=office.py?jw_action=sys_admf_msg'),\
      align="center", colspan='2')
  table.add_row().add_item(webproc.tag('A', 'Award administration', 'href=award.py?jw_action=awardf_adm'),\
      align="center", colspan='2')
 
  #print webproc.tag('A', 'Modify online details', 'href=office.py?jw_action=select_person1&next_prog=onlinef_edit')
  page.data.append(table.pr_table())
  page.output()
  return


##############################################################################
def select_person1 (form, db, param, conn):
  """This screen is used to select a person, adult or scout, needs to passed some parameters in the form:

       next_prog - where to go from here
  """

  next_prog = form.getfirst('next_prog', '')
  next_module = form.getfirst('next_module', '')
  surname = form.getfirst('surname', '')
  if next_prog == '':
    app_error(form, param, conn, message = 'Invalid input')
    return

  param_list = []

  jw_header(param, conn, menu_item = 800)
  print '<p>'

  cInp = 'First chars of Surname <INPUT TYPE="TEXT" NAME="surname" size="40" VALUE="' + surname + '"><br>'
  cInp += '<INPUT TYPE="SUBMIT" VALUE="Submit">'
  for k in form.keys():
    if k in ('jw_action', 'surname'):
      continue
    cInp += '<INPUT TYPE="HIDDEN" NAME="%s" VALUE="%s">' % (k, form[k].value)
  cInp += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="select_person1">'

  print webproc.tag('FORM', cInp, 'METHOD="POST" NAME="select_person1" ACTION="office.py"')

  if surname != '':
    list = dbobj.person_list(db, surname, 'A')
    table = webproc.table()
    for l in list.list:
      name = l['forename'] + ' '
      if len(l['initials']) > 0:
        name += l['initials'] + ' '
      name += l['surname']
      link = 'href=%s?jw_action=%s&person_id=%s' % (next_module, next_prog, l['scout_id'])
      for k in form.keys():
        if k in ('jw_action', 'surname'):
          continue
        link += '&%s=%s' % (k, form[k].value)
      table.add_row().add_item(webproc.tag('A', name, link))
    print table.pr_table()

  # This section just used for testing
  #print cgi.print_form(form)
  # end of test section
  webproc.form_footer()
  return

##############################################################################
def onlinef_edit(form, db, param, conn, id_msg = '', email_msg = '', pw_msg = ''):
  """Form to edit online details"""
  if not conn.superuser:
    app_error(form, param, conn, message = 'Invalid authority')

  next_prog = form.getfirst('next_prog', '')
  call_prog = form.getfirst('call_prog', '')
  scout_id = int(form.getfirst('person_id', '0'))

  adult = dbobj.adultrec(db, scout_id)
  if not adult.found:
    app_error(form, param, conn, message = 'Invalid identifier')
    return

  ol_id = form.getfirst('ol_id', adult.on_line_id)
  ol_email = form.getfirst('ol_email', adult.email)

  jw_header(param, conn, menu_item = 801)

  print '<hr>'
  print adult_disp_dets(adult, param) + '<BR>'

  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  if id_msg == '':
    edit_row(table, 'On-line ID:', 'ol_id', ol_id) 
  else:
    edit_row(table, 'On-line ID:', 'ol_id', ol_id, 0, id_msg, req=1) 
  if email_msg == '':
    edit_row(table, 'E-Mail:', 'ol_email', ol_email) 
  else:
    edit_row(table, 'E-Mail:', 'ol_email', ol_email, 0, email_msg, req=1) 
  #print '<hr>'

  item = table.add_row().add_item('Password')
  if pw_msg != '':
    item.data += '<br><SPAN CLASS="validation_message">' + pw_msg + '</SPAN>'
    item.styleclass = 'error'

  table.last_row().add_item('<INPUT TYPE="PASSWORD" NAME="pass1">')

  table.add_row().add_item('Repeat Password')
  table.last_row().add_item('<INPUT TYPE="PASSWORD" NAME="pass2">')

  #item = webproc.table_item('<INPUT TYPE="PASSWORD" NAME="password1">')

  item = table.add_row().add_item('<INPUT TYPE="SUBMIT" VALUE="SUBMIT">')
  item.data += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="onlinep_edit"'
  item.data += '<INPUT TYPE="HIDDEN" NAME="next_prog" VALUE="' + next_prog + '">'
  item.data += '<INPUT TYPE="HIDDEN" NAME="call_prog" VALUE="' + call_prog + '">'
  item.data += '<INPUT TYPE="HIDDEN" NAME="scout_id" VALUE=' + str(scout_id) + '>'

  print webproc.tag('FORM', table.pr_table(), 'METHOD="POST", NAME="ONLINEF_EDIT" ACTION="office.py"')


  webproc.form_footer()
  return

##############################################################################
def onlinep_edit(form, db, param, conn):
  """Processes the online edit form """
  # Get values of form fields
  next_prog = form.getfirst('next_prog', '')
  call_prog = form.getfirst('call_prog', '')
  scout_id = int(form.getfirst('scout_id', '0'))
  ol_id = form.getfirst('ol_id', '')
  ol_email = form.getfirst('ol_email', '')
  pass1 = form.getfirst('pass1', '')
  pass2 = form.getfirst('pass2', '')

  if not conn.superuser:
    app_error(form, param, conn, message = 'Invalid authority')
    return

  adult = dbobj.adultrec(db, scout_id)
  if not adult.found:
    app_error(form, param, conn, message = 'Invalid identifier')
    return

  if ol_id != adult.on_line_id:
    scout = dbobj.scoutrec(db, 0)
    scout.find_on_line_id(ol_id)
    if scout.scout_id != 0:
      ## the online id entered is not unique 
      onlinef_edit(form, db, param, conn, id_msg = 'Online ID is already in use')
      return

  if ol_email == '':
    onlinef_edit(form, db, param, conn, email_msg = 'E mail address must be entered')
    return

  if pass1 != '' and pass2 != '':
    if pass1 != pass2:
      onlinef_edit(form, db, param, conn, pw_msg = 'Password must be entered twice, exactly the same')
      return

  update_id = 0
  update_pw = 0
  
  if adult.on_line_id != ol_id:
    adult.on_line_id = ol_id
    update_id = 1
  adult.email = ol_email
  adult.update()

  if pass1 != '':
    adult.update_pw(pass1, '', conn.superuser)
    update_pw = 1

    # Create the mail message
    outer = MIMEMultipart()

    # Mail headers
    outer['Subject'] = 'Online account for ' + param.title
    outer['From'] = param.fromaddr
    outer['To'] = adult.email
    outer.preamble = 'Online account details'
    outer.epilogue = ''

    #Add the html header
    textfile = param.template_dir + '/' + param.email_header
    mf = open(textfile)
    msg_body = mf.read()
    mf.close()

    #Add the body of the email
    textfile = param.template_dir + '/' + param.email_account_create
    mf = open(textfile)
    msg_body += mf.read()
    mf.close()

    #Add the footer of the email
    textfile = param.template_dir + '/' + param.email_footer
    mf = open(textfile)
    msg_body += mf.read()
    mf.close()

    # Replace the placeholders 
    msg_body = string.replace(msg_body, '%forename%', adult.forename)
    msg_body = string.replace(msg_body, '%surname%', adult.surname)
    msg_body = string.replace(msg_body, '%title%', param.title)
    msg_body = string.replace(msg_body, '%site%', param.baseurl)
    msg_body = string.replace(msg_body, '%pythondir%', param.pythondir)
    msg_body = string.replace(msg_body, '%online_id%', adult.on_line_id)
    msg_body = string.replace(msg_body, '%password%', pass1)


    msgfile = MIMEText(msg_body, 'html')
    outer.attach(msgfile)

    mailserver = smtplib.SMTP(param.smtpserver)
    mailserver.sendmail(param.fromaddr, adult.email, outer.as_string())
    mailserver.quit()


  sys_admin(form, db, param, conn, message = 'Update successful')
  return

##############################################################################
def rolef_add1(form, db, param, conn, id_msg = '', email_msg = '', pw_msg = ''):
  """Form to add an adult role"""

  # get parameters from form
  ou_id = int(form.getfirst('ou_id', '0'))
  surname = form.getfirst('surname', '')
  disp_ou = int(form.getfirst('disp_ou', '0'))

  ourec = dbobj.ourec(db, ou_id)
  mngt_ou = ourec.get_mngt()

  # Build a display string for the top of the screen.
  if mngt_ou.found:
    levelstr = 'Add a new role to: <B>%s: %s</B>' % (ourec.name, mngt_ou.name)
  else:
    levelstr = 'Add a new role to: <B>%s</B>' % ourec.name

  # If the record was not found, exit with error
  if not ourec.found:
    app_error(form, param, conn, message = 'Org unit not found')
    return

  conn.ou_security(ou_id)

  # If you have edit rights here, you can add roles
  if not conn.write:
    app_error(form, param, conn, message = 'Invalid authority')
    return

  #Start building the form
  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  # Create table to  select from existing adults
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  table.add_row().add_item(levelstr, align = 'CENTER', colspan='2')
  cInp = 'First characters of Surname <INPUT TYPE="TEXT" NAME="surname" size="40" VALUE="%s"><br>'\
      % surname
  cInp += '<INPUT TYPE="SUBMIT" VALUE="Submit"><BR>'
  cInp += webproc.jbutton('Cancel', "ou_logic.py?jw_action=ouf_disp&ou_id=%d" % ou_id)

  form = webproc.form('office.py', cInp)
  form.add_hidden('ou_id', ou_id)
  form.add_hidden('disp_ou', disp_ou)
  form.add_hidden('jw_action', 'rolef_add1')
  page.data.append(form.pr_form())

  if surname != '':
    list = dbobj.person_list(db, surname, 'A')
    for l in list.list:
      name = l['forename'] + ' '
      if len(l['initials']) > 0:
        name += l['initials'] + ' '
      name += l['surname']
      table.add_row().add_item(webproc.tag('A', name,\
          'href=office.py?jw_action=rolef_add2&scout_id=%d&ou_id=%d&disp_ou=%d'%\
          (l['scout_id'], ou_id, disp_ou)))

  page.data.append(table.pr_table())
  page.output()

  return

##############################################################################
def rolef_add2(form, db, param, conn, id_msg = '', email_msg = '', pw_msg = ''):
  """Second Form to add an adult role"""

  # get parameters from form

  ou_id = int(form.getfirst('ou_id', '0'))
  scout_id = int(form.getfirst('scout_id', '0'))
  disp_ou = int(form.getfirst('disp_ou', '0'))
  descr = ''
  sec_level = 1

  ourec = dbobj.ourec(db, ou_id)
  mngt_ou = ourec.get_mngt()

  # If the record was not found, exit with error
  if not ourec.found:
    app_error(form, param, conn, message = 'Invalid org unit')
    return

  adult = dbobj.adultrec(db, scout_id)
  if not adult.found:
    app_error(form, param, conn, message = 'Invalid adult ID')
    return

  conn.ou_security(ou_id)

  # If you have edit rights here, you can add roles
  if not conn.write:
    app_error(form, param, conn, message = 'Invalid authority')
    return

  role = adult.role_by_ou(ourec.ou_id)
  if role.found:
    descr = role.title
    sec_level = role.security   

  #Start building the form
  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)
 
  outtab = outtable(param)

  # Create table to display values
  table = intable(param)

  if mngt_ou.found:
    disp = '%s: %s' % (ourec.name, mngt_ou.name)
  else:
    disp = '%s' % ourec.name

  if ourec.mngt:
    nDisp_ou = ourec.ou_owner
  else:
    nDisp_ou = disp_ou

  table.add_row().add_item('Add a role to')
  table.last_row().add_item(disp, header = 1, align='LEFT')

  table.add_row().add_item('Person:')
  item = table.last_row().add_item(adult.forename, header=1, align='LEFT')
  if adult.initials != '':
    item.data += ' ' + adult.initials
  item.data += ' ' + adult.surname
  item.header = 1

  table.add_row().add_item('Role description:')
  table.last_row().add_item('<INPUT TYPE="TEXT" NAME="descr" SIZE="50" MAXSIZE="100" VALUE="' + descr + '">')

  table.add_row().add_item('Security level:')
  if sec_level:
    table.last_row().add_item('Edit<INPUT TYPE="RADIO" NAME="sec_level" VALUE="1" CHECKED>  View only<INPUT TYPE="RADIO" NAME="sec_level" VALUE="0">')
  else:
    table.last_row().add_item('Edit<INPUT TYPE="RADIO" NAME="sec_level" VALUE="1">  View only<INPUT TYPE="RADIO" NAME="sec_level" VALUE="0" CHECKED>')

  table.add_row().add_item('<INPUT TYPE="SUBMIT" VALUE="Submit">')
  table.last_row().add_item(webproc.jbutton('Cancel',\
      'ou_logic.py?jw_action=ouf_disp&ou_id=%d' % (ou_id)))

  form = webproc.form('office.py', table.pr_table())
  form.add_hidden('ou_id', ou_id)
  form.add_hidden('disp_ou', nDisp_ou)
  form.add_hidden('scout_id', scout_id)
  form.add_hidden('jw_action', 'rolep_add')

  outtab.add_row().add_item(form.pr_form(), valign="TOP", rowspan='2')

  # Table to display leader details
  table = webproc.table(cellpadding = '5', cellspacing = param.it_cellspc, border = param.it_brdr)
  table.add_row().add_item('Name')
  item = table.last_row().add_item(adult.forename, header = 1, align = "LEFT")
  if adult.initials != '':
    item.data += ' ' + adult.initials
  item.data += ' ' + adult.surname
  table.add_row().add_item('Address')
  table.last_row().add_item(adult.addr1, header = 1, align = "LEFT")
  if adult.addr2 != '':
    table.add_row().add_item(' ')
    table.last_row().add_item(adult.addr2, header = 1, align = "LEFT")
  if adult.p_code != '' or adult.addr3 != '':
    table.add_row().add_item(' ')
    item = table.last_row().add_item('', header = 1, align = "LEFT")
    if adult.p_code != '':
      item.data = adult.p_code + ' '
    if adult.addr3 != '':
      item.data += adult.addr3
  table.add_row().add_item('Phone (H)')
  table.last_row().add_item(adult.telephone_h, header = 1, align = "LEFT")
  table.add_row().add_item('Phone (W)')
  table.last_row().add_item(adult.telephone_w, header = 1, align = "LEFT")
  table.add_row().add_item('Phone (Mobile)')
  table.last_row().add_item(adult.mobile, header = 1, align = "LEFT")
  table.add_row().add_item('E Mail')
  table.last_row().add_item(adult.email, header = 1, align = "LEFT")

  table.add_row().add_item(webproc.jbutton("Edit %s's details" % adult.forename,\
      'scout.py?jw_action=scoutf_edit&scout_id=%d&&ou_id=%d&nxt_module=ou.py&nxt_prog=ouf_disp&disp_ou=%d'\
      % (adult.scout_id, ou_id, nDisp_ou)))

  outtab.last_row().add_item(table.pr_table(), valign="TOP")

  # Table to display leader awards
  table = intable(param)
  table.add_row().add_item(' ')
  table.last_row().add_item(webproc.jbutton('Edit leader awards',\
      'award.py?jw_action=awardleadf_disp&leader_id=%d&ou_id=%d' % (adult.scout_id, ou_id)))

  # The scout record does all award stuff
  adult.achieve_list()
  for a in adult.achievelist:
    table.add_row().add_item(a.name)

  outtab.add_row().add_item(table.pr_table(), valign="TOP")

  page.data.append(outtab.pr_table())
  page.output()
  return


##############################################################################
def rolep_add(form, db, param, conn):
  """Processes the role add form(s)"""
  # Get values of form fields

  ou_id = int(form.getfirst('ou_id', '0'))
  scout_id = int(form.getfirst('scout_id', '0'))
  descr = form.getfirst('descr', '')
  sec_level = int(form.getfirst('sec_level', 0))
  nDisp_ou = int(form.getfirst('disp_ou', '0'))

  #if not conn.superuser:
  #  app_error(form, param, conn, message = 'Invalid authority')

  adult = dbobj.adultrec(db, scout_id)
  if not adult.found:
    app_error(form, param, conn, message = 'Invalid identifier')
    return

  ourec = dbobj.ourec(db, ou_id)
  if not ourec.found:
    app_error(form, param, conn, message = 'Invalid identifier')
    return

  mngt_ou = ourec.get_mngt()
  if not mngt_ou.found:
    ourec.add_mngt()
  mngt_ou = ourec.get_mngt()

  role = adult.role_by_ou(ourec.ou_id)

  conn.ou_security(ou_id)

  # If you have edit rights here, you can add roles
  if not conn.write:
    app_error(form, param, conn, message = 'Invalid authority')
    return

  role.scout_id = scout_id
  role.ou_id = ou_id
  role.title = descr
  role.security = sec_level
  role.status = 'C'
  role.add_edit()
  #dbobj.log_action(db, conn.scout_id, action, scout_id, type_id, sec_level)
  db.commit()

  ou.ouf_disp(form, db, param, conn, ou_id = nDisp_ou)

  return

##############################################################################
def rolep_del(form, db, param, conn):
  """Processes the role delete process"""
  # Get values of form fields

  nOu = int(form.getfirst('ou_id', '0'))
  scout_id = int(form.getfirst('scout_id', '0'))

  conn.ou_security(nOu)

  if not conn.superuser:
    app_error(form, param, conn, message = 'Invalid authority')
    return

  adult = dbobj.adultrec(db, scout_id)

  ourec = dbobj.ourec(db, nOu)

  if not adult.found:
    app_error(form, param, conn, message = 'Invalid identifier')
    return

  role = dbobj.rolerec(db, 0)
  role.find_role(nOu, scout_id)

  if role.found:
    #dbobj.log_action(db, conn.scout_id, action, role.scout_id, role.level_id, role.security)
    role.delete()

  if ourec.mngt:
    ou.ouf_disp(form, db, param, conn, ou_id = ourec.ou_owner)
  else:
    ou.ouf_disp(form, db, param, conn, ou_id = nOu)

  return


###############################################################################
def persf_edit(form, db, param, conn, message = ''):
  """personal details edit screen"""

  nUser = int(form.getfirst('user_id', '0'))

  User = dbobj.adultrec(db, nUser)
  if not User.found:
    app_error(form, param, conn, message="Invalid user identifier: " + str(nParent))
    return 

  # Can only edit your own details
  if nUser != conn.scout_id:
    #go to top of browse tree
    security_page(form, param, conn)
    return 

  jw_header(param, conn)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  cSubmitted = form.getfirst('submitted', 'N')
  if cSubmitted == 'Y':
    cForename 		= form.getfirst('forename', '')  
    cInitials 		= form.getfirst('initials', '')  
    cSurname 		= form.getfirst('surname', '')  
    cDate_of_Birth	= form.getfirst('date_of_birth', '')  
    cAddr1 		= form.getfirst('addr1', '')  
    cAddr2 		= form.getfirst('addr2', '')  
    cAddr3 		= form.getfirst('addr3', '')  
    cP_Code 		= form.getfirst('p_code', '')  
    cTelephone_h	= form.getfirst('telephone_h', '')  
    cTelephone_w	= form.getfirst('telephone_w', '')  
    cGender 		= form.getfirst('gender', '')  
    cEmail 		= form.getfirst('email', '')  
    cMobile 		= form.getfirst('mobile', '')  
    cAdd_Info 		= form.getfirst('add_info', '')  

  else:
    cForename 		= User.forename
    cInitials 		= User.initials
    cSurname 		= User.surname
    cDate_of_Birth 	= User.date_of_birth
    cAddr1 		= User.addr1
    cAddr2 		= User.addr2
    cAddr3 		= User.addr3
    cP_Code 		= User.p_code
    cTelephone_h	= User.telephone_h
    cTelephone_w	= User.telephone_w
    cGender 		= User.gender
    cEmail 		= User.email
    cMobile 		= User.mobile
    cAdd_Info 		= User.add_info


  # This table organises the personal details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = '65%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'Personal details'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=office.py?jw_action=profile"))
  row.items.append(item)
  table.rows.append(row)

  if cSubmitted == 'Y' and cForename == '':
    edit_row(table, 'Name :', 'forename', cForename, 0, 'Forename is a required field', req=1)
  else:
    edit_row(table, 'Name :', 'forename', cForename, req=1)

  edit_row(table, 'Initials :', 'initials', cInitials)

  if cSubmitted == 'Y' and cSurname == '':
    edit_row(table, 'Surname :', 'surname', cSurname, 0, 'Surname is a required field', req=1)
  else:
    edit_row(table, 'Surname :', 'surname', cSurname, req=1)

  if cDate_of_Birth == '':
    edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'date_of_birth', cDate_of_Birth)
  else:
    if cSubmitted == 'Y' and not val_date(cDate_of_Birth):
      edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'date_of_birth', cDate_of_Birth, 0, 'Invalid date format, please check', req=1)
    else:
      edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'date_of_birth', cDate_of_Birth)

  # Gender
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('SPAN', 'Gender :', 'CLASS="field_descr"'))
  row.items.append(item)
  cLine = '<INPUT TYPE="RADIO" NAME="gender" VALUE="M"'
  if cGender == 'M':
    cLine += ' CHECKED'
  cLine += '>Male&nbsp;&nbsp;<INPUT TYPE="RADIO" NAME="gender" VALUE="F"'
  if cGender == 'F':
    cLine += ' CHECKED'
  cLine +='>Female'
  item = webproc.table_item(cLine)
  row.items.append(item)
  table.rows.append(row)

  edit_row(table, 'Address :', 'addr1', cAddr1)
  edit_row(table, '', 'addr2', cAddr2)
  edit_row(table, '', 'addr3', cAddr3)
  edit_row(table, 'Postal code :', 'p_code', cP_Code, size = 4, maxlen = 4)
  edit_row(table, 'Telephone (Home) :', 'telephone_h', cTelephone_h)
  edit_row(table, 'Telephone (Work) :', 'telephone_w', cTelephone_w)
  edit_row(table, 'E-Mail :', 'email', cEmail)
  edit_row(table, 'Mobile :', 'mobile', cMobile)
  edit_comment(table, 'Additional information :', 'add_info', cAdd_Info)

  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="Userf_edit" VALUE="Submit">')
  item.data += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="persp_edit">'
  item.data += '<INPUT TYPE="HIDDEN" NAME="user_id" VALUE="' + str(User.scout_id)+ '">'
  item.data += '<INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y"> '
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="persf_edit" action="office.py"')

  print cForm 

  webproc.form_footer()
  return


##############################################################################
def persp_edit(form, db, param, conn):
  """Processes the input from the personal details edit screen """

  nUser = int(form.getfirst('user_id', '0'))

  User = dbobj.adultrec(db, nUser)
  if not User.found:
    app_error(form, param, conn, message="Invalid User identifier")
    return

  # Can only edit personal details
  if nUser != conn.scout_id:
    #go to top of browse tree
    security_page(form, param, conn)
    return 

  User.forename 	= form.getfirst('forename', '')
  User.initials 	= form.getfirst('initials', '')
  User.surname 		= form.getfirst('surname', '')
  User.date_of_birth 	= form.getfirst('date_of_birth', '')
  User.mobile	 	= form.getfirst('mobile', '')
  User.email	 	= form.getfirst('email', '')
  User.add_info 	= form.getfirst('add_info', '')
  User.gender	 	= form.getfirst('gender', '')
  User.addr1	 	= form.getfirst('addr1', '')
  User.addr2	 	= form.getfirst('addr2', '')
  User.addr3	 	= form.getfirst('addr3', '')
  User.p_code	 	= form.getfirst('p_code', '')
  User.telephone_h 	= form.getfirst('telephone_h', '')
  User.telephone_w 	= form.getfirst('telephone_w', '')

  if User.forename == '' or User.surname == '':
    persf_edit(form, db, param, conn)
    return

  if not val_date(User.date_of_birth):
    persf_edit(form, db, param, conn)
    return

  User.update()

  profile(form, db, param, conn)

  return


##############################################################################
def extractf_unit(form, db, param, conn, id_msg = '', email_msg = '', pw_msg = ''):
  """Form to extract unit details"""

  # Check if permitted
  if not conn.sign_in:
    app_error(form, param, conn, message = 'Invalid authority')

  # get parameters from form

  unit_id = int(form.getfirst('unit_id', '0'))

  # Get the unit record
  unit = dbobj.unitrec(db, unit_id)
  if not unit.found:
    app_error(form, param, conn, message = 'Invalid parameter')

  #Start building the form
  jw_header(param, conn, menu_item = 803)

  # Create outer table
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  row = webproc.table_row()

  # display the level details at the top
  item = webproc.table_item('Extract and mail unit member details', align = 'CENTER', colspan='4', header = 1)
  row.items.append(item)
  table.rows.append(row)
  row = webproc.table_row()

  # Create form to select fields to be extracted
  cCheck = '<B>SCOUT<BR></B>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_forename" VALUE="Y" CHECKED> First name<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_initials" VALUE="Y" CHECKED> Initials<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_surname" VALUE="Y" CHECKED> Surname<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_dob" VALUE="Y" CHECKED> Date of Birth<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_age" VALUE="Y" CHECKED> Age<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_address" VALUE="Y" CHECKED> Address<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_email" VALUE="Y" CHECKED> E-mail address<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_gender" VALUE="Y" CHECKED> Gender<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_status" VALUE="Y" CHECKED> Status<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_school" VALUE="Y" CHECKED> School<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="sc_add_info" VALUE="Y" CHECKED> Additional info<BR>'
  item = webproc.table_item(cCheck, valign="TOP")
  row.items.append(item)

  cCheck = '<B>PARENT 1</B><BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p1_forename" VALUE="Y" CHECKED> First name<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p1_initials" VALUE="Y" CHECKED> Initials<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p1_surname" VALUE="Y" CHECKED> Surname<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p1_phone_h" VALUE="Y" CHECKED> Phone (H)<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p1_phone_w" VALUE="Y" CHECKED> Phone (W)<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p1_mobile" VALUE="Y" CHECKED> Mobile<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p1_email" VALUE="Y" CHECKED> E-mail address<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p1_add_info" VALUE="Y" CHECKED> Additional info<BR>'
  item = webproc.table_item(cCheck, valign="TOP")
  row.items.append(item)

  cCheck = '<B>PARENT 2</B><BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p2_forename" VALUE="Y" CHECKED> First name<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p2_initials" VALUE="Y" CHECKED> Initials<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p2_surname" VALUE="Y" CHECKED> Surname<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p2_phone_h" VALUE="Y" CHECKED> Phone (H)<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p2_phone_w" VALUE="Y" CHECKED> Phone (W)<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p2_mobile" VALUE="Y" CHECKED> Mobile<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p2_email" VALUE="Y" CHECKED> E-mail address<BR>'
  cCheck += '<INPUT TYPE="CHECKBOX" NAME="p2_add_info" VALUE="Y" CHECKED> Additional info<BR>'
  item = webproc.table_item(cCheck, valign="TOP")
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  cCheck = '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="extractp_unit">'
  cCheck += '<INPUT TYPE="HIDDEN" NAME="unit_id" VALUE="' + str(unit.unit_id) + '">'
  cCheck += '<INPUT TYPE="SUBMIT" VALUE="Submit">'
  item = webproc.table_item(cCheck)
  row.items.append(item)
  table.rows.append(row)

  print webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="extractf_unit" ACTION="office.py"')

  # Form just for cancel
  cInp = '<BR><INPUT TYPE="SUBMIT" VALUE="Cancel">'
  cInp += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="unitf_disp">'
  print webproc.tag('FORM', cInp, 'METHOD="POST" NAME="extr" ACTION="scout.py"')


  webproc.form_footer()
  return

##############################################################################
def extractp_unit(form, db, param, conn):
  """Processes the creation and mailing of unit extract details"""
  # Get values of form fields

  unit_id = int(form.getfirst('unit_id', '0'))

  unit = dbobj.unitrec(db, unit_id)
  if not unit.found:
    app_error(form, param, conn, message = 'Invalid identifier')

  # If you have edit rights here, you can add roles
  # can_edit = edit_check(db, type, type_id, conn.scout_id)
  if not conn.sign_in:
    app_error(form, param, conn, message = 'Invalid authority')
    return

  d = datetime.datetime.today()
  filename = 'extract-%s-%s-%s.csv' % (d.year, d.month, d.day)
  fullname = param.extract_dir + '/' + filename
  f = open(fullname, 'w+')
  heading = ''
  if form.getfirst('sc_forename', '') == 'Y':
    heading += 'Scout name, '
  if form.getfirst('sc_initials', '') == 'Y':
    heading += 'Initials, '
  if form.getfirst('sc_surname', '') == 'Y':
    heading += 'Surname, '
  if form.getfirst('sc_dob', '') == 'Y':
    heading += 'Date of Birth, '
  if form.getfirst('sc_age', '') == 'Y':
    heading += 'Age, '
  if form.getfirst('sc_address', '') == 'Y':
    heading += 'Address1, Address2, Address3, Postal code, '
  if form.getfirst('sc_email', '') == 'Y':
    heading += 'E mail address, '
  if form.getfirst('sc_gender', '') == 'Y':
    heading += 'Gender, '
  if form.getfirst('sc_status', '') == 'Y':
    heading += 'Status, '
  if form.getfirst('sc_school', '') == 'Y':
    heading += 'School, '
  if form.getfirst('sc_add_info', '') == 'Y':
    heading += 'Additional information, '

  heading += 'Parent 1, '
  if form.getfirst('p1_forename', '') == 'Y':
    heading += 'Parent name, '
  if form.getfirst('p1_initials', '') == 'Y':
    heading += 'Initials, '
  if form.getfirst('p1_surname', '') == 'Y':
    heading += 'Surname, '
  if form.getfirst('p1_phone_h', '') == 'Y':
    heading += 'Phone (H), '
  if form.getfirst('p1_phone_w', '') == 'Y':
    heading += 'Phome (W), '
  if form.getfirst('p1_mobile', '') == 'Y':
    heading += 'Mobile, '
  if form.getfirst('p1_email', '') == 'Y':
    heading += 'E-mail address, '
  if form.getfirst('p1_add_info', '') == 'Y':
    heading += 'Additional information, '

  heading += 'Parent 1, '
  if form.getfirst('p2_forename', '') == 'Y':
    heading += 'Parent name, '
  if form.getfirst('p2_initials', '') == 'Y':
    heading += 'Initials, '
  if form.getfirst('p2_surname', '') == 'Y':
    heading += 'Surname, '
  if form.getfirst('p2_phone_h', '') == 'Y':
    heading += 'Phone (H), '
  if form.getfirst('p2_phone_w', '') == 'Y':
    heading += 'Phome (W), '
  if form.getfirst('p2_mobile', '') == 'Y':
    heading += 'Mobile, '
  if form.getfirst('p2_email', '') == 'Y':
    heading += 'E-mail address, '
  if form.getfirst('p2_add_info', '') == 'Y':
    heading += 'Additional information, '

  f.write(heading + '\n')

  unit.scout_list()
  for s in unit.scoutlist:
    detail = ''
    if form.getfirst('sc_forename', '') == 'Y':
      detail += no_comma(s.forename) + ', '
    if form.getfirst('sc_initials', '') == 'Y':
      detail += no_comma(s.initials) + ', '
    if form.getfirst('sc_surname', '') == 'Y':
      detail += no_comma(s.surname) + ', '
    if form.getfirst('sc_dob', '') == 'Y':
      detail += str(s.date_of_birth) + ', '
    if form.getfirst('sc_age', '') == 'Y':
      detail += str(s.years) + ' years & ' + str(s.months) + ' Months, '
    if form.getfirst('sc_address', '') == 'Y':
      detail += '%s, %s, %s, %s, ' % (no_comma(s.addr1), no_comma(s.addr2), no_comma(s.addr3), no_comma(s.p_code))
    if form.getfirst('sc_email', '') == 'Y':
      detail += no_comma(s.email) + ', '
    if form.getfirst('sc_gender', '') == 'Y':
      detail += no_comma(s.gender) + ', '
    if form.getfirst('sc_status', '') == 'Y':
      detail += no_comma(s.status) + ', '
    if form.getfirst('sc_school', '') == 'Y':
      detail += no_comma(s.school) + ', '
    if form.getfirst('sc_add_info', '') == 'Y':
      detail += no_comma(s.add_info) + ', '
   
    # Blank column
    detail += ', ' 
    p1 = dbobj.adultrec(db, s.parent1)
    if form.getfirst('p1_forename', '') == 'Y':
      detail += no_comma(p1.forename) + ', '
    if form.getfirst('p1_initials', '') == 'Y':
      detail += no_comma(p1.initials) + ', '
    if form.getfirst('p1_surname', '') == 'Y':
      detail += no_comma(p1.surname) + ', '
    if form.getfirst('p1_phone_h', '') == 'Y':
      detail += no_comma(p1.telephone_h) + ', '
    if form.getfirst('p1_phone_w', '') == 'Y':
      detail += no_comma(p1.telephone_w) + ', '
    if form.getfirst('p1_mobile', '') == 'Y':
      detail += no_comma(p1.mobile) + ', '
    if form.getfirst('p1_email', '') == 'Y':
      detail += no_comma(p1.email) + ', '
    if form.getfirst('p1_add_info', '') == 'Y':
      detail += no_comma(p1.add_info) + ', '
 
    detail += ', ' 
    p2 = dbobj.adultrec(db, s.parent2)
    if p2.found:
      if form.getfirst('p2_forename', '') == 'Y':
        detail += no_comma(p2.forename) + ', '
      if form.getfirst('p2_initials', '') == 'Y':
        detail += no_comma(p2.initials) + ', '
      if form.getfirst('p2_surname', '') == 'Y':
        detail += no_comma(p2.surname) + ', '
      if form.getfirst('p2_phone_h', '') == 'Y':
        detail += no_comma(p2.telephone_h) + ', '
      if form.getfirst('p2_phone_w', '') == 'Y':
        detail += no_comma(p2.telephone_w) + ', '
      if form.getfirst('p2_mobile', '') == 'Y':
        detail += no_comma(p2.mobile) + ', '
      if form.getfirst('p2_email', '') == 'Y':
        detail += no_comma(p2.email) + ', '
      if form.getfirst('p2_add_info', '') == 'Y':
        detail += no_comma(p2.add_info) + ', '
 
    f.write(detail + '\n')

  # Get details of the logged in user
  user = dbobj.adultrec(db, conn.scout_id)  

  # Create the mail message
  outer = MIMEMultipart()

  # Mail headers
  outer['Subject'] = 'Scout extract'
  outer['From'] = param.fromaddr
  outer['To'] = user.email
  outer.preamble = 'Scout detail of extract'
  outer.epilogue = ''

  #Add the explanatory text to the message
  textfile = param.template_dir + '/' + param.email_extract_msg
  mf = open(textfile)
  msgfile = MIMEText(mf.read())
  outer.attach(msgfile)

  # Attach the created file to the e-mail.
  f.seek(0)
  msgfile = MIMEText(f.read())
  msgfile.add_header('Content-Disposition', 'attachment', filename=filename)
  outer.attach(msgfile)

  mailserver = smtplib.SMTP(param.smtpserver)
  #mailserver.set_debuglevel(1)
  mailserver.sendmail(param.fromaddr, user.email, outer.as_string())
  mailserver.quit()

  f.close()

  heir_disp.unitf_disp(form, db, param, conn, inp_unit = unit.unit_id)
  return

##############################################################################
def no_comma(inp_string):
  cStr = inp_string
  if cStr is None:
    cStr = ''
  cStr = cStr.replace('\n', '')
  cStr = cStr.replace('\r', ' ')
  cStr = cStr.replace('\t', '')
  return cStr.replace(',', '')


##############################################################################
def adult_disp_dets(adult, param):
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(adult.forename + ' ', header = 1, width = '50%', align = 'left')
  if adult.initials != '':
    item.data += adult.initials + ' '
  item.data += adult.surname
  row.items.append(item)

  item = webproc.table_item('<B>Phone (H): </B>' + adult.telephone_h, width = '50%', align = 'left')
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item(adult.addr1, align = 'left')
  row.items.append(item)
  item = webproc.table_item('<B>Phone (W): </B>' + adult.telephone_w, width = '50%', align = 'left')
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item(adult.addr2, align = 'left')
  row.items.append(item)
  item = webproc.table_item('<B>Phone (Mob): </B>' + adult.mobile, width = '50%', align = 'left')
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item(adult.addr3 + ' ' + adult.p_code, align = 'left')
  row.items.append(item)
  table.rows.append(row)

  return table.pr_table()

##############################################################################
def sys_admf_msg(form, db, param, conn):
  """This page displays new messages for sys_admins """
 
  # Only superusers here
  if not conn.sign_in or not conn.superuser:
    security_page(form, param, conn)
    return

  msg_status = form.getfirst('msg_status', 'N')

  # Print the top of the page
  jw_header(param, conn)

  table = webproc.table(cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, width='100%', border = param.it_brdr)
  row = webproc.table_row()
  if msg_status == '*':
    item = webproc.table_item(webproc.tag('H2', 'ALL messages for system administrators'), colspan="4")
    row.items.append(item)
    item = webproc.table_item(webproc.jbutton('Display new and pending only', 'office.py?jw_action=sys_admf_msg&msg_status=N', need_form=1), align="RIGHT")
    row.items.append(item)
  else:
    item = webproc.table_item(webproc.tag('H2', 'New messages for system administrators'), colspan="4")
    row.items.append(item)
    item = webproc.table_item(webproc.jbutton('Display all messages', 'office.py?jw_action=sys_admf_msg&msg_status=*', need_form=1), align = "RIGHT")
    row.items.append(item)
  table.rows.append(row)

  new_messages = dbobj.sys_admin_msg_list(db, status=msg_status)
  for msg in new_messages.messagelist:

    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('A', msg.name, 'href=office.py?jw_action=sys_admf_disp&msg_id=' + str(msg.msg_id)))
    row.items.append(item)
    item = webproc.table_item(msg.subject)
    row.items.append(item)
    item = webproc.table_item(msg.create_tm)
    row.items.append(item)
    if msg_status == '*':
      item = webproc.table_item(msg.status)
      row.items.append(item)
    table.rows.append(row)

  if msg_status != '*':
    pend_messages = dbobj.sys_admin_msg_list(db, status='P')
    if len(pend_messages.messagelist) > 0:
      row = webproc.table_row()
      item = webproc.table_item(webproc.tag('H3', 'Pending messages'))
      row.items.append(item)
      table.rows.append(row)
      for msg in pend_messages.messagelist:
        row = webproc.table_row()
        item = webproc.table_item(webproc.tag('A', msg.name, 'href=office.py?jw_action=sys_admf_disp&msg_id=' + str(msg.msg_id)))
        row.items.append(item)
        item = webproc.table_item(msg.subject)
        row.items.append(item)
        item = webproc.table_item(msg.create_tm)
        row.items.append(item)
        table.rows.append(row)


  print table.pr_table()
  webproc.form_footer()
  return




##############################################################################
def sys_admf_disp(form, db, param, conn):

  # Only superusers here
  if not conn.sign_in or not conn.superuser:
    security_page(form, param, conn)
    return

  message_id = form.getfirst('msg_id', '')
  message = dbobj.messagerec(db, int(message_id))
  if not message.found:
    app_error(form, param, conn, message = 'Invalid message identifier')
    return

  jw_header(param, conn)

  table = webproc.table(cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, width='100%', border = param.it_brdr)

  row = webproc.table_row()
  item = webproc.table_item('Name', width="20%")
  row.items.append(item)
  item = webproc.table_item(message.name)
  row.items.append(item)
  table.rows.append(row)

  disp_line(table, 'Email address', message.email)
  disp_line(table, 'Phone no', message.telephone)
  disp_line(table, 'Subject', message.subject)

  row = webproc.table_row()
  item = webproc.table_item(message.body, colspan="2")
  row.items.append(item)
  table.rows.append(row)

  edit_comment(table, 'Response :', 'msg_response', '')

  row = webproc.table_row()
  item = webproc.table_item('<B>Previous updates:</B><BR>' + str(message.msg_response), colspan="2")
  item.data = string.replace(item.data, '\n', '<BR>')
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  cButt = '<INPUT TYPE="BUTTON" onclick="submitform(\'' + message.status + '\')", value="Update">' + '&nbsp&nbsp'
  if message.status != 'C':
    cButt += '<INPUT TYPE="BUTTON" onclick="submitform(\'C\')", value="Mark as closed">' + '&nbsp&nbsp'
  if message.status != 'P':
    cButt += '<INPUT TYPE="BUTTON" onclick="submitform(\'P\')", value="Mark as pending">' + '&nbsp&nbsp'
    cButt += '<INPUT TYPE="BUTTON" onclick="submitform(\' \')", value="Cancel">' + '&nbsp&nbsp'
  item = webproc.table_item(cButt, colspan="2")
  item.data += '<INPUT TYPE="HIDDEN" NAME="msg_id" VALUE=' + str(message.msg_id) + '>'
  item.data += '<INPUT TYPE="HIDDEN" NAME="status" VALUE="' + message.status + '">'
  item.data += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="sys_admp_disp">'
  row.items.append(item)
  table.rows.append(row)

  print webproc.tag('FORM', table.pr_table(), 'ID="f1disp" ACTION="office.py" METHOD="POST" NAME="msg_f1"')
  js = '<SCRIPT LANGUAGE="Javascript" TYPE="text/javascript">\nfunction submitform(inp_status) {\n  var inp_form = document.getElementById(\'f1disp\');\n  inp_form.status.value=inp_status\n  inp_form.submit()\n}\n</SCRIPT>'
  print js

  webproc.form_footer()
  return

##############################################################################
def sys_admp_disp(form, db, param, conn):

  # Only superusers here
  if not conn.sign_in or not conn.superuser:
    security_page(form, param, conn)
    return

  message_id = form.getfirst('msg_id', '')
  message = dbobj.messagerec(db, int(message_id))
  if not message.found:
    app_error(form, param, conn, message = 'Invalid message identifier')
    return

  # Get variables
  status = form.getfirst('status', '')
  msg_response = form.getfirst('msg_response', '')

  if string.strip(status) != '' and string.strip(msg_response) != '':
    # check status
    if string.find('CNRP', status) == -1: 
      sys_admf_msg(form, db, param, conn)
      return
    user = dbobj.adultrec(db, conn.scout_id)

    message.status = status
    if message.msg_response == None:
      message.msg_response = ''
    if message.msg_response != '':
      message.msg_response = message.msg_response + '\n\n'
    message.msg_response = message.msg_response + 'Update by :' + user.forename + ' ' + user.surname + ' at: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    message.msg_response += '\n' + msg_response
    message.update()

  sys_admf_msg(form, db, param, conn)
  return

##############################################################################
def emailf_ou(form, db, param, conn, id_msg = '', email_msg = ''):
  """Form to create email to unit members"""

  # Check if permitted
  if not conn.sign_in:
    app_error(form, param, conn, message = 'Invalid authority')

  # get parameters from form

  ou_id = int(form.getfirst('ou_id', '0'))

  # Get the unit record
  ourec = dbobj.ourec(db, ou_id)
  if not ourec.found:
    app_error(form, param, conn, message = 'Invalid parameter')
    return

  #Start building the form
  jw_header(param, conn, menu_item = 803)

  # Create outer table
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  row = webproc.table_row()

  # display the level details at the top
  item = webproc.table_item('Email to unit members and leaders', align = 'CENTER', colspan='2', header = 1)
  row.items.append(item)
  table.rows.append(row)

  # Create subject line
  row = webproc.table_row()
  item = webproc.table_item('Subject:&nbsp')
  item.data += '<INPUT TYPE="TEXT" SIZE="80" NAME="subject" TABINDEX=1>'
  row.items.append(item)
  table.rows.append(row)
 
  row = webproc.table_row()
  item = webproc.table_item('Mail message:<BR>')
  item.data += '<TEXTAREA COLS="80" ROWS="15" NAME="msg_body" TABINDEX=2></TEXTAREA>'
  row.items.append(item)
  table.rows.append(row)
 
  row = webproc.table_row()
  cCheck = '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="emailp_ou">'
  cCheck += '<INPUT TYPE="HIDDEN" NAME="ou_id" VALUE="' + str(ourec.ou_id) + '">'
  cCheck += '<INPUT TYPE="SUBMIT" VALUE="Submit">'
  item = webproc.table_item(cCheck)
  item.data += '&nbsp&nbsp&nbsp' + webproc.jbutton('Cancel', 'ou_logic.py?jw_action=ouf_disp&ou_id=' + str(ourec.ou_id), need_form=0)
  row.items.append(item)
  table.rows.append(row)

  print webproc.tag('FORM', table.pr_table(), 'METHOD="POST" ACTION="office.py"')

  webproc.form_footer()
  return

##############################################################################
def emailp_ou(form, db, param, conn):
  """Processes the creation and mailing of unit email details"""
  # Get values of form fields

  ou_id = int(form.getfirst('ou_id', '0'))
  subject = form.getfirst('subject', '')
  msg_body = form.getfirst('msg_body', '')

  msg_body = '<P>' + msg_body + '</P>'
  msg_body = string.replace(msg_body, '\r\n\r\n', '</P><P>')
  msg_body = string.replace(msg_body, '\r\n', '<BR>')

  if subject == '' or msg_body == '':
    ou.ouf_disp(form, db, param, conn, ou_id = ou_id)
    return

  ourec = dbobj.ourec(db, ou_id)
  if not ourec.found:
    app_error(form, param, conn, message = 'Invalid identifier')

  # If you have edit rights here, you can add roles
  # can_edit = edit_check(db, type, type_id, conn.scout_id)
  if not conn.sign_in:
    app_error(form, param, conn, message = 'Invalid authority')
    return

  error_file = open('/tmp/jim1.log', 'w')

  # Here we spawn off a back ground process to send the emails
  pid = os.spawnl(os.P_NOWAIT, 'unit-email.py', 'unit-email.py', str(ourec.ou_id), subject, msg_body, str(conn.scout_id))
  #pid = os.spawnl(os.P_NOWAIT, 'unit-email.py', 'unit-email.py', "param1", "param2")

  error_file.write("PID = %d\nou_id = %d\nsubject = '%s'\nmsg = '%s'\nuser = %d\n" % (pid, ourec.ou_id, subject, msg_body, conn.scout_id))
  error_file.close()

  ou.ouf_disp(form, db, param, conn, ou_id = ourec.ou_id)
  return


##############################################################################
# Mail program logic, decides which form/screen to display

try:

  form = cgi.FieldStorage()
  param = dbobj.paramrec()
  db = dbobj.dbinstance(param.dbname)
  conn = dbobj.connectrec(db)

  if conn.new_conn:
    app_error(form, param, conn, message = 'Invalid selection')
  else:  
    if form.has_key('jw_action'):
      # if a form action is specified do it
      if form.getfirst("jw_action") == "sys_admin":
        sys_admin(form, db, param, conn)
      elif form.getfirst("jw_action") == "select_person1":
        select_person1(form, db, param, conn)
      elif form.getfirst("jw_action") == "onlinef_edit":
        onlinef_edit(form, db, param, conn)
      elif form.getfirst("jw_action") == "onlinep_edit":
        onlinep_edit(form, db, param, conn)
      elif form.getfirst("jw_action") == "rolef_add1":
        rolef_add1(form, db, param, conn)
      elif form.getfirst("jw_action") == "rolef_add2":
        rolef_add2(form, db, param, conn)
      elif form.getfirst("jw_action") == "rolep_add":
        rolep_add(form, db, param, conn)
      elif form.getfirst("jw_action") == "rolep_del":
        rolep_del(form, db, param, conn)
      elif form.getfirst("jw_action") == "persf_edit":
        persf_edit(form, db, param, conn)
      elif form.getfirst("jw_action") == "persp_edit":
        persp_edit(form, db, param, conn)
      elif form.getfirst("jw_action") == "extractf_unit":
        extractf_unit(form, db, param, conn)
      elif form.getfirst("jw_action") == "extractp_unit":
        extractp_unit(form, db, param, conn)
      elif form.getfirst("jw_action") == "sys_admf_msg":
        sys_admf_msg(form, db, param, conn)
      elif form.getfirst("jw_action") == "sys_admf_disp":
        sys_admf_disp(form, db, param, conn)
      elif form.getfirst("jw_action") == "sys_admp_disp":
        sys_admp_disp(form, db, param, conn)
      elif form.getfirst("jw_action") == "emailf_ou":
        emailf_ou(form, db, param, conn)
      elif form.getfirst("jw_action") == "emailp_ou":
        emailp_ou(form, db, param, conn)

      else:
        # Display the home page if you don't know what to do
        app_error(form, param, conn, message = 'Invalid selection')
    else:
      # Display the home page if you don't know what to do
      app_error(form, param, conn, message = 'Invalid selection input')
except:  
  error_proc()
  raise

db.commit()
