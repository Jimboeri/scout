#!/usr/bin/python
 
import string
import random
import webproc
# Would have liked to use it, but only avail in 2.3
#import datetime
import time

##############################################################################
def rand_string(nSize=20):
  """Returns a string of random characters that is nSize long"""
  cString = ''
  while len(cString) < nSize:
    cString = cString + str(random.randint(1,9))
  return cString

##############################################################################
def char_int(inp_char):
  """Returns an integer relating to character value. If an error returns 0"""
  try:
    nInt = int(inp_char)
  except:
    nInt = 0
  return nInt

##############################################################################
def char_float(inp_char):
  """Returns a floating number relating to charachter input. If an error, returns 0"""
  try:
    nFloat = float(inp_char)
  except:
    nFloat = 0.0
  return nFloat

##############################################################################
def pr_str(inp_string):
  """Always returns a printable string, even if input is None"""
  if inp_string is None:
    return ''
  else:
    return str(inp_string)

##############################################################################
def all_int(cInp):
  """Always returns an integer, returns 0 if none """
  nRet = 0
  if cInp is not None:
    try:
      nRet = int(cInp)
    except:
      nRet = 0
  return nRet

##############################################################################
def val_date(cInp_dt):
  """Character date validation routine """

  # No imput
  if cInp_dt is None:
    return 0

  lDate = string.split(cInp_dt, '-')

  if len(lDate) != 3:
    return 0

  for i in lDate:
    if not i.isdigit():
      return 0

  try:
    dt = time.strptime(cInp_dt, '%Y-%m-%d')
  except:
    return 0

  return 1

##############################################################################
def edit_row(table, descr, fld_name , fld_value, is_valid = 1, validation_msg = '', req = 0, size = 0, maxlen = 0):
  """Creates a table row that will display a field in an edit form
Parameters
  table - a webproc.table() instance
  descr - The description to be displayed
  fld_name - The field name to be used for the <INPUT> file
  fld_value - The initial value of the field
  is_valid (1) - is set is valid, otherwise the validation message is displayed
  req (0) - If set to 1, displays an asterisk to indicate the field is required
  size (0) - If set will be used to define the display size of the field
  maxlen (0) _ If set used to define the maxlen of the <INPUT? field
 """
  row = webproc.table_row()
  item = webproc.table_item(webproc.tag('SPAN', descr, 'CLASS="field_descr"'))
  if not is_valid:
    item.data += '<BR><SPAN CLASS="validation_message">' + validation_msg + '</SPAN>'
    item.styleclass = 'error'
  row.items.append(item)
  item = webproc.table_item('<INPUT TYPE="TEXT" NAME="' + fld_name + '" VALUE ="' + pr_str(fld_value) + '"')
  if size > 0:
    item.data += ' SIZE="' + str(size) + '"'
  if maxlen > 0:
    item.data += ' MAXLENGTH="' + str(maxlen) + '"'
  item.data += '>'

  if req:
    item.data += '&nbsp;*'
  row.items.append(item)
  table.rows.append(row)
  return

##############################################################################
def edit_comment(table, descr, fld_name , fld_value, rows=5, cols=80, colspan=2):
  """Creates a table row that will display a textarea box in an edit form """
  cColSpan = repr(colspan)
  cLine = webproc.tag('SPAN', descr, 'CLASS="field_descr"') + '<BR>'
  cLine += '<TEXTAREA name="' + fld_name + '" ROWS="' + str(rows) + '" COLS="' + str(cols) + '">' + pr_str(fld_value) + '</TEXTAREA>' 
  table.add_row().add_item(cLine, colspan=cColSpan)
  return

##############################################################################
def disp_line(table, value1 = '', value2 = '', value3 = ''):
  """Displays values in a table"""
  row = webproc.table_row()
  item = webproc.table_item(value1)
  row.items.append(item)
  if value2 != '':
    item = webproc.table_item(value2)
    row.items.append(item)
    if value3 != '':
      item = webproc.table_item(value3)
      row.items.append(item)
  table.rows.append(row)
  return

##############################################################################
#cDate = '2004-02-32'
#print val_date(cDate)

