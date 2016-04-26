#!/usr/bin/python2

import cgi
import os
import cgitb; cgitb.enable()
#import pg
import string
import webproc
from webscout import *
import dbobj
import Cookie
from procs import *
import time
import ou
#import textwrap
#import common
 
###############################################################################
def scoutf_disp(form, db, param, conn, message = '', scout_id = 0, ou_id = 0):
  """Displays scout details
Function acceps the following parameters
  scout_id
  ou_id
The following cgi form fields are also accepted
  scout_id
  ou_id
  disp_ou - if defined says which ou to display if cancelling this screen"""

  if scout_id == 0:  
    nScout = int(form.getfirst('scout_id', 0))
    nOu = int(form.getfirst('ou_id', 0))
  else:
    nScout = scout_id
    nOu = ou_id
  nDisp_ou = int(form.getfirst('disp_ou', 0))

  # If not form scout id, do the home page thing
  if nScout == 0:
    home_page(form, db, param, conn, menu_id=1)
    return

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    # go to top of browse tree
    home_page(form, db, param, conn, menu_id=1)
    return 

  if not nOu:
    roles = scout.role_list()
    if len(roles):
      nOu = roles[0].ou_id

  ourec = dbobj.ourec(db, nOu)

  disp_ou = dbobj.ourec(db, nDisp_ou)

  scout.check_junior(ourec, param)

  conn.ou_security(nOu)

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  #page.data.append(conn.__str__())

  #define outer table, hold scout details at the op, parents on the left, & achievments on the right
  outtab = outtable(param)

  # top row if for Scout details
  outrow = outtab.add_row()

  # This table organises the scouts personal details
  table = intable(param)

  # Title
  table.add_row().add_item(webproc.tag('H3', 'Scout details'))
  # Display up to button if ou exists
  if disp_ou.found:
    table.append_item(webproc.jbutton('Up to ' + disp_ou.name,\
        "ou_logic.py?jw_action=ouf_disp&ou_id=%d" % disp_ou.ou_id, need_form=1))
  elif ourec.found:
    table.append_item(webproc.jbutton('Up to ' + ourec.name,\
        "ou_logic.py?jw_action=ouf_disp&ou_id=%d" % ourec.ou_id, need_form=1))
  item = table.last_row().add_item('&nbsp;')
  role = scout.role_by_ou(nOu)
  if conn.write:
    if role.status == 'C':
      item.data = webproc.jbutton('Lapse membership',\
          "scout.py?jw_action=scoutf_inactive&scout_id=%d&ou_id=%d&disp_ou=%d"\
          % (scout.scout_id, ourec.ou_id, nDisp_ou), need_form=1)
    else:
      item.data = webproc.jbutton('Renew membership',\
          "scout.py?jw_action=scoutf_renew&scout_id=%d&ou_id=%d&disp_ou=%d"\
          % (scout.scout_id, ourec.ou_id, nDisp_ou), need_form=1)

  item = table.last_row().add_item(' ')
  if conn.read:
    item.data = webproc.jbutton('Awards & badges',\
        "award.py?jw_action=awardf_disp&scout_id=%d&ou_id=%d" % (scout.scout_id, nOu), need_form=1)

  # name etc
  row = table.add_row()
  row.add_item(webproc.tag('B', '%s %s %s' % (scout.forename, scout.initials, scout.surname)))
  item = row.add_item('<B>Status: </B>')
  if role.status == 'C':
    item.data += "Current"
  else:
    item.data += "Membership lapsed"
  item = row.add_item('&nbsp;')
  if conn.write:
    item.data = webproc.jbutton("Edit %s's details" % scout.forename,\
        'scout.py?jw_action=scoutf_edit&scout_id=%d&ou_id=%d&disp_ou=%d'\
        % (scout.scout_id, nOu, nDisp_ou), need_form=1)

  if conn.read:
    row = table.add_row()
    row.add_item('<B>Date of birth : </B>' + pr_str(scout.date_of_birth))
    row.add_item('<B>Gender : </B>' + pr_str(scout.gender))
    if conn.write:
      row.add_item(' ')
      row.add_item(webproc.jbutton('Transfer to another org unit',\
          'scout.py?jw_action=scoutf_transfer&scout_id=%d&ou_id=%d' %\
          (scout.scout_id, ourec.ou_id), need_form=1))

    disp_line(table, '<B>School : </B>' + pr_str(scout.school),\
        '<B>Mobile phone no : </B>' + pr_str(scout.mobile))
    disp_line(table, '<B>E-Mail address : </B>' + pr_str(scout.email))
  disp_line(table, '<B>Unit name : </B>%s &nbsp&nbsp<B>Section : </B>%s' %\
     (ourec.name, ourec.struct_name))

  # Additional info, if it exists
  if scout.add_info is not None and scout.add_info != '' and conn.sign_in:
    row = table.add_row()
    row.add_item(webproc.tag('B', 'Additional Information : <BR>') + pr_str(scout.add_info), colspan = '2')

  # Output the scout's details
  outrow.add_item(table.pr_table(), colspan = '2')

  # This table organises the scouts personal details
  table = intable(param)

  if scout.junior:
    # If the scout is a junior, display parent details
    parent = dbobj.adultrec(db, scout.parent1)

    # Row 1 Title
    disp_line(table, webproc.tag('H3', "Parent's Info"))

    if parent.found:
      cName = webproc.tag('B', '%s %s %s' % (parent.forename, parent.initials, parent.surname))
      cLink = '&nbsp;'
      if conn.write:
        cLink = webproc.jbutton("Edit %s's details" % parent.forename,\
            'scout.py?jw_action=scoutf_edit&scout_id=%d&kid_id=%d&ou_id=%d&disp_ou=%d&nxt_module=scout.py&nxt_prog=scoutf_disp&parent=p1'\
            % (parent.scout_id, scout.scout_id, nOu, nDisp_ou), need_form=0)

        cLink += '&nbsp&nbsp' + webproc.tag("A", "Change this parent",\
            'href=office.py?jw_action=select_person1&next_module=scout.py&next_prog=parent1f_mod1&scout_id=%d&ou_id=%d'\
            % (scout.scout_id, nOu) + ' CLASS="small_disp"')
      disp_line(table, cName, cLink)

      if conn.sign_in:
        disp_line(table, pr_str(parent.addr1))
        disp_line(table, pr_str(parent.addr2))
        disp_line(table, pr_str(parent.p_code) + ' ' + pr_str(parent.addr3))
        disp_line(table, '<B>Phone (H) : </B>%s' % pr_str(parent.telephone_h),\
            '<B>Phone (W) : </B>%s' % pr_str(parent.telephone_w))
        disp_line(table, '<B>Mobile : </B>' + pr_str(parent.mobile),\
            '<B>E-Mail : </B>' + pr_str(parent.email))
 
        # Additional info, if it exists
        if parent.add_info is not None:
          table.add_row().add_item(webproc.tag('B', 'Additional Information : <BR>') + pr_str(parent.add_info), colspan = '2')

      # Second Parent -row 1 if record exists
      parent2 = dbobj.adultrec(db, scout.parent2)
      if parent2.found:
        disp_line(table, webproc.tag('B', '<BR>Second parent :'))
        cName = webproc.tag('B', string.strip(parent2.forename) + ' ' + string.strip(parent2.initials) + ' ' + string.strip(parent2.surname))
        cLink = '&nbsp;'
        if conn.write:
          cLink = webproc.jbutton("Edit %s's details" % parent2.forename,\
             'scout.py?jw_action=scoutf_edit&scout_id=%d&kid_id=%d&ou_id=%d&disp_ou=%d&nxt_module=scout.py&nxt_prog=scoutf_disp&parent=p2'\
              % (parent2.scout_id, scout.scout_id, nOu, nDisp_ou), need_form=0)
          cLink += '&nbsp&nbsp&nbsp' + webproc.tag('A', 'Remove link',\
              "href=scout.py?jw_action=parent2f_remove&&scout_id=%d&ou_id=%d CLASS=small_disp"\
              % (scout.scout_id, nOu))

        disp_line(table, cName, cLink)
        if conn.sign_in:
          disp_line(table, webproc.tag('B', 'Mobile : ') + pr_str(parent2.mobile), webproc.tag('B', 'E-Mail : ') + pr_str(parent2.email))

          # Second parent - Additional info, if it exists
          if parent2.add_info is not None:
            row = table.add_row()
            row.add_item(webproc.tag('B', 'Additional Information : <BR>') + pr_str(parent2.add_info), colspan = '2')
      else:
        cLink = webproc.jbutton('Add second parent details',\
            'office.py?jw_action=select_person1&next_module=scout.py&next_prog=parent2f_add&scout_id=%d&ou_id=%d'\
            % (scout.scout_id, nOu))
        disp_line(table, cLink, ' ')

  else:
    # this person is an adult
    # Lets see if there are any kids
    adult = dbobj.adultrec(db, scout.scout_id)
    kids = adult.kids_list()
    if len(kids):
      table.append_item("<B>Children linked with this person</B>")
      for k in kids:
        table.append_item("%s %s" % (k.forename, k.surname), new_row = 1)

  outtab.add_row().add_item(table.pr_table())


  # This table organises the scouts actual achievements
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc,\
      border = param.it_brdr)

  # Row 1 Title
  disp_line(table, webproc.tag('H4', "Awards and badges obtained"))

  # Build lists of awards and achievements
  scout.all_award_info()

  if len(scout.achievelist) > 0:
    for a in scout.achievelist:
      row = table.add_row()
      row.add_item(a.name)
  else:
      row = table.add_row()
      row.add_item('No badges or awards')

  if conn.sign_in:
    pass

  outtab.last_row().add_item(table.pr_table(), valign='TOP', width="25%")

  page.data.append(outtab.pr_table())
  page.output()




###############################################################################
def scoutf_edit(form, db, param, conn, message = ''):
  """Scout edit form.
Requires both the scout_id and the ou_id for the relevant ou as this defines some options
Also uses the following form fields to decide which screen to return to
  nxt_module
  nxt_prog

"""

  nScout = int(form.getfirst('scout_id', 0))
  nOu = int(form.getfirst('ou_id', '0'))
  cDisp_ou = form.getfirst('disp_ou', '0')

  # These modules may not always be present
  cNxt_module = form.getfirst('nxt_module', '')
  cNxt_prog = form.getfirst('nxt_prog', '')
  nKid_id = int(form.getfirst('kid_id', '0'))
  cParent_code = form.getfirst('parent', '').upper()

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid scout id')
    return 

  if not nOu:
    roles = scout.role_list()
    if len(roles):
      nOu = roles[0].ou_id

  ourec = dbobj.ourec(db, nOu)

  scout.check_junior(ourec, param)

  if cParent_code == 'P1' or cParent_code == 'P2':
    scout.junior = 0

  conn.pers_security(scout)

  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  if message != '':
    page.data.append(message)

  # Initialise variables for display
  cSubmitted = form.getfirst('submitted', 'N')
  if cSubmitted == 'Y':
    cForename 		= form.getfirst('forename', '')  
    cInitials 		= form.getfirst('initials', '')  
    cSurname 		= form.getfirst('surname', '')  
    cDate_of_Birth	= form.getfirst('date_of_birth', '')  
    cSchool 		= form.getfirst('school', '')  
    cGender 		= form.getfirst('gender', '')  
    cEmail 		= form.getfirst('email', '')  
    cMobile 		= form.getfirst('mobile', '')  
    cAdd_Info 		= form.getfirst('add_info', '')  
    cAddr1 		= form.getfirst('addr1', '')  
    cAddr2 		= form.getfirst('addr2', '')  
    cAddr3 		= form.getfirst('addr3', '')  
    cP_code 		= form.getfirst('p_code', '')  
    cTelephone_w	= form.getfirst('telephone_w', '')  
    cTelephone_h	= form.getfirst('telephone_h', '')  
    cFax		= form.getfirst('fax', '')  
  else:
    cForename 		= scout.forename
    cInitials 		= scout.initials
    cSurname 		= scout.surname
    cDate_of_Birth 	= scout.date_of_birth
    cSchool 		= scout.school
    cGender 		= scout.gender
    cEmail 		= scout.email
    cMobile 		= scout.mobile
    cAdd_Info 		= scout.add_info
    cAddr1 		= scout.addr1
    cAddr2 		= scout.addr2
    cAddr3 		= scout.addr3
    cP_code 		= scout.p_code
    cTelephone_w	= scout.telephone_w
    cTelephone_h	= scout.telephone_h
    cFax		= scout.fax

  outtab = outtable(param)

  # This table organises the scouts personal details
  table = intable(param)

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
  table.append_item(webproc.tag('H2', 'Scout details'))
  table.append_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>',\
      styleclass = 'error')
  table.append_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=scoutf_disp&scout_id=%d"\
      % scout.scout_id))

  if cSubmitted == 'Y' and cForename == '':
    edit_row(table, 'Name :', 'forename', cForename, 0, 'Forename is a required field', req=1)
  else:
    edit_row(table, 'Name :', 'forename', cForename, req=1)

  edit_row(table, 'Initials :', 'initials', cInitials)

  if cSubmitted == 'Y' and cSurname == '':
    edit_row(table, 'Surname :', 'surname', cSurname, 0, 'Surname is a required field', req=1)
  else:
    edit_row(table, 'Surname :', 'surname', cSurname, req=1)

  # DoB only required if in a junior OU or the DoB is invalid
  if scout.junior:
    if cSubmitted == 'Y' and not val_date(cDate_of_Birth):
      edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'date_of_birth', cDate_of_Birth, 0, 'Invalid date format, please check', req=1)
    else:
      edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'date_of_birth', cDate_of_Birth, req=1)
  else:
    if cSubmitted == 'Y' and cDate_of_Birth != '' and not val_date(cDate_of_Birth):
      edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'date_of_birth', cDate_of_Birth, 0,\
          'Invalid date format, please check')
    else:
      edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'date_of_birth', cDate_of_Birth)
   
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

  if not scout.junior or cAddr1 != '':
    if cParent_code == 'P2':
      # The second parent does not need an address
      edit_row(table, 'Address :', 'addr1', cAddr1)
    else:
      if cSubmitted == 'Y' and cAddr1 == '':
        edit_row(table, 'Address :', 'addr1', cAddr1, 0, 'Address must be entered', req=1)
      else:
        edit_row(table, 'Address :', 'addr1', cAddr1, req=1)
    edit_row(table, '', 'addr2', cAddr2)
    edit_row(table, '', 'addr3', cAddr3)
    edit_row(table, 'Post code :', 'p_code', cP_code)
    edit_row(table, 'Telephone (Home) :', 'telephone_h', cTelephone_h)
    edit_row(table, 'Telephone (Work) :', 'telephone_w', cTelephone_w)
    edit_row(table, 'Fax :', 'fax', cFax)

  if ourec.junior:
    edit_row(table, 'School :', 'school', cSchool)
  edit_row(table, 'E-Mail :', 'email', cEmail)
  edit_row(table, 'Mobile :', 'mobile', cMobile)
  edit_comment(table, 'Additional information :', 'add_info', cAdd_Info)

  # Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="scoutf_edit" VALUE="Submit">')

  form = webproc.form('scout.py', table.pr_table())
  form.add_hidden('jw_action', 'scoutp_edit')
  form.add_hidden('scout_id', scout.scout_id)
  form.add_hidden('ou_id', nOu)
  form.add_hidden('nxt_module', cNxt_module)
  form.add_hidden('nxt_prog', cNxt_prog)
  form.add_hidden('disp_ou', cDisp_ou)
  form.add_hidden('kid_id', nKid_id)
  form.add_hidden('parent', cParent_code)
  form.add_hidden('submitted', 'Y')

  # Output the scout edit form
  page.data.append(form.pr_form())
  page.output()
  return


##############################################################################
def scoutp_edit(form, db, param, conn):
  """Processes the input from the scout edit screen """

  nScout = int(form.getfirst('scout_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))
  cDisp_ou = form.getfirst('disp_ou', '0')

  # These modules may not always be present
  cNxt_module = form.getfirst('nxt_module', '')
  cNxt_prog = form.getfirst('nxt_prog', '')
  nKid_id = int(form.getfirst('kid_id', '0'))
  cParent_code = form.getfirst('parent', '')


  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message = "Invalid scout id")
    return

  if not nOu:
    roles = scout.role_list()
    if len(roles):
      nOu = roles[0].ou_id

  ourec = dbobj.ourec(db, nOu)

  scout.check_junior(ourec, param)
  if cParent_code.upper() == 'P1' or cParent_code.upper() == 'P2':
    scout.junior = 0

  conn.pers_security(scout)

  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  scout.forename 	= form.getfirst('forename', '')
  scout.initials 	= form.getfirst('initials', '')
  scout.surname 	= form.getfirst('surname', '')
  if form.getfirst('date_of_birth', '') != '':
    scout.date_of_birth = form.getfirst('date_of_birth', '')
  scout.mobile	 	= form.getfirst('mobile', '')
  scout.email	 	= form.getfirst('email', '')
  scout.add_info 	= form.getfirst('add_info', '')
  scout.school	 	= form.getfirst('school', '')
  scout.gender	 	= form.getfirst('gender', '')
  scout.addr1	 	= form.getfirst('addr1', '')
  scout.addr2	 	= form.getfirst('addr2', '')
  scout.addr3	 	= form.getfirst('addr3', '')
  scout.p_code	 	= form.getfirst('p_code', '')
  scout.telephone_w 	= form.getfirst('telephone_w', '')
  scout.telephone_h 	= form.getfirst('telephone_h', '')
  scout.fax	 	= form.getfirst('fax', '')

  if scout.forename == '' or scout.surname == '':
    scoutf_edit(form, db, param, conn)
    return

  if scout.junior:
    if not val_date(scout.date_of_birth):
      scoutf_edit(form, db, param, conn)
      return
  else:
    if scout.addr1 == '' and cParent_code.upper() != 'P2':
      scoutf_edit(form, db, param, conn, message = 'Revalidate address field')
      return

  scout.update()

  # Lets keep parent records talking to each other

  p1 = dbobj.adultrec(db, scout.parent1)
  p2 = dbobj.adultrec(db, scout.parent2)

  if p1.found:
    if scout.parent2 != 0 and p1.partner_id == 0:
      p1.partner_id = scout.parent2
      p1.update()

  if p2.found:
    if scout.parent1 != 0 and p2.partner_id == 0:
      p2.partner_id = scout.parent1
      p1.update()

  dbobj.log_action(db, conn.scout_id, 2, scout.scout_id)

  if cNxt_module == 'ou.py' and cNxt_prog == 'ouf_disp':
    nOu_next = int(form.getfirst('disp_ou', '0'))
    ou.ouf_disp(form, db, param, conn, ou_id = nOu_next)
  if cNxt_module == 'scout.py' and cNxt_prog == 'scoutf_disp':
    scoutf_disp(form, db, param, conn, scout_id = nKid_id)
  else:
    scoutf_disp(form, db, param, conn)
  return


#J###########################################################################
def scoutf1_add(form, db, param, conn):
  """Displays first form required to add a new scout.
This form collects the first name and surname only, then links to scoutf3_junioradd()
  if the OU is for junior members (under 14) or to scoutf2_add() for all other members

Required form fields
  ou_id

Calls 
  ou.home_page()
  scoutf_sub_name()
Screen has links to
  scoutf2_add()
 """

  # Initialise variables, reuse form variables if needed as validation may be occuring
  cSubmitted		= form.getfirst('submitted', 'N')
  cScout_forename 	= form.getfirst('scout_forename', '')
  cScout_initials 	= form.getfirst('scout_initials', '')
  cScout_surname 	= form.getfirst('scout_surname', '')

  # Must have a valid unit to add the scout to
  nOu_id = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu_id)
  if not ourec.found:
    ou.home_page(form, db, param, conn, msg = "Org unit not found")
    return

  conn.ou_security(nOu_id)

  if not conn.write:
    # go to top of browse tree
    ou.home_page(form, db, param, conn, msg="No editing rights")
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  # This table hold all output and separates the options
  outtab = outtable(param)

  # This table organises the form
  table = intable(param)

  scoutf_sub_name(table, ourec, cSubmitted, cScout_forename, cScout_initials, cScout_surname)

  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="scoutf1_add" VALUE="Submit">')
  # Output the scout edit form
  form = webproc.form('scout.py', table.pr_table(), method='POST', name='scoutf1_add')
  if ourec.junior:
    form.add_hidden('jw_action', 'scoutf3_junioradd')
  else:
    form.add_hidden('jw_action', 'scoutf2_add')
  form.add_hidden('ou_id', ourec.ou_id)
  form.add_hidden('submitted', 'N')

  outtab.add_row().add_item(form.pr_form())

  page.data.append(outtab.pr_table())
  page.output()
  return
  

#J###########################################################################
def scoutf2_add(form, db, param, conn):
  """Displays form required to add a new adult scout/member
This screen is called if the calling OU does not specify that members are under 14

Calls:
  ou.home_page()
  scoutf1_add()
  scoutf_sub_name()
Links to:
  scoutp1_add()
  scoutp2_add()
 """

  # Must have a valid unit to add the scout to
  nOu_id = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu_id)
  if not ourec.found:
    ou.home_page(form, db, param, conn, msg = "Org unit not found")
    return

  conn.ou_security(nOu_id)

  if not conn.write:
    # go to top of browse tree
    ou.home_page(form, db, param, conn, msg="No editing rights")
    return 

  # Initialise variables, reuse form variables if needed as validation may be occuring
  cSubmitted		= form.getfirst('submitted', 'N')
  cScout_forename 	= form.getfirst('scout_forename', '')
  cScout_initials 	= form.getfirst('scout_initials', '')
  cScout_surname 	= form.getfirst('scout_surname', '')
  cScout_date_of_birth 	= form.getfirst('scout_date_of_birth', '')
  cScout_school 	= form.getfirst('scout_school', '')
  cScout_gender 	= form.getfirst('scout_gender', '')
  cP_addr1 		= form.getfirst('p_addr1', '')
  cP_addr2 		= form.getfirst('p_addr2', '')
  cP_addr3 		= form.getfirst('p_addr3', '')
  cP_code 		= form.getfirst('p_code', '')
  ctelephone_h 		= form.getfirst('telephone_h', '')
  ctelephone_w 		= form.getfirst('telephone_w', '')
  cemail 		= form.getfirst('email', '')
  cmobile 		= form.getfirst('mobile', '')
  cScout_add_info 	= form.getfirst('scout_add_info', '')
  nScout_parent_id 	= all_int(form.getfirst('scout_parent_id', '0'))

  # Must have a surname and fore name
  if cScout_forename == '' or cScout_surname == '':
    scoutf1_add(form, db, param, conn)
    return

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  # This table hold all output and separates the options
  outtab = outtable(param)

  # This table organises the form
  table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
      cellspacing = param.it_cellspc, border = param.it_brdr)

  scoutf_sub_name(table, ourec, cSubmitted, cScout_forename, cScout_initials, cScout_surname)

  # Once we have the name and forename, we can check for existing users
  #process a senior member addition
  if cSubmitted == 'Y' and cP_addr1 == "":
    edit_row(table, 'Address :', 'p_addr1', cP_addr1, is_valid = 0,\
        validation_msg = "Address must be entered", req=1)
  else:
    edit_row(table, 'Address :', 'p_addr1', cP_addr1, req=1)
  edit_row(table, '', 'p_addr2', cP_addr2)
  edit_row(table, '', 'p_addr3', cP_addr3)
  edit_row(table, 'Postal Code :', 'p_code', cP_code, size = 4, maxlen = 4)
  edit_row(table, 'Phone (H) :', 'telephone_h', ctelephone_h)
  edit_row(table, 'Phone (W) :', 'telephone_w', ctelephone_w)
  edit_row(table, 'Mobile :', 'mobile', cmobile)
  edit_row(table, 'E-Mail :', 'email', cemail)
  edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'scout_date_of_birth', cScout_date_of_birth)

  # Gender
  table.add_row().add_item(webproc.tag('SPAN', 'Gender :', 'CLASS="field_descr"'))
  cLine = '<INPUT TYPE="RADIO" NAME="scout_gender" VALUE="M"'
  if cScout_gender == 'M':
    cLine += ' CHECKED'
  cLine += '>Male&nbsp;&nbsp;<INPUT TYPE="RADIO" NAME="scout_gender" VALUE="F"'
  if cScout_gender == 'F':
    cLine += ' CHECKED'
  cLine +='>Female'
  table.last_row().add_item(cLine)

  #edit_row(table, 'School :', 'scout_school', cScout_school)
  edit_row(table, 'E-Mail :', 'email', cemail)
  edit_row(table, 'Mobile :', 'mobile', cmobile)

  edit_comment(table, 'Additional information :', 'scout_add_info', cScout_add_info)
  #    return Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="scoutf_add" VALUE="Submit">')

  # Output the scout edit form
  form = webproc.form('scout.py', table.pr_table(), method='POST', name='scout_add')
  form.add_hidden('jw_action', 'scoutp1_add')
  form.add_hidden('ou_id', ourec.ou_id)
  form.add_hidden('submitted', 'Y')

  outtab.add_row().add_item(form.pr_form())

  perslist = dbobj.person_search(db, cScout_surname.rstrip(), cScout_forename[0:2].rstrip())
  # Only do this if names exist
  if len(perslist):
    # This table organises the form
    table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
        cellspacing = param.it_cellspc, border = param.it_brdr)
    table.add_row().add_item('Is the person you want to add listed here?<BR>\
      If so, just click on the name.', header=1)
    for pers in perslist:
      p_name = '%s %s' % (pers.forename, pers.surname)
      table.add_row().add_item(webproc.tag('A', p_name,\
          "href=scout.py?jw_action=scoutp2_add&ou_id=%d&scout_id=%d"\
          % (nOu_id, pers.scout_id)))

    outtab.last_row().add_item(table.pr_table(), width='25%', valign='TOP')

  page.data.append(outtab.pr_table())
  page.output()
  return
 
#J###########################################################################
def scoutf3_junioradd(form, db, param, conn):
  """Displays form required to add a new junior scout/member
This screen is called if the calling OU does not specify that members are under 14

Calls:
  ou.home_page()
  scoutf1_add()
  scoutf_sub_name()
Links to:
  scoutp1_add()
  scoutp2_add()
 """

  # Must have a valid unit to add the scout to
  nOu_id = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu_id)
  if not ourec.found:
    ou.home_page(form, db, param, conn, msg = "Org unit not found")
    return

  conn.ou_security(nOu_id)

  if not conn.write:
    # go to top of browse tree
    ou.home_page(form, db, param, conn, msg="No editing rights")
    return 

  # Initialise variables, reuse form variables if needed as validation may be occuring
  cSubmitted		= form.getfirst('submitted_f3', 'N')
  cScout_forename 	= form.getfirst('scout_forename', '')
  cScout_initials 	= form.getfirst('scout_initials', '')
  cScout_surname 	= form.getfirst('scout_surname', '')
  cScout_date_of_birth 	= form.getfirst('scout_date_of_birth', '')
  cScout_school 	= form.getfirst('scout_school', '')
  cScout_gender 	= form.getfirst('scout_gender', '')
  cemail 		= form.getfirst('email', '')
  cmobile 		= form.getfirst('mobile', '')
  cScout_add_info 	= form.getfirst('scout_add_info', '')

  # Variables for parent details
  if form.getfirst('parent_exist', 'N').upper() == 'Y':
    lParent_exist = 1
  else:
    lParent_exist = 0
  nParent_id		= int(form.getfirst('parent_id', '0'))
  cP1_forename 		= form.getfirst('p1_forename', '')
  cP1_initials 		= form.getfirst('p1_initials', '')
  cP1_surname 		= form.getfirst('p1_surname', '')
  cP1_addr1 		= form.getfirst('p1_addr1', '')
  cP1_addr2 		= form.getfirst('p1_addr2', '')
  cP1_addr3 		= form.getfirst('p1_addr3', '')
  cP1_p_code 		= form.getfirst('p1_p_code', '')
  cP1_telephone_h 	= form.getfirst('p1_telephone_h', '')
  cP1_telephone_w 	= form.getfirst('p1_telephone_w', '')
  cP1_email 		= form.getfirst('p1_email', '')
  cP1_gender 		= form.getfirst('p1_gender', '')
  cP1_mobile 		= form.getfirst('p1_mobile', '')
  cP1_add_info 		= form.getfirst('p1_add_info', '')
  cP2_forename 		= form.getfirst('p2_forename', '')
  cP2_initials 		= form.getfirst('p2_initials', '')
  cP2_surname 		= form.getfirst('p2_surname', '')
  cP2_telephone_h 	= form.getfirst('p2_telephone_h', '')
  cP2_telephone_w 	= form.getfirst('p2_telephone_w', '')
  cP2_email 		= form.getfirst('p2_email', '')
  cP2_gender 		= form.getfirst('p2_gender', '')
  cP2_mobile 		= form.getfirst('p2_mobile', '')
  cP2_add_info 		= form.getfirst('p2_add_info', '')

  # Must have a surname and fore name
  if cScout_forename == '' or cScout_surname == '':
    scoutf1_add(form, db, param, conn)
    return

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  if param.testing:
    page.data.append("<BR><B>Scoutf3_junioradd</B>")

  # This table hold all output and separates the options
  outtab = outtable(param)

  # This table organises the form
  table = intable(param)
      #webproc.table(width='100%', cellpadding = param.it_cellpad,\
      #cellspacing = param.it_cellspc, border = param.it_brdr)

  scoutf_sub_name(table, ourec, cSubmitted, cScout_forename, cScout_initials, cScout_surname)

  # Once we have the name and forename, we can check for existing users
  #process a senior member addition
  if cSubmitted == 'Y' and not val_date(cScout_date_of_birth):
    edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'scout_date_of_birth', cScout_date_of_birth, 0, 'Invalid date format, please check', req=1)
  else:
    edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'scout_date_of_birth', cScout_date_of_birth, req=1)

  edit_row(table, 'Mobile :', 'mobile', cmobile)
  edit_row(table, 'E-Mail :', 'email', cemail)

  # Gender
  table.add_row().add_item(webproc.tag('SPAN', 'Gender :', 'CLASS="field_descr"'))
  cLine = '<INPUT TYPE="RADIO" NAME="scout_gender" VALUE="M"'
  if cScout_gender == 'M':
    cLine += ' CHECKED'
  cLine += '>Male&nbsp;&nbsp;<INPUT TYPE="RADIO" NAME="scout_gender" VALUE="F"'
  if cScout_gender == 'F':
    cLine += ' CHECKED'
  cLine +='>Female'
  table.last_row().add_item(cLine)

  edit_row(table, 'School :', 'scout_school', cScout_school)

  edit_comment(table, 'Additional information :', 'scout_add_info', cScout_add_info)

  # Put the scout details into a outer table cell
  outtab.append_item(table.pr_table())
  # Make a new table
  table = intable(param)

  perslist = dbobj.person_search(db, cScout_surname.rstrip(), cScout_forename[0:2].rstrip())
  # Only do this if names exist
  # This table organises the form
  if perslist:
    table.add_row().add_item('Is the person you want to add listed here?<BR>\
      If so, just click on the name.', header=1)
  for pers in perslist:
    p_name = '%s %s' % (pers.forename, pers.surname)
    table.add_row().add_item(webproc.tag('A', p_name,\
        "href=scout.py?jw_action=scoutp2_add&ou_id=%d&scout_id=%d"\
        % (nOu_id, pers.scout_id)))

  outtab.last_row().add_item(table.pr_table(), width='25%', valign='TOP')

  # Create fresh table for parent details  
  table = intable(param)

  if lParent_exist:
    p1 = dbobj.adultrec(db, nParent_id)
    p2 = dbobj.adultrec(db, p1.partner_id)

  if lParent_exist and p1.found:
    # Code for when parent selected from right side
    table.append_item("<B>Parent details</B>", new_row = 1,colspan='2')
    table.append_item("&nbsp", new_row = 1, colspan='2')
    table.append_item(webproc.jbutton('Click here if these are not the right parents',\
        'scout.py?jw_action=scoutf3_junioradd&scout_forename=%s&scout_initials=%s&scout_surname=%s&scout_date_of_birth=%s&scout_school=%s&scout_gender=%s&scout_add_info=%s&parent_exist=N&&ou_id=%d' %\
       (cScout_forename, cScout_initials, cScout_surname, cScout_date_of_birth, cScout_school,\
       cScout_gender, cScout_add_info, ourec.ou_id)))
    table.append_item('<B>%s %s %s</B>' % (p1.forename, p1.initials, p1.surname),\
        new_row = 1, colspan='2')
    disp_if_not_blank(table, 'Address', p1.addr1)
    disp_if_not_blank(table, '', p1.addr2)
    disp_if_not_blank(table, '', p1.p_code + ' ' + p1.addr3)
    disp_if_not_blank(table, 'Phone (home)', p1.telephone_h)
    disp_if_not_blank(table, 'Phone (work)', p1.telephone_w)
    disp_if_not_blank(table, 'Phone (Mobile)', p1.mobile)
    disp_if_not_blank(table, 'Additional info', p1.add_info)

    if p2.found:
      table.append_item("&nbsp", new_row = 1, colspan='2')
      table.append_item('<B>%s %s %s</B>' % (p2.forename, p2.initials, p2.surname),\
          new_row = 1, colspan='2')
      disp_if_not_blank(table, 'Address', p2.addr1)
      disp_if_not_blank(table, '', p2.addr2)
      disp_if_not_blank(table, '', p2.p_code + ' ' + p2.addr3)
      disp_if_not_blank(table, 'Phone (home)', p2.telephone_h)
      disp_if_not_blank(table, 'Phone (work)', p2.telephone_w)
      disp_if_not_blank(table, 'Phone (Mobile)', p2.mobile)
      disp_if_not_blank(table, 'Additional info', p2.add_info)

    table.append_item("&nbsp", new_row = 1, colspan='2')

  else:
    # Display fields for parents to be added
    # Row 2, 'Parent 1 title
    table.add_row().add_item(webproc.tag('H4', 'Parent 1'))
  
    # P1 forename
    if cSubmitted == 'Y' and cP1_forename == '':
      edit_row(table, 'Name :', 'p1_forename', cP1_forename, 0, 'Forename is a required field', req=1)
    else:
      edit_row(table, 'Name :', 'p1_forename', cP1_forename, req=1)

    # Initials
    edit_row(table, 'Initials :', 'p1_initials', cP1_initials)
 
    # surname
    if cSubmitted == 'Y' and cP1_surname == '':
      edit_row(table, 'Name :', 'p1_surname', cP1_surname, 0, 'Surname is a required field', req=1)
    else:
      edit_row(table, 'Name :', 'p1_surname', cP1_surname, req=1)

    # Row 5, address
    if cSubmitted == 'Y' and cP1_addr1 == '':
      edit_row(table, 'Address :', 'p1_addr1', cP1_addr1, 0, 'Address is a required field', req=1)
    else:
      edit_row(table, 'Address :', 'p1_addr1', cP1_addr1, req=1)

    edit_row(table, '', 'p1_addr2', cP1_addr2)
    edit_row(table, '', 'p1_addr3', cP1_addr3)
    edit_row(table, 'Postal Code :', 'p1_p_code', cP1_p_code, size = 4, maxlen = 4)
    edit_row(table, 'Phone (H) :', 'p1_telephone_h', cP1_telephone_h)
    edit_row(table, 'Phone (W) :', 'p1_telephone_w', cP1_telephone_w)
    edit_row(table, 'Mobile :', 'p1_mobile', cP1_mobile)
    edit_row(table, 'E-Mail :', 'p1_email', cP1_email)
    edit_comment(table, 'Additional information :', 'p1_add_info', cP1_add_info)

     # Parent 2
    table.add_row().add_item(webproc.tag('H4', 'Parent 2'))

    edit_row(table, 'Name :', 'p2_forename', cP2_forename)
    edit_row(table, 'Initials :', 'p2_initials', cP2_initials)
    edit_row(table, 'Surname :', 'p2_surname', cP2_surname)
    edit_row(table, 'Phone (H) :', 'p2_telephone_h', cP2_telephone_h)
    edit_row(table, 'Phone (W) :', 'p2_telephone_w', cP2_telephone_w)
    edit_row(table, 'Mobile :', 'p2_mobile', cP2_mobile)
    edit_row(table, 'E-Mail :', 'p2_email', cP2_email)
    edit_comment(table, 'Additional information :', 'p2_add_info', cP2_add_info)
    # End of new parent add details


  #    return Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="scoutf_add" VALUE="Submit">')

  outtab.append_item(table.pr_table(), new_row = 1, valign='TOP')

  # Build a list of OU's that we will search for parents
  # First we navigate up to the 'group' level. Defined by param instance

  table = intable(param)
  ou_top = ourec
  while ou_top.ou_struct != param.group_ou_struct:
    ou_top = dbobj.ourec(db, ou_top.ou_owner)
    if not ou_top.found:
      break

  # If a group record has not been found, use the original
  if ou_top.ou_struct != param.group_ou_struct:
    ou_top = ourec

  parents = []
  parents_in_sub_ou(ou_top, parents, cScout_surname)

  for p in parents:
    p2 = dbobj.adultrec(db, p.partner_id)
    if not p2.found:
      name = "%s %s" % (p.forename, p.surname)
    elif p.surname == p2.surname:
      name = "%s & %s %s" % (p.forename, p2.forename, p.surname)
    else:
      name = "%s %s & %s %s" % (p.forename, p.surname, p2.forename, p2.surname)
    disp = "<B>%s</B><BR>%s<BR>" % (name, p.addr1)
    if p.addr2 != '':
      disp += p.addr2 + '<BR>'
    if p.addr3 != '' or p.p_code.strip() != '':
      disp += '%sp %s<BR>' % (p.addr3, p.p_code)

    disp += webproc.jbutton('Use ' + name, 'scout.py?jw_action=scoutf3_junioradd&scout_forename=%s&scout_initials=%s&scout_surname=%s&scout_date_of_birth=%s&scout_school=%s&scout_gender=%s&scout_add_info=%s&parent_exist=Y&parent_id=%d&ou_id=%d' %\
       (cScout_forename, cScout_initials, cScout_surname, cScout_date_of_birth, cScout_school,\
       cScout_gender, cScout_add_info, p.scout_id, ourec.ou_id))

    table.append_item(disp, new_row=1)
    table.append_item("&nbsp", new_row=1)


  outtab.append_item(table.pr_table(), valign='TOP')

  # Output the scout edit form
  form = webproc.form('scout.py', outtab.pr_table(), name='scout_addf3')
  form.add_hidden('jw_action', 'scoutp3_add')
  form.add_hidden('ou_id', ourec.ou_id)
  form.add_hidden('submitted_f3', 'Y')
  if lParent_exist and p1.found:
    form.add_hidden('parent_exist', 'Y')
    form.add_hidden('parent_id', str(p1.scout_id))

  page.data.append(form.pr_form())
  page.output()
  return


##############################################################################
def parents_in_sub_ou(ourec, parentlist, in_surname):
  """This procedure is used iteratively to process all OU's in a heirarchy"""
  # First add parents from this OU
  prnts = ourec.parent_list(surname = in_surname)
  for p in prnts:
    # We must only add the parent if they don't already exist on the list
    exist = 0
    for t in parentlist:
      if t.scout_id == p.scout_id:
        exist = 1
        break

    if not exist:
      parentlist.append(p)

  chld = ourec.child_list()
  for c in chld:
    parents_in_sub_ou(c, parentlist, in_surname)
    
  return

##############################################################################
def disp_if_not_blank(table, descr, value):
  """Adds a new line to the table if the value is not blank"""
  value = value.strip()
  if str(value) is not None and str(value) != '':
    table.append_item(descr, new_row = 1)
    table.append_item(str(value))
  return


##############################################################################
def scoutf_sub_name(table, ou, cSubmitted, cScout_forename, cScout_initials, cScout_surname):
  """Common routine for displaying scout name details in add screens
Links to:
  ou.ouf_disp()"""
  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = '25%'
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = '33%'
  colgr.cols.append(col)

  # 3rd column
  col = webproc.table_col()
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  table.add_row().add_item(webproc.tag('H3', 'Scout details'))
  table.last_row().add_item('<SPAN CLASS="validation_message">* denotes required field</SPAN>', styleclass = 'error')
  table.last_row().add_item(webproc.tag('A', 'Cancel', "href=ou.py?jw_action=ouf_disp&ou_id=" + str(ou.ou_id)))

  if cSubmitted == 'Y' and cScout_forename == '':
    edit_row(table, 'Name :', 'scout_forename', cScout_forename, 0, 'Forename is a required field', req=1)
  else:
    edit_row(table, 'Name :', 'scout_forename', cScout_forename, req=1)

  edit_row(table, 'Initials :', 'scout_initials', cScout_initials)

  if cSubmitted == 'Y' and cScout_surname == '':
    edit_row(table, 'Surname :', 'scout_surname', cScout_surname, 0, 'Surname is a required field', req=1)
  else:
    edit_row(table, 'Surname :', 'scout_surname', cScout_surname, req=1)
  return


##############################################################################
def scoutp1_add(form, db, param, conn):
  """Processes the input from the scout add screen for adults """

  nOu = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu)
  
  if not ourec.found:
    ou.home_page(form, db, param, conn)
    return

  # Initialise variables, reuse form variables if needed as validation may be occuring
  cSubmitted		= form.getfirst('submitted', 'N')
  cScout_forename 	= form.getfirst('scout_forename', '')
  cScout_initials 	= form.getfirst('scout_initials', '')
  cScout_surname 	= form.getfirst('scout_surname', '')
  cScout_date_of_birth 	= form.getfirst('scout_date_of_birth', '')
  cScout_gender 	= form.getfirst('scout_gender', '')
  cP_addr1 		= form.getfirst('p_addr1', '')
  cP_addr2 		= form.getfirst('p_addr2', '')
  cP_addr3 		= form.getfirst('p_addr3', '')
  cP_code 		= form.getfirst('p_code', '')
  ctelephone_h 		= form.getfirst('telephone_h', '')
  ctelephone_w 		= form.getfirst('telephone_w', '')
  cemail 		= form.getfirst('email', '')
  cmobile 		= form.getfirst('mobile', '')
  cScout_add_info 	= form.getfirst('scout_add_info', '')
  nScout_parent_id 	= all_int(form.getfirst('scout_parent_id', '0'))
  cSenior_junior	= form.getfirst('senior_junior', ' ')

  conn.ou_security(nOu)
  can_edit = conn.write

  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  if cScout_forename == '' or cScout_surname == '':
    scoutf1_add(form, db, param, conn)
    return

  if cP_addr1 == '':
    scoutf2_add(form, db, param, conn)
    return

  adult = dbobj.adultrec(db, 0)
  adult.forename 	= cScout_forename
  adult.initials 	= cScout_initials
  adult.surname 	= cScout_surname
  adult.date_of_birth 	= cScout_date_of_birth
  adult.mobile	 	= cmobile
  adult.email	 	= cemail
  adult.add_info 	= cScout_add_info
  adult.gender	 	= cScout_gender
  adult.add()

  role = dbobj.rolerec(db, 0)
  role.scout_id = adult.scout_id
  role.ou_id = ourec.ou_id
  role.status = 'C'
  role.add_edit()
  ou.ouf_disp(form, db, param, conn, ou_id = ourec.ou_id)  
  return
 
##############################################################################
def scoutp2_add(form, db, param, conn):
  """Processes the input from the already existing scout add screen
This module adds a role record to link this member with this OU
Then it call ou.ouf_disp()
"""

  nOu = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu)
  
  if not ourec.found:
    ou.home_page(form, db, param, conn)
    return

  conn.ou_security(nOu)
  can_edit = conn.write

  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  scout = dbobj.adultrec(db, int(form.getfirst('scout_id', '0')))
  if scout.found:
    role = dbobj.rolerec(db, 0)
    role.scout_id = scout.scout_id
    role.ou_id = ourec.ou_id
    role.status = 'C'
    role.add_edit()

  ou.ouf_disp(form, db, param, conn, ou_id = ourec.ou_id)  
  return

##############################################################################
def scoutp3_add(form, db, param, conn):
  """Processes the input from the Junior scout add screen for Juniors
Called by : scoutf3_junioradd()
Calls ou.ouf_disp
Initialises variables from form input
Validates OU and user security
Validates required fields:
  Junior birthday
  Parent name & surname
  Parent address
Adds a scout record
Adds parent(s) records
adds a role record for the scout
"""

  nOu = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu)
  
  if not ourec.found:
    ou.home_page(form, db, param, conn)
    return

  # Initialise variables, reuse form variables if needed as validation may be occuring
  cSubmitted		= form.getfirst('submitted', 'N')
  cScout_forename 	= form.getfirst('scout_forename', '')
  cScout_initials 	= form.getfirst('scout_initials', '')
  cScout_surname 	= form.getfirst('scout_surname', '')
  cScout_date_of_birth 	= form.getfirst('scout_date_of_birth', '')
  cScout_gender 	= form.getfirst('scout_gender', '')
  cemail 		= form.getfirst('email', '')
  cmobile 		= form.getfirst('mobile', '')
  cScout_add_info 	= form.getfirst('scout_add_info', '')

  # Variables for parent details
  nParent_id 		= int(form.getfirst('parent_id', '0'))
  cP1_forename 		= form.getfirst('p1_forename', '')
  cP1_initials 		= form.getfirst('p1_initials', '')
  cP1_surname 		= form.getfirst('p1_surname', '')
  cP1_addr1 		= form.getfirst('p1_addr1', '')
  cP1_addr2 		= form.getfirst('p1_addr2', '')
  cP1_addr3 		= form.getfirst('p1_addr3', '')
  cP1_p_code 		= form.getfirst('p1_p_code', '')
  cP1_telephone_h 	= form.getfirst('p1_telephone_h', '')
  cP1_telephone_w 	= form.getfirst('p1_telephone_w', '')
  cP1_email 		= form.getfirst('p1_email', '')
  cP1_gender 		= form.getfirst('p1_gender', '')
  cP1_mobile 		= form.getfirst('p1_mobile', '')
  cP1_add_info 		= form.getfirst('p1_add_info', '')
  cP2_forename 		= form.getfirst('p2_forename', '')
  cP2_initials 		= form.getfirst('p2_initials', '')
  cP2_surname 		= form.getfirst('p2_surname', '')
  cP2_telephone_h 	= form.getfirst('p2_telephone_h', '')
  cP2_telephone_w 	= form.getfirst('p2_telephone_w', '')
  cP2_email 		= form.getfirst('p2_email', '')
  cP2_gender 		= form.getfirst('p2_gender', '')
  cP2_mobile 		= form.getfirst('p2_mobile', '')
  cP2_add_info 		= form.getfirst('p2_add_info', '')

  if form.getfirst('parent_exist', 'N').upper() == 'Y':
    lParent_exist = 1
  else:
    lParent_exist = 0

  if lParent_exist:
    p1 = dbobj.adultrec(db, nParent_id)
    if not p1.found:
      scoutf3_junioradd(form, db, param, conn)
      return
    p2 = dbobj.adultrec(db, p1.partner_id)


  conn.ou_security(nOu)
  can_edit = conn.write

  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  if cScout_forename == '' or cScout_surname == '':
    scoutf1_add(form, db, param, conn)
    return

  if not val_date(cScout_date_of_birth):
    scoutf3_junioradd(form, db, param, conn)
    return
 
  if not lParent_exist:
    # need to do these checks if we are adding parents
    if cP1_forename == '' or cP1_surname == '':
      scoutf3_junioradd(form, db, param, conn)
      return

    if cP1_addr1 == '':
      scoutf3_junioradd(form, db, param, conn)
      return

  # OK Lets add the scout record
  scout = dbobj.scoutrec(db, 0)
  scout.forename 	= cScout_forename
  scout.initials 	= cScout_initials
  scout.surname 	= cScout_surname
  scout.date_of_birth 	= cScout_date_of_birth
  scout.mobile	 	= cmobile
  scout.email	 	= cemail
  scout.add_info 	= cScout_add_info
  scout.gender	 	= cScout_gender
  if lParent_exist:
    scout.parent1	= p1.scout_id
    scout.parent2	= p2.scout_id
  scout.add()

  # Add the role record for the scout
  role = dbobj.rolerec(db, 0)
  role.scout_id = scout.scout_id
  role.ou_id = ourec.ou_id
  role.status = 'C'
  role.add_edit()

  if not lParent_exist:
    # Create the first parent
    p1 = dbobj.adultrec(db, 0)
    p1.forename = cP1_forename
    p1.initials = cP1_initials
    p1.surname = cP1_surname
    p1.addr1 = cP1_addr1
    p1.addr2 = cP1_addr2
    p1.addr3 = cP1_addr3
    p1.p_code = cP1_p_code
    p1.telephone_h = cP1_telephone_h
    p1.telephone_w = cP1_telephone_w
    p1.email = cP1_email 
    p1.gender = cP1_gender
    p1.mobile = cP1_mobile 
    p1.add_info = cP1_add_info
    p1.add()
    scout.parent1 = p1.scout_id 

    # Create the second parent
    if cP2_forename != '' and cP2_surname != '':
      p2 = dbobj.adultrec(db, 0)
      p2.forename = cP2_forename
      p2.initials = cP2_initials
      p2.surname = cP2_surname
      p2.addr1 = cP1_addr1
      p2.addr2 = cP1_addr2
      p2.addr3 = cP1_addr3
      p2.p_code = cP1_p_code
      p2.telephone_h = cP2_telephone_h
      p2.telephone_w = cP2_telephone_w
      p2.email = cP2_email 
      p2.gender = cP2_gender
      p2.mobile = cP2_mobile 
      p2.add_info = cP2_add_info
      p2.add()
      scout.parent2 = p2.scout_id 

    # Must update to set parent details
    scout.update()

  db.commit()

  ou.ouf_disp(form, db, param, conn, ou_id = ourec.ou_id)  
  return
 
"""
############################################################################
def scoutf_add(form, db, param, conn):
  pass
    # Must have a valid unit to add the scout to
  nOu_id = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu_id)
  if not ourec.found:
    ou.home_page(form, db, param, conn, msg = "Org unit not found")
    return

  conn.ou_security(nOu_id)

  if not conn.write:
    # go to top of browse tree
    ou.home_page(form, db, param, conn, msg="No editing rights")
    return 

  # Initialise variables, reuse form variables if needed as validation may be occuring
  cSubmitted		= form.getfirst('submitted', 'N')
  cScout_forename 	= form.getfirst('scout_forename', '')
  cScout_initials 	= form.getfirst('scout_initials', '')
  cScout_surname 	= form.getfirst('scout_surname', '')
  cScout_date_of_birth 	= form.getfirst('scout_date_of_birth', '')
  cScout_school 	= form.getfirst('scout_school', '')
  cScout_gender 	= form.getfirst('scout_gender', '')
  cP_addr1 		= form.getfirst('p_addr1', '')
  cP_addr2 		= form.getfirst('p_addr2', '')
  cP_addr3 		= form.getfirst('p_addr3', '')
  cP_code 		= form.getfirst('p_code', '')
  ctelephone_h 		= form.getfirst('telephone_h', '')
  ctelephone_w 		= form.getfirst('telephone_w', '')
  cemail 		= form.getfirst('email', '')
  cmobile 		= form.getfirst('mobile', '')
  cScout_add_info 	= form.getfirst('scout_add_info', '')
  nScout_parent_id 	= all_int(form.getfirst('scout_parent_id', '0'))
  cMemb_exist 		= form.getfirst('memb_exist', 'N')
  nScout_id 		= int(form.getfirst('scout_id', 0))
  cFull_screen		= form.getfirst('full_screen', '')

  cSenior_junior	= ' '

  if cMemb_exist == 'Y':
    cMsg = 'Memb exists'
    pers = dbobj.personrec(db, nScout_id)
    if pers.found:
      role = pers.role_by_ou(nOu_id)
      if role.found:
        role.status = 'C'
        role.add_edit()
      else:
        role.scout_id = nScout_id
        role.ou_id = nOu_id
        role.status = 'C'
        role.add_edit()
      db.commit()
    else:
      cMsg += '<BR>Person not found'
    ou.ouf_disp(form, db, param, conn, ou_id = nOu_id, msg = cMsg)
    return

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  # This table hold all output and separates the options
  outtable = webproc.table(width='100%', cellpadding = param.ot_cellpad,\
      cellspacing = param.ot_cellspc, border = param.ot_brdr)

  # This table organises the form
  table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
      cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = '25%'
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = '33%'
  colgr.cols.append(col)

  # i3rd column
  col = webproc.table_col()
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  table.add_row().add_item(webproc.tag('H3', 'Scout details'))
  table.last_row().add_item('<SPAN CLASS="validation_message">* denotes required field</SPAN>', styleclass = 'error')
  table.last_row().add_item(webproc.tag('A', 'Cancel', "href=ou.py?jw_action=ouf_disp&ou_id=" + str(ourec.ou_id)))

  if cSubmitted == 'Y' and cScout_forename == '':
    edit_row(table, 'Name :', 'scout_forename', cScout_forename, 0, 'Forename is a required field', req=1)
  else:
    edit_row(table, 'Name :', 'scout_forename', cScout_forename, req=1)

  edit_row(table, 'Initials :', 'scout_initials', cScout_initials)

  if cSubmitted == 'Y' and cScout_surname == '':
    edit_row(table, 'Surname :', 'scout_surname', cScout_surname, 0, 'Surname is a required field', req=1)
  else:
    edit_row(table, 'Surname :', 'scout_surname', cScout_surname, req=1)

  # Once we have the name and forename, we can check for existing users
  if cScout_surname != '' and cScout_forename != '':
    if not ourec.junior:
      #process a senior member addition
      edit_row(table, 'Address :', 'p_addr1', cP_addr1)
      edit_row(table, '', 'p_addr2', cP_addr2)
      edit_row(table, '', 'p_addr3', cP_addr3)
      edit_row(table, 'Postal Code :', 'p_code', cP_code, size = 4, maxlen = 4)
      edit_row(table, 'Phone (H) :', 'telephone_h', ctelephone_h)
      edit_row(table, 'Phone (W) :', 'telephone_w', ctelephone_w)
      edit_row(table, 'Mobile :', 'mobile', cmobile)
      edit_row(table, 'E-Mail :', 'email', cemail)
      cSenior_junior = 'S'
    else:
      cSenior_junior = 'J'
      if cSubmitted == 'Y' and cFull_screen == 'Y' and ourec.junior and not val_date(cScout_date_of_birth):
        edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'scout_date_of_birth', cScout_date_of_birth,\
            0, 'Invalid date format, please check', req=1)
      else:
        edit_row(table, 'Date of Birth (YYYY-MM-DD):', 'scout_date_of_birth', cScout_date_of_birth, req=1)

      # Gender
      table.add_row().add_item(webproc.tag('SPAN', 'Gender :', 'CLASS="field_descr"'))
      cLine = '<INPUT TYPE="RADIO" NAME="scout_gender" VALUE="M"'
      if cScout_gender == 'M':
        cLine += ' CHECKED'
      cLine += '>Male&nbsp;&nbsp;<INPUT TYPE="RADIO" NAME="scout_gender" VALUE="F"'
      if cScout_gender == 'F':
        cLine += ' CHECKED'
      cLine +='>Female'
      table.last_row().add_item(cLine)

      edit_row(table, 'School :', 'scout_school', cScout_school)
      edit_row(table, 'E-Mail :', 'email', cemail)
      edit_row(table, 'Mobile :', 'mobile', cmobile)
 
    edit_comment(table, 'Additional information :', 'scout_add_info', cScout_add_info)
  #    return Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="scoutf_add" VALUE="Submit">')

  # Output the scout edit form
  form = webproc.form('scout.py', table.pr_table(), method='POST', name='scout_add')
  form.add_hidden('jw_action', 'scoutp1_add')
  form.add_hidden('ou_id', ourec.ou_id)
  form.add_hidden('submitted', 'Y')
  if cSenior_junior == 'S':
    form.add_hidden('senior_junior', 'S')
  elif cSenior_junior == 'J':
    form.add_hidden('senior_junior', 'J')


  outtable.add_row().add_item(form.pr_form())

  if cScout_surname != '' and cScout_forename != '':
    perslist = dbobj.person_search(db, cScout_surname.rstrip(), cScout_forename[0:2].rstrip())
    # Only do this if names exist
    if len(perslist):
      # This table organises the form
      table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
          cellspacing = param.it_cellspc, border = param.it_brdr)
      table.add_row().add_item('Is the person you want to add listed here?<BR>\
        If so, just click on the name.', header=1)
      for pers in perslist:
        p_name = '%s %s' % (pers.forename, pers.surname)
        table.add_row().add_item(webproc.tag('A', p_name,\
            "href=scout.py?jw_action=scoutf_add&ou_id=%d&memb_exist=Y&scout_id=%d"\
            % (nOu_id, pers.scout_id)))

      outtable.last_row().add_item(table.pr_table(), width='25%', valign='TOP')

  page.data.append(outtable.pr_table())
  page.output()
  return


##############################################################################
def scoutp_add(form, db, param, conn):
  "Processes the input from the scout add screen "
  pass
  nOu = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu)
  
  if not ourec.found:
    ou.home_page(form, db, param, conn)

  # Initialise variables, reuse form variables if needed as validation may be occuring
  cSubmitted		= form.getfirst('submitted', 'N')
  cScout_forename 	= form.getfirst('scout_forename', '')
  cScout_initials 	= form.getfirst('scout_initials', '')
  cScout_surname 	= form.getfirst('scout_surname', '')
  cScout_date_of_birth 	= form.getfirst('scout_date_of_birth', '')
  cScout_school 	= form.getfirst('scout_school', '')
  cScout_gender 	= form.getfirst('scout_gender', '')
  cP_addr1 		= form.getfirst('p_addr1', '')
  cP_addr2 		= form.getfirst('p_addr2', '')
  cP_addr3 		= form.getfirst('p_addr3', '')
  cP_code 		= form.getfirst('p_code', '')
  ctelephone_h 		= form.getfirst('telephone_h', '')
  ctelephone_w 		= form.getfirst('telephone_w', '')
  cemail 		= form.getfirst('email', '')
  cmobile 		= form.getfirst('mobile', '')
  cScout_add_info 	= form.getfirst('scout_add_info', '')
  nScout_parent_id 	= all_int(form.getfirst('scout_parent_id', '0'))
  cMemb_exist 		= form.getfirst('memb_exist', 'N')
  nScout_id 		= int(form.getfirst('scout_id', 0))
  cSenior_junior	= form.getfirst('senior_junior', ' ')
  cFull_screen		= form.getfirst('full_screen', '')

  conn.ou_security(nOu)
  can_edit = conn.write

  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  if cScout_forename == '' or cScout_surname == '':
    scoutf_add(form, db, param, conn)
    return

  if cSenior_junior == 'J':
    if not val_date(cScout_date_of_birth):
      scoutf_add(form, db, param, conn)
      return

  elif cSenior_junior == 'S':
    if cP_addr1 == '':
      scoutf_add(form, db, param, conn)
      return
    adult = dbobj.adultrec(db, 0)
    adult.forename 	= cScout_forename
    adult.initials 	= cScout_initials
    adult.surname 	= cScout_surname
    adult.date_of_birth 	= cScout_date_of_birth
    adult.mobile	 	= cmobile
    adult.email	 	= cemail
    adult.add_info 	= cScout_add_info
    adult.add()

    role = dbobj.rolerec(db, 0)
    role.scout_id = adult.scout_id
    role.ou_id = ourec.ou_id
    role.status = 'C'
    role.add_edit()
    ou.ouf_disp(form, db, param, conn, ou_id = ourec.ou_id)  
    return

  scoutf_add1(form, db, param,conn)
  return

##############################################################################
def scoutf_add1(form, db, param, conn):
  "Displays form required to add a parents for a new scout "
  pass
  # Must have a valid unit to add the scout to
  nOu_id = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu_id)
  if not ourec.found:
    app_error(form, param, conn, message="Invalid unit")
    return

  conn.ou_security(nOu_id)
  can_edit = conn.write

  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  # Initialise variables, reuse form variables if needed as validation may be occuring

  #These variables need to be saved from the first scout add screen
  cScout_forename 	= form.getfirst('scout_forename', '')
  cScout_initials 	= form.getfirst('scout_initials', '')
  cScout_surname 	= form.getfirst('scout_surname', '')
  cScout_date_of_birth 	= form.getfirst('scout_date_of_birth', '')
  cScout_school 	= form.getfirst('scout_school', '')
  cScout_gender 	= form.getfirst('scout_gender', '')
  cScout_email 		= form.getfirst('scout_email', '')
  cScout_mobile 	= form.getfirst('scout_mobile', '')
  cScout_add_info 	= form.getfirst('scout_add_info', '')

  # These variables will be new on the first time the screen is displayed
  cParent_submit 	= form.getfirst('scoutf_add1_submitted', 'N')
  cP1_forename 		= form.getfirst('p1_forename', '')
  cP1_initials 		= form.getfirst('p1_initials', '')
  cP1_surname 		= form.getfirst('p1_surname', '')
  cP1_addr1 		= form.getfirst('p1_addr1', '')
  cP1_addr2 		= form.getfirst('p1_addr2', '')
  cP1_addr3 		= form.getfirst('p1_addr3', '')
  cP1_p_code 		= form.getfirst('p1_p_code', '')
  cP1_telephone_h 	= form.getfirst('p1_telephone_h', '')
  cP1_telephone_w 	= form.getfirst('p1_telephone_w', '')
  cP1_email 		= form.getfirst('p1_email', '')
  cP1_gender 		= form.getfirst('p1_gender', '')
  cP1_mobile 		= form.getfirst('p1_mobile', '')
  cP1_add_info 		= form.getfirst('p1_add_info', '')
  cP2_forename 		= form.getfirst('p2_forename', '')
  cP2_initials 		= form.getfirst('p2_initials', '')
  cP2_surname 		= form.getfirst('p2_surname', '')
  cP2_telephone_h 	= form.getfirst('p2_telephone_h', '')
  cP2_telephone_w 	= form.getfirst('p2_telephone_w', '')
  cP2_email 		= form.getfirst('p2_email', '')
  cP2_gender 		= form.getfirst('p2_gender', '')
  cP2_mobile 		= form.getfirst('p2_mobile', '')
  cP2_add_info 		= form.getfirst('p2_add_info', '')

  if cP1_surname == '':
    cP1_surname = cScout_surname

  # Blank list to store parent details in.
  parentlist = []
  same_surname = []

  # We will start one level up in ou structure if it exists

  nOu_top = ourec.ou_owner
  if not nOu_top:
    nOu_top = ourec.ou_id
  
  # Get the top OU we are going to search from
  ou_top = dbobj.ourec(db, nOu_top)
  # Get parents in top OU
  ou_top.parent_list()
  for p in ou_top.parentlist:
    add_parent(parentlist, p)
    if p.surname == cScout_surname:
      same_surname.append(p)

  # Get a list of OU children
  ou_top.child_list()
  for o in ou_top.childlist:
    o.parent_list()
    for p in o.parentlist:
      add_parent(parentlist, p)
      if p.surname == cScout_surname:
        same_surname.append(p)


    # We are going to go dowm one level too
    o.child_list()
    for c in o.childlist:
      c.parent_list()
      for p in c.parentlist:
        add_parent(parentlist, p)
        if p.surname == cScout_surname:
          same_surname.append(p)


  parentlist = dbobj.sort_by_attr(parentlist, 'surname')

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  # This table hold all output and separates the options
  outtable = webproc.table(width='100%', cellpadding = param.ot_cellpad, cellspacing = param.ot_cellspc, border = param.ot_brdr)

  outtable.add_row().add_item(webproc.tag('H3', 'Parent details for ' + cScout_forename + ' ' + cScout_surname))

  #############################################################################
  # This table organises the form for parent with the same name
  if len(same_surname):
    table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

    table.add_row().add_item(webproc.tag('H4', 'Parents with the same surname'))

    for p in same_surname:
      table.add_row().add_item('%s %s' % (p.forename, p.surname))

    outtable.add_row().add_item(table.pr_table())

  #############################################################################
  # This table organises the form for parent with the same name
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  table.add_row().add_item(webproc.tag('H4', 'Other parents from %s' % ou_top.name))
  for p in parentlist:
    table.add_row().add_item('%s %s' % (p.forename, p.surname))

  outtable.add_row().add_item(table.pr_table())

  #############################################################################
  # This table organises the form for direct parent input
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = '25%'
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = '33%'
  colgr.cols.append(col)

  # i3rd column
  col = webproc.table_col()
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  table.add_row().add_item(' ')
  table.last_row().add_item('<SPAN CLASS="validation_message">* denotes required field</SPAN>', styleclass = 'error')
  table.last_row().add_item(webproc.tag('A', 'Cancel', "href=ou.py?jw_action=ouf_disp&ou_id=%d" % ourec.ou_id))

  # Row 2, 'Parent 1 title
  table.add_row().add_item(webproc.tag('H4', 'Parent 1'))

  # P1 forename
  if cParent_submit == 'Y' and cP1_forename == '':
    edit_row(table, 'Name :', 'p1_forename', cP1_forename, 0, 'Forename is a required field', req=1)
  else:
    edit_row(table, 'Name :', 'p1_forename', cP1_forename, req=1)

  # Initials
  edit_row(table, 'Initials :', 'p1_initials', cP1_initials)
 
  # surname
  if cParent_submit == 'Y' and cP1_surname == '':
    edit_row(table, 'Name :', 'p1_surname', cP1_surname, 0, 'Surname is a required field', req=1)
  else:
    edit_row(table, 'Name :', 'p1_surname', cP1_surname, req=1)

  # Row 5, address
  if cParent_submit == 'Y' and cP1_addr1 == '':
    edit_row(table, 'Address :', 'p1_addr1', cP1_addr1, 0, 'Address is a required field', req=1)
  else:
    edit_row(table, 'Address :', 'p1_addr1', cP1_addr1, req=1)

  edit_row(table, '', 'p1_addr2', cP1_addr2)
  edit_row(table, '', 'p1_addr3', cP1_addr3)
  edit_row(table, 'Postal Code :', 'p1_p_code', cP1_p_code, size = 4, maxlen = 4)
  edit_row(table, 'Phone (H) :', 'p1_telephone_h', cP1_telephone_h)
  edit_row(table, 'Phone (W) :', 'p1_telephone_w', cP1_telephone_w)
  edit_row(table, 'Mobile :', 'p1_mobile', cP1_mobile)
  edit_row(table, 'E-Mail :', 'p1_email', cP1_email)
  edit_comment(table, 'Additional information :', 'p1_add_info', cP1_add_info)

   # Parent 2
  table.add_row().add_item(webproc.tag('H4', 'Parent 2'))

  edit_row(table, 'Name :', 'p2_forename', cP2_forename)
  edit_row(table, 'Initials :', 'p2_initials', cP2_initials)
  edit_row(table, 'Surname :', 'p2_surname', cP2_surname)
  edit_row(table, 'Phone (H) :', 'p2_telephone_h', cP2_telephone_h)
  edit_row(table, 'Phone (W) :', 'p2_telephone_w', cP2_telephone_w)
  edit_row(table, 'Mobile :', 'p2_mobile', cP2_mobile)
  edit_row(table, 'E-Mail :', 'p2_email', cP2_email)
  edit_comment(table, 'Additional information :', 'p2_add_info', cP2_add_info)

  # Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="scoutf_add" VALUE="Submit">')
  form = webproc.form('scout.py', table.pr_table(), 'scoutf_add1')

  # we need to pass on a lot of info from the previous screen to be processed
  form.add_hidden("jw_action", "scoutp_add1")
  form.add_hidden("ou_id", ourec.ou_id)
  form.add_hidden("scoutf_add1_submitted", "Y")
  form.add_hidden("scout_forename", cScout_forename)
  form.add_hidden("scout_initials", cScout_initials)
  form.add_hidden("scout_surname", cScout_surname)
  form.add_hidden("scout_date_of_birth", cScout_date_of_birth)
  form.add_hidden("scout_school", cScout_school)
  form.add_hidden("scout_gender", cScout_gender)
  form.add_hidden("scout_email", cScout_email)
  form.add_hidden("scout_mobile", cScout_mobile)
  form.add_hidden("scout_add_info", cScout_add_info)

  # Output the scout edit form
  outtable.add_row().add_item(form.pr_form())
  
  page.data.append(outtable.pr_table())
  page.output()
 
  return
  """

##############################################################################
def add_parent(list, parent):
  found = 0
  for x in list:
    if x.scout_id == parent.scout_id:
      found = 1
      break
  if not found:
    list.append(parent)
  return

"""
##############################################################################
def scoutp_add1(form, db, param, conn):
  "Processes the input from the second (parent add) scout add screen "
  pass
  
  nUnit = int(form.getfirst('unit_id', '0'))
  unit = dbobj.unitrec(db, nUnit)
  if not unit.found:
    app_error(form, param, conn, message="Invalid unit")
    return

  can_edit = edit_check(db, 'U', unit.unit_id, conn.scout_id)
  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  # Initialise scout record
  scout = dbobj.scoutrec(db, 0)
  scout.forename 	= form.getfirst('scout_forename', '')
  scout.initials 	= form.getfirst('scout_initials', '')
  scout.surname 	= form.getfirst('scout_surname', '')
  scout.date_of_birth 	= form.getfirst('scout_date_of_birth', '')
  scout.mobile	 	= form.getfirst('scout_mobile', '')
  scout.email	 	= form.getfirst('scout_email', '')
  scout.add_info 	= form.getfirst('scout_add_info', '')
  scout.school	 	= form.getfirst('scout_school', '')
  scout.unit_id		= unit.unit_id

  if scout.forename == '' or scout.surname == '':
    scoutf_add(form, db, param, conn)
    return

  if not val_date(scout.date_of_birth):
    scoutf_add(form, db, param, conn)
    return

  # initialise first parent record
  parent1 = dbobj.adultrec(db, 0)
  parent1.forename 	= form.getfirst('p1_forename', '')
  parent1.initials 	= form.getfirst('p1_initials', '')
  parent1.surname 	= form.getfirst('p1_surname', '')
  parent1.addr1 	= form.getfirst('p1_addr1', '')
  parent1.addr2 	= form.getfirst('p1_addr2', '')
  parent1.addr3 	= form.getfirst('p1_addr3', '')
  parent1.p_code 	= form.getfirst('p1_p_code', '')
  parent1.telephone_h 	= form.getfirst('p1_telephone_h', '')
  parent1.telephone_w 	= form.getfirst('p1_telephone_w', '')
  parent1.mobile 	= form.getfirst('p1_mobile', '')
  parent1.email 	= form.getfirst('p1_email', '')
  parent1.add_info 	= form.getfirst('p1_add_info', '')
  
  if parent1.forename == '' or parent1.surname == '' or parent1.addr1 == '':
    scoutf_add1(form, db, param, conn)
    return

  parent1.add()
  dbobj.log_action(db, conn.scout_id, 11, parent1.scout_id)
  scout.parent1 = parent1.scout_id

  if form.getfirst('p2_forename', '') != '':
    # Just forename needed for second parent
    parent2 = dbobj.adultrec(db, 0)
    parent2.forename 	= form.getfirst('p2_forename', '')
    parent2.initials 	= form.getfirst('p2_initials', '')
    parent2.surname 	= form.getfirst('p2_surname', '')
    parent2.addr1 	= form.getfirst('p1_addr1', '')
    parent2.addr2 	= form.getfirst('p1_addr2', '')
    parent2.addr3 	= form.getfirst('p1_addr3', '')
    parent2.p_code 	= form.getfirst('p1_p_code', '')
    parent2.telephone_h 	= form.getfirst('p2_telephone_h', '')
    parent2.telephone_w 	= form.getfirst('p2_telephone_w', '')
    parent2.mobile 	= form.getfirst('p2_mobile', '')
    parent2.email 	= form.getfirst('p2_email', '')
    parent2.add_info 	= form.getfirst('p2_add_info', '')
    parent2.partner_id  = parent1.scout_id
    if parent2.surname == '':
      parent2.surname = parent1.surname
    if parent2.telephone_h == '':
      parent2.telephone_h = parent1.telephone_h
    parent2.add()
    dbobj.log_action(db, conn.scout_id, 11, parent2.scout_id)
    parent1.partner_id = parent2.scout_id
    parent1.update()
    scout.parent2 = parent2.scout_id

  scout.add()
  dbobj.log_action(db, conn.scout_id, 1, scout.scout_id)

  return

##############################################################################
def scoutp_add2(form, db, param, conn):
  "Processes the input from directly selecting a scout, just adds a role record"
  pass
  nOu = int(form.getfirst('ou_id', '0'))
  nScout = int(form.getfirst('scout_id', '0'))

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    app_error(form, param, conn, message="Invalid scout identifier")
    return

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message="Invalid security")
    return

  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  roles = scout.role_list()
  curr_role = dbobj.rolerec(db, 0)
  curr_role.find_role(nOu, nScout)
  if curr_role.found:
    curr_role.status = 'C'
    curr_role.update()

  ou.ouf_disp(form, db, param, conn)

  return
  """

###############################################################################
def parentf_edit(form, db, param, conn, message = ''):
  """Parent edit screen"""

  nScout = int(form.getfirst('scout_id', '0'))
  nParent = int(form.getfirst('parent_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))

  parent = dbobj.adultrec(db, nParent)
  if not parent.found:
    app_error(form, param, conn, message="Invalid parent identifier: " + str(nParent))
    return 

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message="Invalid scout identifier")
    return 

  conn.pers_security(scout)
  if not conn.write:
    #go to top of browse tree
    security_page(form, param, conn)
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

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

  outtable = webproc.table(width='100%', cellpadding = param.ot_cellpad, cellspacing = param.ot_cellspc, border = param.ot_brdr)

  outrow = webproc.table_row()

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

  # Row 1 Title
  table.add_row().add_item(webproc.tag('H2', 'Parent details'))
  table.last_row().add_item('<SPAN CLASS="validation_message">* denotes required field</SPAM>',\
      styleclass = 'error')
  table.last_row().add_item(webproc.tag('A', 'Cancel',\
      "href=scout.py?jw_action=scoutf_disp&scout_id=%d" % scout.scout_id))

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
  edit_row(table, 'Postal code :', 'p_code', cP_Code, size = 4, maxlen = 4)
  edit_row(table, 'Telephone (Home) :', 'telephone_h', cTelephone_h)
  edit_row(table, 'Telephone (Work) :', 'telephone_w', cTelephone_w)
  edit_row(table, 'E-Mail :', 'email', cEmail)
  edit_row(table, 'Mobile :', 'mobile', cMobile)
  edit_comment(table, 'Additional information :', 'add_info', cAdd_Info)

  # Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="parentf_edit" VALUE="Submit">')

  # Output the scout edit form

  outform = webproc.form('scout.py', table.pr_table(), 'parentff_edit')
  outform.add_hidden('jw_action', 'parentp_edit')
  outform.add_hidden('scout_id', scout.scout_id)
  outform.add_hidden('parent_id', parent.scout_id)
  outform.add_hidden('ou_id', nOu)
  outform.add_hidden('jw_action', 'Y')

  # The edit form is the LHS column 1 of the outer table
  outitem = webproc.table_item(outform.pr_form())
  outitem.rowspan = '2'
  outrow.items.append(outitem)

  #Second col of row one of outer table displays other kids for this parent
  cData = webproc.tag('H3', 'Scouts linked to this parent')
  parent.kids_list()
  for k in parent.kidlist:
    cData += webproc.tag('P', webproc.tag('A', k.forename + ' ' + k.initials + ' ' + k.surname, 'href=scout.py?jw_action=scoutf_disp&scout_id=' + str(k.scout_id)))

  outitem = webproc.table_item(cData)
  outitem.width = '33%'
  outitem.valign = 'TOP'
  outrow.items.append(outitem)

  outtable.rows.append(outrow)
  
  page.data.append(outtable.pr_table())
  page.output()
  return


##############################################################################
def parentp_edit(form, db, param, conn):
  """Processes the input from the parent edit screen """

  nScout = int(form.getfirst('scout_id', '0'))
  nParent = int(form.getfirst('parent_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message="Invalid scout identifier")
    return

  parent = dbobj.adultrec(db, nParent)
  if not parent.found:
    app_error(form, param, conn, message="Invalid parent identifier")
    return

  conn.pers_security(scout)
  if not conn.write:
    #go to top of browse tree
    security_page(form, param, conn)
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
  dbobj.log_action(db, conn.scout_id, 12, parent.scout_id)

  scoutf_disp(form, db, param, conn)
  return

###############################################################################
def scoutf_inactive(form, db, param, conn, message = ''):
  """Form to display to confirm scout being made non-current"""

  nScout = int(form.getfirst('scout_id', 0))
  nOu = int(form.getfirst('ou_id', 0))

  # If not form cout id, do the home page thing
  if nScout == 0:
    app_error(form, param, conn, message = "Invalid scout code")
    return

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    # go to top of browse tree
    app_error(form, param, conn, message = "Invalid scout code")
    return 

  if nOu != 0:
    ourec = dbobj.ourec(db, nOu)
  else:
    roles = scout.role_list(status = 'C')
    if len(roles):
      ourec = dbobj.ourec(db, roles[0].ou_id)
    else:
      # just a placeholder so it is defined, should not happen
      ourec = dbobj.ourec(db, 0)

  if not ourec.found:
    # go to top of browse tree
    app_error(form, param, conn, message = "Invalid ou code")
    return 

  roles = scout.role_list(status = 'C')

  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn, message = "Invalid request")
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)
  if message != '' and message is not None:
    page.data.append(message)

  # This table organises the scouts personal details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # Title
  table.add_row().add_item(webproc.tag('H3', 'Scout details'))
  table.last_row().add_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=scoutf_disp&scout_id=" + str(scout.scout_id)), align = 'right')

  # name etc
  table.add_row().add_item(webproc.tag('B', string.strip(scout.forename) + ' ' + string.strip(scout.initials) + ' ' + string.strip(scout.surname)), colspan = '2')

  disp_line(table, '<B>Date of birth : </B>' + pr_str(scout.date_of_birth), '<B>Gender : </B>' + pr_str(scout.gender))
  disp_line(table, '<B>Unit name : </B>%s' % ourec.name)

  # Additional info, if it exists
  if scout.add_info is not None and scout.add_info != '':
    table.add_row().add_item(webproc.tag('B', 'Additional Information : <BR>') + pr_str(scout.add_info), colspan = '2')

  # Form buttons
  table.add_row().add_item('<H2>This will lapse the membership of this scout. Do you want to continue?</H2>', colspan = '2', align = 'center')

  table.add_row().add_item('<INPUT TYPE="RADIO" NAME="INACTIVE" VALUE="Y">Lapse membership? &nbsp;&nbsp;<INPUT TYPE="RADIO" NAME="INACTIVE" VALUE="N" CHECKED> Cancel', colspan = '2', align = 'center')

  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="scoutf_edit" VALUE="Submit">', colspan = '2', align = 'center')

  # Output the scout edit form
  #cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="scoutf_edit" action="scout.py"')

  form = webproc.form('scout.py', table.pr_table())
  form.add_hidden('jw_action', 'scoutp_inactive')
  form.add_hidden('scout_id', scout.scout_id)
  form.add_hidden('ou_id', ourec.ou_id)

  page.data.append(form.pr_form())
  page.output()
  return

##############################################################################
def scoutp_inactive(form, db, param, conn):
  """Processes the input from the scout inactivation screen """

  nScout = int(form.getfirst('scout_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))
  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message = "Invalid scout id")
    return

  role = scout.role_by_ou(nOu)
  if not role.found:
    # go to top of browse tree
    app_error(form, param, conn, message = "Invalid ou code")
    return 

  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  cInactive = form.getfirst('INACTIVE', 'N')
  if cInactive == 'Y':
    scout.ch_status('L')
    role.status = 'L'
    role.add_edit()
    #dbobj.log_action(db, conn.scout_id, 201, scout.scout_id, scout.unit_id)

  scoutf_disp(form, db, param, conn, scout_id = nScout, ou_id = nOu)
  return

###############################################################################
def scoutf_renew(form, db, param, conn, message = ''):
  """Form to display to confirm scout having membership renewed"""

  nScout = int(form.getfirst('scout_id', 0))
  nOu = int(form.getfirst('ou_id', 0))

  # If not form cout id, do the home page thing
  if nScout == 0:
    app_error(form, param, conn, message = "Invalid scout code")
    return

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    # go to top of browse tree
    app_error(form, param, conn, message = "Invalid scout code")
    return 

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid org unit code')
    return 

  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn, message = "Invalid request")
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)
 
  # This table organises the scouts personal details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # Title
  table.add_row().add_item(webproc.tag('H3', 'Scout details'))
  table.last_row().add_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=scoutf_disp&scout_id=%d&ou_id=%d" % (scout.scout_id, ourec.ou_id)), align = 'right')

  # name etc
  table.add_row().add_item(webproc.tag('B', string.strip(scout.forename) + ' ' + string.strip(scout.initials) + ' ' + string.strip(scout.surname)), colspan = '2')

  disp_line(table, '<B>Date of birth : </B>' + pr_str(scout.date_of_birth), '<B>Gender : </B>' + pr_str(scout.gender))
  disp_line(table, '<B>Unit name : </B>' + pr_str(ourec.name), '<B>Section : </B>' + pr_str(ourec.ou_struct))

  # Additional info, if it exists
  if scout.add_info is not None and scout.add_info != '':
    table.add_row().add_item(webproc.tag('B', 'Additional Information : <BR>') + pr_str(scout.add_info), colspan = '2')

  # Form buttons
  table.add_row().add_item('<H2>This will renew this scouts membership, do you want to continue?</H2>', colspan = '2', align = 'center')

  row = webproc.table_row()
  table.add_row().add_item('<INPUT TYPE="RADIO" NAME="RENEWAL" VALUE="Y">Renew the membership of this scout&nbsp;&nbsp;<INPUT TYPE="RADIO" NAME="RENEW" VALUE="N" CHECKED> Cancel', colspan = '2', align = 'center')

  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="scoutf_renew" VALUE="Submit">', colspan = '2', align = 'center')

  # Output the scout edit form
  form = webproc.form('scout.py', table.pr_table())
  form.add_hidden('jw_action', 'scoutp_renew')
  form.add_hidden('scout_id', scout.scout_id)
  form.add_hidden('ou_id', ourec.ou_id)


  page.data.append(form.pr_form())
  page.output()
 
  return

##############################################################################
def scoutp_renew(form, db, param, conn):
  """Processes the input from the scout renewal screen """

  nScout = int(form.getfirst('scout_id', '0'))
  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message = "Invalid scout id")

  nOu = int(form.getfirst('ou_id', '0'))
  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    app_error(form, param, conn, message = "Invalid org unit id")
    return

  iconn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  cRenewal = form.getfirst('RENEWAL', 'N')
  if cRenewal == 'Y':
    role = scout.role_by_ou(nOu)
    role.status = 'C'
    role.add_edit()
    #dbobj.log_action(db, conn.scout_id, 202, scout.scout_id, scout.unit_id)

  scoutf_disp(form, db, param, conn)
  return

###############################################################################
def scoutf_sendup(form, db, param, conn, message = ''):
  """Form to display to confirm scout going up to the next unit"""

  nScout = int(form.getfirst('scout_id', 0))

  # If not form cout id, do the home page thing
  if nScout == 0:
    app_error(form, param, conn, message = "Invalid scout code")
    return

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    # go to top of browse tree
    app_error(form, param, conn, message = "Invalid scout code")
    return 

  unit = dbobj.unitrec(db, scout.unit_id)
  if not unit.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid unit code')
    return 

  group = dbobj.grouprec(db, unit.group_id)
  if not group.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid group code')
    return 

  unit_selection = group.unit_list(section = unit.next_sect)

  can_edit = edit_check(db, 'U', scout.unit_id, conn.scout_id)
  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn, message = "Invalid request")
    return 

  jw_header(param, conn)
  if message != '':
    print webproc.tag('H2', message)

  # This table organises the scouts personal details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # Title
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'Scout details'))
  #item.colspan = '2'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=scoutf_disp&scout_id=" + str(scout.scout_id)), align = 'right')
  row.items.append(item)
  table.rows.append(row)

  # name etc
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('B', string.strip(scout.forename) + ' ' + string.strip(scout.initials) + ' ' + string.strip(scout.surname)), colspan = '2')
  row.items.append(item)
  table.rows.append(row)

  disp_line(table, '<B>Date of birth : </B>' + pr_str(scout.date_of_birth), '<B>Gender : </B>' + pr_str(scout.gender))
  disp_line(table, '<B>Current Unit name : </B>' + pr_str(unit.name), '<B>Section : </B>' + pr_str(unit.sect_name))

  # Additional info, if it exists
  if scout.add_info is not None and scout.add_info != '':
    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('B', 'Additional Information : <BR>') + pr_str(scout.add_info))
    item.colspan = '2'
    row.items.append(item)
    table.rows.append(row)

  if len(unit_selection) > 0:
    # Does the group have a nit to move up to?

    # Form buttons
    row = webproc.table_row()
    item = webproc.table_item('<H3>This will transfer this scout to the next unit up, do you want to continue?</H3>', colspan = '2', align = 'center')
    row.items.append(item)
    table.rows.append(row)

    for u in unit_selection:
      row = webproc.table_row()
      item = webproc.table_item('<INPUT TYPE="RADIO" NAME="SENDUP" VALUE=' + str(u.unit_id) + '>Transfer to' + u.name, colspan = '2', align = 'center')
      row.items.append(item)
      table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('<INPUT TYPE="RADIO" NAME="SENDUP" VALUE=0 > Cancel', colspan = '2', align = 'center')
    row.items.append(item)
    table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="scoutf_renew" VALUE="Submit"><INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="scoutp_sendup"> <INPUT TYPE="HIDDEN" NAME="scout_id" VALUE="' + str(scout.scout_id)+ '">', colspan = '2', align = 'center')
    row.items.append(item)
    table.rows.append(row)

  else:
    # There is no unit for this scout to move up to

    row = webproc.table_row()
    item = webproc.table_item('There is no unit to move up to in this group', colspan = '2', align = 'center')
    row.items.append(item)
    table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="scoutf_renew" VALUE="Submit"><INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="scoutf_disp"> <INPUT TYPE="HIDDEN" NAME="scout_id" VALUE="' + str(scout.scout_id)+ '">', colspan = '2', align = 'center')
    row.items.append(item)
    table.rows.append(row)


  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="scoutf_sendup" action="scout.py"')

  print cForm

  webproc.form_footer()

##############################################################################
def scoutp_sendup(form, db, param, conn):
  """Processes the input from the scout send up screen """

  nScout = int(form.getfirst('scout_id', '0'))
  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message = "Invalid scout id")

  nUnit = int(form.getfirst('SENDUP', '0'))

  if nUnit == 0:
    scoutf_disp(form, db, param, conn)
    return

  unit = dbobj.unitrec(db, nUnit)
  if not unit.found:
    app_error(form, param, conn, message = "Invalid unit id")

  can_edit = edit_check(db, 'U', scout.unit_id, conn.scout_id)
  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
    return 
  nOld_unit = scout.unit_id
  scout.unit_id = unit.unit_id
  scout.set_unit(unit.unit_id)

  dbobj.log_action(db, conn.scout_id, 101, scout.scout_id, scout.unit_id, nOld_unit)

  scoutf_disp(form, db, param, conn)
  return

###############################################################################
def scoutf_transfer(form, db, param, conn, message = ''):
  """Form to display to confirm scout transfer to another unit"""

  nScout = int(form.getfirst('scout_id', 0))
  cLevel_cd = form.getfirst('level_cd', 'G')
  nLevel_id = int(form.getfirst('level_id', 0))

  # If not form cout id, do the home page thing
  if nScout == 0:
    app_error(form, param, conn, message = "Invalid scout code")
    return

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    # go to top of browse tree
    app_error(form, param, conn, message = "Invalid scout code")
    return 

  unit = dbobj.unitrec(db, scout.unit_id)
  if not unit.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid unit code')
    return 

  group = dbobj.grouprec(db, unit.group_id)
  if not group.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid group code')
    return 

  unit_selection = group.unit_list()

  can_edit = edit_check(db, 'U', scout.unit_id, conn.scout_id)
  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn, message = "Invalid request")
    return 

  jw_header(param, conn)
  if message != '':
    print webproc.tag('H2', message)

  # This table organises the scouts personal details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # Title
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'Scout details'))
  #item.colspan = '2'
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=scoutf_disp&scout_id=" + str(scout.scout_id)), align = 'right')
  row.items.append(item)
  table.rows.append(row)

  # name etc
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('B', string.strip(scout.forename) + ' ' + string.strip(scout.initials) + ' ' + string.strip(scout.surname)), colspan = '2')
  row.items.append(item)
  table.rows.append(row)

  disp_line(table, '<B>Date of birth : </B>' + pr_str(scout.date_of_birth), '<B>Gender : </B>' + pr_str(scout.gender))
  disp_line(table, '<B>Current Unit name : </B>' + pr_str(unit.name), '<B>Section : </B>' + pr_str(unit.sect_name))
  disp_line(table, '<B>Current Group name : </B>' + pr_str(group.name))

  # Additional info, if it exists
  if scout.add_info is not None and scout.add_info != '':
    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('B', 'Additional Information : <BR>') + pr_str(scout.add_info))
    item.colspan = '2'
    row.items.append(item)
    table.rows.append(row)

  if len(unit_selection) > 0:
    # Does the group have a nit to move up to?

    # Form buttons
    row = webproc.table_row()
    item = webproc.table_item('<H3>This will transfer this person to the next unit selected, do you want to continue?</H3>', colspan = '2', align = 'center')
    row.items.append(item)
    table.rows.append(row)

    for u in unit_selection:
      row = webproc.table_row()
      item = webproc.table_item('<INPUT TYPE="RADIO" NAME="TRANSFER" VALUE=' + str(u.unit_id) + '>Transfer to' + u.name, colspan = '2', align = 'center')
      row.items.append(item)
      table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('<INPUT TYPE="RADIO" NAME="TRANSFER" VALUE=0 > Cancel', colspan = '2', align = 'center')
    row.items.append(item)
    table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="scoutf_transfer" VALUE="Submit"><INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="scoutp_transfer"> <INPUT TYPE="HIDDEN" NAME="scout_id" VALUE="' + str(scout.scout_id)+ '">', colspan = '2', align = 'center')
    item.data += '<INPUT TYPE="HIDDEN" NAME="level_cd" VALUE="U">'
    row.items.append(item)
    table.rows.append(row)

  else:
    # There is no unit for this scout to move up to

    row = webproc.table_row()
    item = webproc.table_item('There is no unit to move up to in this group', colspan = '2', align = 'center')
    row.items.append(item)
    table.rows.append(row)

    row = webproc.table_row()
    item = webproc.table_item('<INPUT TYPE="SUBMIT" NAME="scoutf_renew" VALUE="Submit"><INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="scoutf_disp"> <INPUT TYPE="HIDDEN" NAME="scout_id" VALUE="' + str(scout.scout_id)+ '">', colspan = '2', align = 'center')
    row.items.append(item)
    table.rows.append(row)


  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="scoutf_sendup" action="scout.py"')

  print cForm

  webproc.form_footer()

##############################################################################
def scoutp_transfer(form, db, param, conn):
  """Processes the input from the scout transfer screen """

  nScout = int(form.getfirst('scout_id', '0'))
  cLevel_cd = form.getfirst('level_cd', '')

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message = "Invalid scout id")

  nUnit = int(form.getfirst('TRANSFER', '0'))

  # Unit code of 0 is a "cancel"
  if nUnit == 0:
    scoutf_disp(form, db, param, conn)
    return

  # If it is not a Unit code, redisplay the transfer screen
  if cLevel_cd != 'U':
    scoutf_transfer(form, db, param, conn)

  unit = dbobj.unitrec(db, nUnit)
  if not unit.found:
    app_error(form, param, conn, message = "Invalid unit id")

  can_edit = edit_check(db, 'U', scout.unit_id, conn.scout_id)
  if not can_edit:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  nOld_unit = scout.unit_id
  scout.unit_id = unit.unit_id
  scout.set_unit(unit.unit_id)
  dbobj.log_action(db, conn.scout_id, 102, scout.scout_id, scout.unit_id, nOld_unit)

  scoutf_disp(form, db, param, conn)
  return

##############################################################################
def adultf_add(form, db, param, conn):
  """Displays form required to add a adult, not associated with any scout """

  # Initialise variables, reuse form variables if needed as validation may be occuring

  # These variables will be new on the first time the screen is displayed
  cAdult_submit 	= form.getfirst('adult_submit', 'N')
  cP1_forename 		= form.getfirst('p1_forename', '')
  cP1_initials 		= form.getfirst('p1_initials', '')
  cP1_surname 		= form.getfirst('p1_surname', '')
  cP1_addr1 		= form.getfirst('p1_addr1', '')
  cP1_addr2 		= form.getfirst('p1_addr2', '')
  cP1_addr3 		= form.getfirst('p1_addr3', '')
  cP1_p_code 		= form.getfirst('p1_p_code', '')
  cP1_telephone_h 	= form.getfirst('p1_telephone_h', '')
  cP1_telephone_w 	= form.getfirst('p1_telephone_w', '')
  cP1_email 		= form.getfirst('p1_email', '')
  cP1_gender 		= form.getfirst('p1_gender', '')
  cP1_mobile 		= form.getfirst('p1_mobile', '')
  cP1_gender 		= form.getfirst('p1_gender', '')
  cP1_add_info 		= form.getfirst('p1_add_info', '')

  jw_header(param, conn, menu_item=2)

  # This table organises the form
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = '25%'
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = '33%'
  colgr.cols.append(col)

  # i3rd column
  col = webproc.table_col()
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Title
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'Add an adult'))
  row.items.append(item)

  item = webproc.table_item('<SPAN CLASS="validation_message">* denotes required field</SPAN>')
  item.styleclass = 'error'
  row.items.append(item)

  item = webproc.table_item(webproc.tag('A', 'Cancel', "href=scout.py?jw_action=home_page"))
  row.items.append(item)
  table.rows.append(row)

  # P1 forename
  if cAdult_submit == 'Y' and cP1_forename == '':
    edit_row(table, 'Name :', 'p1_forename', cP1_forename, 0, 'Forename is a required field', req=1)
  else:
    edit_row(table, 'Name :', 'p1_forename', cP1_forename, req=1)

  # Initials
  edit_row(table, 'Initials :', 'p1_initials', cP1_initials)
 
  # surname
  if cAdult_submit == 'Y' and cP1_surname == '':
    edit_row(table, 'Surname :', 'p1_surname', cP1_surname, 0, 'Surname is a required field', req=1)
  else:
    edit_row(table, 'Surname :', 'p1_surname', cP1_surname, req=1)

  # Row 5, address
  edit_row(table, 'Address :', 'p1_addr1', cP1_addr1)
  edit_row(table, '', 'p1_addr2', cP1_addr2)
  edit_row(table, '', 'p1_addr3', cP1_addr3)
  edit_row(table, 'Postal Code :', 'p1_p_code', cP1_p_code, size = 4, maxlen = 4)
  edit_row(table, 'Phone (H) :', 'p1_telephone_h', cP1_telephone_h)
  edit_row(table, 'Phone (W) :', 'p1_telephone_w', cP1_telephone_w)
  edit_row(table, 'Mobile :', 'p1_mobile', cP1_mobile)
  edit_row(table, 'E-Mail :', 'p1_email', cP1_email)

  # Gender
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('SPAN', 'Gender :', 'CLASS="field_descr"'))
  row.items.append(item)
  cLine = '<INPUT TYPE="RADIO" NAME="p1_gender" VALUE="M"'
  if cP1_gender == 'M':
    cLine += ' CHECKED'
  cLine += '>Male&nbsp;&nbsp;<INPUT TYPE="RADIO" NAME="p1_gender" VALUE="F"'
  if cP1_gender == 'F':
    cLine += ' CHECKED'
  cLine +='>Female'
  item = webproc.table_item(cLine)
  row.items.append(item)
  table.rows.append(row)

  edit_comment(table, 'Additional information :', 'p1_add_info', cP1_add_info)

  # Form buttons
  row = webproc.table_row()

  # we need to pass on a lot of info from the previous screen to be processed
  cFields = '<INPUT TYPE="SUBMIT" NAME="adultf_add" VALUE="Submit">'
  cFields += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="adultp_add">'
  cFields += '<INPUT TYPE="HIDDEN" NAME="adult_submit" VALUE="Y">'
  item = webproc.table_item(cFields)
  row.items.append(item)
  table.rows.append(row)

  # Output the scout edit form
  cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="adultf_add" action="scout.py"')

  print cForm

  webproc.form_footer()
  return

##############################################################################
def adultp_add(form, db, param, conn):
  """Processes the input from the adult add screen """

  # initialise first parent record
  parent = dbobj.adultrec(db, 0)
  parent.forename 	= form.getfirst('p1_forename', '')
  parent.initials 	= form.getfirst('p1_initials', '')
  parent.surname 	= form.getfirst('p1_surname', '')
  parent.addr1 		= form.getfirst('p1_addr1', '')
  parent.addr2 		= form.getfirst('p1_addr2', '')
  parent.addr3 		= form.getfirst('p1_addr3', '')
  parent.p_code 	= form.getfirst('p1_p_code', '')
  parent.telephone_h 	= form.getfirst('p1_telephone_h', '')
  parent.telephone_w 	= form.getfirst('p1_telephone_w', '')
  parent.mobile 	= form.getfirst('p1_mobile', '')
  parent.email 		= form.getfirst('p1_email', '')
  parent.gender		= form.getfirst('p1_gender', '')
  parent.add_info 	= form.getfirst('p1_add_info', '')
  
  if parent.forename == '' or parent.surname == '':
    adultf_add(form, db, param, conn)
    return

  parent.add()
  dbobj.log_action(db, conn.scout_id, 11, parent.scout_id)

  ou.home_page(form, db, param, conn, 'home page selected')

  return

###############################################################################
def parent2f_remove(form, db, param, conn, message = ''):
  """Parent2 removal screen"""

  nScout = int(form.getfirst('scout_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message="Invalid scout identifier")
    return 

  parent = dbobj.adultrec(db, scout.parent2)
  if not parent.found:
    app_error(form, param, conn, message="Invalid parent identifier: " + str(nParent))
    return 

  conn.pers_security(scout)
  if not conn.write:
    #go to top of browse tree
    security_page(form, param, conn)
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  # This table
  table = webproc.table(width='100%', cellpadding = '3', cellspacing = param.it_cellspc, border = '1')

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = '50%'
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = '50%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Initial statement
  item = table.add_row().add_item('This will remove the link between the child/scout ',\
      colspan='2', align='CENTER')
  item.data += '<B>' + scout.forename + ' ' + scout.surname + '</B> and the parent/guardian <B>'
  item.data += parent.forename + ' ' + parent.surname + '<BR>'

  # Second statement
  table.add_row().add_item('This is normally only required when there has been a change in family circumstances which has removed the requirement for the relationship to be recorded, or a data entry error has meant that the wrong parent/guardian was initially linked to the child/scout.<BR>', colspan = '2', styleclass = 'red', align = 'CENTER')

  # Scout details
  item = table.add_row().add_item(webproc.tag('B', 'Child/scout details<BR>'))
  item.data += scout.forename + ' '
  if scout.initials != '':
    item.data += scout.initials + ' '
  item.data += scout.surname + '<BR>'
  if scout.gender != '':
    item.data += 'Gender : ' + scout.gender + '<BR>'

  # Scout details
  item = table.last_row().add_item(webproc.tag('B', 'Parent/guardian details<BR>'))
  item.data += parent.forename + ' '
  if parent.initials != '':
    item.data += parent.initials + ' '
  item.data += parent.surname + '<BR>'
  if parent.gender != '':
    item.data += 'Gender : ' + parent.gender + '<BR>'

  # Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="parent2f_remove" VALUE="Remove relationship/link">')

  outform = webproc.form('scout.py', table.pr_table(), 'parent2f_remove')
  outform.add_hidden('jw_action', 'parent2p_remove')
  outform.add_hidden('scout_id', scout.scout_id)
  outform.add_hidden('ou_id', nOu)

  # Output the scout edit form
  page.data.append(outform.pr_form())
  page.output()
  return


##############################################################################
def parent2p_remove(form, db, param, conn):
  """Processes the input from the parent 2 removal screen"""

  nScout = int(form.getfirst('scout_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message="Invalid scout identifier")
    return

  parent = dbobj.adultrec(db, scout.parent2)
  if not parent.found:
    app_error(form, param, conn, message="Invalid parent identifier")
    return

  conn.pers_security(scout)
  if not conn.write:
    #go to top of browse tree
    security_page(form, param, conn)
    return 

  scout.parent2 = 0

  scout.update()
  dbobj.log_action(db, conn.scout_id, 301, scout.scout_id, parent.scout_id)

  scoutf_disp(form, db, param, conn, scout_id = scout.scout_id, ou_id = nOu)
  return

##############################################################################
def parent2f_add(form, db, param, conn, message = ''):
  """Parent2 add screen"""

  nScout = int(form.getfirst('scout_id', '0'))
  nParent = int(form.getfirst('person_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message="Invalid scout identifier")
    return 

  parent = dbobj.adultrec(db, nParent)
  if not parent.found:
    app_error(form, param, conn, message="Invalid parent identifier: " + str(nParent))
    return 

  conn.pers_security(scout)
  if not conn.write:
    #go to top of browse tree
    security_page(form, param, conn)
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  # This table
  table = webproc.table(width='100%', cellpadding = '3', cellspacing = param.it_cellspc, border = '1')

  # define colum details
  colgr = webproc.table_colgroup()
  # Field descriptions
  col = webproc.table_col()
  col.width = '50%'
  colgr.cols.append(col)

  # Field input
  col = webproc.table_col()
  col.width = '50%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Initial statement
  item = table.add_row().add_item('This will add a link between the child/scout ',\
      colspan='2', align='CENTER')
  item.data += '<B>' + scout.forename + ' ' + scout.surname + '</B> and the parent/guardian <B>'
  item.data += parent.forename + ' ' + parent.surname + '<BR>'

  # Second statement
  table.add_row().add_item('This is normally only required when there has been a change in family circumstances which hasmeant there is now another parent/guardian, or a data entry error has meant that the wrong parent/guardian was initially linked to the child/scout.<BR>', colspan = '2', styleclass = 'red', align = 'CENTER')

  # Scout details
  item = table.add_row().add_item(webproc.tag('B', 'Child/scout details<BR>'))
  item.data += scout.forename + ' '
  if scout.initials != '':
    item.data += scout.initials + ' '
  item.data += scout.surname + '<BR>'
  if scout.gender != '':
    item.data += 'Gender : ' + scout.gender + '<BR>'

  # Scout details
  item = table.last_row().add_item(webproc.tag('B', 'Parent/guardian details<BR>'))
  item.data += parent.forename + ' '
  if parent.initials != '':
    item.data += parent.initials + ' '
  item.data += parent.surname + '<BR>'
  if parent.gender != '':
    item.data += 'Gender : ' + parent.gender + '<BR>'

  # Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="parent2f_add" VALUE="Add relationship/link">')

  outform = webproc.form('scout.py', table.pr_table(), 'parent2f_add')
  outform.add_hidden('jw_action', 'parent2p_add')
  outform.add_hidden('scout_id', scout.scout_id)
  outform.add_hidden('parent_id', parent.scout_id)
  outform.add_hidden('ou_id', nOu)

  # Output the scout edit form
  page.data.append(outform.pr_form())
  page.output()
  return

##############################################################################
def parent2p_add(form, db, param, conn):
  """Processes the input from the parent 2 add screen"""

  nScout = int(form.getfirst('scout_id', '0'))
  nParent = int(form.getfirst('parent_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message="Invalid scout identifier")
    return

  parent = dbobj.adultrec(db, nParent)
  if not parent.found:
    app_error(form, param, conn, message="Invalid parent identifier")
    return

  conn.pers_security(scout)
  if not conn.write:
    #go to top of browse tree
    security_page(form, param, conn)
    return 

  scout.parent2 = nParent

  scout.update()
  dbobj.log_action(db, conn.scout_id, 302, scout.scout_id, parent.scout_id)

  scoutf_disp(form, db, param, conn, scout_id=scout.scout_id, ou_id = nOu)
  return

##############################################################################
def parent1f_mod1(form, db, param, conn, message = ''):
  """Parent1 modify screen"""

  # Get form parameters
  nScout = int(form.getfirst('scout_id', '0'))
  nParent = int(form.getfirst('person_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))

  # Get scout details
  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    app_error(form, param, conn, message="Invalid scout identifier")
    return 

  # Get original parent details
  oldparent1 = dbobj.adultrec(db, scout.parent1)
  if not oldparent1.found:
    app_error(form, param, conn, message="Invalid parent identifier: " + str(nParent))
    return 
 
  oldparent2 = dbobj.adultrec(db, scout.parent2)

  # Get new parent details
  newparent1 = dbobj.adultrec(db, nParent)
  if not newparent1.found:
    app_error(form, param, conn, message="Invalid parent identifier: " + str(nParent))
    return 
  newparent2 = dbobj.adultrec(db,newparent1.partner_id)

  # Check if we are allowed to do this
  conn.pers_security(scout)
  if not conn.write:
    #go to top of browse tree
    security_page(form, param, conn)
    return 

  # Print page header
  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  # Create a display table
  table = webproc.table(width='100%', cellpadding = '3', cellspacing = param.it_cellspc, border = '1')

  # define colum details
  colgr = webproc.table_colgroup()
  # Scout details
  col = webproc.table_col()
  col.width = '34%'
  colgr.cols.append(col)

  # Existing parent details
  col = webproc.table_col()
  col.width = '33%'
  colgr.cols.append(col)

  # New parent details
  col = webproc.table_col()
  col.width = '33%'
  colgr.cols.append(col)

  table.colgroups.append(colgr) 

  # Row 1 Initial statement
  table.add_row().add_item('This will add a link between the child/scout <B>%s %s</B> and the parent/guardian <B>%s %s<BR>' %\
      (scout.forename, scout.surname, newparent1.forename, newparent1.surname),\
      colspan = '3', align = 'CENTER')

  # Second statement
  table.add_row().add_item('This is normally only required when there has been a change in family circumstances which has meant there is now another parent/guardian, or a data entry error has meant that the wrong parent/guardian was initially linked to the child/scout.<BR>',\
      colspan = '3', styleclass = 'red', align = 'CENTER')

  # Scout details
  item = table.add_row().add_item(webproc.tag('B', 'Child/scout details<BR>'))
  item.data += scout.forename + ' '
  if scout.initials != '':
    item.data += scout.initials + ' '
  item.data += scout.surname + '<BR>'
  if scout.gender != '':
    item.data += 'Gender : ' + scout.gender + '<BR>'

  # Original parent details
  item = table.last_row().add_item(webproc.tag('B', 'Original parent/guardian details<BR>'))
  item.data += '%s %s %s<BR>' % (oldparent1.forename, oldparent1.initials, oldparent1.surname)
  if oldparent1.gender != '':
    item.data += 'Gender : ' + oldparent1.gender + '<BR>'

  if oldparent2.found:
    item.data += '<B>Partner,</B><BR>%s %s %s<BR>' % (oldparent2.forename, oldparent2.initials, oldparent2.surname)
    if oldparent2.gender != '':
      item.data += 'Gender : ' + oldparent2.gender + '<BR>'

  # New parent details
  item = table.last_row().add_item(webproc.tag('B', 'Selected parent/guardian details<BR>'))
  item.data += '%s %s %s<BR>' % (newparent1.forename, newparent1.initials, newparent1.surname)
  if newparent1.gender != '':
    item.data += 'Gender : ' + newparent1.gender + '<BR>'

  if newparent2.found:
    item.data += '<B>Partner,</B><BR>%s %s %s<BR>' % (newparent2.forename, newparent2.initials, newparent2.surname)
    if newparent2.gender != '':
      item.data += 'Gender : ' + newparent2.gender + '<BR>'

  url =  'scout.py?jw_action=parent1p_mod&scout_id=%s&person_id=%s&ou_id=%d&act_code=' % (scout.scout_id, newparent1.scout_id, nOu)

  # Only 1 existing parent
  if not oldparent2.found:
    text = 'Change the primary parent from %s %s to %s %s' % (oldparent1.forename, oldparent1.surname, newparent1.forename, newparent1.surname)
    table.add_row().add_item(webproc.jbutton(text, url + '1'), colspan='3')
    # if there are 2 new parents
    if newparent2.found:
      text = 'Change the primary parent from %s %s to %s %s and %s %s' % (oldparent1.forename, oldparent1.surname, newparent1.forename, newparent1.surname, newparent2.forename, newparent2.surname)
      table.add_row().add_item(webproc.jbutton(text, url + '2'), colspan='3')

  # Has 2 existing parents
  else:
    # If the new parent has a partner
    if newparent2.found:
      text = 'Change the parents from %s %s and %s %s to %s %s and %s %s' % (oldparent1.forename, oldparent1.surname, oldparent2.forename, oldparent2.surname, newparent1.forename, newparent1.surname, newparent2.forename, newparent2.surname)
      table.add_row().add_item(webproc.jbutton(text, url + '2'), colspan='3')

    # new parent does not have a partner
    else:
      text = 'Change the parents from %s %s and %s %s to %s %s' % (oldparent1.forename, oldparent1.surname, oldparent2.forename, oldparent2.surname, newparent1.forename, newparent1.surname)
      table.add_row().add_item_item(webproc.jbutton(text, url + '3'), colspan='3')

      text = 'Change the parents from %s %s and %s %s to %s %s and %s %s' % (oldparent1.forename, oldparent1.surname, oldparent2.forename, oldparent2.surname, newparent1.forename, newparent1.surname, oldparent2.forename, oldparent2.surname)
      table.add_row().add_item(webproc.jbutton(text, url + '1'), colspan='3')


  table.add_row().add_item(webproc.jbutton('Cancel', url + '0'))

  # Output the scout edit form
  page.data.append(table.pr_table())
  page.output()
  return

##############################################################################
def parent1p_mod(form, db, param, conn):
  """Processes the input from the parent 1 modification screen"""

  nScout = int(form.getfirst('scout_id', '0'))
  nParent = int(form.getfirst('person_id', '0'))
  nact_code = int(form.getfirst('act_code', '0'))
  nOu = int(form.getfirst('ou_id', '0'))

  # if the action code is not 0 (cancel)
  if nact_code != 0:

    # get the scout details
    scout = dbobj.scoutrec(db, nScout)
    if not scout.found:
      app_error(form, param, conn, message="Invalid scout identifier")
      return

    conn.pers_security(scout)
    if not conn.write:
      #go to top of browse tree
      security_page(form, param, conn)
      return 

    newparent1 = dbobj.adultrec(db, nParent)
    if not newparent1.found:
      app_error(form, param, conn, message="Invalid parent identifier")
      return
    newparent2 = dbobj.adultrec(db, newparent1.partner_id)
    nold_parent1 = scout.parent1
    nold_parent2 = scout.parent2

  if nact_code == 1:
    # Replace Parent 1 only
    scout.parent1 = nParent
    scout.update()
    dbobj.log_action(db, conn.scout_id, 303, scout.scout_id, scout.parent1, nold_parent1)
  elif nact_code == 2:
    # Replace Parent 1 only and Parent 2
    scout.parent1 = nParent
    scout.parent2 = newparent2.scout_id
    scout.update()
    dbobj.log_action(db, conn.scout_id, 303, scout.scout_id, scout.parent1, nold_parent1)
    dbobj.log_action(db, conn.scout_id, 301, scout.scout_id, nold_parent2)
    dbobj.log_action(db, conn.scout_id, 302, scout.scout_id, scout.parent2)
  elif nact_code == 3:
    # Replace Parent 1 only remove parent 2
    scout.parent1 = nParent
    scout.parent2 = 0
    scout.update()
    dbobj.log_action(db, conn.scout_id, 303, scout.scout_id, scout.parent1, nold_parent1)
    dbobj.log_action(db, conn.scout_id, 301, scout.scout_id, scout.parent2)


  scoutf_disp(form, db, param, conn, scout_id = nScout, ou_id = nOu)
  return


##############################################################################
# Mail program logic, decides which form/screen to display
form = cgi.FieldStorage()
param = dbobj.paramrec()
db = dbobj.dbinstance(param.dbname)
conn = dbobj.connectrec(db)

cAct = form.getfirst("jw_action", '')

if conn.new_conn:
  oCookie = Cookie.SimpleCookie()
  oCookie[conn.ref_id] = conn.auth_key
  oCookie[conn.ref_id]["Max-Age"] = 31536000
  cCookie = oCookie.output()
  ou.home_page(form, db, param, conn, oCookie = oCookie)
else:  
  # if a form action is specified do it
  if cAct == "home_page":
    ou.home_page(form, db, param, conn, 'home page selected')
  elif cAct == "ouf_disp":
    ou.ouf_disp(form, db, param, conn)
  elif cAct == "scoutf_disp":
    scoutf_disp(form, db, param, conn)   
  elif cAct == "scoutf_edit":
    scoutf_edit(form, db, param, conn)
  elif cAct == "scoutp_edit":
    scoutp_edit(form, db, param, conn)
  elif cAct == "scoutf1_add":
    scoutf1_add(form, db, param, conn)
  elif cAct == "scoutf2_add":
    scoutf2_add(form, db, param, conn)
  elif cAct == "scoutf3_junioradd":
    scoutf3_junioradd(form, db, param, conn)
  #elif cAct == "scoutp_add":
  #  scoutp_add(form, db, param, conn)
  elif cAct == "scoutp1_add":
    scoutp1_add(form, db, param, conn)
  elif cAct == "scoutp2_add":
    scoutp2_add(form, db, param, conn)
  elif cAct == "scoutp3_add":
    scoutp3_add(form, db, param, conn)
  #elif cAct == "scoutf_add1":
  #  scoutf_add1(form, db, param, conn)
  #elif cAct == "scoutp_add1":
  #  scoutp_add1(form, db, param, conn)
  elif cAct == "scoutf_inactive":
    scoutf_inactive(form, db, param, conn)
  elif cAct == "scoutp_inactive":
    scoutp_inactive(form, db, param, conn)
  elif cAct == "scoutf_renew":
    scoutf_renew(form, db, param, conn)
  elif cAct == "scoutp_renew":
    scoutp_renew(form, db, param, conn)
  elif cAct == "scoutf_sendup":
    scoutf_sendup(form, db, param, conn)
  elif cAct == "scoutp_sendup":
    scoutp_sendup(form, db, param, conn)
  elif cAct == "scoutf_transfer":
    scoutf_transfer(form, db, param, conn)
  elif cAct == "scoutp_transfer":
    scoutp_transfer(form, db, param, conn)
  elif cAct == "parentf_edit":
    parentf_edit(form, db, param, conn)
  elif cAct == "parentp_edit":
    parentp_edit(form, db, param, conn)
  elif cAct == "adultf_add":
    adultf_add(form, db, param, conn)
  elif cAct == "adultp_add":
    adultp_add(form, db, param, conn)
  elif cAct == "parent2f_remove":
    parent2f_remove(form, db, param, conn)
  elif cAct == "parent2p_remove":
    parent2p_remove(form, db, param, conn)
  elif cAct == "parent2f_add":
    parent2f_add(form, db, param, conn)
  elif cAct == "parent2p_add":
    parent2p_add(form, db, param, conn)
  elif cAct == "parent1f_mod1":
    parent1f_mod1(form, db, param, conn)
  elif cAct == "parent1f_mod1":
    parent1f_mod2(form, db, param, conn)
  elif cAct == "parent1p_mod":
    parent1p_mod(form, db, param, conn)

  else:
    # Display the home page if you don't know what to do
    ou.home_page(form, db, param, conn, menu_id=1)

db.commit()
db.close()

