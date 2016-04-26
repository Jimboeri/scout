#!/usr/bin/python2

import cgi
import cgitb; cgitb.enable()
import webproc 
from webproc import tag
from webscout import *
import dbobj
import Cookie
from procs import *
import time
import datetime
from signinproc import login_form 
from ou import ouf_disp, home_page
import StringIO
import csv
import pyExcelerator
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart

##############################################################################
def awardf_disp (form, db, param, conn, scout_id = 0, ou_id = 0):
  """Displays awards and possible awards for a scout """

  if scout_id == 0:
    nScout = int(form.getfirst('scout_id', 0))
  else:
    nScout = scout_id

  if ou_id == 0:
    nOu = int(form.getfirst('ou_id', 0))
  else:
    nOu = ou_id

  disp_achievements = form.getfirst('disp_ach', 'N').upper()

  # If not form scout id, do the home page thing
  if nScout == 0:
    home_page(form, db, param, conn, menu_id=1)
    return

  if not conn.sign_in:
    login_form(form, db, param, conn, next_proc='awardf_disp')
    return

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    # go to top of browse tree
    home_page(form, db, param, conn, menu_id=1)
    return 

  if nOu == 0:
    scout.role_list()
    if len(scout.rolelist):
      nOu = scout.rolelist[0].ou_id

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    # go to top of browse tree
    app_error(form, param, conn, message = "Invalid Ou id %d" % nOu)
    return 

  conn.ou_security(nOu)

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  #define outer table, hold scout details at the op, parents on the left, & achievments on the right
  outtable = webproc.table(width='100%', border = param.ot_brdr,\
      cellspacing = param.ot_cellspc, cellpadding = param.ot_cellpad)

  # top row if for Scout details
  outrow = outtable.add_row()

  # Create scout details table
  table = sub_scout_dets(scout, ourec, param)
  item = table.last_row().add_item(' ')
  item = table.last_row().add_item(' ')
  if conn.read and disp_achievements != 'Y':
    item.data = webproc.jbutton('Show achievement details',\
        "award.py?jw_action=awardf_disp&scout_id=%d&ou_id=%d&disp_ach=Y"\
        % (scout.scout_id, nOu), need_form=1)

  # Output the scout's details
  outitem = outrow.add_item(table.pr_table(), colspan='3')
  # Second row of the outer table contains award and achievement data
  outrow = outtable.add_row()

  # This table organises the scouts actual achievements
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # Row 1 Title
  disp_line(table, tag('H4', "Awards and badges obtained"))

  # Build lists of awards and achievements
  scout.all_award_info()

  ourec.ou_owners()
  ourec.award_list()

  if len(scout.achievelist) > 0:
    for a in scout.achievelist:
      item = table.add_row().add_item(a.name)
      if not a.awd_presented:
        item.data += ' (award not yet presented)'
      if conn.write:
        item.data = tag('A', item.data,\
          'href=award.py?jw_action=achievef_present&scout_id=%d&award_id=%d&ou_id=%d' %\
          (a.scout_id, a.award_id, nOu))
  else:
      row = table.add_row()
      row.add_item('No badges or awards')

  outrow.add_item(table.pr_table(), valign='TOP')

  # This table organises the scouts work in progress
  if len(scout.achieve_wiplist) > 0:
    table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

    # Row 1 Title
    disp_line(table, tag('H4', "Awards and badges being worked on"))

    if len(scout.achieve_wiplist) > 0:
      for a in scout.achieve_wiplist:
        row = table.add_row()
        #row.add_item(a.name)
        row.add_item(tag('A', a.name,\
            'href=award.py?jw_action=achievef_add&scout_id=%d&award_id=%d&ou_id=%d'\
            % (scout.scout_id, a.award_id, ourec.ou_id)))
    else:
        table.add_row().add_item('No badges or awards')

    outrow.add_item(table.pr_table(), valign='TOP')

  # This table organises the scouts awards to be achieved

  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # Row 1 Title
  disp_line(table, tag('H4', "Awards and badges still available"))

  if len(scout.award_todolist) > 0:
    for a in scout.award_todolist:
      if conn.write:
        table.add_row().add_item(tag('A', a.name,\
            'href=award.py?jw_action=achievef_add&scout_id=%d&award_id=%d&ou_id=%d'\
            % (scout.scout_id, a.award_id, ourec.ou_id)))
      else:
        table.add_row.add_item(a.name)

  else:
    table.add_row().add_item('No badges or awards')

  outitem = outrow.add_item(table.pr_table(), valign='TOP')
  page.data.append(outtable.pr_table())

  # This section displays achievement details
  if conn.read and disp_achievements == 'Y':
    outtable = webproc.table(width='100%', border = param.ot_brdr,\
        cellspacing = param.ot_cellspc, cellpadding = param.ot_cellpad)

    table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
        cellspacing = param.it_cellspc, border = param.it_brdr)
    # This section displays achievement details
    subachlist = dbobj.subach_list(db, scout.scout_id)

    outtable.add_row().add_item('Achievement details', header=1, colspan='2')
    table.add_row().add_item('Award name', header=1, align='LEFT')
    table.last_row().add_item('Sub level name', header = 1, align='LEFT')
    table.last_row().add_item('Date obtained', header = 1, align='LEFT')

    for ac in subachlist:
      award = dbobj.awardrec(db, ac.award_id)
      subaward = dbobj.award_sublevel(db, ac.award_id, ac.sub_award_id)

      if award.award_type != 1:
        # Award type 1 is weros, they are displayed separately
        table.add_row().add_item(award.name)
        table.last_row().add_item(subaward.name)
        table.last_row().add_item(ac.dt_obtained)
    outtable.add_row().add_item(table.pr_table(), valign='TOP')

    if ourec.ou_struct == 6 or ourec.struct_parent == 6:
      # This is now cubs
      table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
          cellspacing = param.it_cellspc, border = param.it_brdr)
      table.add_row().add_item('Award name', header=1, align='LEFT')
      table.last_row().add_item('Sub level name', header = 1, align='LEFT')
      table.last_row().add_item('Date obtained', header = 1, align='LEFT')

      for ac in subachlist:
        award = dbobj.awardrec(db, ac.award_id)
        subaward = dbobj.award_sublevel(db, ac.award_id, ac.sub_award_id)

        if award.award_type == 1:
          # Award type 1 is weros, they are displayed separately
          table.add_row().add_item(award.name)
          table.last_row().add_item(subaward.name)
          table.last_row().add_item(ac.dt_obtained)
      outtable.last_row().add_item(table.pr_table(), valign='TOP', width='50%')

    page.data.append(outtable.pr_table())
    # End of achievement detail display

  page.output()

  return

##############################################################################
def achievef_add (form, db, param, conn, scout_id = 0, award_id = 0, ou_id = 0):
  """Allows scout to obtain awards """

  # get parameters
  if scout_id == 0:
    nScout = int(form.getfirst('scout_id', 0))
  else:
    nScout = scout_id
  if award_id == 0:
    nAward = int(form.getfirst('award_id', 0))
  else:
    nAward = award_id
  if ou_id == 0:
    nOu = int(form.getfirst('ou_id', 0))
  else:
    nOu = ou_id

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    # go to top of browse tree
    app_error(form, param, conn, message = "Invalid Scout id")
    return 

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    # go to top of browse tree
    app_error(form, param, conn, message = "Invalid OU id")
    return 

  conn.ou_security(nOu)

  # Arranges the screen
  outtable = webproc.table(width='100%', border = param.ot_brdr, cellspacing = param.ot_cellspc, cellpadding = param.ot_cellpad)

  outtable.add_row().add_item(sub_scout_dets(scout, ourec, param).pr_table())

  award = dbobj.awardrec(db, nAward)
  if not award.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid award id')
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  # get the record, if it exists
  achieve = dbobj.achieverec(db, scout.scout_id, award.award_id)
  if achieve.found:
    achieve.sublevels()


  # define table for award details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  if len(award.sublevel) == 0:
    table.add_row().add_item(tag('H4', 'Award achievement'))
    cLine = '%s %s achieved %s on (YYYY-MM-DD) <INPUT TYPE="TEXT" NAME="inp_dt"\
      VALUE="%s" SIZE="10" MAXLENGTH="10">\
      <INPUT TYPE="HIDDEN" NAME="whole_award" VALUE="1"' % \
      (scout.forename, scout.surname, award.name, datetime.date.today().isoformat())
    table.add_row().add_item(cLine)
  else:
    table.add_row().add_item(tag('H4', 'Either achieved full award'))
    cLine = '%s %s achieved the <B>%s</B> on (YYYY-MM-DD) <INPUT TYPE="TEXT" NAME="inp_dt" VALUE="%s" SIZE="10" MAXLENGTH="10">' % \
    (scout.forename, scout.surname, award.name, datetime.date.today().isoformat())
    table.add_row().add_item(cLine)
    table.add_row().add_item('The whole award has been achieved: <INPUT TYPE="CHECKBOX" NAME="whole_award" VALUE="1">')


  outtable.add_row().add_item(table.pr_table())

  if len(award.sublevel) > 0:
    # define table for award details
    table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
    table.add_row().add_item(tag('H4', 'Or identify components achieved'))
    alevels = []
    bMandatory = 0
    nOpt_done = 0
    for sl in award.sublevel:
      # get the sub achievement record
      sa = dbobj.achievesubrec(db, scout.scout_id, award.award_id, sl.sub_award_id)
      # if this achievement has not been completed
      if not sl.optional:
        if not bMandatory:
          table.add_row().add_item(tag('H4', 'Mandatory items'))
          bMandatory = 1
        if not sa.complete:
        # This is mandatory
          if sl.num_req > 1:
            table.add_row().add_item('<INPUT TYPE="CHECKBOX" NAME="sl_%d" VALUE="1" >%s (%d completed so far)' % (sl.sub_award_id, sl.name, len(sa.units)))
          else:
            table.add_row().add_item('<INPUT TYPE="CHECKBOX" NAME="sl_%d" VALUE="1" >%s' % (sl.sub_award_id, sl.name))
          alevels.append(sl.sub_award_id)
        else:
          table.add_row().add_item('Achieved - %s' % sl.name)

    bOptional = 0
    for sl in award.sublevel:
      # get the sub achievement record
      sa = dbobj.achievesubrec(db, scout.scout_id, award.award_id, sl.sub_award_id)
      if sl.optional:
        if not bOptional:
          # Print a heading if needed
          table.add_row().add_item(tag('H4', 'Optional items, %d needed'\
            % award.opt_needed))
          bOptional = 1
        if not sa.complete:
          if sl.num_req > 1:
            table.add_row().add_item('<INPUT TYPE="CHECKBOX" NAME="sl_%d" VALUE="1" >%s (%d completed so far)' % (sl.sub_award_id, sl.name, len(sa.units)))
          else:
            table.add_row().add_item('<INPUT TYPE="CHECKBOX" NAME="sl_%d" VALUE="1" >%s' % (sl.sub_award_id, sl.name))
          alevels.append(sl.sub_award_id)
        else:
          table.add_row().add_item('Achieved - %s' % sl.name)

    # This is a string holding all sub_award_id numbers used in the form. Used to scheck results.
    cLevels = ''
    for al in alevels:
      if len(cLevels) > 0:
        cLevels += ',' + str(al)
      else:
        cLevels = str(al)

    table.last_row().last_item().data += '<INPUT TYPE="HIDDEN" NAME="cLevels" VALUE="%s">' % (cLevels)
  
    outtable.add_row().add_item(table.pr_table())

  # define table for comments and to confirm award presented
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  edit_comment(table, 'Comments on this achievement', 'cComment', '')
  outtable.add_row().add_item(table.pr_table())

  # Hidden form fields for form 
  item = outtable.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="achievef_add" VALUE="Add Award">')
  item.data +='<INPUT TYPE="HIDDEN" NAME="scout_id" VALUE="%d">' % (scout.scout_id)
  item.data += '<INPUT TYPE="HIDDEN" NAME="award_id" VALUE="%d">' % (award.award_id)
  item.data += '<INPUT TYPE="HIDDEN" NAME="ou_id" VALUE="%d">' % (nOu)
  item.data += '<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="achievep_add">'


  # Display the table
  page.data.append(tag('FORM', outtable.pr_table(), 'METHOD="POST" NAME="achievef_add" ACTION="award.py"'))

  page.output()

  return

##############################################################################
def achievep_add(form, db, param, conn):
  """Processes the input from the achievement addition screen """

  #Initialise input variables
  nScout_id = int(form.getfirst('scout_id', '0'))
  nAward_id = int(form.getfirst('award_id', '0'))
  nOu_id = int(form.getfirst('ou_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')
  whole_award = int(form.getfirst('whole_award', '0'))
  cLevels = form.getfirst('cLevels', '')
  cComment = form.getfirst('cComment', '')
  award_dt = form.getfirst('inp_dt', '')
  need_presentation = 0

  if not val_date(award_dt):
    achievef_add(form, db, param, conn)
    return

  scout = dbobj.scoutrec(db, nScout_id)
  if not scout.found:
    app_error(form, param, conn, message = "Invalid scout id")
    return

  award = dbobj.awardrec(db, nAward_id)
  if not award.found:
    app_error(form, param, conn, message = "Invalid Award id")
    return

  conn.pers_security(scout)
  if not conn.write:
    security_page(form, param, conn)
    return

 # Initialise the achieve record

  achieve = dbobj.achieverec(db, scout.scout_id, award.award_id)

  # If the whole award is obtained in one hit
  if whole_award:
    achieve.scout_id = nScout_id
    achieve.award_id = nAward_id
    achieve.dt_obtained = award_dt
    achieve.status = 'H'
    achieve.comments = cComment
    need_presentation = 1
    if achieve.found:
      achieve.update()
    else:
      achieve.add()
    dbobj.log_action(db, conn.scout_id, 3101, scout.scout_id, award.award_id)

    # I still need to decide if I am going to automatially create all sub level achievement records
  else:
    # only some sub levels achieved.
    aLevels = cLevels.split(',')
    nChanges = 0
    # First loop to see if we need to store anything
    for lev in aLevels:
      if len(lev) > 0:
        sub_award_id = int(lev)
        # form send '1'if ticked
        done = int(form.getfirst('sl_' + lev, '0'))
        if done:
          nChanges += 1

    if nChanges > 0:
      # OK now we have to do something, 
      # First, if there is no overall achieve record, create it
      if not achieve.found:
        achieve.scout_id = nScout_id
        achieve.award_id = nAward_id
        achieve.dt_obtained = award_dt
        achieve.status = 'W'
        achieve.comments = cComment
        achieve.add()

      for lev in aLevels:
        sub_award_id = int(lev)
        # form send '1'if ticked
        done = int(form.getfirst('sl_' + lev, '0'))
        if done:
          subachieve = dbobj.achievesubrec(db, 0, 0, 0)
          subachieve.scout_id = nScout_id
          subachieve.award_id = nAward_id
          subachieve.sub_award_id = sub_award_id
          subachieve.dt_obtained = award_dt
          subachieve.comments = cComment
          subachieve.add()

    # We've added maybe some achievements, lets see if we can add the award
    if achieve.check_complete():
      achieve.status = 'H'
      achieve.dt_obtained = award_dt
      achieve.update()
      need_presentation = 1

  # If we have just achieved an award we need to know if it has been presented
  if need_presentation:
    achievef_present(form, db, param, conn, scout_id = achieve.scout_id,\
        award_id = achieve.award_id, ou_id = nOu_id)
  else:
    awardf_disp(form, db, param, conn, scout_id = scout.scout_id)
  return

##############################################################################
def achievef_present (form, db, param, conn, scout_id = 0, award_id = 0, ou_id = 0):
  """Edits a few acheievement values """

  # get parameters
  if scout_id == 0:
    nScout = int(form.getfirst('scout_id', 0))
  else:
    nScout = scout_id
  if award_id == 0:
    nAward = int(form.getfirst('award_id', 0))
  else:
    nAward = award_id
  if ou_id == 0:
    nOu = int(form.getfirst('ou_id', 0))
  else:
    nOu = ou_id


  # If not form scout id, do the home page thing
  if nScout == 0:
    app_error(form, param, conn, message = 'Invalid award id')
    return

  if not conn.sign_in:
    login_form(form, db, param, conn, next_proc='achievef_present')
    return

  scout = dbobj.scoutrec(db, nScout)
  if not scout.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid scout id')
    return 

  award = dbobj.awardrec(db, nAward)
  if not award.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid award id')
    return 

  # Arranges the screen
  outtable = webproc.table(width='100%', border = param.ot_brdr, cellspacing = param.ot_cellspc, cellpadding = param.ot_cellpad)

  conn.pers_security(scout)
  if not conn.write:
    security_page(form, param, conn)
    return

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    app_error(form, param, conn, message = 'Invalid OU id')
    return
 
  # Create scout details table
  outtable.add_row().add_item(sub_scout_dets(scout, ourec, param).pr_table())

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  # get the record, if it exists
  achieve = dbobj.achieverec(db, scout.scout_id, award.award_id)
  if achieve.found:
    achieve.sublevels()


  # define table for achievement updates
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  table.add_row().add_item(tag('H4', award.name))
  table.add_row().add_item("Achieved on : " + achieve.dt_obtained)
  if achieve.comments is not None and achieve.comments != '':
    table.add_row().add_item('Comments:<BR>' + achieve.comments)

  item = table.add_row().add_item('Has the award been presented : ')
  if achieve.awd_presented:
    item.data += '<INPUT TYPE="RADIO" NAME="awd_presented" VALUE="1" CHECKED> Yes \
      <INPUT TYPE="RADIO" NAME="awd_presented" VALUE="0"> No'
  else:
    item.data += '<INPUT TYPE="RADIO" NAME="awd_presented" VALUE="1"> Yes \
      <INPUT TYPE="RADIO" NAME="awd_presented" VALUE="0" CHECKED> No'

  table.add_row().add_item('<INPUT TYPE="SUBMIT" VALUE="Submit">')

  form = webproc.form('award.py', table.pr_table())
  form.add_hidden('jw_action', 'achievep_present')
  form.add_hidden("scout_id", achieve.scout_id)
  form.add_hidden("award_id", achieve.award_id)
  form.add_hidden("ou_id", nOu)


  outtable.add_row().add_item(form.pr_form())


  # Display the table
  page.data.append(outtable.pr_table())

  page.output()

  return

##############################################################################
def achievep_present(form, db, param, conn):
  """Processes the input from the achievement presentation addition form """

  #Initialise input variables
  nScout_id = int(form.getfirst('scout_id', '0'))
  nAward_id = int(form.getfirst('award_id', '0'))
  nOu = int(form.getfirst('ou_id', '0'))
  cComment = form.getfirst('cComment', '')
  nAwd_presented = int(form.getfirst('awd_presented', '0'))

  scout = dbobj.scoutrec(db, nScout_id)
  if not scout.found:
    app_error(form, param, conn, message = "Invalid scout id")
    return

  award = dbobj.awardrec(db, nAward_id)
  if not award.found:
    app_error(form, param, conn, message = "Invalid Award id")
    return

  # Security check
  conn.pers_security(scout)
  if not conn.write:
    security_page(form, param, conn)
    return

  # Initialise the achieve record
  achieve = dbobj.achieverec(db, scout.scout_id, award.award_id)
  if not achieve.found:
    app_error(form, param, conn, message = "Invalid Achievement details")
    return

  # If the whole award is obtained in one hit
  if achieve.dt_obtained is not None and achieve.status == 'H':
    if nAwd_presented != achieve.awd_presented:
      achieve.awd_presented = nAwd_presented
      achieve.update()
      dbobj.log_action(db, conn.scout_id, 3199, scout.scout_id, award.award_id)

  awardf_disp(form, db, param, conn, scout_id = scout.scout_id, ou_id = nOu)
  return



##############################################################################
def awardf_adm (form, db, param, conn, in_struct_id = 0):
  """Award administration top level program"""

  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  if in_struct_id:
    struct_id = in_struct_id
  else:
    struct_id = int(form.getfirst('struct_id', '0'))

  struct_list = dbobj.struct_list(db, no_mngt=1)

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  # This table organises the awards to be displayed
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # Row 1 Title
  table.add_row().add_item(tag('H2', "Award administration"), colspan='2')

  for struct in struct_list:

    # Display existing awards and add award button
    table.add_row().add_item(tag('A', struct.s_name, "href=award.py?jw_action=awardf_adm&struct_id=%d" %\
        struct.ou_struct), colspan='2', header=1, align='LEFT')
    if struct.ou_struct == struct_id:
      table.last_row().add_item(webproc.jbutton('Add award',\
          'award.py?jw_action=awardf_edit&ou_struct=%d&new_award=Y' % struct.ou_struct))
      awards = struct.award_list()
      for a in awards:
        table.add_row().add_item(' ', width="10%")
        table.last_row().add_item(tag('A', a.name, 'href=award.py?jw_action=awardf_edit&award_id=%d' % a.award_id))

  page.data.append(table.pr_table())

  page.output()

  return

##############################################################################
def awardf_edit (form, db, param, conn, in_award_id = 0, add_sublevel = 0, in_ou_struct = 0):
  """Award edit display program"""

  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  # If parameters are not passed from calling directly, look to the web form
  if in_award_id == 0:
    awd_id = int(form.getfirst('award_id', '0'))
  else:
    awd_id = in_award_id

  if in_ou_struct == 0:
    ou_struct = int(form.getfirst('ou_struct', '0'))
  else:
    ou_struct = in_ou_struct

  # setup variables
  new_award = form.getfirst('new_award', 'N')
  new_sublevel = form.getfirst('new_sublevel', 'N')

  #Get ou_struct instance
  ou_structrec = dbobj.ou_structrec(db, ou_struct) 

  # Create award instance
  award = dbobj.awardrec(db, awd_id)
  if new_award == 'N':
    if not award.found:
      app_error(form, param, conn, message = 'Invalid award ID')
      return

    award_type = dbobj.awardtyperec(db, award.award_type)
    ou_structrec = dbobj.ou_structrec(db, award_type.ou_struct)

  if not ou_structrec.found:
    app_error(form, param, conn, message = 'Invalid structure ID')
    return


  # setup variables
  name = form.getfirst('name', award.name)
  descr = form.getfirst('descr', award.descr)
  opt_needed = form.getfirst('opt_needed', str(award.opt_needed))
  prereq = int(form.getfirst('prereq', str(award.prereq)))

  # need other awards to build list for dependancies
  awd_list = ou_structrec.award_list()

  # Init the dependancies selection field
  if prereq == 0:
    dep_sel = '<OPTION VALUE=0 SELECTED>None'
  else:
    dep_sel = '<OPTION VALUE=0>None'

  # remove current record from the list
  for a in awd_list:
    if a.award_id == award.award_id:
      awd_list.remove(a)
    else:
      if a.award_id == prereq:
        dep_sel += '<OPTION VALUE=%d SELECTED>%s' % (a.award_id, a.name)
      else:
        dep_sel += '<OPTION VALUE=%d>%s' % (a.award_id, a.name)

  dep_sel = tag('SELECT', dep_sel, 'NAME="prereq"')

  # initialise award_type options and input
  at_opt = ''
  award_types = ou_structrec.award_types_list()

  for at in award_types:
    if at.award_type == award.award_type:
      at_opt += '<OPTION VALUE=%d SELECTED>%s' % (at.award_type, at.name)
    else:
      at_opt += '<OPTION VALUE=%d>%s' % (at.award_type, at.name)
  at_opt = tag('SELECT', at_opt, 'NAME="award_type"')

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  # Arranges the screen
  outtable = webproc.table(width='100%', border = param.ot_brdr, cellspacing = param.ot_cellspc, cellpadding = param.ot_cellpad)

  # This table organises the award top level details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  # Row 1 Title
  if new_award == 'Y':  
    table.add_row().add_item(tag('H2', "New award entry"), colspan='2')
  else:
    table.add_row().add_item(tag('H2', "Award modification"), colspan='2')
  table.last_row().add_item(webproc.jbutton('Return to awards', 'award.py?jw_action=awardf_adm&struct_id=%d'\
      % ou_structrec.ou_struct, need_form=0))
  table.add_colgroup().add_col(width="25%")


  edit_row(table, 'Name', 'name', award.name, size=80, maxlen=80)

  edit_comment(table, 'Full description', 'descr', award.descr)

  table.add_row().add_item('<b>This award must be obtained first:</b>')
  table.last_row().add_item(dep_sel)
  table.last_row().add_item('<B>Award_type:</B>')
  table.last_row().add_item(at_opt)

  nOpt = 0
  for o in award.sublevel:
    if o.optional:
      nOpt += 1

  if nOpt > 1 > 0:
    edit_row(table, 'Optional sub levels required:', 'opt_needed', str(award.opt_needed), size=2)

  edit_row(table, 'Years this award is valid', 'yrs_valid', award.yrs_valid, size=2, maxlen=2)
  table.last_row().add_item('<B>Collective award?:</B>')
  if award.collective:
    table.last_row().add_item('<INPUT TYPE="CHECKBOX" NAME="collective" VALUE="1" CHECKED>')
  else:
    table.last_row().add_item('<INPUT TYPE="CHECKBOX" NAME="collective" VALUE="1">')

  edit_row(table, 'Months this award is valid', 'mth_valid', award.mth_valid, size=2, maxlen=2)

  item = table.last_row().add_item('<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="awardp_edit">')
  item.data += '<INPUT TYPE="HIDDEN" NAME="award_id" VALUE="%d">' % award.award_id
  item.data += '<INPUT TYPE="HIDDEN" NAME="new_award" VALUE="%s">' % new_award
  item.data += '<INPUT TYPE="HIDDEN" NAME="struct_id" VALUE=%d>' % ou_structrec.ou_struct
  item.data += '<INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'

  table.add_row().add_item('<INPUT TYPE="SUBMIT" VALUE="Submit">')

  outtable.add_row().add_item(tag('FORM', table.pr_table(), 'METHOD="POST" NAME="awardf_edit" ACTION="award.py"'))

  if new_award != "Y" and new_sublevel != 'Y':
    outtable.add_row().add_item(webproc.jbutton('Add sub level',\
        'award.py?jw_action=awardf_edit&award_id=%d&new_sublevel=Y'\
        % (award.award_id), need_form=1), align="RIGHT")

  for sub in award.sublevel:
    # This table organises the a existing sublevel
    table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
    table.add_row().add_item(tag('H4', "Sublevel"), colspan='2')
    table.add_colgroup().add_col(width="25%")
    edit_row(table, 'Name', 'name', sub.name, size=60, maxlen=80)
    edit_comment(table, 'Full description', 'descr', sub.descr)
    table.last_row().last_item().rowspan="2"
    table.last_row().add_item('Is this level :')
    cOpt = '<INPUT TYPE="RADIO" NAME="optional" VALUE="0"'
    if not sub.optional:
      cOpt += ' CHECKED'
    cOpt += '>Mandatory<BR><INPUT TYPE="RADIO" NAME="optional" VALUE="1"'
    if sub.optional:
      cOpt += ' CHECKED'
    cOpt += '>Optional'
    table.last_row().add_item(cOpt)
 
    table.add_row().add_item('Number of times this level must be achieved:')
    table.last_row().add_item('<INPUT TYPE="text" NAME="num_req" VALUE="%d" SIZE="2">' % sub.num_req)

    item = table.last_row().add_item('<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="awardsubp_edit">')
    item.data += '<INPUT TYPE="HIDDEN" NAME="award_id" VALUE="%d">' % sub.award_id
    item.data += '<INPUT TYPE="HIDDEN" NAME="sub_award_id" VALUE="%d">' % sub.sub_award_id
    item.data += '<INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
    table.add_row().add_item('<INPUT TYPE="SUBMIT" VALUE="Submit">')

    outtable.add_row().add_item(tag('FORM', table.pr_table(), 'METHOD="POST" NAME="awardf_edit" ACTION="award.py"'))

  if new_sublevel == 'Y':
    # This table organises the a new sublevel
    table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
    table.add_row().add_item(tag('H4', "New sublevel"), colspan='2')
    table.add_colgroup().add_col(width="25%")
    edit_row(table, 'Name', 'name', '', size=60, maxlen=80)
    edit_comment(table, 'Full description', 'descr', '')
    table.last_row().last_item().rowspan="2"
    table.last_row().add_item('Is this level :')
    cOpt = '<INPUT TYPE="RADIO" NAME="optional" VALUE="0" CHECKED>Mandatory<BR>\
      <INPUT TYPE="RADIO" NAME="optional" VALUE="1">Optional'
    table.last_row().add_item(cOpt)
    table.add_row().add_item('Number of times this level must be achieved:')
    table.last_row().add_item('<INPUT TYPE="text" NAME="num_req" VALUE="1" SIZE="2">')


    item = table.last_row().add_item('<INPUT TYPE="HIDDEN" NAME="jw_action" VALUE="awardsubp_edit">')
    item.data += '<INPUT TYPE="HIDDEN" NAME="award_id" VALUE="%d">' % award.award_id
    item.data += '<INPUT TYPE="HIDDEN" NAME="new_subaward" VALUE="Y">'
    item.data += '<INPUT TYPE="HIDDEN" NAME="submitted" VALUE="Y">'
    table.add_row().add_item('<INPUT TYPE="SUBMIT" VALUE="Submit">')

    outtable.add_row().add_item(tag('FORM', table.pr_table(), 'METHOD="POST" NAME="awardf_edit" ACTION="award.py"'))


  page.data.append(outtable.pr_table())

  page.output()

  return

##############################################################################
def awardp_edit(form, db, param, conn):
  """Processes the input from the award addition screen """

  #Initialise input variables
  nAward_id = int(form.getfirst('award_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')
  nAward_type = int(form.getfirst('award_type', '0'))
  cName = form.getfirst('name', '')
  cDescr = form.getfirst('descr', '')
  nPrereq = int(form.getfirst('prereq', '0'))
  nOpt_needed = int(form.getfirst('opt_needed', '0'))
  new_award = form.getfirst('new_award', 'N')
  ou_struct = int(form.getfirst('ou_struct', '0'))
  new_sublevel = form.getfirst('new_sublevel', 'N')
  nYrs_valid = int(form.getfirst('yrs_valid', '0'))
  nMth_valid = int(form.getfirst('mth_valid', '0'))
  nCollective = int(form.getfirst('collective', '0'))

  if cName == '':
    awardf_edit(form, db, param, conn, in_award_id = nAward_id)
    return

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  award = dbobj.awardrec(db, nAward_id)
  award.award_type = nAward_type
  award.name = cName
  award.descr = cDescr
  award.prereq = nPrereq
  award.opt_needed = nOpt_needed
  award.yrs_valid = nYrs_valid
  award.mth_valid = nMth_valid
  award.collective = nCollective
 
  if new_award == 'Y':
    award.add()
    #dbobj.log_action(db, conn.scout_id, 3001, award.award_id)

  else: 
    if not award.found:
      app_error(form, param, conn, message = "Invalid Award id")
      return

    award.update()
    #dbobj.log_action(db, conn.scout_id, 3002, award.award_id)

  awardf_adm(form, db, param, conn, in_struct_id = award.ou_struct)
  return

##############################################################################
def awardsubp_edit(form, db, param, conn):
  """Processes the input from the award sublevel addition screen """

  #Initialise input variables
  nAward_id = int(form.getfirst('award_id', '0'))
  nSub_award_id = int(form.getfirst('sub_award_id', '0'))
  cSubmitted = form.getfirst('submitted', 'N')
  cName = form.getfirst('name', '')
  cDescr = form.getfirst('descr', '')
  nOptional = int(form.getfirst('optional', '0'))
  nNum_req = int(form.getfirst('num_req', '0'))
  new_subaward = form.getfirst('new_subaward', 'N')
  
  if cName == '':
    awardf_edit(form, db, param, conn, in_award_id = nAward_id)
    return

  # Security check
  if not conn.superuser:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  award = dbobj.awardrec(db, nAward_id)
  if not award.found:
    app_error(form, param, conn, message = "Invalid Award id")
    return

  subaward = dbobj.award_sublevel(db, nAward_id, nSub_award_id)
  subaward.name = cName
  subaward.descr = cDescr
  subaward.optional = nOptional
  subaward.num_req = nNum_req

  if new_subaward == 'Y':
    subaward.add()
    dbobj.log_action(db, conn.scout_id, 3011, award.award_id)
  else:
    if not subaward.found:
      app_error(form, param, conn, message = "Invalid Sub Award Level id")
      return
    subaward.update()
    dbobj.log_action(db, conn.scout_id, 3012, award.award_id)

  awardf_edit(form, db, param, conn, in_award_id = award.award_id)
  return


##############################################################################
def ouf1_achieve (form, db, param, conn):
  """Allows First screen to input achievements for a unit"""

  # get parameters
  nOu = int(form.getfirst('ou_id', 0))

  # If not form scout id, do the home page thing
  if nOu == 0:
    home_page(form, db, param, conn, menu_id=1)
    return

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    # go to top of browse tree
    home_page(form, db, param, conn, menu_id=1)
    return 

  # Security check
  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  awl = ourec.award_list()

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  outtab = outtable(param)

  # define table for award details
  table = intable(param)

  memblist = memb_ch(form)

  if len(memblist) == 0:
    # No members selected
    outtab.append_item('<H2>You must select members for the awards on the previous screen.\
        <BR>Please press "Back" and try again')
  else:
    table.add_row().add_item('<B>Achievements will be given to these people.</B>')
    for nScout_id in memblist:
      scout = dbobj.scoutrec(db, nScout_id)
      table.add_row().add_item('%s %s' % (scout.forename, scout.surname))

    outtab.append_item(table.pr_table())
    table = intable(param)
    table.append_item('<B>Select the award(s) to work with</B>')
    for aw in awl:
      if aw.collective:
        table.append_item('<INPUT TYPE="CHECKBOX" NAME="AWARD%d" VALUE=%d>%s' %\
            (aw.award_id, aw.award_id, aw.name), new_row = 1)
    outtab.append_item(table.pr_table())

  outtab.append_item('<INPUT TYPE="SUBMIT" VALUE="Submit"', new_row = 1)
  form = webproc.form('award.py', outtab.pr_table())
  form.add_hidden('jw_action', 'ouf2_achieve')
  form.add_hidden('ou_id', nOu)

  for nScout_id in memblist:
    form.add_hidden("MEMB%d" % nScout_id, 'Y')

  page.data.append(form.pr_form())

  page.output()

  return

##############################################################################
def ouf2_achieve (form, db, param, conn):
  """Displays second screen to input achievements for a unit"""

  # get parameters
  nOu = int(form.getfirst('ou_id', 0))
  cComment = form.getfirst('comment', '')
  inp_dt = form.getfirst('inp_dt', '')

  # If not form scout id, do the home page thing
  if nOu == 0:
    home_page(form, db, param, conn, menu_id=1)
    return

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    # go to top of browse tree
    home_page(form, db, param, conn, menu_id=1)
    return 

  # Security check
  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  awl = ourec.award_list()

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  outtab = outtable(param)

  # define table for award details
  table = intable(param)

  memblist = memb_ch(form)
  awardlist = award_ch(form)

  if len(awardlist) == 0:
    ouf_disp(form, db, param, conn)
    return

  if len(memblist) == 0:
    # No members selected
    outtab.append_item('<H2>You must select members for the awards on the previous screen.\
        <BR>Please press "Back" and try again')
  else:
    table.add_row().add_item('<B>Achievements will be given to these people.</B>')
    for nScout_id in memblist:
      scout = dbobj.scoutrec(db, nScout_id)
      table.add_row().add_item('%s %s' % (scout.forename, scout.surname))

    outtab.append_item(table.pr_table(), valign="TOP")
    table = intable(param)
    table.append_item('<B>Select the achievements</B>')
    for tawd in awardlist:
      awardrec = dbobj.awardrec(db, tawd)
      if len(awardrec.sublevel) == 0:
        # There are no sublevels for this award
        table.append_item('<INPUT TYPE="CHECKBOX" NAME="WAWARD%d" VALUE=%d><B> %s</B>' %\
            (awardrec.award_id, awardrec.award_id, awardrec.name), new_row = 1)
      else:
        table.append_item('<B>%s</B>' % awardrec.name, new_row = 1)
        for asl in awardrec.sublevel:
          cName = "SAWARD%dSUB%d" % (awardrec.award_id, asl.sub_award_id)
          if form.has_key(cName):
            table.append_item('&nbsp&nbsp<INPUT TYPE="CHECKBOX" NAME="%s" VALUE=%d CHECKED> %s' %\
                (cName, asl.sub_award_id, asl.name), new_row = 1)
          else:
            table.append_item('&nbsp&nbsp<INPUT TYPE="CHECKBOX" NAME="%s" VALUE=%d> %s' %\
                (cName, asl.sub_award_id, asl.name), new_row = 1)


    outtab.append_item(table.pr_table(), valign="TOP")
    table = intable(param)
 
    table.add_row().add_item('Select date achieved on (YYYY-MM-DD):\
        <INPUT TYPE="TEXT" NAME="inp_dt" VALUE="%s" SIZE="10" MAXLENGTH="10">' %\
        (inp_dt))
   
    edit_comment(table, 'Comments on this achievement', 'comment', cComment) 

    table.append_item('<INPUT TYPE="SUBMIT" VALUE="Add Achievement(s)">',\
        new_row = 1)

    outtab.append_item(table.pr_table(), new_row = 1, colspan = 2)
    form = webproc.form('award.py', outtab.pr_table())

    for nScout_id in memblist:
      form.add_hidden("MEMB%d" % nScout_id, 'Y')

    for nAward_id in awardlist:
      form.add_hidden("AWARD%d" % nAward_id, nAward_id)
    form.add_hidden('jw_action', 'oup_achieve')
    form.add_hidden('ou_id', nOu)


  page.data.append(form.pr_form())

  page.output()

  return

##############################################################################
def oup_achieve(form, db, param, conn):
  """Processes the input from the ou collective """

  #Initialise input variables
  nOu = int(form.getfirst('ou_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')
  cComment = form.getfirst('comment', '')
  award_dt = form.getfirst('inp_dt', '')

  # If not form scout id, do the home page thing
  if nOu == 0:
    home_page(form, db, param, conn, menu_id=1)
    return

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    # go to top of browse tree
    home_page(form, db, param, conn, menu_id=1)
    return 

  # Security check
  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  if not val_date(award_dt):
    ouf2_achieve(form, db, param, conn)
    return


  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  table = intable(param)
  nAwards = 0

  memblist = memb_ch(form)
  awardlist = saward_ch(form)

  waward = []
  keys = form.keys()
  for x in keys:
    if x[0:6] == 'WAWARD':
      z = int(x[6:])
      if not z in waward:
        waward.append(z)
 
  saward = []
  for x in keys:
    if x[0:6] == 'SAWARD':
      y = x.find('SUB')
      z = int(x[6:y])
      if not z in saward:
        saward.append(z)
 
  for s in memblist:
    # Lets get the scout
    pers = dbobj.personrec(db, s)
    str = 'Scout %s %s, id = %d<BR>' % (pers.forename, pers.surname, pers.scout_id)
    # Lets do the whole awards first
    for w in waward:
      # get the achievement records if it exists 
      achieve = dbobj.achieverec(db, s, w)
      str += '  Whole Awd_id = %d, found = %d, done = %d<BR>' % (w, achieve.found, achieve.done)
      if not achieve.done:
        award = dbobj.awardrec(db, w)
        achieve.scout_id = s
        achieve.award_id = w
        achieve.dt_obtiained = award_dt
        achieve.comments = cComment
        achieve.status = 'H'
        #achieve.add()
        str += '<B> Award %d added <B></BR>' % w
        if nAwards == 0:
          table.append_item('<B>The following awards need to be presented:<B>')
        table.append_item('%s %s achieved %s' % (pers.forename, pers.surname, award.name), new_row = 1)
        nAwards += 1

    # and not for awards with sub levels
    for sub in awardlist:
      # Now lets cycle through the awards on offer.    
      achieve = dbobj.achieverec(db, s, sub)
      if not achieve.done:
        # Lets work out which sub awards we need to do
        subaward = []
        root = 'SAWARD%dSUB' % sub
        for x in keys:
          if x[0:len(root)] == root:
            z = int(x[len(root):])
            if not z in subaward:
              subaward.append(z)

        for sub_award in subaward:
          # lets cyvle through thos sub awards acheived
          sub_ach = dbobj.achievesubrec(db, s, sub, sub_award)
          if not sub_ach.complete:
            # Only need to do something if not complete
            sub_ach.scout_id = s
            sub_ach.award_id = sub
            sub_ach.sub_award_id = sub_award
            sub_ach.dt_obtained = award_dt
            sub_ach.comments = cComment
            sub_ach.add()
            str += ' Award %d, sub %d - incomplete, substep added<BR>' % (sub, sub_award)
          else:
            str += ' Award %d, sub %d - complete, no action req<BR>' % (sub, sub_award)

        achieve.check_complete()
        if achieve.done:
          award = dbobj.awardrec(db, sub)
          achieve.status = 'H'
          achieve.dt_obtained = award_dt
          achieve.update()
          str += '<B> Award %d added <B></BR>' % sub_award
          if nAwards == 0:
            table.append_item('<B>The following awards need to be presented:<B>')
          table.append_item('%s %s achieved %s' % (pers.forename, pers.surname, award.name), new_row = 1)
          nAwards += 1
                  
  if nAwards == 0:
    table.append_item("<B>No awards were achieved</B>", new_row = 1)

  table.append_item(webproc.jbutton('Continue', 'ou_logic.py?jw_action=ouf_disp&ou_id=%d'\
      % nOu), new_row = 1)
 
  page.data.append(table.pr_table())

  if param.testing:
    page.data.append(str)

  page.output()

  return

##############################################################################
def werof_achieve (form, db, param, conn, ou_id = 0):
  """Displays wero to input achievements for a unit, member selection"""

  # get parameters
  if ou_id:
    nOu = ou_id
  else:
    nOu = int(form.getfirst('ou_id', 0))

  cComment = form.getfirst('cComment', '')
  inp_dt = form.getfirst('inp_dt', datetime.date.today().isoformat())

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    # go to top of browse tree
    home_page(form, db, param, conn, menu_id=1)
    return 

  # Either this OU or its parent needs to have a ou_struct id of 6 which is for Cubs

  if not ourec.ou_struct == 6:
    if not ourec.parent_id == 6:
      app_error(form, param, conn, message = "Only available for Cubs")
      return

  # This extracts the scout id's to be moved and make a list of them
  memblist = memb_ch(form)

  for nScout_id in memblist:
    scout = dbobj.scoutrec(db, nScout_id)
 
  bronze_wero = dbobj.awardrec(db, 0)
  silver_wero = dbobj.awardrec(db, 0)
  gold_wero = dbobj.awardrec(db, 0)

  # This code is to extract wero award records, not dependant on award_ids. 
  # NB Wero award type = 1
  weros = dbobj.award_list(db, 1)
  for a in weros:
    if a.prereq == 0:
      bronze_wero = a
      for a1 in weros:
        if a1.prereq == bronze_wero.award_id:
          silver_wero = a1
          for a2 in weros:
            if a2.prereq == silver_wero.award_id:
              gold_wero = a2
              break
          break
      break

  # Security check
  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")
  #define outer table, hold leader details at the op, parents on the left, & achievments on the right
  outtable = webproc.table(width='100%', border = param.ot_brdr,\
      cellspacing = param.ot_cellspc, cellpadding = param.ot_cellpad)

  # define table for award details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
      cellspacing = param.it_cellspc, border = param.it_brdr)

  table.add_row().add_item('To award <B>WERO</B> achievements'\
      , colspan='3', align='CENTER')

  outtable.add_row().add_item(table.pr_table(), colspan='2')

  # define table for person details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
     cellspacing = param.it_cellspc, border = param.it_brdr)

  # This extracts the scout id's to be moved and make a list of them
  memblist = memb_ch(form)

  table.add_row().add_item('<B>Achievements will be given to these people.</B>')
  for nScout_id in memblist:
    scout = dbobj.scoutrec(db, nScout_id)
    table.add_row().add_item('%s %s' % (scout.forename, scout.surname))

  outtable.add_row().add_item(table.pr_table(), valign = 'TOP', width='25%')
 
  # define table for award details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
      cellspacing = param.it_cellspc, border = param.it_brdr)

  table.add_row().add_item('Select the WERO components achieved. If achieved more than once, select the number of activities for this group, starting from the left.', colspan='3')

  # Display award components
  for s in bronze_wero.sublevel:
    table.add_row().add_item('<B>%s</B>' % s.name, width='18%')
    item = table.last_row().add_item('')
    for x in range (1, s.num_req+1):
      cName = 'COMP%d-%d' % (s.sub_award_id, x)
      nVal = int(form.getfirst(cName, '0'))
      if nVal:
        item.data += '<INPUT TYPE="CHECKBOX" NAME="%s" VALUE="1" CHECKED>\n' % cName
      else:
        item.data += '<INPUT TYPE="CHECKBOX" NAME="%s" VALUE="1">\n' % cName


  table.add_row().add_item('Date achieved (YYYY-MM-DD) : \
    <INPUT TYPE="TEXT" NAME="inp_dt" VALUE="%s" SIZE="10" MAXLENGTH="10">' %\
    (inp_dt), colspan='3')

  edit_comment(table, 'Comments on this achievement', 'cComment', '', colspan=3) 
  # Hidden form fields for form i

  outtable.last_row().add_item(table.pr_table())
  
  outtable.add_row().add_item('<INPUT TYPE="SUBMIT" NAME="werof_achieve" VALUE="Add WERO Achievements">')

  form = webproc.form('award.py', outtable.pr_table())
  form.add_hidden('jw_action', 'werop_achieve')
  form.add_hidden("ou_id", nOu)
  for nScout_id in memblist:
    form.add_hidden("MEMB%d" % nScout_id, 'Y')

  page.data.append(form.pr_form())
  page.output()

  return

##############################################################################
def werop_achieve(form, db, param, conn):
  """Processes the input from the wero achievement screen """

  #Initialise input variables
  nOu = int(form.getfirst('ou_id', 0))
  cSubmitted = form.getfirst('submitted', 'N')
  cComment = form.getfirst('cComment', '')
  award_dt = form.getfirst('inp_dt', '')
  need_presentation = 0

  # Security check
  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  if not val_date(award_dt):
    werof_achieve(form, db, param, conn)
    return

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    app_error(form, param, conn, message = "Invalid Org Unit id")
    return

  if not ourec.ou_struct == 6:
    if not ourec.parent_id == 6:
      app_error(form, param, conn, message = "Only available for Cubs")
      return

  bronze_wero = dbobj.awardrec(db, 0)
  silver_wero = dbobj.awardrec(db, 0)
  gold_wero = dbobj.awardrec(db, 0)

  # This code is to extract wero award records, not dependant on award_ids. 
  # NB Wero award type = 1
  weros = dbobj.award_list(db, 1)
  for a in weros:
    if a.prereq == 0:
      bronze_wero = a
      for a1 in weros:
        if a1.prereq == bronze_wero.award_id:
          silver_wero = a1
          for a2 in weros:
            if a2.prereq == silver_wero.award_id:
              gold_wero = a2
              break
          break
      break

  if not bronze_wero.found:
    app_error(form, param, conn, message = "Invalid Award id")
    return

  # Security check
  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  #werof_achieve(form, db, param, conn)
  #return

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  # define table for award details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)

  table.add_row().add_item('<B>Details of awards obtained</B>', colspan='2', align='CENTRE')

  # This extracts the scout id's to be moved and make a list of them
  memblist = memb_ch(form)

  # Build array of which components to add and how many
  keys = form.keys()
  keys.sort()
  complist = []
  comp = 0
  num = 0
  for k in keys:
    # Is this a component field
    c = ex_sub(k)
    if not c:
      continue
    if comp == 0:
      comp = c
    num += 1
    if c != comp:
      # lets add this to the list
      complist.append([comp, num-1])
      comp = c
      num = 1
  # finished processing keys, store the last step
  if num:
    complist.append([comp, num])

  nAwardsAchieved = 0
  
  for nScout_id in memblist:
    scout = dbobj.scoutrec(db, nScout_id)
     
    if scout.found:
      #page.data.append('<BR>%s %s being processed, scout_id = %d' % (scout.forename, scout.surname, scout.scout_id))
      for step in complist:
        subaward = dbobj.award_sublevel(db, bronze_wero.award_id, step[0]) 
        #page.data.append('<BR>--%s being processed' % (subaward.name))
        for index in range(step[1]):
          #page.data.append('<BR>----instance %d being processed' % (index))
          # Start with Bronze wero
          if sub_to_wero(db, scout, bronze_wero, subaward, award_dt, cComment):
            pass
            #page.data.append('<BR>------Bronze wero step added')
          else:
            #page.data.append('<BR>------Bronze wero step already completed')
            # OK the bronze has been done, lets check silver
            if sub_to_wero(db, scout, silver_wero, subaward, award_dt, cComment):
              pass
              #page.data.append('<BR>------Silver wero step added')
            else:
              #page.data.append('<BR>------Silver wero step already completed')
              # OK the silver has been done, lets check gold
              sub_to_wero(db, scout, gold_wero, subaward, award_dt, cComment)
             
      # We've added maybe some achievements, lets see if we can any awards
      
      nAwardsAchieved += check_wero(db, scout, bronze_wero, table, award_dt)
      nAwardsAchieved += check_wero(db, scout, silver_wero, table, award_dt)
      nAwardsAchieved += check_wero(db, scout, gold_wero, table, award_dt)

  if nAwardsAchieved == 0:
    table.add_row().add_item('No specific awards were achieved', colspan='2', align='CENTRE')

  table.add_row().add_item(webproc.jbutton('Return to %s'%ourec.name, 'ou_logic.py?jw_action=ouf_disp&ou_id=%d'%ourec.ou_id, need_form=1))
  
  page.data.append(table.pr_table())
  
  page.output()

  return

##############################################################################
def sub_to_wero(db, scout, wero, subaward, award_dt, comment):
  """This procedure adds a step to a wero achievement. If successful, returns 1,\
     if could not add because this component of the wero is completed, returns 0"""

  nResult = 0
  # Start with Bronze wero
  achieve = dbobj.achieverec(db, scout.scout_id, wero.award_id)

  if not achieve.found:
    achieve.scout_id = scout.scout_id
    achieve.award_id = wero.award_id
    achieve.dt_obtained = award_dt
    achieve.status = 'W'       # Means work-in-progress
    achieve.comments = comment
    achieve.add()
      
  subachieve = dbobj.achievesubrec(db, scout.scout_id, wero.award_id, subaward.sub_award_id)

  if achieve.status == 'W' and len(subachieve.units) < subaward.num_req:
    # Add the subachievement for the wero
    subachieve.scout_id = scout.scout_id
    subachieve.award_id = wero.award_id
    subachieve.sub_award_id = subaward.sub_award_id
    subachieve.dt_obtained = award_dt
    subachieve.comments = comment
    subachieve.add()
    nResult = 1
  else:
    nResult = 0

  return nResult

##############################################################################
def ex_sub(key):
  step = 0
  if key[0:4] == 'COMP':
    # j is the postition in the key name that relates to the hyphen
    j = key[4:].find('-')
    # c is an integer of the subaward_id
    step = int(key[4:j+4])
  return step

##############################################################################
def check_wero(db, scout, wero, table, award_dt):
  """This procedure checks to see if a wero has now been achieved.
     If so the record is update appropriately"""
  achieve = dbobj.achieverec(db, scout.scout_id, wero.award_id)
  if achieve.found and achieve.status == 'W':
  # We've added maybe some achievements, lets see if we can add the award
    if achieve.check_complete():
      achieve.status = 'H'
      achieve.dt_obtained = award_dt
      achieve.update()
      table.add_row().add_item('<B>%s %s - %s</B>' % (scout.forename, scout.surname, wero.name))
      return 1
  return 0

##############################################################################
def werof_extract(form, db, param, conn):
  """This page obtains details needed to do an extract of Wero information"""

  nOu = int(form.getfirst('ou_id', 0))

  # Security check
  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  # define table for award details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
      cellspacing = param.it_cellspc, border = param.it_brdr)

  table.add_row().add_item('<INPUT TYPE="RADIO" NAME="extract" VALUE="email-csv">e-mail file')
  table.add_row().add_item('<INPUT TYPE="RADIO" NAME="extract" VALUE="display">Display on screen')
  table.add_row().add_item('<INPUT TYPE="SUBMIT" VALUE="Submit">')

  outform = webproc.form('award.py', table.pr_table())
  outform.add_hidden('jw_action', 'werop_extract')
  outform.add_hidden("ou_id", nOu)

  keys = form.keys()
  for k in keys:
    if k[0:4] == 'MEMB':
      outform.add_hidden(k, form.getfirst(k))

  page.data.append(outform.pr_form())
  page.output()

  return

##############################################################################
def werop_extract(form, db, param, conn):
  """Processes the input from the wero extract screen """

  #Initialise input variables
  nOu = int(form.getfirst('ou_id', '0'))
  extract_choice = form.getfirst('extract', '')

  extract = []

  conn.ou_security(nOu)
  # Security check
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    app_error(form, param, conn, message = "Invalid Org Unit id")
    return

  bronze_wero = dbobj.awardrec(db, 0)
  silver_wero = dbobj.awardrec(db, 0)
  gold_wero = dbobj.awardrec(db, 0)

  # This code is to extract wero award records, not dependant on award_ids. 
  # NB Wero award type = 1
  weros = dbobj.award_list(db, 1)
  for a in weros:
    if a.prereq == 0:
      bronze_wero = a
      for a1 in weros:
        if a1.prereq == bronze_wero.award_id:
          silver_wero = a1
          for a2 in weros:
            if a2.prereq == silver_wero.award_id:
              gold_wero = a2
              break
          break
      break

  # This extracts the scout's and make a list of them
  memblist = memb_ch(form)
  members = []

  if len(memblist) == 0:
    members = ourec.member_list(status = 'C')
    children = ourec.child_list()
    for kid in children:
      if not kid.mngt:
        kid_memb = kid.member_list(status = 'C')
        for km in kid_memb:
          members.append(km)
  else:
    for m in memblist:
      members.append(dbobj.scoutrec(db, m))

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")
  table = webproc.table(cellpadding = param.it_cellpad,\
      cellspacing = param.it_cellspc, border = 1)

  table.add_row().add_item(' ')
  table.last_row().add_item('BRONZE', colspan='30', align='CENTER', header=1)
  table.last_row().add_item('SILVER', colspan='30', align='CENTER', header=1)
  table.last_row().add_item('GOLD', colspan='30', align='CENTER', header=1)

  table.add_row().add_item(' ')
  
  table.append_item(' ')

  for memb in members:
    row = table.add_row()
    row.add_item('%s %s' % (memb.forename, memb.surname))
    ex_wero(db, memb, bronze_wero, row, 'Orange')
    ex_wero(db, memb, silver_wero, row, 'Dimgray')
    ex_wero(db, memb, gold_wero, row, 'Yellow')

  if extract_choice == 'display':
    table.append_item(' ', new_row = 1)
    table.append_item(webproc.jbutton('Return', 'ou_logic.py?jw_action=ouf_disp&ou_id=%d' %\
        ourec.ou_id), new_row = 1)
    page.data.append(table.pr_table())
    page.output()
    return

  elif extract_choice == 'email-csv':
    user = dbobj.personrec(db, conn.scout_id)
    # Create the mail message
    outer = MIMEMultipart()

    # Mail headers
    outer['Subject'] = 'Wero extract for %s' % ourec.name
    outer['From'] = param.fromaddr
    outer['To'] = user.email
    outer.preamble = 'Wero extract'
    outer.epilogue = ''

    #Add the explanatory text to the message
    textfile = param.template_dir + '/' + param.email_extract_msg
    mf = open(textfile)
    msgfile = MIMEText(mf.read())
    outer.attach(msgfile)

    # Attach the created file to the e-mail.
    msgfile = MIMEText(table.pr_table())
    msgfile.add_header('Content-Disposition', 'attachment', filename='Wero.xls')
    outer.attach(msgfile)

    mailserver = smtplib.SMTP(param.smtpserver)
    #mailserver.set_debuglevel(1)
    mailserver.sendmail(param.fromaddr, user.email, outer.as_string())
    mailserver.quit()

    #outfile = file('/tmp/wero.xls', 'w')
    #outfile.write(table.pr_table())
    #outfile.close()

  ouf_disp(form, db, param, conn, ou_id = nOu)
  return

##############################################################################
def ex_wero(db, scout, wero, row, colour):
  """Adds details of a wero to a table row.
    If the wero substep has been achieved, displays in appropriate colour"""
  achieve = dbobj.achieverec(db, scout.scout_id, wero.award_id)
  col = ''
  if achieve.done:
    col = colour
  for sl in wero.sublevel:
    ex_sub_award(db, scout, sl, row, col)
  return


##############################################################################
def ex_sub_award(db, scout, subaward, row, colour):
  """Procedure only defined in werop_extract(), called from ex_wero()
    Obtains acheivement details for wero sub-step and scout
    Outputs '*' for those passed in the row"""
  sub_ach = dbobj.achievesubrec(db, scout.scout_id, subaward.award_id,\
     subaward.sub_award_id)
  nCnt = 0
  for sau in sub_ach.units:
    row.add_item('*', bgcolor = colour)
    nCnt += 1
    if nCnt == subaward.num_req:
      break
  for x in range(subaward.num_req - nCnt):
    row.add_item('&nbsp')
  return


##############################################################################
def awardleadf_disp (form, db, param, conn, leader_id = 0):
  """Displays awards and possible awards for a lader"""

  nOu = int(form.getfirst('ou_id', '0'))

  if leader_id == 0:  
    nLeader = int(form.getfirst('leader_id', 0))
  else:
    nLeader = leader_id

  # If not form leader id, do the home page thing
  if nLeader == 0:
    home_page(form, db, param, conn, menu_id=1)
    return

  if not conn.sign_in:
    login_form(form, db, param, conn, next_proc='awardf_disp')
    return

  leader = dbobj.adultrec(db, nLeader)
  if not leader.found:
    # go to top of browse tree
    home_page(form, db, param, conn, menu_id=1)
    return

  if not conn.superuser:
    home_page(form, db, param, conn, menu_id=1)
    return

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  #define outer table, hold leader details at the op, parents on the left, & achievments on the right
  outtab = outtable(param)

  # top row if for Scout details
  outrow = outtab.add_row()

  # Create leader details table
  table = sub_leader_dets(leader, param)

  # Output the leader's details
  outitem = outrow.add_item(table.pr_table(), colspan='3')

  # Second row of the outer table contains the members and adult roles
  outrow = outtab.add_row()

  # This table organises the leaders actual achievements
  table = intable(param)

  # Row 1 Title
  disp_line(table, tag('H4', "Awards and badges obtained"))

  # Build lists of awards and achievements
  leader.all_award_info()

  if len(leader.achievelist) > 0:
    for a in leader.achievelist:
      item = table.add_row().add_item(a.name)
      if not a.awd_presented:
        item.data += ' (award not yet presented)'
      if conn.sign_in:
        item.data = tag('A', item.data,\
          'href=award.py?jw_action=achievef_present&scout_id=%d&award_id=%d' %\
          (a.scout_id, a.award_id))
  else:
      row = table.add_row()
      row.add_item('No badges or awards')

  outrow.add_item(table.pr_table(), valign='TOP')

  # This table organises the lader work in progress
  if len(leader.achieve_wiplist) > 0:
    table = intable(param)

    # Row 1 Title
    disp_line(table, tag('H4', "Awards and badges being worked on"))

    if len(leader.achieve_wiplist) > 0:
      for a in leader.achieve_wiplist:
        row = table.add_row()
        #row.add_item(a.name)
        row.add_item(tag('A', a.name, 'href=award.py?jw_action=achievef_add&scout_id=%d&award_id=%d' % (leader.scout_id, a.award_id)))
    else:
        row = table.add_row()
        row.add_item('No badges or awards')

    outtab.append_item(table.pr_table(), valign='TOP')

  # This table organises the leaders wwards to be achieved

  table = intable(param)

  # Row 1 Title
  disp_line(table, tag('H4', "Awards and badges still available"))

  if len(leader.award_todolist) > 0:
    for a in leader.award_todolist:
      row = table.add_row()
      row.add_item(tag('A', a.name, 'href=award.py?jw_action=achievef_add&scout_id=%d&award_id=%d' % (leader.scout_id, a.award_id)))
  else:
      row = table.add_row()
      row.add_item('No badges or awards')

  outtab.append_item(table.pr_table(), valign='TOP')

  outtab.append_item(webproc.jbutton('Return',\
        "office.py?jw_action=rolef_add2&scout_id=%d&ou_id=%d"\
        % (leader.scout_id, nOu), need_form = 1), new_row = 1)

  page.data.append(outtab.pr_table())

  page.output()

  return

##############################################################################
def awardf_extract(form, db, param, conn):
  """This page obtains details needed to do an extract of Collective award information"""

  nOu = int(form.getfirst('ou_id', 0))

  # Security check
  conn.ou_security(nOu)
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  ourec = dbobj.ourec(db, nOu)
  ou_structrec = dbobj.ou_structrec(db, ourec.ou_struct)
  award_types = ou_structrec.award_types_list()

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  page.data.append("<H2>SELECT OPTIONS FOR THE AWARD EXTRACT</H2>")

  # define table for award details
  table = webproc.table(width='100%', cellpadding = param.it_cellpad,\
      cellspacing = param.it_cellspc, border = param.it_brdr)

  table.append_item('<INPUT TYPE="RADIO" NAME="extract" VALUE="email-csv">e-mail file', new_row = 1)
  table.append_item('<INPUT TYPE="RADIO" NAME="extract" VALUE="display">Display on screen', new_row = 1)
  table.append_item('&nbsp', new_row = 1)
  type_index = 1
  for t in award_types:
    table.append_item('<INPUT TYPE="CHECKBOX" name="TYPE%d" VALUE=%d>%s' %\
        (type_index, t.award_type, t.name), new_row = 1)
    type_index += 1

  table.append_item('&nbsp', new_row = 1)
  table.add_row().add_item('<INPUT TYPE="SUBMIT" VALUE="Submit">')

  outform = webproc.form('award.py', table.pr_table())
  outform.add_hidden('jw_action', 'awardp_extract')
  outform.add_hidden("ou_id", nOu)

  keys = form.keys()
  for k in keys:
    if k[0:4] == 'MEMB':
      outform.add_hidden(k, form.getfirst(k))

  page.data.append(outform.pr_form())
  page.output()

  return

##############################################################################
def awardp_extract(form, db, param, conn):
  """Processes the input from the wero extract screen """

  #Initialise input variables
  nOu = int(form.getfirst('ou_id', '0'))
  extract_choice = form.getfirst('extract', '')
  aType = []

  # What types of awards are we going to do here
  type_index = 1
  while form.has_key('TYPE%d' % type_index):
    if int(form.getfirst('TYPE%d' % type_index)):
      aType.append(int(form.getfirst('TYPE%d' % type_index)))
      type_index += 1

  extract = []

  conn.ou_security(nOu)
  # Security check
  if not conn.write:
    # go to top of browse tree
    security_page(form, param, conn)
    return 

  ourec = dbobj.ourec(db, nOu)
  if not ourec.found:
    app_error(form, param, conn, message = "Invalid Org Unit id")
    return

  # This extracts the scout's and make a list of them
  memblist = memb_ch(form)
  members = []

  if len(memblist) == 0:
    members = ourec.member_list(status = 'C')
    children = ourec.child_list()
    for kid in children:
      if not kid.mngt:
        kid_memb = kid.member_list(status = 'C')
        for km in kid_memb:
          members.append(km)
  else:
    for m in memblist:
      members.append(dbobj.scoutrec(db, m))

  # Lets get the list of possible awards
  aAwards = ourec.award_list()

  page = scout_page(title=param.title, css=[param.css_file])
  page.do_heading(param, conn, form, help="award.html")

  table = webproc.table(cellpadding = param.it_cellpad,\
      cellspacing = param.it_cellspc, border = 1)

  # Headers
  row1 = table.add_row()
  row2 = table.add_row()
  row1.add_item(' ')
  row2.add_item(' ')
  # we'll do it an award type at a time
  for t in aType:
    award_type = dbobj.awardtyperec(db, t)
    for a in aAwards:
      if a.award_type == t:
        # If the award if of the type we want to process
        top_item = row1.add_item('%s' % (a.name))
        # we need to know how many colums will be displayed
        cols = 0
        for s in a.sublevel:
          #One field per sub level
          itm = row2.add_item(s.name)
          cols += s.num_req
          if s.num_req > 1:
            itm.colspan = s.num_req
        if cols == 0:
          #If the award has no sublevels
          row2.add_item(' ')
          cols = 1
        top_item.colspan = cols


  table.add_row().add_item(' ')
  
  table.append_item(' ')

  for memb in members:
    row = table.add_row()
    row.add_item('%s %s' % (memb.forename, memb.surname))
    for t in aType:
      award_type = dbobj.awardtyperec(db, t)
      for a in aAwards:
        if a.award_type == t:
          ach = dbobj.achieverec(db, memb.scout_id, a.award_id)
          if not ach.found:
            # The achievement has not happened, must fill with blanks
            if len(a.sublevel) == 0:
              row.add_item('&nbsp')
            else:
              for sl in a.sublevel:
                for x in range(sl.num_req):
                  row.add_item('&nbsp')
          elif ach.done:
            #achievement has been done, fill with X's
            if len(a.sublevel) == 0:
              row.add_item('X', bgcolor="YELLOW")
            else:
              for sl in a.sublevel:
                for tmp in range(sl.num_req):
                  row.add_item('X', bgcolor="YELLOW")
          else:
            # The award must be work in prohgress   
            if len(a.sublevel) == 0:
              # This should never happen
              row.add_item('Problem')
            else:
              for sl in a.sublevel:
                sub_ach = dbobj.achievesubrec(db, memb.scout_id, a.award_id, sl.sub_award_id)
                pr_cols = 0
                if sub_ach.found:
                  # How many cols to put X in
                  pr_cols = len(sub_ach.units)
                  if pr_cols > sl.num_req:
                    pr_cols = sl_num_req # fixes possible DB inconsistencies
                  for i in range(pr_cols):
                    row.add_item('X')
                for i in range(sl.num_req - pr_cols):      
                  row.add_item('&nbsp')

  if extract_choice == 'display':
    table.append_item(' ', new_row = 1)
    table.append_item(webproc.jbutton('Return', 'ou_logic.py?jw_action=ouf_disp&ou_id=%d' %\
        ourec.ou_id), new_row = 1)
    page.data.append(table.pr_table())
    page.output()
    return

  elif extract_choice == 'email-csv':
    user = dbobj.personrec(db, conn.scout_id)
    # Create the mail message
    outer = MIMEMultipart()

    # Mail headers
    outer['Subject'] = 'Wero extract for %s' % ourec.name
    outer['From'] = param.fromaddr
    outer['To'] = user.email
    outer.preamble = 'Wero extract'
    outer.epilogue = ''

    #Add the explanatory text to the message
    textfile = param.template_dir + '/' + param.email_extract_msg
    mf = open(textfile)
    msgfile = MIMEText(mf.read())
    outer.attach(msgfile)

    # Attach the created file to the e-mail.
    msgfile = MIMEText(table.pr_table())
    msgfile.add_header('Content-Disposition', 'attachment', filename='Wero.xls')
    outer.attach(msgfile)

    mailserver = smtplib.SMTP(param.smtpserver)
    #mailserver.set_debuglevel(1)
    mailserver.sendmail(param.fromaddr, user.email, outer.as_string())
    mailserver.quit()

    #outfile = file('/tmp/wero.xls', 'w')
    #outfile.write(table.pr_table())
    #outfile.close()

  ouf_disp(form, db, param, conn, ou_id = nOu)
  return

##############################################################################
def ex_award_row(db, scout, wero, row, colour):
  """Adds details of a wero to a table row.
    If the wero substep has been achieved, displays in appropriate colour"""
  achieve = dbobj.achieverec(db, scout.scout_id, wero.award_id)
  col = ''
  if achieve.done:
    col = colour
  for sl in wero.sublevel:
    ex_sub_award(db, scout, sl, row, col)
  return




##############################################################################
# Mail program logic, decides which form/screen to display
def main():
  form = cgi.FieldStorage()
  param = dbobj.paramrec()
  db = dbobj.dbinstance(param.dbname)
  conn = dbobj.connectrec(db)

  if conn.new_conn:
    oCookie = Cookie.SmartCookie()
    oCookie[conn.ref_id] = conn.auth_key
    oCookie[conn.ref_id]["Max-Age"] = 31536000
    cCookie = oCookie.output()
    app_error(form, param, conn, message = 'Invalid selection')
  else:  
    if form.has_key('jw_action'):
      jw_act = form.getfirst('jw_action', '')
      # if a form action is specified do it
      if jw_act == "awardf_disp":
        awardf_disp(form, db, param, conn)
      elif jw_act == "achievef_add":
        achievef_add(form, db, param, conn)
      elif jw_act == "achievep_add":
        achievep_add(form, db, param, conn)
      elif jw_act == "achievef_present":
        achievef_present(form, db, param, conn)
      elif jw_act == "achievep_present":
        achievep_present(form, db, param, conn)
      elif jw_act == "awardf_adm":
        awardf_adm(form, db, param, conn)
      elif jw_act == "awardf_edit":
        awardf_edit(form, db, param, conn)
      elif jw_act == "awardp_edit":
        awardp_edit(form, db, param, conn)
      elif jw_act == "awardsubp_edit":
        awardsubp_edit(form, db, param, conn)
      elif jw_act == "ouf1_achieve":
        ouf1_achieve(form, db, param, conn)
      elif jw_act == "ouf2_achieve":
        ouf2_achieve(form, db, param, conn)
      elif jw_act == "oup_achieve":
        oup_achieve(form, db, param, conn)
      elif jw_act == "werof_achieve":
        werof_achieve(form, db, param, conn)
      elif jw_act == "werop_achieve":
        werop_achieve(form, db, param, conn)
      elif jw_act == "werop_extract":
        werop_extract(form, db, param, conn)
      elif jw_act == "awardf_extract":
        awardf_extract(form, db, param, conn)
      elif jw_act == "awardp_extract":
        awardp_extract(form, db, param, conn)
      elif jw_act == "awardleadf_disp":
        awardleadf_disp(form, db, param, conn)

      else:
        # Display the home page if you don't know what to do
        app_error(form, param, conn, message = 'Invalid selection - ' + jw_act)
    else:
      # Display the home page if you don't know what to do
      app_error(form, param, conn, message = 'Invalid selection input')
  
  db.commit()
  return

if __name__ == '__main__':
  main()  

