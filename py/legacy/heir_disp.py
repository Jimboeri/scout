#!/usr/bin/python2

import cgi
import os
import cgitb; cgitb.enable()
#import pg
import string
import webproc
from webscout import *
import dbobj
#import Cookie
from procs import *
import time
import ou
#from scout import scoutf_disp
 

##############################################################################
def home_page(form, db, param, conn, menu_id = 1, ocookie = None, msg = ''):
  """Displays the home page for the user """
  
  if conn.home_ou_id == 0 or conn.home_ou_id is None:
    if conn.last_ou_id == 0 or conn.last_ou_id is None:
      nOu = 1
    else:
      nOu = conn.last_ou_id
  else:
    nOu = conn.home_ou_id

  if conn.new_conn and ocookie is not None:
    ou.ouf_disp(form, db, param, conn, ocookie = ocookie, ou_id = nOu)
  else:
    ou.ouf_disp(form, db, param, conn, ou_id = nOu)

  return

###############################################################################
def onl_agreef_disp(form, db, param, conn, message = ''):
  """Displays form requesting online agreescout level of the browse tree. Displays scout details"""
  jw_header(param, conn, menu_item=2)

  webproc.form_footer()

##############################################################################
def can_email(db, unit, group, conn):
  """Procedure to determine if a connection can send email to a unit"""

  #First check roles in this group
  rlist = unit.role_list()
  for rl in rlist:
    if rl.scout_id == conn.scout_id:
      return 1
      break

  # Check roles at the group level
  rlist = group.role_list()
  for rl in rlist:
    if rl.scout_id == conn.scout_id:
      return 1
      break

  # OK now get all units in the group
  ulist = group.unit_list()
  for ul in ulist:
    if ul.unit_id == unit.unit_id:
      # we've already checked this unit
      continue
  
    rlist = ul.role_list()
    for rl in rlist:
      if rl.scout_id == conn.scout_id:
        return 1
        break

  # If we get this far, we haven't found it
  return 0

###############################################################################
def natf_disp(form, db, param, conn, message = '', cCookie = ''):
  """Top level of the browse tree. Displays national details and list of areas defined. """

  menu_itm = 996
  #check if this is the users home page
  if conn.home_level == 'N':
    menu_itm = 1

  conn.last_level = 'N'
  conn.last_level_id = 1
  conn.update()

  nat = dbobj.nationalrec(db)

  can_edit = edit_check(db, 'N', 1, conn.scout_id)

  jw_header(param, conn, menu_item=menu_itm, cCookie = cCookie)
  if message != '':
    print webproc.tag('H2', message)

  #define outer table, hold district details at the op, groups on the left, & adult roles on the right
  outtable = webproc.table(width='100%', cellpadding = param.ot_cellpad, cellspacing = param.ot_cellspc, border = param.ot_brdr)

  # top row for National details
  outrow = webproc.table_row()
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', nat.name))
  row.items.append(item)
  table.rows.append(row)
  if conn.superuser:
    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('A', 'Edit national details', 'href=heir_acd.py?jw_action=natf_edit'), align="RIGHT", colspan = "2")
    row.items.append(item)
    table.rows.append(row)


  outitem = webproc.table_item(table.pr_table(), colspan = '2')
  outrow.items.append(outitem)
  outtable.rows.append(outrow)

  # Next outer table row has area details and adult roles
  outrow = webproc.table_row()
  # Table for areas of this nation
  table = webproc.table(cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, width='100%', border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'AREAS'))
  row.items.append(item)

  if conn.superuser:
    item = webproc.table_item(webproc.tag('A', 'Add new Area', 'href=heir_acd.py?jw_action=areaf_add'), align = 'RIGHT')
    row.items.append(item)
  table.rows.append(row)

  nat.area_list()
  for a in nat.arealist:
    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('A', a.name, 'href=scout.py?jw_action=areaf_disp&area_id=' + str(a.area_id)))
    row.items.append(item)
    if conn.superuser and a.curr_memb == 0:
      item = webproc.table_item(webproc.tag('A', 'Del', 'href=heir_acd.py?jw_action=areap_del&area_id=' + str(a.area_id) + ' class=small_disp'))
      item.align = 'RIGHT'
      row.items.append(item)

    table.rows.append(row)


  # Output the list of areas
  outitem = webproc.table_item(table.pr_table())
  outrow.items.append(outitem)

  # Role information
  table = webproc.table(cellpadding = '0', cellspacing = '0', width='100%', border = '0')
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'Adult roles'))
  row.items.append(item)
  if can_edit:
    item = webproc.table_item(webproc.tag('A', 'Add new', 'href=office.py?jw_action=rolef_add1&type=N&type_id=1'), align='RIGHT')
    row.items.append(item)

  table.rows.append(row)
  nat.role_list()
  for r in nat.rolelist:
    row = webproc.table_row()
    name = r.forename + ' '
    if r.initials != '':
      name += r.initials + ' '
    name += r.surname
    if can_edit:
      name = webproc.tag('A', name, 'href=office.py?jw_action=rolef_add2&type=N&type_id=1&scout_id=' + str(r.scout_id))
    item = webproc.table_item(name)
    row.items.append(item)
    item = webproc.table_item(r.title)
    row.items.append(item)
    if can_edit:
      item = webproc.table_item(webproc.tag('A', 'Del', 'href=office.py?jw_action=rolep_del&type=N&type_id=1&scout_id=' + str(r.scout_id) + ' class=small_disp'))
      row.items.append(item)
    table.rows.append(row)

  # Print the roles info
  outitem = webproc.table_item(table.pr_table(), valign='top')
  outrow.items.append(outitem)
  outtable.rows.append(outrow)

  # Display the details
  print outtable.pr_table()
  webproc.form_footer()
  return



###############################################################################
def areaf_disp(form, db, param, conn, message = '', inp_area = 0):
  """Area level of the browse tree. Displays area details and list of districts defined. """

  nArea = int(form.getfirst('area_id', str(inp_area)))

  menu_itm = 995
  nCurr_memb = 0
  # If not form Area id, take the last one from the connection rec
  if nArea == 0:
    # Take it from the home id rather than last id if possible
    if conn.home_level == 'A' and conn.home_id != 0:
      nArea = conn.home_id
      menu_itm = 1
    else:
      nArea = conn.last_level_id
  else:
    #check if this is the users home page
    if conn.home_level == 'A' and conn.home_id == nArea:
      menu_itm = 1
 
  area = dbobj.arearec(db, nArea)
  if not area.found:
    # go to top of browse tree
    natf_disp(form, db, param, conn)
    return 

  conn.last_level = 'A'
  conn.last_level_id = area.area_id
  conn.update()

  can_edit = edit_check(db, 'A', area.area_id, conn.scout_id)

  jw_header(param, conn, menu_item=menu_itm)
  if message != '':
    print webproc.tag('H2', message)

  #define outer table, hold district details at the op, groups on the left, & adult roles on the right
  outtable = webproc.table(width='100%', cellpadding = param.ot_cellpad, cellspacing = param.ot_cellspc, border = param.ot_brdr)

  # top row if for Area details
  outrow = webproc.table_row()
  table = webproc.table(width='100%', cellspacing = param.it_cellspc, border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', area.name + ' area'))
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Up to national level', "href=scout.py?jw_action=natf_disp"), align = 'right')
  row.items.append(item)
  table.rows.append(row)

  if conn.superuser:
    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('A', 'Edit area details', 'href=heir_acd.py?jw_action=areaf_edit&area_id=' + str(area.area_id)), align="RIGHT", colspan = "2")
    row.items.append(item)
    table.rows.append(row)


  outitem = webproc.table_item(table.pr_table(), colspan = '2')
  outrow.items.append(outitem)
  outtable.rows.append(outrow)

  # Next outer table row has unit details and adult roles
  outrow = webproc.table_row()
  # Table for districts of this area
  table = webproc.table(cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, width='100%', border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'DISTRICTS in this AREA'))
  row.items.append(item)

  if conn.superuser:
    item = webproc.table_item(webproc.tag('A', 'Add new District', 'href=heir_acd.py?jw_action=distf_add&area_id=' + str(area.area_id)), align = 'RIGHT')
    row.items.append(item)

  table.rows.append(row)

  area.district_list()
  for d in area.districtlist:
    nCurr_memb += 1
    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('A', d.name, 'href=scout.py?jw_action=distf_disp&dist_id=' + str(d.dist_id)))
    row.items.append(item)
    table.rows.append(row)
    if conn.superuser and d.curr_memb == 0:
      item = webproc.table_item(webproc.tag('A', 'Del', 'href=heir_acd.py?jw_action=distp_del&dist_id=' + str(d.dist_id) + ' class=small_disp'))
      item.align = 'RIGHT'
      row.items.append(item)

  # Output the list of districts
  outitem = webproc.table_item(table.pr_table())
  outrow.items.append(outitem)

  # Role information
  table = webproc.table(cellpadding = '0', cellspacing = '0', width='100%', border = '0')
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'Adult roles'))
  row.items.append(item)
  if can_edit:
    item = webproc.table_item(webproc.tag('A', 'Add new', 'href=office.py?jw_action=rolef_add1&type=A&type_id=' + str(area.area_id)), align='RIGHT')
    row.items.append(item)

  table.rows.append(row)
  area.role_list()
  for r in area.rolelist:
    nCurr_memb += 1
    row = webproc.table_row()
    name = r.forename + ' '
    if r.initials != '':
      name += r.initials + ' '
    name += r.surname
    if can_edit:
      name = webproc.tag('A', name, 'href=office.py?jw_action=rolef_add2&type=A&type_id=' + str(area.area_id) + '&scout_id=' + str(r.scout_id))
    item = webproc.table_item(name)
    row.items.append(item)
    item = webproc.table_item(r.title)
    row.items.append(item)
    if can_edit:
      item = webproc.table_item(webproc.tag('A', 'Del', 'href=office.py?jw_action=rolep_del&type=A&type_id=' + str(area.area_id) + '&scout_id=' + str(r.scout_id) + ' class=small_disp'))
      row.items.append(item)
    table.rows.append(row)

  # Print the roles info
  outitem = webproc.table_item(table.pr_table(), valign='top')
  outrow.items.append(outitem)
  outtable.rows.append(outrow)

  # Display the details
  print outtable.pr_table()
  webproc.form_footer()

  if nCurr_memb != area.curr_memb:
    area.curr_memb = nCurr_memb
    area.update()

  return


###############################################################################
def distf_disp(form, db, param, conn, message = '', inp_dist = 0):
  """District level of the browse tree. Displays district details and list of groups defined. """

  nDist = int(form.getfirst('dist_id', inp_dist))

  menu_itm = 994
  nCurr_memb = 0
  # If not form District id, take the last one from the connection rec
  if nDist == 0:
    # Take it from the home id rather than last id if possible
    if conn.home_level == 'D' and conn.home_id != 0:
      nDist = conn.home_id
      menu_itm = 1
    else:
      nDist = conn.last_level_id
  else:
    #check if this is the users home page
    if conn.home_level == 'D' and conn.home_id == nDist:
      menu_itm = 1

  dist = dbobj.districtrec(db, nDist)
  if not dist.found:
    # go to top of browse tree
    natf_disp(form, db, param, conn)
    return 

  area = dbobj.arearec(db, dist.area_id)
  if not area.found:
    # go to top of browse tree
    natf_disp(form, db, param, conn)
    return 

  conn.last_level = 'D'
  conn.last_level_id = dist.dist_id
  conn.update()

  can_edit = edit_check(db, 'D', dist.dist_id, conn.scout_id)

  jw_header(param, conn, menu_item=menu_itm)
  if message != '':
    print webproc.tag('H2', message)

  #define outer table, hold district details at the op, groups on the left, & adult roles on the right
  outtable = webproc.table(width='100%', cellpadding = param.ot_cellpad, cellspacing = param.ot_cellspc, border = param.ot_brdr)

  # top row if for District details
  outrow = webproc.table_row()
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', dist.name + ' district'))
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Up to area - ' + area.name, "href=scout.py?jw_action=areaf_disp&area_id=" + str(dist.area_id)), align = 'right')
  row.items.append(item)
  table.rows.append(row)

  if conn.superuser:
    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('A', 'Edit district details', 'href=heir_acd.py?jw_action=distf_edit&dist_id=' + str(dist.dist_id)), align="RIGHT", colspan = "2")
    row.items.append(item)
    table.rows.append(row)


  outitem = webproc.table_item(table.pr_table(), colspan = '2')
  outrow.items.append(outitem)
  outtable.rows.append(outrow)

  # Next outer table row has unit details and adult roles
  outrow = webproc.table_row()
  # Table for units of this group
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'GROUPS in this DISTRICT'))
  row.items.append(item)

  if can_edit:
    item = webproc.table_item(webproc.tag('A', 'Add new Group', 'href=heir_acd.py?jw_action=groupf_add&dist_id=' + str(dist.dist_id)), align = 'RIGHT')
    row.items.append(item)
  table.rows.append(row)

  dist.group_list()

  for g in dist.grouplist:
    nCurr_memb += 1
    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('A', g.name, 'href=scout.py?jw_action=groupf_disp&group_id=' + str(g.group_id)))
    row.items.append(item)
    table.rows.append(row)
    if conn.superuser and g.curr_memb == 0:
      item = webproc.table_item(webproc.tag('A', 'Del', 'href=heir_acd.py?jw_action=groupp_del&group_id=' + str(g.group_id) + ' class=small_disp'))
      item.align = 'RIGHT'
      row.items.append(item)


  # Output the list of groups
  outitem = webproc.table_item(table.pr_table())
  outrow.items.append(outitem)

  # Role information
  table = webproc.table(cellpadding = '0', cellspacing = '0', width='100%', border = '0')
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'Adult roles'))
  row.items.append(item)
  if can_edit:
    item = webproc.table_item(webproc.tag('A', 'Add new', 'href=office.py?jw_action=rolef_add1&type=D&type_id=' + str(dist.dist_id)), align='RIGHT')
    row.items.append(item)
  table.rows.append(row)
  dist.role_list()
  for r in dist.rolelist:
    nCurr_memb += 1
    row = webproc.table_row()
    name = r.forename + ' '
    if r.initials != '':
      name += r.initials + ' '
    name += r.surname
    if can_edit:
      name = webproc.tag('A', name, 'href=office.py?jw_action=rolef_add2&type=D&type_id=' + str(dist.dist_id) + '&scout_id=' + str(r.scout_id))
    item = webproc.table_item(name)
    row.items.append(item)
    item = webproc.table_item(r.title)
    row.items.append(item)
    if can_edit:
      item = webproc.table_item(webproc.tag('A', 'Del', 'href=office.py?jw_action=rolep_del&type=D&type_id=' + str(dist.dist_id) + '&scout_id=' + str(r.scout_id) + ' class=small_disp'))
      row.items.append(item)
    table.rows.append(row)

  # Print the roles info
  outitem = webproc.table_item(table.pr_table(), valign='top')
  outrow.items.append(outitem)
  outtable.rows.append(outrow)


  # Display the details
  print outtable.pr_table()
  webproc.form_footer()

  if nCurr_memb != dist.curr_memb:
    dist.curr_memb = nCurr_memb
    dist.update()

  return


###############################################################################
def groupf_disp(form, db, param, conn, message = '', inp_group = 0):
  """Group level of the browse tree. Displays group details and list of units defined. """

  nGroup = int(form.getfirst('group_id', inp_group))
  menu_itm = 993
  nCurr_memb = 0
  # If not form group id, take the last one from the connection rec
  if nGroup == 0:
    # Take it from the home id rather than last id if possible
    if conn.home_level == 'G' and conn.home_id != 0:
      nGroup = conn.home_id
      menu_itm = 1
    else:
      nGroup = conn.last_level_id
  else:
    #check if this is the users home page
    if conn.home_id == nGroup and conn.home_level == 'G':
      menu_itm = 1

  group = dbobj.grouprec(db, nGroup)
  if not group.found:
    # go to top of browse tree
    natf_disp(form, db, param, conn)
    return 

  dist = dbobj.districtrec(db, group.dist_id)
  if not dist.found:
    # go to top of browse tree
    natf_disp(form, db, param, conn)
    return 

  conn.last_level = 'G'
  conn.last_level_id = group.group_id
  conn.update()

  can_edit = edit_check(db, 'G', group.group_id, conn.scout_id)

  jw_header(param, conn, menu_item=menu_itm)
  if message != '':
    print webproc.tag('H2', message)

  #define outer table, hold group details at the op, units on the left, & adult roles on the right
  outtable = webproc.table(width='100%', cellpadding = param.ot_cellpad, cellspacing = param.ot_cellspc, border = param.ot_brdr)

  # top row if for Unit details
  outrow = webproc.table_row()
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H2', group.name + ' group'), colspan='2')
  row.items.append(item)
  item = webproc.table_item(webproc.tag('A', 'Up to district - ' + dist.name, "href=scout.py?jw_action=distf_disp&dist_id=" + str(group.dist_id)), align = 'right')
  row.items.append(item)
  table.rows.append(row)

  row = webproc.table_row()
  item = webproc.table_item('<B>Address :</B>', valign='top')
  if group.addr1 is not None and group.addr1 != '':
    item.data += '<BR>' + pr_str(group.addr1)
  if group.addr2 is not None and group.addr2 != '':
    item.data += '<BR>' + pr_str(group.addr2)
  if group.addr3 is not None and group.addr3 != '':
    item.data += '<BR>' + pr_str(group.addr3)
  if group.p_code is not None and group.p_code != '':
    item.data += ' ' + pr_str(group.p_code)
  row.items.append(item)
  item = webproc.table_item('<B>Phone :</B>' + pr_str(group.telephone), valign='TOP')
  row.items.append(item)

  if conn.superuser:
    item = webproc.table_item(webproc.tag('A', 'Edit group details', 'href=heir_acd.py?jw_action=groupf_edit&group_id=' + str(group.group_id)), align="RIGHT")
    row.items.append(item)
  table.rows.append(row)

  outitem = webproc.table_item(table.pr_table(), colspan = '2')
  outrow.items.append(outitem)
  outtable.rows.append(outrow)

  # Next outer table row has unit details and adult roles
  outrow = webproc.table_row()
  # Table for units of this group
  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'UNITS in this GROUP'))
  row.items.append(item)

  if can_edit:
    item = webproc.table_item(webproc.tag('A', 'Add new unit', 'href=heir_acd.py?jw_action=unitf_add&group_id=' + str(group.group_id)), align = 'RIGHT')
    row.items.append(item)
  table.rows.append(row)

  group.unit_list()
  for u in group.unitlist:
    nCurr_memb += 1
    row = webproc.table_row()
    item = webproc.table_item(webproc.tag('A', u.name, 'href=scout.py?jw_action=unitf_disp&unit_id=' + str(u.unit_id)))
    row.items.append(item)

    if conn.superuser and u.curr_memb == 0:
      item = webproc.table_item(webproc.tag('A', 'Del', 'href=heir_acd.py?jw_action=unitp_del&unit_id=' + str(u.unit_id) + ' class=small_disp'))
      item.align = 'RIGHT'
      row.items.append(item)

    table.rows.append(row)
  # Output the list of units
  outitem = webproc.table_item(table.pr_table())
  outrow.items.append(outitem)

  # Role information
  table = webproc.table(cellpadding = '0', cellspacing = '0', width='100%', border = '0')
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('H3', 'Adult roles'))
  row.items.append(item)
  if can_edit:
    item = webproc.table_item(webproc.tag('A', 'Add new', 'href=office.py?jw_action=rolef_add1&type=G&type_id=' + str(group.group_id)), align='RIGHT')
    row.items.append(item)
  table.rows.append(row)
  group.role_list()
  for r in group.rolelist:
    nCurr_memb += 1
    row = webproc.table_row()
    name = r.forename + ' '
    if r.initials != '':
      name += r.initials + ' '
    name += r.surname
    if can_edit:
      name = webproc.tag('A', name, 'href=office.py?jw_action=rolef_add2&type=G&type_id=' + str(group.group_id) + '&scout_id=' + str(r.scout_id))
    item = webproc.table_item(name)
    row.items.append(item)
    item = webproc.table_item(r.title)
    row.items.append(item)
    if can_edit:
      item = webproc.table_item(webproc.tag('A', 'Del', 'href=office.py?jw_action=rolep_del&type=G&type_id=' + str(group.group_id) + '&scout_id=' + str(r.scout_id) + ' class=small_disp'))
      row.items.append(item)
    table.rows.append(row)

  # Print the roles info
  outitem = webproc.table_item(table.pr_table(), valign='top')
  outrow.items.append(outitem)
  outtable.rows.append(outrow)

  # Display the details
  print outtable.pr_table()
  webproc.form_footer()

  if nCurr_memb != group.curr_memb:
    group.curr_memb = nCurr_memb
    group.update()

  return

###############################################################################
def unitf_disp(form, db, param, conn, message = '', inp_unit = 0):
  """Unit level of the browse tree. Displays unit details and list of scouts defined. """
  nUnit = int(form.getfirst('unit_id', inp_unit))
  # Counter for current members, scouts and role members
  nCurr_memb = 0

  menu_itm = 992
  # If not form unit id, take the last one from the connection rec
  if nUnit == 0:
    # Take it from the home id rather than last id if possible
    if conn.home_level == 'U' and conn.home_id != 0:
      nUnit = conn.home_id
      menu_itm = 1
    else:
      nUnit = conn.last_level_id
  else:
    #check if this is the users home page
    if conn.home_id == nUnit and conn.home_level == 'U':
      menu_itm = 1

  unit = dbobj.unitrec(db, nUnit)
  if not unit.found:
    # go to top of browse tree
    app_error(form, param, conn, message = 'Invalid unit id')
    return 

  group = dbobj.grouprec(db, unit.group_id)

  conn.last_level = 'U'
  conn.last_level_id = unit.unit_id
  conn.update()

  security = dbobj.security(db, conn.scout_id, 'U', unit.unit_id)

  # Define any input parameters
  cStatus = form.getfirst('disp_status', 'C')

  jw_header(param, conn, menu_item=menu_itm)
  if message != '':
    print webproc.tag('H2', message)


  #define outer table, hold unit details at the top, members on the left, & adult roles on the right
  outtable = webproc.table(width='100%', cellpadding = param.ot_cellpad, cellspacing = param.ot_cellspc, border = param.ot_brdr)

  # top row if for Unit details

  table = webproc.table(width='100%', cellpadding = param.it_cellpad, cellspacing = param.it_cellspc, border = param.it_brdr)
  table.add_row().add_item(webproc.tag('H2', unit.name))
  table.last_row().add_item('Group: ' + group.name, align='CENTRE')
  item = table.last_row().add_item(webproc.jbutton('Up to group - ' + group.name,\
    "scout.py?jw_action=groupf_disp&group_id=" + str(unit.group_id), need_form=1), align = 'right')
  if security.edit_unit:
    item.data += '&nbsp' + webproc.jbutton('Collective awards', 'award.py?jw_action=unitf1_achieve&unit_id=%d' % unit.unit_id)
  
  table.add_row().add_item('<B>Meeting time :</B> ' + pr_str(unit.meet_time))
  table.last_row().add_item('Section: ' + unit.sect_name, align='CENTRE')
  item = table.last_row().add_item('', align='RIGHT')
  if security.edit_unit:
    item.data = webproc.jbutton('Extract member details', 'office.py?jw_action=extractf_unit&unit_id=%d' % unit.unit_id, need_form=0)
  if can_email(db, unit, group, conn):
    item.data += '&nbsp&nbsp&nbsp' + webproc.jbutton('Email unit', 'office.py?jw_action=emailf_unit&unit_id=%d' % unit.unit_id, need_form=0)
    if conn.superuser:
      item.data += '&nbsp&nbsp&nbsp' + webproc.jbutton('Edit unit details', 'heir_acd.py?jw_action=unitf_edit&unit_id=%d' % unit.unit_id, need_form=0)

  outtable.add_row().add_item(table.pr_table(), colspan = '2')

  # Scout unit members display
  unit.scout_list()

  table = webproc.table(cellpadding = '0', cellspacing = '0', width='100%', border = '0')

  # top row if for Unit details

  if cStatus == 'C':
    table.add_row().add_item(webproc.tag('H3', 'UNIT Members (current)'))
    table.last_row().add_item(webproc.tag('DIV', webproc.jbutton('(Display all including inactive)',\
      'scout.py?jw_action=unitf_disp&disp_status=A&unit_id=%d' % unit.unit_id, need_form=0),\
      'ALIGN="RIGHT"'))
  else:
    table.add_row().add_item(webproc.tag('H3', 'UNIT Members (including inactive)'))
    table.last_row().add_item( webproc.tag('DIV', webproc.jbutton('(Display current only)',\
      'scout.py?jw_action=unitf_disp&disp_status=C&unit_id=%d' % unit.unit_id, need_form = 0),\
      'ALIGN="RIGHT"'))

  if security.edit_unit:
    table.last_row().add_item(webproc.jbutton('Add new member', 'scout.py?jw_action=scoutf_add&unit_id=%d'\
      % unit.unit_id, need_form=0), align = 'RIGHT')

  for s in unit.scoutlist:
    table.add_row().add_item(webproc.tag('A', string.strip(s.forename) + ' ' + string.strip(s.surname),\
      'href=scout.py?jw_action=scoutf_disp&scout_id=%d' % s.scout_id), colspan = '2')
    item = table.last_row().add_item('%d years & %d months' % (s.years, s.months), align = 'right')
    if s.age > unit.end_age:
      item.styleclass = 'error'
    nCurr_memb += 1

  if cStatus == 'A':
    table.add_row().add_item(webproc.tag('H4', 'Inactive'))
    group = dbobj.grouprec(db, unit.group_id)
    grscouts = group.all_scout_list()
    for s in grscouts:
      if s.status == 'L':
        if (s.age + 0.5) > unit.start_age and (s.age - 0.5) < unit.end_age:
          table.add_row().add_item(webproc.tag('A', string.strip(s.forename) + ' ' + string.strip(s.surname),\
            'href=scout.py?jw_action=scoutf_disp&scout_id=' + str(s.scout_id)))
          table.last_row().add_item(webproc.tag('A', 'Renew membership',\
            'href=scout.py?jw_action=scoutf_renew&scout_id=%d&unit_id=%d' % (s.scout_id, unit.unit_id)))
          item = table.last_row().add_item('%d years & %d months' % (s.years, s.months), align = 'right')

  outtable.add_row().add_item(table.pr_table())

  # Placeholder for role information
  table = webproc.table(cellpadding = '0', cellspacing = '0', width='100%', border = '0')
  table.add_row().add_item(webproc.tag('H3', 'Adult roles'))
  if security.edit_unit:
    table.last_row().add_item(webproc.jbutton('Add new', 'office.py?jw_action=rolef_add1&type=U&type_id=%d'\
      % unit.unit_id, need_form=0), align='RIGHT')
  unit.role_list()
  for r in unit.rolelist:
    name = r.forename + ' '
    if r.initials != '':
      name += r.initials + ' '
    name += r.surname
    if security.edit_unit:
      name = webproc.tag('A', name, 'href=office.py?jw_action=rolef_add2&type=U&type_id=' + str(unit.unit_id) + '&scout_id=' + str(r.scout_id))
    table.add_row().add_item(name)
    table.last_row().add_item(r.title)
    if security.edit_unit:
      table.last_row().add_item(webproc.tag('A', 'Del', 'href=office.py?jw_action=rolep_del&type=U&type_id=' + str(unit.unit_id) + '&scout_id=' + str(r.scout_id) + ' class=small_disp'))
    nCurr_memb += 1


  # Print the roles table
  outitem = outtable.last_row().add_item(table.pr_table())
  outitem.valign = 'TOP'

  # Now print the table
  print outtable.pr_table()

  webproc.form_footer()

  if nCurr_memb != unit.curr_memb:
    unit.curr_memb = nCurr_memb
    unit.update()



