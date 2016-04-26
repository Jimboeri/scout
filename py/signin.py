#!/usr/bin/python2

import cgi
import cgitb; cgitb.enable()
import dbobj
from signinproc import *
#from login_proc import *
 
##############################################################################
# Main program logic, decides which form/screen to display

form = cgi.FieldStorage()
param = dbobj.paramrec()
db = dbobj.dbinstance(param.dbname)
conn = dbobj.connectrec(db)

if conn.new_conn:
  #oCookie = Cookie.SmartCookie()
  #oCookie[conn.ref_id] = conn.auth_key
  #oCookie[conn.ref_id]["Max-Age"] = 31536000
  #cCookie = oCookie.output()
  app_error(form, param, conn, message = 'Invalid selection')
else:  
  if form.has_key('jw_action'):
    # if a form action is specified do it
    if form.getfirst("jw_action") == "profile":
      profile(form, db, param, conn)
    elif form.getfirst("jw_action") == "passwdf_edit":
      passwdf_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "passwdp_edit":
      passwdp_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "set_homef_edit":
      set_homef_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "set_homep_edit":
      set_homep_edit(form, db, param, conn)
    elif form.getfirst("jw_action") == "logout_form":
      logout_form(form, db, param, conn)
    elif form.getfirst("jw_action") == "login_form":
      login_form(form, db, param, conn)
    elif form.getfirst("jw_action") == "login_proc":
      login_proc(form, db, param, conn)
    elif form.getfirst("jw_action") == "pwhint_f1":
      pwhint_f1(form, db, param, conn)
    elif form.getfirst("jw_action") == "pwhint_p1":
      pwhint_p1(form, db, param, conn)
    elif form.getfirst("jw_action") == "pwhint_p2":
      pwhint_p2(form, db, param, conn)
    elif form.getfirst("jw_action") == "olp_agree":
      olp_agree(form, db, param, conn)

    else:
      # Display the home page if you don't know what to do
      app_error(form, param, conn, message = 'Invalid selection')
  else:
    # Display the home page if you don't know what to do
    app_error(form, param, conn, message = 'Invalid selection input')
  
db.commit()

