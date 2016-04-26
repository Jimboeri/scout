#!/usr/bin/python2

"""This is a stand alone module that contains only the function login_proc()
"""

import os
import string
import webproc
from webscout import *
import dbobj
import time
from award import achievef_present, awardf_disp
from signinproc import login_form, olf_agree
from ou import home_page
 

##############################################################################
def login_proc(form, db, param, conn):
  """Processes the login form.
The module requires the username (li_name) and password (li_password) to be passed from the form.
Errors returned if:
  li_name not present
  user name not found in DB
  password invalid
If the user has not agreed to the online agreement, it is presented for acceptance (olf_agree() in signinproc.py)
The connection record is updated
Control passed to the following procedures based on 'next_proc' parameter:
	achievef_present()
	awardf_disp()
  else
        home_page()
"""

  if not form.has_key("li_name"):
    login_form(form, db, param, conn, "User not entered")
    return

  #if not form.has_key("li_password"):
  #  login_form(form, db, param, conn, "Password not entered")
  #  return
  
  # get login name & pw from the form
  cOn_line_id = form.getfirst("li_name", '')
  cPassword = form.getfirst('li_password', '')  

  # See if the user exists
  # Initialise object
  oScout = dbobj.scoutrec(db, 0)

  # search for on_line_id
  nScout_id = oScout.find_on_line_id(cOn_line_id)
  if nScout_id == 0:
    login_form(form, db, param, conn, "User not entered")
    return

  oScout = dbobj.adultrec(db, nScout_id)
  
  # Check password
  if not oScout.check_pw(cPassword):
    login_form(form, db, param, conn, "Password invalid")
    return

  if oScout.online_agree_dt == '' or oScout.online_agree_dt is None:
    olf_agree(form, db, param, conn, str(oScout.scout_id), cPassword)
    return

  conn.scout_id = nScout_id
  conn.update()

  if form.getfirst('next_proc', '') == 'achievef_present':
    achievef_present(form, db, param, conn)
  elif form.getfirst('next_proc', '') == 'awardf_disp':
    awardf_disp(form, db, param, conn)
  else:
    home_page(form, db, param, conn, menu_id=1)

  return


