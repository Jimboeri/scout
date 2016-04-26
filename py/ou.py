#!/usr/bin/python

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
#import scout
 

##############################################################################
def home_page(form, db, param, conn, menu_id = 1, oCookie = None, msg = ''):
  """Displays the home page for the user """
  
  #jw_header(param, conn, menu_item=1, cCookie = cCookie)
  #print "Env Cookie: " + os.environ.get("HTTP_COOKIE") + '<br>'
  #print "Inp Cookie: " + cCookie + '<br>'
  #print "Conn.new_conn: " + str(conn.new_conn) + '<br>'
  #print "Conn.found: " + str(conn.found) + '<br>'
  #print 'Form = '
  #print form
  #print "<br>jw_action = " + form.getfirst("jw_action")
  #print '<br>Msg = ' + msg
  #webproc.form_footer()
  
  if conn.home_ou_id == 0 or conn.home_ou_id is None:
    if conn.last_ou_id == 0 or conn.last_ou_id is None:
      nOu = 1
    else:
      nOu = conn.last_ou_id
  else:
    nOu = conn.home_ou_id

  if conn.new_conn:
    ouf_disp(form, db, param, conn, oCookie = oCookie, ou_id = nOu, msg = msg)
  else:
    ouf_disp(form, db, param, conn, ou_id = nOu, msg = msg)

  return

###############################################################################
def ouf_disp(form, db, param, conn, message = '', oCookie = None, ou_id = 0, msg = ''):
  """Organisational unit display screen.

  Screen has links to these modules:
    oup_view()
    ouf_disp()
    ouf_edit()
    ouf_add()
    oup_all_members()
    oup_action Redirects to
      oup_move()
      award.werof_achieve()
      award.werof_extract()
    oup_expand()
    oup_del()
    scout.scoutf1_add()
    scout.scoutf_disp()
    office.rolef_add1()
    office.rolef_add2()
    office.rolep_del()
Accepts these parameters
  Form, db, conn, message
  oCookie - cookie instance from cookie module
  ou_id - ou_id to be displayed
  msg - message to be displayed
Looks for these cgi form fields
  ou_id - ou to be displayed, over written by input parameter if it is non-zero
 """

  # Initialise variables
  nCurr_child = 0
  nCurr_memb = 0
  nCurr_mngt = 0
  menu_itm = 996

  nOu_id = int(form.getfirst('ou_id', 1))
  if ou_id != 0:
    nOu_id = ou_id

  # Home page stuff - need to review
  if nOu_id == 0:
    # Take it from the home id rather than last id if possible
    if conn.home_ou_id != 0:
      nOu_id = conn.home_ou_id
      menu_itm = 1
    else:
      nOu_id = conn.last_ou_id
  else:
    #check if this is the users home page
    if conn.home_ou_id == nOu_id:
      menu_itm = 1

  ou = dbobj.ourec(db, nOu_id)
  if not ou.found:
    app_error(form, param, conn, message = "Invalid org unit id")
    return

  ou_owner = dbobj.ourec(db, ou.ou_owner)

  conn.ou_security(nOu_id)

  if conn.last_ou_id != nOu_id:
    conn.last_ou_id = nOu_id
    conn.update()

  ou_disp = dbobj.ou_disprec(db, ou.ou_id, conn.scout_id)

  page = scout_page(title=param.title, ocookie = oCookie, css=[param.css_file])
  page.do_heading(param, conn, form, ou_id = nOu_id)
  page.data.append(msg)

  #define outer table, hold district details at the op, groups on the left, & adult roles on the right
  outtable = webproc.table(width='100%', cellpadding = param.ot_cellpad, cellspacing = param.ot_cellspc, border = param.ot_brdr)

  ############################################################################
  # top row for OU details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  table.add_row().add_item(webproc.tag('H2', ou.name))

  if param.testing:
    item = table.append_item('Management = %d<BR>Junior = %d' % (ou.mngt, ou.junior))

  if conn.sign_in:
    item = table.last_row().add_item('', align = 'right')
    if ou_disp.show_actions:
      item.data = webproc.jbutton('Show less actions',\
        "ou_logic.py?jw_action=oup_view&ou_id=%d&expand=0" % ou.ou_id)
    else:
      item.data = webproc.jbutton('Show more actions',\
        "ou_logic.py?jw_action=oup_view&ou_id=%d&expand=1" % ou.ou_id)

  if ou.ou_owner != 0:
    if ou_owner.found:
      table.last_row().add_item('', align = 'right')
      table.last_row().last_item().data += webproc.jbutton('Up to %s' % ou_owner.name,\
        "ou_logic.py?jw_action=ouf_disp&ou_id=%d" % ou_owner.ou_id)

  if conn.write:
    table.last_row().add_item(webproc.jbutton('Edit',\
      "ou_logic.py?jw_action=ouf_edit&ou_id=%d" % ou.ou_id), align = 'right')

  if conn.sign_in and ou_disp.show_actions:
    # need to build table of options to move to
    table.add_row()
    ou_opt = []
    if ou_owner.found:
      ou_opt.append([ou_owner.ou_id, ou_owner.name])
      ou_opt.append([0, '------------------------------'])
      ow_list = ou_owner.child_list()
      if len(ow_list) > 0:
        for o in ow_list:
          if not o.mngt and o.ou_id != ou.ou_id:
            ou_opt.append([o.ou_id, o.name])
        ou_opt.append([0, '------------------------------'])
    ow_list = ou.child_list()
    for o in ow_list:
      if not o.mngt:
        ou_opt.append([o.ou_id, o.name])

    temp = '<SELECT NAME="ou_move_to">\n<OPTION value=0 SELECTED>Select destination..</OPTION>\n'
    for o in ou_opt:
      temp += '<OPTION value=%d>%s</OPTION>\n' %(o[0], o[1])
    temp += '</SELECT>\n'
    item = table.last_row().add_item(temp)

    f_submit = webproc.form_input("SUBMIT", name="ou_action", value="Move")
    item.data += f_submit.pr_input()

    # Add sub ou's here
    table.last_row().add_item(webproc.jbutton('Add sub Unit',\
        "ou_logic.py?jw_action=ouf_add&ou_id=%d" % ou.ou_id), align = 'right')

    # display inactive members or not
    if ou_disp.all_members:
      table.last_row().add_item(webproc.jbutton('Current members only',\
        "ou_logic.py?jw_action=oup_all_members&ou_id=%d&all_members=0" % ou.ou_id),\
        align = 'right')
    else:
      table.last_row().add_item(webproc.jbutton('Show all members',\
        "ou_logic.py?jw_action=oup_all_members&ou_id=%d&all_members=1" % ou.ou_id),\
        align = 'right')

    # If cubs display wero award button here
    if ou.ou_struct == 6 or ou.struct_parent == 6:
      # This adds activities that go towards a wero
      f_submit = webproc.form_input("SUBMIT", name="ou_action", value="Wero")
      table.last_row().add_item(f_submit.pr_input())

      #This extract wero achievements for an OU, used to review or display
      f_submit = webproc.form_input("SUBMIT", name="ou_action", value="Extract Wero info")
      table.last_row().add_item(f_submit.pr_input())

    # This adds activities that go towards a wero
    f_submit = webproc.form_input("SUBMIT", name="ou_action", value="Collective Awards")
    table.last_row().add_item(f_submit.pr_input())

    #This extracts award achievements for an OU, used to review or display
    table.last_row().add_item(webproc.jbutton('Extract Award info', 'award.py?jw_action=awardf_extract&ou_id=%d' % ou.ou_id))

    #This sends an email to an OU
    table.last_row().add_item(webproc.jbutton('Send e-mail', 'office.py?jw_action=emailf_ou&ou_id=%d' % ou.ou_id))


  outtable.add_row().add_item(table.pr_table(), colspan = '2')

  # Create a row for units, members and roles
  outtable.add_row()

  # Next outer table row has child OU details and members
  ############################################################################
  # Table for children OU's of this OU
  ou.member_list(status='C')
  ou.child_list()

  table = webproc.table(cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, width='100%', border = param.it_brdr)

  table.add_row().add_item(' ')
  table.last_row().add_item(webproc.jbutton('Add new member', 'scout.py?jw_action=scoutf1_add&ou_id=%d'\
    % ou.ou_id), align = 'RIGHT')

  for child in ou.childlist:
    if not child.mngt:
      nCurr_child += 1
      # Check if expanded or not
      if ou_disp.exp_ou.count(child.ou_id):
        table.add_row().add_item(webproc.tag('A', '<IMAGE SRC="../minus.jpg" BORDER=0>',\
            'HREF=ou_logic.py?jw_action=oup_expand&ou_id=%d&ou_sub=%d&expand=0' %\
            (ou.ou_id, child.ou_id)) + ' ' + \
            webproc.tag('A', '<B>%s</B>' % child.name, 'href=ou_logic.py?jw_action=ouf_disp&ou_id=' + str(child.ou_id)))
        if conn.superuser and child.curr_child == 0 and child.curr_memb == 0:
          table.last_row().add_item(webproc.tag('A', 'Del', 'href=ou_logic.py?jw_action=oup_del&ou_id=' +\
              str(child.ou_id) + ' class=small_disp'), align='RIGHT')

        #EXPANDED
        tbl = webproc.table(cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, width='100%', border = 0)
        
        child.child_list()
        child.member_list(status='C')
        for c1 in child.childlist:
          # Show expanded sub OU's
          if not c1.mngt:
            tbl.add_row().add_item('&nbsp&nbsp&nbsp&nbsp')
            tbl.last_row().add_item(webproc.tag('A', '<B>%s</B>' % c1.name,\
                'href=ou_logic.py?jw_action=ouf_disp&ou_id=' + str(c1.ou_id)))
        # Show expanded members
        for m1 in child.memberlist:
          tbl.add_row().add_item(webproc.form_input('CHECKBOX', name='MEMB%s'\
              % m1.scout_id, value='OU%d' % child.ou_id).pr_input())
          #tbl.add_row().add_item('&nbsp&nbsp&nbsp&nbsp')
          tbl.last_row().add_item(webproc.tag('A', "%s %s" % (m1.forename, m1.surname),\
              'href=scout.py?jw_action=scoutf_disp&scout_id=%d&ou_id=%d&disp_ou=%d'\
              % (m1.scout_id, child.ou_id, ou.ou_id)))

        table.add_row().add_item(tbl.pr_table())
      else:
        table.add_row().add_item(webproc.tag('A', '<IMAGE SRC="../plus.jpg" BORDER=0>',\
            'HREF=ou_logic.py?jw_action=oup_expand&ou_id=%d&ou_sub=%d&expand=1') %\
            (ou.ou_id, child.ou_id) + ' ' + \
            webproc.tag('A', '<B>%s</B>' % child.name, 'href=ou_logic.py?jw_action=ouf_disp&ou_id='\
                + str(child.ou_id)))
        if conn.superuser and child.curr_child == 0 and child.curr_memb == 0:
          table.last_row().add_item(webproc.tag('A', 'Del', 'href=ou_logic.py?jw_action=oup_del&ou_id=' +\
              str(child.ou_id) + ' class=small_disp'), align='RIGHT')

  # Members directly of the OU being displayed
  if len(ou.memberlist):
    if nCurr_child:
      table.add_row().add_item('&nbsp')
  for m in ou.memberlist:
    nCurr_memb += 1
    table.add_row().add_item(webproc.form_input('CHECKBOX', name='MEMB%s' % m.scout_id, value='OU%d' % ou.ou_id).pr_input() + '&nbsp&nbsp')
    table.last_row().last_item().data += webproc.tag('A', "%s %s"\
      % (m.forename, m.surname), 'href=scout.py?jw_action=scoutf_disp&scout_id=%d&ou_id=%d&disp_ou=%d'\
      % (m.scout_id, ou.ou_id, ou.ou_id))

  # Do we want to see ALL members
  if ou_disp.all_members:
    table.add_row().add_item('&nbsp')

    ou.member_list(status='L')

    table.add_row().add_item(webproc.tag('H3', 'Inactive members'))
    for m in ou.memberlist:
      table.add_row().add_item(webproc.tag('A', "%s %s" % (m.forename, m.surname),\
        'href=scout.py?jw_action=scoutf_disp&scout_id=%d&ou_id=%d&disp_ou=%d'\
        % (m.scout_id, ou.ou_id, ou.ou_id)))
    for c in ou.childlist:
      c.member_list(status='L')
      if len(c.memberlist):
        table.add_row().add_item(webproc.tag('H4', c.name))
        for cm in c.memberlist:
          table.add_row().add_item(webproc.tag('A', "%s %s" % (cm.forename, cm.surname),\
            'href=scout.py?jw_action=scoutf_disp&scout_id=%d&ou_id=%d&disp_ou=%d'\
            % (cm.scout_id, c.ou_id, ou.ou_id)))

  # Output the list of members
  outtable.last_row().add_item(table.pr_table())

  
  ############################################################################
  # Role information

  if not ou.mngt:
    #don't do this if this is already a management ou
    table = intable(param)
    table.add_row().add_item(webproc.tag('H3', webproc.tag('A', ou.mngt_ou.name,\
        'href=ou_logic.py?jw_action=ouf_disp&ou_id=%d' % ou.mngt_ou.ou_id)))

    if conn.write:
      table.append_item(webproc.jbutton('Add management member',\
          'office.py?jw_action=rolef_add1&ou_id=%d&disp_ou=%d' %\
          (ou.mngt_ou.ou_id, ou.ou_id)), align='RIGHT')
 
    ou.mngt_ou.member_list(status='C')
    for r in ou.mngt_ou.memberlist:
      nCurr_mngt += 1
      name = r.forename + ' '
      if r.initials != '':
        name += r.initials + ' '
      name += r.surname
      if conn.write:
        name = webproc.tag('A', name, 'href=office.py?jw_action=rolef_add2&ou_id=%d&scout_id=%d'\
            % (ou.mngt_ou.ou_id, r.scout_id))
      table.add_row().add_item(name)
      table.last_row().add_item(r.title)
      if conn.write:
        table.last_row().add_item(webproc.tag('A', 'Del',\
            'href=office.py?jw_action=rolep_del&ou_id=%d&scout_id=%d class=small_disp'\
            % (ou.mngt_ou.ou_id, r.scout_id)))

    # Print the roles info
    outtable.last_row().add_item(table.pr_table(), valign='top')
  #End or role/management info
  
  # Display the details
  form = webproc.form('ou_logic.py', outtable.pr_table())
  form.add_hidden('jw_action', 'oup_action')
  form.add_hidden('ou_id', ou.ou_id)

  page.data.append(form.pr_form())
  #webproc.form_footer()
  page.output()

  lUpdate = 0
  if nCurr_child != ou.curr_child:
    ou.curr_child = nCurr_child
    lUpdate = 1

  if nCurr_memb + nCurr_mngt != ou.curr_memb:
    ou.curr_memb = nCurr_memb + nCurr_mngt
    lUpdate = 1

  if lUpdate:
    ou.update()

  return



###############################################################################
def ouf_edit(form, db, param, conn, message = ''):
  """Org Unit edit module"""

  # Initial variables
  lAdd = int(form.getfirst('add', 0))
  nOu = int(form.getfirst('ou_id', 0))
  nOu_owner = int(form.getfirst('ou_owner', 0))
  nOu_struct = int(form.getfirst('ou_struct', 0))
  cSubmitted = form.getfirst('submitted', 'N')

  conn.ou_security(nOu)

  # Security check
  if not conn.write:
    security_page(form, param, conn)
    return 

  ou = dbobj.ourec(db, nOu)
  ou_owner = dbobj.ourec(db, ou.ou_owner)

  # If not new unit and unit id is undefined, do the home page thing
  if not lAdd:
    if not ou.found:
      app_error(form, param, conn, message = 'Org Unit ID error')
      return
  else:
    # make sure it is initialised
    ou = dbobj.ourec(db, 0)

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

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
  table.last_row().add_item(webproc.tag('A', 'Cancel', "href=ou_logic.py?jw_action=ouf_disp&ou_id=%d" %\
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
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="ouf_edit" VALUE="Submit">')
  
  form = webproc.form('ou_logic.py', table.pr_table(), name='ouf_edit')
  form.add_hidden('jw_action', 'oup_edit')
  form.add_hidden('ou_id', nOu)
  form.add_hidden('submitted', 'Y')

  if lAdd:
    form.add_hidden('add', '1')
    form.add_hidden('ou_owner', str(nOu_owner))
    form.add_hidden('ou_struct', str(nOu_struct))

  # Output the scout edit form
  #cForm = webproc.tag('FORM', table.pr_table(), 'METHOD="POST" NAME="ouf_edit" action="ou_logic.py"')

  page.data.append(form.pr_form())
  #webproc.form_footer()
  page.output()

  return

##############################################################################
def oup_edit(form, db, param, conn):
  """Processes the input from the Org Unit edit screen """

  #Initialise input variables
  lAdd = int(form.getfirst('add', 0))
  nOu = int(form.getfirst('ou_id', '0'))
  nOu_owner = int(form.getfirst('ou_owner', '0'))
  nOu_struct = int(form.getfirst('ou_struct', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  conn.ou_security(nOu)
  # Security check
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 


  ou = dbobj.ourec(db, nOu)
  if not ou.found and not lAdd:
    app_error(form, param, conn, message = "Invalid org unit id")
    return

  if form.getfirst('name','') == '':
    ouf_edit(form, db, param, conn)
    return

  if lAdd:
    # need an new object to build.
    ou = dbobj.ourec(db, nOu)
    if nOu_owner == 0 or nOu_struct == 0:
      app_error(form, param, conn, message = "Invalid parameters for OU add")
      return
    ou.ou_owner = nOu_owner
    ou.ou_struct = nOu_struct
 
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

  if lAdd:
    ou.add()
  else:
    ou.update()
  dbobj.log_action(db, conn.scout_id, 2002, 0, ou.ou_id)

  ouf_disp(form, db, param, conn, ou_id = nOu)
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
  # Owning OU must exist
  if not ou_owner.found:
    app_error(form, param, conn, message = 'OU ID error')
    return

  # Get ou structure record and lists of possible child OU's
  ou_str = dbobj.ou_structrec(db, ou_owner.ou_struct)
  ou_str.sub_ou_list()

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form)

  # Initialise variables for display
  if cSubmitted == 'Y':
    cGeneric 	= form.getfirst('generic', '')  
  else:
    cGeneric 	= ''

  # This table organises the page
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
  table.add_row().add_item(webproc.tag('H2', 'New Org Unit input'))
  table.last_row().add_item(webproc.tag('A', 'Cancel', "href=ou_logic.py?jw_action=ouf_disp&ou_id=%d" % ou_owner.ou_id))

  # First row
  table.add_row().add_item("Add new sub unit to : %s" % ou_owner.name)

  # Generate section list
  for x in ou_str.children:
    table.add_row().add_item('<INPUT TYPE="RADIO" NAME="ou_struct" VALUE=%d> %s' % (x.ou_struct, x.s_name))

  for x in ou_str.generic_list:
    table.add_row().add_item('<INPUT TYPE="RADIO" NAME="ou_struct" VALUE=%d> %s' % (x.ou_struct, x.s_name))

  # Form buttons
  table.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="ouf_add" VALUE="Submit">')

  form = webproc.form('ou_logic.py', table.pr_table(), name='ouf_add')
  form.add_hidden('jw_action', 'oup_add')
  form.add_hidden('ou_owner', str(ou_owner.ou_id))
  form.add_hidden('add', '1')
  form.add_hidden('submitted', 'Y')

  page.data.append(form.pr_form())
  # Output the scout edit form
  page.output()

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
  nOu_owner = int(form.getfirst('ou_owner', '0'))
  nOu_struct = int(form.getfirst('ou_struct', '0'))
  cSubmitted = form.getfirst('submitted', 'N')

  ou_owner = dbobj.ourec(db, nOu_owner)
  if not ou_owner.found:
    app_error(form, param, conn, message = "Invalid OU id")
    return

  # If no structure entered, ask again
  if nOu_struct == 0:
    ouf_add(form, db, param, conn)
    return

  ou_struct = dbobj.ou_structrec(db, nOu_struct)
  if not ou_struct.found:
    app_error(form, param, conn, message = "Invalid OU structure id")
    return


  ouf_edit(form, db, param, conn)

  return


##############################################################################
def oup_del(form, db, param, conn):
  """Processes the delete request """

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #Initialise input variables
  nOu = int(form.getfirst('ou_id', '0'))
  ou = dbobj.ourec(db, nOu)

  if not ou.found:
    app_error(form, param, conn, message = "Invalid org unit id")
    return

  if ou.curr_memb or ou.curr_child:
    app_error(form, param, conn, message = "Org Unit still has current members")
    return

  ou.child_list()
  ou.member_list(status='C')
  if len(ou.childlist) > 0:
    app_error(form, param, conn, message = "Org Unit still has current members")
    return

  if len(ou.memberlist) > 0:
    app_error(form, param, conn, message = "Org Unit still has current members")
    return

  nOu_owner = ou.ou_owner

  # Log the action first
  dbobj.log_action(db, conn.scout_id, 2003, 0, ou.ou_id)
  ou.delete()


  ouf_disp(form, db, param, conn, ou_id = nOu_owner)
  return

##############################################################################
def oup_expand(form, db, param, conn):
  """Processes the expand ou display option """

  #Initialise input variables
  nOu = int(form.getfirst('ou_id', '0'))
  nOu_sub = int(form.getfirst('ou_sub', '0'))
  nExpand = int(form.getfirst('expand', '0'))

  ou = dbobj.ourec(db, nOu)
  if not ou.found:
    app_error(form, param, conn, message = "Invalid org unit id")
    return

  ou_disp = dbobj.ou_disprec(db, ou.ou_id, conn.scout_id)

  if nExpand:
    if not ou_disp.exp_ou.count(nOu_sub):
      ou_disp.exp_ou.append(nOu_sub)
      ou_disp.update()
  else:
    if ou_disp.exp_ou.count(nOu_sub):
      ou_disp.exp_ou.remove(nOu_sub)
      ou_disp.update()

  ouf_disp(form, db, param, conn, ou_id = nOu)
  return

##############################################################################
def oup_view(form, db, param, conn):
  """Processes the expand ou display option """

  #Initialise input variables
  nOu = int(form.getfirst('ou_id', '0'))
  nExpand = int(form.getfirst('expand', '0'))

  ou = dbobj.ourec(db, nOu)
  if not ou.found:
    app_error(form, param, conn, message = "Invalid org unit id")
    return

  ou_disp = dbobj.ou_disprec(db, ou.ou_id, conn.scout_id)

  if nExpand:
    ou_disp.show_actions = 1
    ou_disp.update()
  else:
    ou_disp.show_actions = 0
    ou_disp.update()

  ouf_disp(form, db, param, conn, ou_id = nOu)
  return

##############################################################################
def oup_all_members(form, db, param, conn):
  """Processes the expand ou display option """

  #Initialise input variables
  nOu = int(form.getfirst('ou_id', '0'))
  nAll_members = int(form.getfirst('all_members', '0'))

  ou = dbobj.ourec(db, nOu)
  if not ou.found:
    app_error(form, param, conn, message = "Invalid org unit id")
    return

  ou_disp = dbobj.ou_disprec(db, ou.ou_id, conn.scout_id)

  if nAll_members:
    ou_disp.all_members = 1
  else:
    ou_disp.all_members = 0

  ou_disp.update()

  ouf_disp(form, db, param, conn, ou_id = nOu)
  return


###############################################################################
def oup_move(form, db, param, conn, message = ''):
  """Org Unit move module"""

  # Initial variables
  nOu = int(form.getfirst('ou_id', 0))
  nOu_move_to = int(form.getfirst('ou_move_to', 0))

  #if nOu_move_to == 0:
  #  ouf_disp(form, db, param, conn, ou_id = nOu)
  #  return

  # Security check

  conn.ou_security(nOu)

  if not conn.write:
    security_page(form, param, conn)
    return 

  newou = dbobj.ourec(db, nOu_move_to)
  if not newou.found:
    ouf_disp(form, db, param, conn, ou_id = nOu_from)
    return

  # This extracts the scout id's to be moved and make a list of them
  memblist = memb_ch(form)

  for nScout_id in memblist:
    scout = dbobj.scoutrec(db, nScout_id)
    # Lets get the ou_id we're moving from from the value in the form
    nOu_from = int(form.getfirst('MEMB%d' % nScout_id, 0)[2:])
    oldou = dbobj.ourec(db, nOu_from)
    role = scout.role_by_ou(nOu_from)
    # If we've got the role record, update it
    if role.found:
      role.ou_id = nOu_move_to
      role.add_edit()
    if oldou.found:
      oldou.update_num()

  #Update the numbers of current members etc
  newou.update_num()

  db.commit()

  # redisplay the original ou details
  ouf_disp(form, db, param, conn, ou_id = nOu)

  return

