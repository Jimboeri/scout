#!/usr/bin/python2
#
# This module contains code for add/change/delete of
#	Units
#	Groups
#	Districts
#	Areas

import cgi
#import os
import cgitb; cgitb.enable()
#import pg
import string
import webproc
from webscout import *
import dbobj
import Cookie
from procs import *
#import time
import heir_disp
#import textwrap
#import common
 
###############################################################################
def ouf_edit(form, db, param, conn, message = ''):
  """Org Unit edit module"""

  nOu = int(form.getfirst('ou_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  ou = dbobj.ourec(db, nOu)
  ou_owner = dbobj.ourec(db, ou.ou_owner)

  # If not new unit and unit id is undefined, do the home page thing
  if not ou.found:
    app_error(form, param, conn, message = 'Org Unit ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
    cMeet_time 	= form.getfirst('meet_time', '')  
    cPhone 	= form.getfirst('phone', '')  
    cFax 	= form.getfirst('fax', '')  
    cP_addr1 	= form.getfirst('p_addr1', '')  
    cP_addr2 	= form.getfirst('p_addr2', '')  
    cP_addr3 	= form.getfirst('p_addr3', '')  
    cP_code 	= form.getfirst('p_code', '')  
    cM_addr1 	= form.getfirst('m_addr1', '')  
    cM_addr2 	= form.getfirst('m_addr2', '')  
    cM_addr3 	= form.getfirst('m_addr3', '')  
    cM_code 	= form.getfirst('m_code', '')  
  else:
    cName 	= ou.name
    cMeet_time 	= ou.meet_time
    cPhone 	= ou.phone
    cFax 	= ou.fax
    cP_addr1 	= ou.p_addr1
    cP_addr2 	= ou.p_addr2
    cP_addr3 	= ou.p_addr3
    cP_code 	= ou.p_code
    cM_addr1 	= ou.m_addr1
    cM_addr2 	= ou.m_addr2
    cM_addr3 	= ou.m_addr3
    cM_code 	= ou.m_code



  # This table organises the org unit details
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

  # Row 1 Name
  table.add_row().add_item(webproc.tag('H2', 'Org Unit details'))
  table.last_row().add_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>',\
    styleclass = 'error')
  table.last_row().add_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=ouf_disp&ou_id=%d" %\
    ou.ou_id))

  if cSubmitted == 'Y' and cName == '':
    edit_row(table, 'Name :', 'name', cName, 0, 'Name is a required field', req=1, size=60)
  else:
    edit_row(table, 'Name :', 'name', cName, req=1, size=60)

  edit_row(table, 'Meeting time :', 'meet_time', cMeet_time, size=60)
  edit_row(table, 'Phone number:', 'phone', cPhone, size=60)
  edit_row(table, 'Fax number:', 'fax', cFax, size=60)
  edit_row(table, 'Physical address:', 'p_addr1', cP_addr1, size=60)
  edit_row(table, '', 'p_addr2', cP_addr2, size=60)
  edit_row(table, '', 'p_addr3', cP_addr3, size=60)
  edit_row(table, '', 'p_code', cP_code, size=10)
  edit_row(table, 'Mailing address:', 'm_addr1', cM_addr1, size=60)
  edit_row(table, '', 'm_addr2', cM_addr2, size=60)
  edit_row(table, '', 'm_addr3', cM_addr3, size=60)
  edit_row(table, '', 'm_code', cM_code, size=10)

  # Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="ouf_edit" VALUE="Submit">\
    <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="oup_edit">\
    <INPUT TYPE="HIDDEN" NAME="ou_id" VALUE="%d">\
    <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">' % nOu)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="ouf_edit" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def oup_edit(form, db, param, conn):
  """Processes the input from the Org Unit edit screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nOu = int(form.getfirst('ou_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  ou = dbobj.ourec(db, nOu)
  if not ou.found:
    app_error(form, param, conn, message = "Invalid org unit id")

  if form.getfirst('name','') == '':
    ouf_edit(form, db, param, conn)
    return

  ou.name	= form.getfirst('name', '')
  ou.meet_time 	= form.getfirst('meet_time', '')
  ou.phone 	= form.getfirst('phone', '')  
  ou.fax 	= form.getfirst('fax', '')  
  ou.p_addr1 	= form.getfirst('p_addr1', '')  
  ou.p_addr2 	= form.getfirst('p_addr2', '')  
  ou.p_addr3 	= form.getfirst('p_addr3', '')  
  ou.p_code 	= form.getfirst('p_code', '')  
  ou.m_addr1 	= form.getfirst('m_addr1', '')  
  ou.m_addr2 	= form.getfirst('m_addr2', '')  
  ou.m_addr3 	= form.getfirst('m_addr3', '')  
  ou.m_code 	= form.getfirst('m_code', '')  

  ou.update()
  dbobj.log_action(db, conn.scout_id, 2002, 0, ou.ou_id)

  heir_disp.ouf_disp(form, db, param, conn, ou_id = ou.ou_id)
  return

###############################################################################
def ouf_add(form, db, param, conn, message = ''):
  """Org Unit add module"""

  nOu_owner = int(form.getfirst('ou_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  ou_owner = dbobj.ourec(db, nOu_owner)
  # Group must exist
  if not ou_owner.found:
    app_error(form, param, conn, message = 'OU ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
    cMeet_time 	= form.getfirst('meet_time', '') 
    cSect_cd	= form.getfirst('sect_cd', '') 
  else:
    cName 	= ''
    cMeet_time 	= ''
    cSect_cd	= '' 

  # This table organises the unit details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Section input
  col = webproc.table_col()
  col.width = '25%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'New Org Unit input'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=groupf_disp&group_id=" + str(group.group_id)))
  row.items.append(item)
  table.rows.append(row)

  # First row
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('SPAN', 'Name', 'CLASS="field_descr"'))
  if cSubmitted == 'Y' and cName == '':
    item.data += '<BR><SPAN CLASS="validation_message">' + 'Name is a required field' + '</SPAN>'
    item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="TEXT" NAME="name" VALUE ="' + pr_str(cName) + '"i SIZE=60')
  item.data += '&nbsp*'
  row.items.append(item)

  # Generate section list
  sect_list = dbobj.section_list(db)
  item = webproc.table_item(webproc.tag('SPAN', 'Select section', 'CLASS="field_descr"'))
  for sect in sect_list.sectionlist:
    # don't display adult section id
    if sect.sect_cd != 'A':
      item.data += '<BR><INPUT TYPE="RADIO" NAME="sect_cd" VALUE="' + sect.sect_cd + '"'
      if sect.sect_cd == cSect_cd:
        item.data += ' CHECKED'
      item.data += '>' + sect.name
  item.rowspan = '6' 
  row.items.append(item)
  table.rows.append(row)

  edit_row(table, 'Meeting time :', 'meet_time', cMeet_time)

  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="unitf_edd" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="unitp_add">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="group_id" VALUE=' + str(nGroup) + '>'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="unitf_add" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def oup_add(form, db, param, conn):
  """Processes the input from the org unit add screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nGroup = int(form.getfirst('group_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  group = dbobj.grouprec(db, nGroup)
  if not group.found:
    app_error(form, param, conn, message = "Invalid group id")

  if form.getfirst('name','') == '':
    unitf_add(form, db, param, conn)
    return

  if form.getfirst('sect_cd','') == '':
    unitf_add(form, db, param, conn)
    return

  # Initialise the unit record
  unit = dbobj.unitrec(db, 0)

  unit.name 		= form.getfirst('name', '')
  unit.meet_time 	= form.getfirst('meet_time', '')
  unit.sect_cd	 	= form.getfirst('sect_cd', '')
  unit.group_id		= group.group_id

  unit.add()
  dbobj.log_action(db, conn.scout_id, 2001, 0, unit.unit_id)

  heir_disp.unitf_disp(form, db, param, conn, inp_unit = unit.unit_id)
  return


###############################################################################
def unitf_edit(form, db, param, conn, message = ''):
  """Unit edit module"""

  nUnit = int(form.getfirst('unit_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  unit = dbobj.unitrec(db, nUnit)
  group = dbobj.grouprec(db, unit.group_id)

  # If not new unit and unit id is undefined, do the home page thing
  if not unit.found:
    app_error(form, param, conn, message = 'Unit ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
    cMeet_time 	= form.getfirst('meet_time', '')  
  else:
    cName 	= unit.name
    cMeet_time 	= unit.meet_time


  # This table organises the scouts personal details
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

  # Row 1 Name
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'Unit details'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=unitf_disp&group_id=" + str(unit.unit_id)))
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item('Group :', styleclass='field_descr')
  row.items.append(item)
  item = webproc.table_item(group.name)
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item('Section :', styleclass='field_descr')
  row.items.append(item)
  item = webproc.table_item(unit.sect_name)
  row.items.append(item)
  table.rows.append(row)

  if cSubmitted == 'Y' and cName == '':
    edit_row(table, 'Name :', 'name', cName, 0, 'Name is a required field', req=1)
  else:
    edit_row(table, 'Name :', 'name', cName, req=1)

  edit_row(table, 'Meeting time :', 'meet_time', cMeet_time)

  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="unitf_edit" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="unitp_edit">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="unit_id" VALUE="' + str(nUnit) + '">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="unitf_edit" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def unitp_edit(form, db, param, conn):
  """Processes the input from the unit edit screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nUnit = int(form.getfirst('unit_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  unit = dbobj.unitrec(db, nUnit)
  if not unit.found:
    app_error(form, param, conn, message = "Invalid unit id")

  if form.getfirst('name','') == '':
    unitf_edit(form, db, param, conn)
    return

  unit.name 		= form.getfirst('name', '')
  unit.meet_time 	= form.getfirst('meet_time', '')

  unit.update()
  dbobj.log_action(db, conn.scout_id, 2002, 0, unit.unit_id)

  heir_disp.unitf_disp(form, db, param, conn, inp_unit = nUnit)
  return

###############################################################################
def unitf_add(form, db, param, conn, message = ''):
  """Unit add module"""

  nGroup = int(form.getfirst('group_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  group = dbobj.grouprec(db, nGroup)
  # Group must exist
  if not group.found:
    app_error(form, param, conn, message = 'Group ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
    cMeet_time 	= form.getfirst('meet_time', '') 
    cSect_cd	= form.getfirst('sect_cd', '') 
  else:
    cName 	= ''
    cMeet_time 	= ''
    cSect_cd	= '' 

  # This table organises the unit details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Section input
  col = webproc.table_col()
  col.width = '25%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'New Unit input'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=groupf_disp&group_id=" + str(group.group_id)))
  row.items.append(item)
  table.rows.append(row)


  # First row
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('SPAN', 'Name', 'CLASS="field_descr"'))
  if cSubmitted == 'Y' and cName == '':
    item.data += '<BR><SPAN CLASS="validation_message">' + 'Name is a required field' + '</SPAN>'
    item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="TEXT" NAME="name" VALUE ="' + pr_str(cName) + '"i SIZE=60')
  item.data += '&nbsp*'
  row.items.append(item)

  # Generate section list
  sect_list = dbobj.section_list(db)
  item = webproc.table_item(webproc.tag('SPAN', 'Select section', 'CLASS="field_descr"'))
  for sect in sect_list.sectionlist:
    # don't display adult section id
    if sect.sect_cd != 'A':
      item.data += '<BR><INPUT TYPE="RADIO" NAME="sect_cd" VALUE="' + sect.sect_cd + '"'
      if sect.sect_cd == cSect_cd:
        item.data += ' CHECKED'
      item.data += '>' + sect.name
  item.rowspan = '6' 
  row.items.append(item)
  table.rows.append(row)

  edit_row(table, 'Meeting time :', 'meet_time', cMeet_time)

  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="unitf_edd" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="unitp_add">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="group_id" VALUE=' + str(nGroup) + '>'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="unitf_add" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def unitp_add(form, db, param, conn):
  """Processes the input from the unit add screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nGroup = int(form.getfirst('group_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  group = dbobj.grouprec(db, nGroup)
  if not group.found:
    app_error(form, param, conn, message = "Invalid group id")

  if form.getfirst('name','') == '':
    unitf_add(form, db, param, conn)
    return

  if form.getfirst('sect_cd','') == '':
    unitf_add(form, db, param, conn)
    return

  # Initialise the unit record
  unit = dbobj.unitrec(db, 0)

  unit.name 		= form.getfirst('name', '')
  unit.meet_time 	= form.getfirst('meet_time', '')
  unit.sect_cd	 	= form.getfirst('sect_cd', '')
  unit.group_id		= group.group_id

  unit.add()
  dbobj.log_action(db, conn.scout_id, 2001, 0, unit.unit_id)

  heir_disp.unitf_disp(form, db, param, conn, inp_unit = unit.unit_id)
  return

##############################################################################
def unitp_del(form, db, param, conn):
  """Processes the delete request """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nUnit = int(form.getfirst('unit_id', '0'))
  unit = dbobj.unitrec(db, nUnit)

  if not unit.found:
    app_error(form, param, conn, message = "Invalid unit id")
    return

  unit.scout_list()
  if len(unit.scoutlist) > 0:
    app_error(form, param, conn, message = "Unit still has current members")
    return

  unit.role_list()
  if len(unit.rolelist) > 0:
    app_error(form, param, conn, message = "Unit still has current members")
    return

  nGroup = unit.group_id

  # Log the action first
  dbobj.log_action(db, conn.scout_id, 2003, 0, unit.unit_id)
  unit.delete()


  heir_disp.groupf_disp(form, db, param, conn, inp_group = nGroup)
  return

###############################################################################
def groupf_edit(form, db, param, conn, message = ''):
  """Group edit module"""

  nGroup = int(form.getfirst('group_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  group = dbobj.grouprec(db, nGroup)
  dist = dbobj.districtrec(db, group.dist_id)

  # If not new unit and unit id is undefined, do the home page thing
  if not group.found:
    app_error(form, param, conn, message = 'Group ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
    cAddr1 	= form.getfirst('addr1', '')  
    cAddr2 	= form.getfirst('addr2', '')  
    cAddr3 	= form.getfirst('addr3', '')  
    cP_Code 	= form.getfirst('p_code', '')  
    cTelephone 	= form.getfirst('telephone', '')  
  else:
    cName 	= group.name
    cAddr1 	= group.addr1
    cAddr2 	= group.addr2
    cAddr3 	= group.addr3
    cP_Code 	= group.p_code
    cTelephone 	= group.telephone


  # This table organises the scouts personal details
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

  # Row 1 Name
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'Group details'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAN>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=groupf_disp&group_id=" + str(group.group_id)))
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item('District :', styleclass='field_descr')
  row.items.append(item)
  item = webproc.table_item(dist.name)
  row.items.append(item)
  table.rows.append(row)

  if cSubmitted == 'Y' and cName == '':
    edit_row(table, 'Name :', 'name', cName, 0, 'Name is a required field', req=1, size=60, maxlen=60)
  else:
    edit_row(table, 'Name :', 'name', cName, req=1, size=60, maxlen=60)

  edit_row(table, 'Address :', 'addr1', cAddr1, size=60, laxlen=60)
  edit_row(table, '', 'addr2', cAddr2, size=60, maxlen=60)
  edit_row(table, '', 'addr3', cAddr3, size=60, maxlen=60)
  edit_row(table, 'Post Code :', 'p_code', cP_Code, size=4, maxlen=4)
  edit_row(table, 'Telephone :', 'telephone', cTelephone, maxlen=40)

  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="groupf_edit" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="groupp_edit">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="group_id" VALUE="' + str(nGroup) + '">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="groupf_edit" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def groupp_edit(form, db, param, conn):
  """Processes the input from the group edit screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nGroup = int(form.getfirst('group_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  group = dbobj.grouprec(db, nGroup)
  if not group.found:
    app_error(form, param, conn, message = "Invalid group id")

  if form.getfirst('name','') == '':
    groupf_edit(form, db, param, conn)
    return

  group.name 		= form.getfirst('name', '')
  group.addr1	 	= form.getfirst('addr1', '')
  group.addr2	 	= form.getfirst('addr2', '')
  group.addr3	 	= form.getfirst('addr3', '')
  group.p_code	 	= form.getfirst('p_code', '')
  group.telephone	= form.getfirst('telephone', '')

  group.update()
  dbobj.log_action(db, conn.scout_id, 2012, 0, group.group_id)

  heir_disp.groupf_disp(form, db, param, conn, inp_group = nGroup)
  return

###############################################################################
def groupf_add(form, db, param, conn, message = ''):
  """Group add module"""

  nDist = int(form.getfirst('dist_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  dist = dbobj.districtrec(db, nDist)
  # Group must exist
  if not dist.found:
    app_error(form, param, conn, message = 'District ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
    cAddr1 	= form.getfirst('addr1', '')  
    cAddr2 	= form.getfirst('addr2', '')  
    cAddr3 	= form.getfirst('addr3', '')  
    cP_Code 	= form.getfirst('p_code', '')  
    cTelephone 	= form.getfirst('telephone', '')  
  else:
    cName 	= ''
    cAddr1 	= ''
    cAddr2 	= ''
    cAddr3 	= ''
    cP_Code 	= ''
    cTelephone 	= ''


  # This table organises the scouts personal details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Section input
  col = webproc.table_col()
  col.width = '25%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'New Group input'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=distf_disp&disp_id=" + str(dist.dist_id)))
  row.items.append(item)
  table.rows.append(row)

  # First row
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('SPAN', 'Name', 'CLASS="field_descr"'))
  if cSubmitted == 'Y' and cName == '':
    item.data += '<BR><SPAN CLASS="validation_message">' + 'Name is a required field' + '</SPAN>'
    item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="TEXT" NAME="name" VALUE ="' + pr_str(cName) + '"i SIZE=60 MAXLEN=60')
  item.data += '&nbsp*'
  row.items.append(item)
  table.rows.append(row)

  edit_row(table, 'Address :', 'addr1', cAddr1, size=60, maxlen=60)
  edit_row(table, '', 'addr2', cAddr2, size=60, maxlen=60)
  edit_row(table, '', 'addr3', cAddr3, size=60, maxlen=60)
  edit_row(table, 'Post Code :', 'p_code', cP_Code, size=4, maxlen=4)
  edit_row(table, 'Telephone :', 'telephone', cTelephone, maxlen=40)


  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="groupf_edd" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="groupp_add">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="dist_id" VALUE=' + str(nDist) + '>'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="groupf_add" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def groupp_add(form, db, param, conn):
  """Processes the input from the group add screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nDist = int(form.getfirst('dist_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  dist = dbobj.districtrec(db, nDist)
  if not dist.found:
    app_error(form, param, conn, message = "Invalid District id")

  if form.getfirst('name','') == '':
    groupf_add(form, db, param, conn)
    return

  # Initialise the unit record
  group = dbobj.grouprec(db, 0)

  group.name 		= form.getfirst('name', '')
  group.dist_id		= dist.dist_id
  group.addr1 		= form.getfirst('addr1', '')
  group.addr2 		= form.getfirst('addr2', '')
  group.addr3		= form.getfirst('addr3', '')
  group.p_code 		= form.getfirst('p_code', '')
  group.telephone	= form.getfirst('telephone', '')

  group.add()
  dbobj.log_action(db, conn.scout_id, 2011, 0, group.group_id)

  heir_disp.groupf_disp(form, db, param, conn, inp_group = group.group_id)
  return

##############################################################################
def groupp_del(form, db, param, conn):
  """Processes the delete request for a group record """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nGroup = int(form.getfirst('group_id', '0'))
  group = dbobj.grouprec(db, nGroup)

  if not group.found:
    app_error(form, param, conn, message = "Invalid Group id")
    return

  group.unit_list()
  if len(group.unitlist) > 0:
    app_error(form, param, conn, message = "Group still has current units")
    return

  group.role_list()
  if len(group.rolelist) > 0:
    app_error(form, param, conn, message = "Group still has current units")
    return

  nDist = group.dist_id

  # Log the action first
  dbobj.log_action(db, conn.scout_id, 2013, 0, group.group_id)
  group.delete()

  heir_disp.distf_disp(form, db, param, conn, inp_dist = nDist)
  return

###############################################################################
def distf_edit(form, db, param, conn, message = ''):
  """District edit module"""

  nDist = int(form.getfirst('dist_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  dist = dbobj.districtrec(db, nDist)
  area = dbobj.arearec(db, dist.area_id)

  # If not new district and dist id is undefined, do the home page thing
  if not dist.found:
    app_error(form, param, conn, message = 'District ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
  else:
    cName 	= dist.name

  # This table organises the scouts personal details
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

  # Row 1 Name
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'Group details'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAN>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=distf_disp&dist_id=" + str(dist.dist_id)))
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item('Area :', styleclass='field_descr')
  row.items.append(item)
  item = webproc.table_item(area.name)
  row.items.append(item)
  table.rows.append(row)

  if cSubmitted == 'Y' and cName == '':
    edit_row(table, 'Name :', 'name', cName, 0, 'Name is a required field', req=1, size=60, maxlen=60)
  else:
    edit_row(table, 'Name :', 'name', cName, req=1, size=60, maxlen=60)

  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="distf_edit" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="distp_edit">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="dist_id" VALUE="' + str(nDist) + '">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="distf_edit" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def distp_edit(form, db, param, conn):
  """Processes the input from the district edit screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nDist = int(form.getfirst('dist_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  dist = dbobj.districtrec(db, nDist)
  if not dist.found:
    app_error(form, param, conn, message = "Invalid district id")

  if form.getfirst('name','') == '':
    distf_edit(form, db, param, conn)
    return

  dist.name 		= form.getfirst('name', '')

  dist.update()
  dbobj.log_action(db, conn.scout_id, 2022, 0, dist.dist_id)

  heir_disp.distf_disp(form, db, param, conn, inp_dist = nDist)
  return

###############################################################################
def distf_add(form, db, param, conn, message = ''):
  """District add module"""

  nArea = int(form.getfirst('area_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  area = dbobj.arearec(db, nArea)
  # Area must exist
  if not area.found:
    app_error(form, param, conn, message = 'Area ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
  else:
    cName 	= ''

  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Section input
  col = webproc.table_col()
  col.width = '25%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'New District input'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=areaf_disp&disp_id=" + str(area.area_id)))
  row.items.append(item)
  table.rows.append(row)

  # First row
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('SPAN', 'Name', 'CLASS="field_descr"'))
  if cSubmitted == 'Y' and cName == '':
    item.data += '<BR><SPAN CLASS="validation_message">' + 'Name is a required field' + '</SPAN>'
    item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="TEXT" NAME="name" VALUE ="' + pr_str(cName) + '"i SIZE=60 MAXLEN=60')
  item.data += '&nbsp*'
  row.items.append(item)
  table.rows.append(row)


  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="distf_add" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="distp_add">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="area_id" VALUE=' + str(nArea) + '>'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="distf_add" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def distp_add(form, db, param, conn):
  """Processes the input from the district add screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nArea = int(form.getfirst('area_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  area = dbobj.arearec(db, nArea)
  if not area.found:
    app_error(form, param, conn, message = "Invalid Area id")

  if form.getfirst('name','') == '':
    distf_add(form, db, param, conn)
    return

  # Initialise the unit record
  dist = dbobj.districtrec(db, 0)

  dist.name	= form.getfirst('name', '')
  dist.area_id	= area.area_id

  dist.add()
  dbobj.log_action(db, conn.scout_id, 2021, 0, dist.dist_id)

  heir_disp.distf_disp(form, db, param, conn, inp_dist = dist.dist_id)
  return

##############################################################################
def distp_del(form, db, param, conn):
  """Processes the delete request for a district record """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nDist = int(form.getfirst('dist_id', '0'))
  dist = dbobj.districtrec(db, nDist)

  if not dist.found:
    app_error(form, param, conn, message = "Invalid District id")
    return

  dist.group_list()
  if len(dist.grouplist) > 0:
    app_error(form, param, conn, message = "District still has current units")
    return

  dist.role_list()
  if len(dist.rolelist) > 0:
    app_error(form, param, conn, message = "District still has current units")
    return

  nArea = dist.area_id

  # Log the action first
  dbobj.log_action(db, conn.scout_id, 2023, 0, dist.dist_id)
  dist.delete()

  heir_disp.areaf_disp(form, db, param, conn, inp_area = nArea)
  return

###############################################################################
def areaf_edit(form, db, param, conn, message = ''):
  """Area edit module"""

  nArea = int(form.getfirst('area_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  area = dbobj.arearec(db, nArea)
  nat = dbobj.nationalrec(db)

  # If not new area and area id is undefined, do the home page thing
  if not area.found:
    app_error(form, param, conn, message = 'Area ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
  else:
    cName 	= area.name

  # This table organises the scouts personal details
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

  # Row 1 Name
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'Area details'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAN>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=areaf_disp&area_id=" + str(area.area_id)))
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item('National :', styleclass='field_descr')
  row.items.append(item)
  item = webproc.table_item(nat.name)
  row.items.append(item)
  table.rows.append(row)

  if cSubmitted == 'Y' and cName == '':
    edit_row(table, 'Name :', 'name', cName, 0, 'Name is a required field', req=1, size=60, maxlen=60)
  else:
    edit_row(table, 'Name :', 'name', cName, req=1, size=60, maxlen=60)

  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="areaf_edit" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="areap_edit">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="area_id" VALUE="' + str(nArea) + '">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="areaf_edit" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def areap_edit(form, db, param, conn):
  """Processes the input from the area edit screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nArea = int(form.getfirst('area_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  area = dbobj.arearec(db, nArea)
  if not area.found:
    app_error(form, param, conn, message = "Invalid area id")

  if form.getfirst('name','') == '':
    areaf_edit(form, db, param, conn)
    return

  area.name	= form.getfirst('name', '')

  area.update()
  dbobj.log_action(db, conn.scout_id, 2032, 0, area.area_id)

  heir_disp.areaf_disp(form, db, param, conn, inp_area = nArea)
  return

###############################################################################
def areaf_add(form, db, param, conn, message = ''):
  """Area add module"""

  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  nat = dbobj.nationalrec(db)
  # Area must exist
  if not nat.found:
    app_error(form, param, conn, message = 'National ID error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
  else:
    cName 	= ''

  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = ''
  colgr.cols.append(col)

  # Section input
  col = webproc.table_col()
  col.width = '25%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'New Area input'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=natf_disp"))
  row.items.append(item)
  table.rows.append(row)

  # First row
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('SPAN', 'Name', 'CLASS="field_descr"'))
  if cSubmitted == 'Y' and cName == '':
    item.data += '<BR><SPAN CLASS="validation_message">' + 'Name is a required field' + '</SPAN>'
    item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="TEXT" NAME="name" VALUE ="' + pr_str(cName) + '"i SIZE=60 MAXLEN=60')
  item.data += '&nbsp*'
  row.items.append(item)
  table.rows.append(row)


  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="areaf_add" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="areap_add">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="areaf_add" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def areap_add(form, db, param, conn):
  """Processes the input from the area add screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  cSubmitted = form.getfirst('submitted', 'N')

  if form.getfirst('name','') == '':
    areaf_add(form, db, param, conn)
    return

  # Initialise the unit record
  area = dbobj.arearec(db, 0)

  area.name	= form.getfirst('name', '')

  area.add()
  dbobj.log_action(db, conn.scout_id, 2031, 0, area.area_id)

  heir_disp.areaf_disp(form, db, param, conn, inp_area = area.area_id)
  return

##############################################################################
def areap_del(form, db, param, conn):
  """Processes the delete request for a area record """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nArea = int(form.getfirst('area_id', '0'))
  area = dbobj.arearec(db, nArea)

  if not area.found:
    app_error(form, param, conn, message = "Invalid Area id")
    return

  area.district_list()
  if len(area.districtlist) > 0:
    app_error(form, param, conn, message = "Area still has current Districts")
    return

  area.role_list()
  if len(area.rolelist) > 0:
    app_error(form, param, conn, message = "Area still has current roles defined")
    return

  # Log the action first
  dbobj.log_action(db, conn.scout_id, 2033, 0, area.area_id)
  area.delete()

  heir_disp.natf_disp(form, db, param, conn)
  return

###############################################################################
def natf_edit(form, db, param, conn, message = ''):
  """National edit module"""

  cSubmitted = form.getfirst('submitted', 'N')

  # Security check
  if not conn.superuser:
    # Only superusers to add units
    security_page(form, param, conn)
    return 

  nat = dbobj.nationalrec(db)

  # If not new area and area id is undefined, do the home page thing
  if not nat.found:
    app_error(form, param, conn, message = 'National record error')
    return

  jw_header(param, conn, menu_item=2)
  if message != '':
    print webproc.tag('H2', message)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cName 	= form.getfirst('name', '')  
  else:
    cName 	= nat.name

  # This table organises the scouts personal details
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

  # Row 1 Name
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', 'National details'))
  row.items.append(item)
  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAN>')
  item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=natf_disp"))
  row.items.append(item)
  table.rows.append(row)

  if cSubmitted == 'Y' and cName == '':
    edit_row(table, 'Name :', 'name', cName, 0, 'Name is a required field', req=1, size=60, maxlen=60)
  else:
    edit_row(table, 'Name :', 'name', cName, req=1, size=60, maxlen=60)

  # Form buttons
  row = webproc.table_row()
  item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="natf_edit" VALUE="Submit">')
  item.data += ' <INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="natp_edit">'
  item.data += ' <INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="natf_edit" action="heir_acd.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def natp_edit(form, db, param, conn):
  """Processes the input from the National edit screen """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  cSubmitted = form.getfirst('submitted', 'N')

  nat = dbobj.nationalrec(db)
  if not nat.found:
    app_error(form, param, conn, message = "Invalid national record")

  if form.getfirst('name','') == '':
    natf_edit(form, db, param, conn)
    return

  nat.name	= form.getfirst('name', '')

  nat.update()
  dbobj.log_action(db, conn.scout_id, 2042, 0)

  heir_disp.natf_disp(form, db, param, conn)
  return



##############################################################################
# Main program logic, decides which form/screen to display

# Initialise the main variables used
# The form contains any form variables passed from previous screens
form = cgi.FieldStorage()
# Parameters used by all prograns
param = dbobj.paramrec()
# Open the database
db = dbobj.dbinstance(param.dbname)
# Get information about the current connection
conn = dbobj.connectrec(db)

if conn.new_conn:
  oCookie = Cookie.SimpleCookie()
  oCookie[conn.ref_id] = conn.auth_key
  oCookie[conn.ref_id]["Max-Age"] = 31536000
  cCookie = oCookie.output()
  heir_disp.home_page(form, db, param, conn, ocookie = oCookie, msg='set cookie')
else:  
  if form.has_key('jw_action'):
    # if a form action is specified do it
    if form.getfirst("jw_action") == "home_page":
      heir_disp.home_page(form, db, param, conn, 'home page selected')
    elif form.getfirst("jw_action") == "natf_disp":
      heir_disp.natf_disp(form, db, param, conn)
    elif form.getfirst("jw_action") == "areaf_disp":
      heir_disp.areaf_disp(form, db, param, conn)
    elif form.getfirst("jw_action") == "distf_disp":
      heir_disp.distf_disp(form, db, param, conn)
    elif form.getfirst("jw_action") == "groupf_disp":
      heir_disp.groupf_disp(form, db, param, conn)
    elif form.getfirst("jw_action") == "unitf_disp":
      heir_disp.unitf_disp(form, db, param, conn)
    elif form.getfirst("jw_action") == "scoutf_disp":
      heir_disp.scoutf_disp(form, db, param, conn)
    elif form.getfirst("jw_action") == "unitf_edit":
      unitf_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "unitp_edit":
      unitp_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "unitf_add":
      unitf_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "unitp_add":
      unitp_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "unitp_del":
      unitp_del(form, db, param, conn)
    elif form.getfirst("jw_action") == "groupf_edit":
      groupf_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "groupp_edit":
      groupp_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "groupf_add":
      groupf_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "groupp_add":
      groupp_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "groupp_del":
      groupp_del(form, db, param, conn)
    elif form.getfirst("jw_action") == "distf_edit":
      distf_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "distp_edit":
      distp_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "distf_add":
      distf_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "distp_add":
      distp_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "distp_del":
      distp_del(form, db, param, conn)
    elif form.getfirst("jw_action") == "areaf_edit":
      areaf_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "areap_edit":
      areap_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "areaf_add":
      areaf_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "areap_add":
      areap_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "areap_del":
      areap_del(form, db, param, conn)
    elif form.getfirst("jw_action") == "natf_edit":
      natf_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "natp_edit":
      natp_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "ouf_disp":
      heir_disp.ouf_disp(form, db, param, conn)
    elif form.getfirst("jw_action") == "ouf_edit":
      ouf_edit(form, db, param, conn)



  else:
      # Display the home page if you don't know what to do
      heir_disp.home_page(form, db, param, conn, menu_id=1)
  

