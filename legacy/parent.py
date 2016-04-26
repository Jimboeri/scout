#!/usr/bin/python
import webproc
import webscout
import dbobj
from procs import *

###############################################################################
def parentf_edit(form, db, param, conn, message = ''):
  """Parent edit screen"""

  nScout = int(form.getfirst('scout_id', '0'))
  nParent = int(form.getfirst('parent_id', '0'))

  parent = dbobj.adultrec(db, nParent)
  if not parent.found:
    webscout.app_error(form, param, conn, message="Invalid parent identifier")
    return 

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    webscout.app_error(form, param, conn, message="Invalid scout identifier")
    return 

  can_edit = edit_check(db, 'P', scout.unit_id, conn.scout_id)
  if not can_edit:
    #go to top of browse tree
    webscout.security_page(form, param, conn)
    return 

  webscout.jw_header(param, conn)
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
    cForename 		= parent.forename
    cInitials 		= parent.initials
    cSurname 		= parent.surname
    cDate_of_Birth 	= parent.date_of_birth
    cAddr1 		= parent.addr1
    cAddr2 		= parent.addr2
    cAddr3 		= parent.addr3
    cP_Code 		= parent.p_code
    cTelephone_h	= parent.telephone_h
    cTelephone_w	= parent.telephone_w
    cGender 		= parent.gender
    cEmail 		= parent.email
    cMobile 		= parent.mobile
    cAdd_Info 		= parent.add_info

  # This table organises the scouts personal details
  table = webproc.table()
  table.width='100%'
  table.cellpadding = '0'
  table.cellspacing = '0'
  table.border = '0'

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
  item = webproc.table_item(webproc.tag('H2', 'Parent details'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=scoutf_disp&scout_id=" + str(scout.scout_id)))
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

  if cSubmitted == 'Y' and not val_date(cDate_of_Birth):
    edit_row(table, 'Date of Birth :', 'date_of_birth', cDate_of_Birth, 0, 'Invalid date format, please check', req=1)
  else:
    edit_row(table, 'Date of Birth :', 'date_of_birth', cDate_of_Birth, req=1)

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
  edit_row(table, 'Postal code :', 'p_code', cP_Code)
  edit_row(table, 'Telephone (Home) :', 'telephone_h', cTelephone_h)
  edit_row(table, 'Telephone (Work) :', 'telephone_w', cTelephone_w)
  edit_row(table, 'E-Mail :', 'email', cEmail)
  edit_row(table, 'Mobile :', 'mobile', cMobile)
  edit_comment(table, 'Additional information :', 'add_info', cAdd_Info)

  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="parentf_edit" VALUE="Submit"><INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="parentp_edit"> <INPUT TYPE="HIDDEN" NAME="scout_id" VALUE="' + str(scout.scout_id)+ '" <INPUT TYPE="HIDDEN" NAME="parent_id" VALUE="' + str(parent.scout_id)+ '"> <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y"> ')
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="parentf_edit" action="scout.py"')

  print cForm

  webproc.form_footer()
  return


##############################################################################
def parentp_edit(form, db, param, conn):
  """Processes the input from the parent edit screen """

  nScout = int(form.getfirst('scout_id', '0'))
  nParent = int(form.getfirst('scout_id', '0'))

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    webscout.app_error(form, param, conn, message="Invalid scout identifier")
    return

  parent = dbobj.adultrec(db, nParent)
  if not parent.found:
    webscout.app_error(form, param, conn, message="Invalid parent identifier")
    return

  can_edit = edit_check(db, 'P', scout.unit_id, conn.scout_id)
  if not can_edit:
    #go to top of browse tree
    webscout.security_page(form, param, conn)
    return 

  parent.forename 	= form.getfirst('forename', '')
  parent.initials 	= form.getfirst('initials', '')
  parent.surname 	= form.getfirst('surname', '')
  parent.date_of_birth 	= form.getfirst('date_of_birth', '')
  parent.mobile	 	= form.getfirst('mobile', '')
  parent.email	 	= form.getfirst('email', '')
  parent.add_info 	= form.getfirst('add_info', '')
  parent.gender	 	= form.getfirst('gender', '')
  parent.addr1	 	= form.getfirst('addr1', '')
  parent.addr2	 	= form.getfirst('addr2', '')
  parent.addr3	 	= form.getfirst('addr3', '')
  parent.p_code	 	= form.getfirst('p_code', '')
  parent.telephone_h 	= form.getfirst('telephone_h', '')
  parent.telephone_w 	= form.getfirst('telephone_w', '')

  if parent.forename == '' or parent.surname == '':
    parentf_edit(form, db, param, conn)
    return

  #if not val_date(parent.date_of_birth):
  #  parentf_edit(form, db, param, conn)
  #  return

  parent.update()

  scoutf_disp(form, db, param, conn)
  return


