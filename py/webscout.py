#!/usr/bin/python
 
import string
import webproc
from webproc import tag
import dbobj
from procs import *
import syslog
import traceback, sys
import cgi

##############################################################################
def edit_check(db, level_type, level_id, scout_id):
  """Routine to see if editing rights should be enabled for the page """
  edit_ok = 0

  security = dbobj.security(db, scout_id, level_type, level_id)

  if security.superuser:
    return 1

  return security.edit_here

##############################################################################
class scout_page(webproc.page):
  """Class for pages in scout db system"""
  def do_heading(self, param, conn, form = None, help='', ou_id = 0):
    oTable = webproc.table(cellpadding = '2', cellspacing = '0', width = '100%', cols = '3', border = 0)
    # Column 1, the logo 
    oTable.append_item('<img border="0" src="' + param.logo + '">', width='100',\
      rowspan='3')
    # Col 2, the Title
    item = oTable.append_item(tag('H1', param.title), width = '*', rowspan='3',\
      align = 'CENTER')
    if conn.sign_in:
      item.data += tag('SPAN', '<BR> Hello %s' % conn.name, 'class="small_disp" align="LEFT"')
    # Col 3, personal dets
    item = oTable.append_item("", width = '10%', align = "CENTER")
    if conn.scout_id != 0 and conn.sign_in:
      item.data = tag('a', 'Profile', 'href="signin.py?jw_action=profile"')
    else:
      item.data = '&nbsp;'

    # Row 2 (only 3 col, the log out as 1st 2 rows use rowspan
    item = oTable.add_row().add_item(' ', align='CENTER')
    if conn.sign_in and ou_id:
      if conn.home_ou_id != ou_id:
        item.data = tag('A', 'Set as home page', 'href="signin.py?jw_action=set_homep_edit"')

    # Row 3 (only 3 col, the log out as 1st 2 rows use rowspan
    item = oTable.add_row().add_item(' ', align = "CENTER")
    if conn.sign_in:
      item.data = tag('A', 'Sign Out', 'href="signin.py?jw_action=logout_form"')
    else:
      item.data = tag('A', 'Sign In', 'href="signin.py?jw_action=login_form"')

    self.head.append(oTable.pr_table())

    oTable = webproc.table(cellpadding = '3', cellspacing = '0', border = 1)

    # Home tab
    item = oTable.append_item(tag('A', "Home", 'href="scout.py?jw_action=home_page"'))
    #if menu_item == 1:
    #  item.bgcolor = "#FFFF00"
    #  item.data = '<b>' + item.data + '</b>'

    # Browse tab
    item = oTable.append_item(tag('A', "Browse", 'href="scout.py?jw_action=ouf_disp&ou_id=1"'))
    #if menu_item == 2:
    #  item.bgcolor = "#FFFF00"
    #  item.data = '<b>' + item.data + '</b>'

    # Sys maintenance tab
    if conn.superuser:
      item = oTable.append_item(tag('A', "System Maintenance", 'href="office.py?jw_action=sys_admin"'))
      #if menu_item >= 800 and menu_item < 900:
      #  item.bgcolor = "#FFFF00"
      #  item.data = '<b>' + item.data + '</b>'

    if help:
      oTable.append_item(tag('A', "Help", 'href="../%s" target="_blank"' % help))

    self.head.append(oTable.pr_table())
    self.head.append('<BR>')

    if param.testing:
      self.head.append(form_disp(form))
      self.head.append(conn.__str__())
    return

##############################################################################
def jw_header(param, conn, menu_item = 1, cCookie = '', message = '', js=[], help=''):
  print "Content-type: text/html"
  if not cCookie == None:
    print cCookie
  print
  print "<html>"
  print "<head>"
  print tag('title', param.title)
  if string.strip(param.css_file) != '':
    print '<link rel="stylesheet" type="text/css" href="' + string.strip(param.css_file) + '">'
  if len(js) > 0:
    print '<script language="Javascript" type="text/javascript">'
    for j in js:
      try:
        mf = open(j)
        print mf.read()
        print "\n"
      except IOError:
        xx = 1
    print '</script>'
  #print '<link rel="shortcut icon" href=../et.jpg">'
  print "</head>"
  print "<body>"
  oTable = webproc.table(cellpadding = '2', cellspacing = '0', width = '100%', cols = '3',\
    border = 0)
  # Column 1, the logo 
  oTable.add_row().add_item('<img border="0" src="' + param.logo + '">', width='100',\
    rowspan='3')
  # Col 2, the Title
  item = oTable.last_row().add_item(tag('H1', param.title), width = '*', rowspan='3',\
    align = 'CENTER')
  if conn.sign_in:
    item.data += tag('SPAN', '<BR> Hello %s' % conn.name, 'class="small_disp" align="LEFT"')
  # Col 3, personal dets
  item = oTable.last_row().add_item("", width = '10%', align = "CENTER")
  if conn.scout_id != 0 and conn.sign_in:
    item.data = tag('a', 'Profile', 'href="signin.py?jw_action=profile"')
  else:
    item.data = '&nbsp;'

  # Row 2 (only 3 col, the log out as 1st 2 rows use rowspan
  item = oTable.add_row().add_item(' ', align='CENTER')
  if conn.sign_in and menu_item > 900:
    item.data = tag('A', 'Set as home page', 'href="signin.py?jw_action=set_homep_edit"')

  # Row 3 (only 3 col, the log out as 1st 2 rows use rowspan
  item = oTable.add_row().add_item(' ', align = "CENTER")
  if conn.sign_in:
    item.data = tag('A', 'Sign Out', 'href="signin.py?jw_action=logout_form"')
  else:
    item.data = tag('A', 'Sign In', 'href="signin.py?jw_action=login_form"')

  print oTable.pr_table()

  oTable = webproc.table(cellpadding = '3', cellspacing = '0', border = 1)

  # Home tab
  item = oTable.add_row().add_item(tag('A', "Home", 'href="scout.py?jw_action=home_page"'))
  if menu_item == 1:
    item.bgcolor = "#FFFF00"
    item.data = '<b>' + item.data + '</b>'

  # Browse tab
  item = oTable.last_row().add_item(tag('A', "Browse", 'href="scout.py?jw_action=natf_disp"'))
  if menu_item == 2:
    item.bgcolor = "#FFFF00"
    item.data = '<b>' + item.data + '</b>'

  # Sys maintenance tab
  if conn.superuser:
    item = oTable.last_row().add_item(tag('A', "System Maintenance", 'href="office.py?jw_action=sys_admin"'))
    if menu_item >= 800 and menu_item < 900:
      item.bgcolor = "#FFFF00"
      item.data = '<b>' + item.data + '</b>'

  if help:
    oTable.last_row().add_item(tag('A', "Help", 'href="../%s" target="_blank"' % help))

  print oTable.pr_table()

  if message is not None and message != "":
    print tag('center', tag('h4', message + '<br>'))
  print '<BR>'
  #if conn.online_agree:
  #  print 'valid'
  #else:
  #  print 'invalid'
  #import os
  #Oenv = os.environ
  #print Oenv


##############################################################################
def prm_header(menu_item = 1):
  print '<table border="1" cellpadding="3" cellspacing="0">'
  print '<tr>'
  if menu_item == 1:
    tbl_item = '<td bgcolor="#FFFF00"><b>&nbsp;'
  else:
    tbl_item = '<td>&nbsp;'
  print tbl_item + tag('A', 'System parameters', 'href="prmproc.py?jw_action=param_form"') + '&nbsp;</td>'
  if menu_item == 2:
    tbl_item = '<td bgcolor="#FFFF00"><b>&nbsp;'
  else:
    tbl_item = '<td>&nbsp;'
  print tbl_item + tag('A', 'Departments', 'href="prmproc.py?jw_action=dept_list"') + '&nbsp;</td>'
  print '</tr>'
  print '</table>'
  print '<hr>'


##############################################################################
def security_page(form, param, conn, message='', url=''):
  print "Content-type: text/html"
  print
  print "<html>"
  print "<head>"
  print tag('title', param.title)
  if string.strip(param.css_file) != '':
    print '<link rel="stylesheet" type="text/css" href="' + string.strip(param.css_file) + '">'
  if url == '':
    cUrl = 'scout.py?jw_action=home_page'
  else:
    cUrl = url
  print '<META HTTP-EQUIV="REFRESH" CONTENT="5; URL=' + cUrl + '">'
  print "</head>"
  print "<body>"
  oTable = webproc.table()
  oTable.cellpadding = '2'
  oTable.cellspacing = '0'
  oTable.width = '100%'
  oTable.cols = '3'
  oTable.border = 0
  row = webproc.table_row()
  # Column 1, the logo if I get one
  item = webproc.table_item('<img border="0" src="' + param.logo + '">')
  item.width='100'
  item.rowspan='2'
  row.items.append(item)
  # Col 2, the Title
  item = webproc.table_item(tag('H1', param.title))
  item.width = '*'
  item.rowspan='2'
  item.align = 'CENTER'
  row.items.append(item)
  # Col 3, personal dets
  item = webproc.table_item("&nbsp")
  item.width = '10%'
  row.items.append(item)
  oTable.rows.append(row)
  print oTable.pr_table()

  oTable = webproc.table()
  oTable.cellpadding = '3'
  oTable.cellspacing = '0'
  oTable.border = 1
  row = webproc.table_row()

  print tag('H2', 'A security error has occured, you will be redirected in a few moments')

  if message is not None and message != "":
    print tag('center', tag('h2', message + '<br>'))
  print '<BR>'

  print tag('A', 'Click here if not redirected in 5 seconds', 'href=scout.py?jw_action="home_page"')

  webproc.form_footer()
  return


##############################################################################
def app_error(form, param, conn, message='', url=''):
  print "Content-type: text/html"
  print
  print "<html>"
  print "<head>"
  print tag('title', param.title)
  if string.strip(param.css_file) != '':
    print '<link rel="stylesheet" type="text/css" href="' + string.strip(param.css_file) + '">'
  if url == '':
    cUrl = 'scout.py?jw_action=home_page'
  else:
    cUrl = url
  print '<META HTTP-EQUIV="REFRESH" CONTENT="20; URL=' + cUrl + '">'
  print "</head>"
  print "<body>"
  oTable = webproc.table()
  oTable.cellpadding = '2'
  oTable.cellspacing = '0'
  oTable.width = '100%'
  oTable.cols = '3'
  oTable.border = 0
  row = webproc.table_row()
  # Column 1, the logo if I get one
  item = webproc.table_item('<img border="0" src="' + param.logo + '">')
  item.width='100'
  item.rowspan='2'
  row.items.append(item)
  # Col 2, the Title
  item = webproc.table_item(tag('H1', param.title))
  item.width = '*'
  item.rowspan='2'
  item.align = 'CENTER'
  row.items.append(item)
  # Col 3, personal dets
  item = webproc.table_item("&nbsp")
  item.width = '10%'
  row.items.append(item)
  oTable.rows.append(row)
  print oTable.pr_table()

  oTable = webproc.table()
  oTable.cellpadding = '3'
  oTable.cellspacing = '0'
  oTable.border = '1'
  row = webproc.table_row()

  print tag('H2', 'A application error has occured, you will be redirected in a few moments')

  if message is not None and message != "":
    print tag('center', tag('h2', message + '<br>'))
  print '<BR>'

  print tag('A', 'Click here if not redirected in 5 seconds', 'href=scout.py?jw_action="home_page"')

  print form

  webproc.form_footer()
  return

##############################################################################
def sub_scout_dets(scout, ou, param, disp_ou = 0):
  """Creates a table with scout details """
  # This table organises the scouts personal details
  table = intable(param)

  if disp_ou != 0:
    nOu = disp_ou
  else:
    nOu = ou.ou_id

  role = scout.role_by_ou(ou.ou_id)

  # Title
  table.append_item(tag('H3', 'Scout details'), colspan = '2')
  table.append_item(webproc.jbutton('Up to ' + ou.name,\
      "scout.py?jw_action=ouf_disp&ou_id=%d" % nOu, need_form=0))

  # name etc
  table.add_row().add_item(tag('B', '%s %s %s' % (scout.forename, scout.initials, scout.surname)))
  item = table.last_row().add_item('<B>Status: </B>')
  if role.status == 'C':
    item.data += "Current"
  else:
    item.data += "Membership lapsed"
  table.last_row().add_item('&nbsp;')

  disp_line(table, '<B>OU name : </B>%s<B> Section : </B>%s'\
      % (pr_str(ou.name), pr_str(ou.struct_name)))

  return table


##############################################################################
def sub_leader_dets(leader, param):
  """Creates a table with leader details """
  # This table organises the leaders personal details
  table = intable(param)

  # Title
  table.add_row().add_item(tag('H3', 'Leader details'), colspan='2')
  #table.last_row().add_item(webproc.jbutton('Up to ' + unit.name, "scout.py?jw_action=unitf_disp&unit_id=" + str(scout.unit_id), need_form=0)))

  # name etc
  table.add_row().add_item(tag('B', '%s %s %s' % (leader.forename, leader.initials, leader.surname)))

  return table


##############################################################################
def error_proc():
  syslog.openlog('PYTHON prog error')

  type, value, tb = sys.exc_info()
  list = traceback.format_tb(tb)
  output = 'Test '
  for x in list:
    output = output + x
  syslog.syslog(x)
  syslog.closelog()

##############################################################################
def form_disp(form):
  out = 'Form details<BR>'
  keys = form.keys()
  for x in keys:
    if isinstance(form.getvalue(x), list):
      for item in form.getlist(x):
        out += '<B>%s</B>: %s<BR>' % (x, item)
    else:
      out += '<B>%s</B>: %s<BR>' % (x, form.getfirst(x, ''))
  out += 'End of form details'
  return out

##############################################################################
def memb_ch(form):
  memb = []
  keys = form.keys()
  for x in keys:
    if x[0:4] == 'MEMB':
      memb.append(int(x[4:]))
  return memb

##############################################################################
def award_ch(form):
  award = []
  keys = form.keys()
  for x in keys:
    if x[0:5] == 'AWARD':
      award.append(int(x[5:]))
  return award

##############################################################################
def saward_ch(form):
  award = []
  keys = form.keys()
  for x in keys:
    if x[0:6] == 'SAWARD':
      y = x.find('SUB')
      z = int(x[6:y])
      if not z in award:
        award.append(z)
  return award

##############################################################################
def sub_award_ch(form, nAward):
  subaward = []
  root = 'SAWARD%dSUB' % nAward
  keys = form.keys()
  for x in keys:
    if x[0:len(root)] == root:
      z = int(x[len(root):])
      if not z in subaward:
        subaward.append(z)
  return subaward


##############################################################################
class outtable(webproc.table):
  def __init__(self, param):
    "This initialises a table with preset values"
    self.width       ="100%"
    self.cellpadding = param.ot_cellpad
    self.cellspacing = param.ot_cellspc
    self.border	     = param.ot_brdr
    self.align		= ''
    self.background	= ''
    self.bgcolor	= ''
    self.bordercolor	= ''
    self.bordercolordark= ''
    self.bordercolorlight= ''
    self.styleclass	= ''
    self.cols		= ''
    self.id		= ''
    self.frame		= ''
    self.rules		= ''
    self.style		= ''
    self.title		= ''
    self.caption	= ''
    self.rows		=[]
    self.colgroups	=[]
 
    return

##############################################################################
class intable(webproc.table):
  def __init__(self, param):
    "This initialises a table with preset values"
    self.width       ="100%"
    self.cellpadding = param.it_cellpad
    self.cellspacing = param.it_cellspc
    self.border	     = param.it_brdr
    self.align		= ''
    self.background	= ''
    self.bgcolor	= ''
    self.bordercolor	= ''
    self.bordercolordark= ''
    self.bordercolorlight= ''
    self.styleclass	= ''
    self.cols		= ''
    self.id		= ''
    self.frame		= ''
    self.rules		= ''
    self.style		= ''
    self.title		= ''
    self.caption	= ''
    self.rows		=[]
    self.colgroups	=[]
 
    return
