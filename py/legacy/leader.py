#!/usr/bin/python

import webproc
import cgi
import cgitb; cgitb.enable()
import webscout
import dbobj
from procs import *
from webscout import *
import heir_disp

###############################################################################
def leaderf_edit(form, db, param, conn, message = ''):
  """Parent edit screen"""

  cLevel = form.getfirst('ou_level', '')
  nOu = int(form.getfirst('ou_id', '0'))
  nLeader = int(form.getfirst('leader_id', '0'))

  leader = dbobj.adultrec(db, nLeader)
  if not leader.found:
    webscout.app_error(form, param, conn, message="Invalid leader identifier")
    return 

  conn.ou_security(nOu)
  can_edit = conn.write

  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
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
    cForename 		= leader.forename
    cInitials 		= leader.initials
    cSurname 		= leader.surname
    cDate_of_Birth 	= leader.date_of_birth
    cAddr1 		= leader.addr1
    cAddr2 		= leader.addr2
    cAddr3 		= leader.addr3
    cP_Code 		= leader.p_code
    cTelephone_h	= leader.telephone_h
    cTelephone_w	= leader.telephone_w
    cGender 		= leader.gender
    cEmail 		= leader.email
    cMobile 		= leader.mobile
    cAdd_Info 		= leader.add_info

  # This table organises the scouts personal details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
    cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = '20%'
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = '40%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  table.add_row().add_item(webproc.tag('H2', 'Leader details'))
  item = table.last_row().add_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>')
  item.styleclass = 'error'
  table.last_row().add_item(webproc.jbutton('Cancel', "office.py?jw_action=rolef_add2&type=%s&type_id=%d&scout_id=%d" % (cLevel, nOu, leader.scout_id)))

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
  table.add_row().add_item(webproc.tag('SPAN', 'Gender :', 'CLASS="field_descr"'))
  cLine = '<INPUT TYPE="RADIO" NAME="gender" VALUE="M"'
  if cGender == 'M':
    cLine += ' CHECKED'
  cLine += '>Male&nbsp;&nbsp;<INPUT TYPE="RADIO" NAME="gender" VALUE="F"'
  if cGender == 'F':
    cLine += ' CHECKED'
  cLine +='>Female'
  table.last_row().add_item(cLine)

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
  item = table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="leaderf_edit" VALUE="Submit">')

  # Output the scout edit form
  cForm = webproc.form('leader.py', table.pr_table()) 
  cForm.add_hidden('Submitted', 'Y')
  cForm.add_hidden("jw_action", "leaderp_edit")
  cForm.add_hidden("leader_id", str(leader.scout_id))
  cForm.add_hidden("ou_level", cLevel)
  cForm.add_hidden("ou_id", str(nOu))

  print cForm.pr_form()
  
  webproc.form_footer()
  return


##############################################################################
def leaderp_edit(form, db, param, conn):
  """Processes the input from the leader.edit screen """

  nLeader = int(form.getfirst('leader_id', '0'))
  cLevel = form.getfirst('ou_level', '')
  nOu = int(form.getfirst('ou_id', '0'))

  leader = dbobj.adultrec(db, nLeader)
  if not leader.found:
    webscout.app_error(form, param, conn, message="Invalid leader identifier")
    return

  conn.ou_security(nOu)
  can_edit = conn.write

  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  leader.forename 	= form.getfirst('forename', '')
  leader.initials 	= form.getfirst('initials', '')
  leader.surname 	= form.getfirst('surname', '')
  leader.date_of_birth 	= form.getfirst('date_of_birth', '')
  leader.mobile	 	= form.getfirst('mobile', '')
  leader.email	 	= form.getfirst('email', '')
  leader.add_info 	= form.getfirst('add_info', '')
  leader.gender	 	= form.getfirst('gender', '')
  leader.addr1	 	= form.getfirst('addr1', '')
  leader.addr2	 	= form.getfirst('addr2', '')
  leader.addr3	 	= form.getfirst('addr3', '')
  leader.p_code	 	= form.getfirst('p_code', '')
  leader.telephone_h 	= form.getfirst('telephone_h', '')
  leader.telephone_w 	= form.getfirst('telephone_w', '')

  if leader.forename == '' or leader.surname == '':
    leaderf_edit(form, db, param, conn)
    return

  #if not val_date(leader.date_of_birth):
  #  leader._edit(form, db, param, conn)
  #  return

  leader.update()


  if cLevel == 'U':
    heir_disp.unitf_disp(form, db, param, conn, inp_unit = nOu)
  elif cLevel == 'G':
    heir_disp.groupf_disp(form, db, param, conn, inp_group = nOu)
  elif cLevel == 'D':
    heir_disp.distf_disp(form, db, param, conn, inp_dist = nOu)
  elif cLevel == 'A':
    heir_disp.areaf_disp(form, db, param, conn, inp_area = nOu)
  elif cLevel == 'N':
    heir_disp.natf_disp(form, db, param, conn)
  else:
    heir_disp.home_page(form, db, param, conn)
 
  return

##############################################################################
# Main module, selects procedure to run
def main():
  form = cgi.FieldStorage()
  param = dbobj.paramrec()
  db = dbobj.dbinstance(param.dbname)
  conn = dbobj.connectrec(db)

  if conn.new_conn:
    app_error(form, param, conn, message = 'Invalid selection')
  else:  
    jw_act = form.getfirst('jw_action', '')
    # if a form action is specified do it
    if jw_act == "leaderf_edit":
      leaderf_edit(form, db, param, conn)
    elif jw_act == "leaderp_edit":
      leaderp_edit(form, db, param, conn)
    else:
      # Display the home page if you don't know what to do
      app_error(form, param, conn, message = 'Invalid selection')
  
  return


if __name__ == '__main__':
  main()
