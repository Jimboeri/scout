#!/usr/bin/python2
#
# This module contains code for add/change/delete of
#	Units
#	Groups
#	Districts
#	Areas

import cgi
import cgitb; cgitb.enable()
#import string
#import webproc
#from webscout import *
import dbobj
import Cookie
#from procs import *
import ou
import award 

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
  ou.home_page(form, db, param, conn, oCookie = oCookie)

else:  
  if form.has_key('jw_action'):
    # if a form action is specified do it
    if form.getfirst("jw_action") == "home_page":
      ou.home_page(form, db, param, conn, 'home page selected')
    elif form.getfirst("jw_action") == "ouf_disp":
      ou.ouf_disp(form, db, param, conn)
    elif form.getfirst("jw_action") == "ouf_edit":
      ou.ouf_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "oup_edit":
      ou.oup_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "ouf_add":
      ou.ouf_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "oup_add":
      ou.oup_add(form, db, param, conn)
    elif form.getfirst("jw_action") == "oup_del":
      ou.oup_del(form, db, param, conn)
    elif form.getfirst("jw_action") == "oup_expand":
      ou.oup_expand(form, db, param, conn)
    elif form.getfirst("jw_action") == "oup_view":
      ou.oup_view(form, db, param, conn)
    elif form.getfirst("jw_action") == "oup_all_members":
      ou.oup_all_members(form, db, param, conn)
    elif form.getfirst("jw_action") == "oup_show_act":
      ou.oup_show_act(form, db, param, conn)
    elif form.getfirst("jw_action") == "oup_action":
      if form.has_key('ou_action'):
        ou_act = form.getfirst('ou_action')
        if ou_act == 'Move':
          ou.oup_move(form, db, param, conn)
        if ou_act == 'Wero':
          award.werof_achieve(form, db, param, conn)
        if ou_act == 'Extract Wero info': 
          award.werof_extract(form, db, param, conn)
        if ou_act == 'Collective Awards': 
          award.ouf1_achieve(form, db, param, conn)
 
    else:
      ou.home_page(form, db, param, conn, menu_id=1)
  else:
      # Display the home page if you don't know what to do
    ou.home_page(form, db, param, conn, menu_id=1)

db.database.commit()
db.database.close() 

