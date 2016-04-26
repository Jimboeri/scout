#!/usr/bin/python2
#
# version 1.1, modified table, row and item to accept element values as
# paramateres
#
 
#import cgitb; cgitb.enable()
import string
import random
import os


##############################################################################
def jbutton (text, url, name='', need_form=0):
  """This function returns an HTML string to create a form button that links to a URL
    text - mandatory - text to be displayed in button
    url - mandatory - url to go to
    name - optional - HTML name
    need_form - if set to 1, will generate form tags around the button. 
        Not needed if inside a form structure already"""
  jbutt = '<INPUT TYPE="BUTTON" VALUE="' + text + '" '
  if name != "":
    jbutt += 'NAME="' + name + '" '
  jbutt += ' onclick="window.location=\'' + url + '\'">'
  if need_form:
    jbutt = tag('FORM', jbutt, 'action="#"')
  return jbutt

##############################################################################
def jswrapper (text):
  """HTML wrapper to put javascript into a web page"""
  cRet = '<SCRIPT LANGUAGE="Javascript" TYPE="text/javascript">\n  <!-- Hide script from old browsers\n'
  cRet += text
  cRet += '\n  // End hiding script from old browsers\n</SCRIPT>'
  return cRet

##############################################################################
def f_print(file, cString):
  """Writes the string out to a file like objact, and appends a newline character"""
  file.write(cString + '\n')
  return

 
##############################################################################
def tag(tag, inp_string, inp_attr=''):
    " Automatically creates and output HTML with correctly formed tags"
    out_string = '<' + tag
    if (inp_attr <> ""):
        out_string = out_string + ' ' + inp_attr
    out_string = out_string + '>' + inp_string + '</' + tag + '>\n'
    return out_string

##############################################################################
# Not yet defined as classes
#   thead
#   tfooter
#   tbody
##############################################################################
class table:
  """ Class to abstract HTML tables. It takes as parameters the following HTML attributes
    and makes them available as data attributes.
	border
	align
	background
	bgcolor
	bordercolor
	bordercolordark
	bordercolorlight
	cellpadding
	cellspacing
	styleclass
	cols
	id
	frame
	rules
	style
	title
	width
	caption
  It also makes 2 lists available as data attributes
    1. rows - this is a list of table_row objects
    2. colgroups - this is a list of table_colgroup objects
"""
  def __init__(self, \
	border=0, \
	align = '', \
	background = '', \
	bgcolor = '', \
	bordercolor = '', \
	bordercolordark = '', \
	bordercolorlight = '', \
	cellpadding = '', \
	cellspacing = '', \
	styleclass = '', \
	cols = '', \
	id = '', \
	frame = '', \
	rules = '', \
	style = '', \
	title = '', \
	width = '', \
	caption = ''):
    """This instantiates the object and sets the parameters as data attributes"""
    self.align		= align
    self.background	= background
    self.bgcolor	= bgcolor
    self.border		= border
    self.bordercolor	= bordercolor
    self.bordercolordark= bordercolordark
    self.bordercolorlight= bordercolorlight
    self.cellpadding	= cellpadding
    self.cellspacing	= cellspacing
    self.styleclass	= styleclass
    self.cols		= cols
    self.id		= id
    self.frame		= frame
    self.rules		= rules
    self.style		= style
    self.title		= title
    self.width		= width
    self.caption	= caption
    self.rows		=[]
    self.colgroups	=[]
  
  def pr_table(self):
    """Processes the objects and returns a string holding an HTML representation of the table"""
    cTable = '<TABLE BORDER="' + str(self.border) + '"'
    if self.align != '':
      cTable += ' ALIGN="' + self.align + '"'
    if self.background != '':
      cTable += ' BACKGROUND="' + self.background + '"'
    if self.bgcolor != '':
      cTable += ' BGCOLOR="' + self.bgcolor + '"'
    if self.bordercolor != '':
      cTable += ' BORDERCOLOR="' + self.bordercolor + '"'
    if self.bordercolordark != '':
      cTable += ' BORDERCOLORDARK="' + self.bordercolordark + '"'
    if self.bordercolorlight != '':
      cTable += ' BORDERCOLORLIGHT="' + self.bordercolorlight + '"'
    if self.cellpadding != '':
      cTable += ' CELLPADDING="' + self.cellpadding + '"'
    if self.cellspacing != '':
      cTable += ' CELLSPACING="' + self.cellspacing + '"'
    if self.styleclass != '':
      cTable += ' CLASS="' + self.styleclass + '"'
    if self.cols != '':
      cTable += ' COLS="' + self.cols + '"'
    if self.frame != '':
      cTable += ' FRAME="' + self.frame + '"'
    if self.id != '':
      cTable += ' ID="' + self.id + '"'
    if self.rules != '':
      cTable += ' RULES="' + self.rules + '"'
    if self.style != '':
      cTable += ' STYLE="' + self.style + '"'
    if self.title != '':
      cTable += ' TITLE="' + self.title + '"'
    if self.width != '':
      cTable += ' WIDTH="' + self.width + '"'
    cTable += '>\n' 

    if self.caption != '':
      cTable += '<CAPTION>\n' + self.caption + '\n</CAPTION>\n'

    for colgr in self.colgroups:
      cTable += colgr.pr_colgr()

    for tr in self.rows:
      cTable += tr.pr_row()

    cTable += '</TABLE>\n'
    return cTable

  def __str__(self):
    """Prints the table in HTML"""
    return self.pr_table()

  def add_row(self, \
        in_list = [],\
	align = '', \
	bgcolor = '', \
	bordercolor = '', \
	bordercolordark = '', \
	bordercolorlight = '', \
	char = '', \
	charoff = '', \
	styleclass = '', \
	id = '', \
	nowrap = 'N', \
	style = '', \
	title = '', \
	valign = ''):
    """Adds a table_row object to the rows data object list.
  The first parameter, in_list, is an optional list of text elements. If present, the table_row
    will be populated with default table_item objects each displaying the text element.
  The table_row object will be returned by the procedure call"""
    row = table_row(align, bgcolor, bordercolor, bordercolordark, \
        bordercolorlight, char , charoff , styleclass , id , nowrap, \
	style , title , valign = '')
    for element in in_list:
      row.add_item(element)
    self.rows.append(row)
    return row

  def insert_row(self, \
        index, \
        in_list = [],\
	align = '', \
	bgcolor = '', \
	bordercolor = '', \
	bordercolordark = '', \
	bordercolorlight = '', \
	char = '', \
	charoff = '', \
	styleclass = '', \
	id = '', \
	nowrap = 'N', \
	style = '', \
	title = '', \
	valign = ''):
    """Inserts a table_row object into the rows data object list.
  The first parameter, index, is where the table_row will be inserted.
    A value of 0 will insert the row at the start of the list.
    If the value is too high, the row will be appended
  The second parameter, in_list, is an optional list of text elements. If present, the table_row
    will be populated with default table_item objects each displaying the text element.
  The table_row object will be returned by the procedure call"""

    row = table_row(align, bgcolor, bordercolor, bordercolordark, \
        bordercolorlight, char , charoff , styleclass , id , nowrap, \
	style , title , valign = '')
    for element in in_list:
      row.add_item(element)
    if index > len(self.rows):
      self.rows.append(row)
    else:
      self.rows.insert(index, row)
    return row


  def last_row(self):
    """Returns the last table_row object in the rows data attribute,
    i.e. the last row in the table"""
    return self.rows[len(self.rows)-1]

  def add_colgroup(self, \
      align='',\
      char='', \
      charoff='', \
      id='', \
      span='', \
      style='', \
      title='', \
      width='', \
      valign='', \
      attribs=''):
    "Adds a table_colgroup object to the table"
    colgroup = table_colgroup(align, char, charoff, id, span, style, title, \
      width, valign, attribs)
    self.colgroups.append(colgroup)
    return colgroup

  def append_item(self,\
        data,\
        new_row=0,\
	align = '', \
	abbr = '', \
	axes = '', \
	background = '', \
	bgcolor = '', \
	bordercolor = '', \
	bordercolordark = '', \
	bordercolorlight = '', \
	char = '', \
	charoff = '', \
	styleclass = '', \
	colspan = '', \
	id = '', \
	nowrap = 'N', \
	header = 0, \
	rowspan = '', \
	style = '', \
	title = '', \
	valign = '', \
	width = ''):
    """This will append a new table_item object to the last table_row. 
    If there are no rows in the list, or if the parameter, new_row is 1,
    then a new table_row is added first. The other parameters are parameters for table_item."""
    if new_row or len(self.rows) == 0:
      self.last_cell = self.add_row().add_item(data,\
          align = align,\
          background = background,\
          bgcolor=bgcolor,\
          styleclass=styleclass,\
          colspan=colspan,\
          header=header,\
          rowspan=rowspan,\
          style=style,\
          valign=valign,\
          width=width)
    else:
      self.last_cell = self.last_row().add_item(data,\
          align = align,\
          background = background,\
          bgcolor=bgcolor,\
          styleclass=styleclass,\
          colspan=colspan,\
          header=header,\
          rowspan=rowspan,\
          style=style,\
          valign=valign,\
          width=width)
    return self.last_cell


##############################################################################
class table_row:
  """ Abstracts a row in a HTML table. It takes as parameters the following HTML attributes
    and makes them available as data attributes.
	align
	bgcolor
	bordercolor
	bordercolordark
	bordercolorlight
	char
	charoff
	styleclass
	id
	nowrap ('N')
	style
	title
	valign
  It also makes a list available as data attribute
    1. items - this is a list of table_item objects
 
"""
  def __init__(self, \
	align = '', \
	bgcolor = '', \
	bordercolor = '', \
	bordercolordark = '', \
	bordercolorlight = '', \
	char = '', \
	charoff = '', \
	styleclass = '', \
	id = '', \
	nowrap = 'N', \
	style = '', \
	title = '', \
	valign = ''):
    self.align		= align
    self.bgcolor	= bgcolor
    self.bordercolor	= bordercolor
    self.bordercolordark= bordercolordark
    self.bordercolorlight= bordercolorlight
    self.char		= char
    self.charoff	= charoff
    self.styleclass	= styleclass
    self.id		= id
    self.nowrap		= nowrap
    self.style		= style
    self.title		= title
    self.valign		= valign
    self.items=[]

  def pr_row(self):
    """Returns an HTML representation of the row. 
    It is typically used in the table.pr_table() procedure"""
    cRow = '<TR'
    if self.align != '':
      cRow += ' ALIGN="' + self.align + '"'
    if self.bgcolor != '':
      cRow += ' BGCOLOR="' + self.bgcolor + '"'
    if self.bordercolor != '':
      cRow += ' BORDERCOLOR="' + self.bordercolor + '"'
    if self.bordercolordark != '':
      cRow += ' BORDERCOLORDARK="' + self.bordercolordark + '"'
    if self.bordercolorlight != '':
      cRow += ' BORDERCOLORLIGHT="' + self.bordercolorlight + '"'
    if string.upper(self.align) == 'CHAR':
      if self.char != '':
        cRow += ' CHAR="' + self.char + '"'
      if self.charoff != '':
        cRow += ' CHAROFF="' + self.charoff + '"'
    if self.styleclass != '':
      cRow += ' CLASS="' + self.styleclass + '"'
    if self.id != '':
      cRow += ' ID="' + self.id + '"'
    if self.nowrap == 'Y':
      cRow += ' NOWRAP'
    if self.style != '':
      cRow += ' STYLE="' + self.style + '"'
    if self.title != '':
      cRow += ' TITLE="' + self.title + '"'
    if self.valign != '':
      cRow += ' VALIGN="' + self.valign + '"'

    cRow += '>\n'

    for itm in self.items:
      cRow += itm.pr_item()

    cRow += '</TR>\n'
    return cRow

  def __str__(self):
    """Prints the object in HTML"""
    return self.pr_row()

  def add_item(self, \
	data='', \
	align = '', \
	abbr = '', \
	axes = '', \
	background = '', \
	bgcolor = '', \
	bordercolor = '', \
	bordercolordark = '', \
	bordercolorlight = '', \
	char = '', \
	charoff = '', \
	styleclass = '', \
	colspan = '', \
	id = '', \
	nowrap = 'N', \
	header = 0, \
	rowspan = '', \
	style = '', \
	title = '', \
	valign = '', \
	width = ''):
    "Adds a table_item to the row object. Parameters are HTML attributes"
    item = table_item(data, align, abbr, axes, background, bgcolor, bordercolor, bordercolordark, \
	bordercolorlight, char, charoff, styleclass, colspan, id, nowrap, header, rowspan, \
	style, title, valign, width)
    self.items.append(item)
    return item

  def insert_item(self, \
        index, \
	data='', \
	align = '', \
	abbr = '', \
	axes = '', \
	background = '', \
	bgcolor = '', \
	bordercolor = '', \
	bordercolordark = '', \
	bordercolorlight = '', \
	char = '', \
	charoff = '', \
	styleclass = '', \
	colspan = '', \
	id = '', \
	nowrap = 'N', \
	header = 0, \
	rowspan = '', \
	style = '', \
	title = '', \
	valign = '', \
	width = ''):
    """Inserts a table_item into the row.
    The parameter index indicates the position, a value of 0 will put the table_item
    at the start of the row"""
    item = table_item(data, align, abbr, axes, background, bgcolor, bordercolor, bordercolordark, \
	bordercolorlight, char, charoff, styleclass, colspan, id, nowrap, header, rowspan, \
	style, title, valign, width)

    if index > len(self.items):
      self.items.append(item)
    else:
      self.items.insert(index, item)
    return item


  def last_item(self):
    "Returns last table_item in the row"
    return self.items[len(self.items)-1]

  def get_no_cols(self, index=-1):
    """Returns number of display columns in a row, or up to an element in a row"""
    nCol = 0
    nIdx = 0
    for item in self.items:
      nCol += item.get_cols()
      nIdx += 1
      if index != -1 and nIdx > index:
        break
    return nCol

  def get_col_item(self, col_no):
    "Returns table_item relating to display column in a HTML table"
    if col_no >= self.get_no_cols():
      return
    if len(self.items) < 1:
      return
    nCol = 0
    for item in self.items: 
      if nCol > col_no:
        return
      if nCol == col_no:
        return item
      nCol += item.get_cols()


##############################################################################
class table_item:
  """ Abstracts a HTML table cell.
    The first parameter, data, takes the text input that will be displayed in the table_item.
    The remaining parameters takes the following HTML attributes
    and makes them available as data attributes.
	align (LEFT, RIGHT, CENTER, JUSTIFY, CHAR)
	abbr
	axes
	background
	bgcolor
	bordercolor
	bordercolordark
	bordercolorlight
	char
	charoff
	styleclass
	colspan
	id
	nowrap ('N')
	header
	rowspan
	style
	title
	valign (TOP, MIDDLE, BOTTOM, BASELINE)
	width
"""
  def __init__(self, data='', \
	align = '', \
	abbr = '', \
	axes = '', \
	background = '', \
	bgcolor = '', \
	bordercolor = '', \
	bordercolordark = '', \
	bordercolorlight = '', \
	char = '', \
	charoff = '', \
	styleclass = '', \
	colspan = '', \
	id = '', \
	nowrap = 'N', \
	header = 0, \
	rowspan = '', \
	style = '', \
	title = '', \
	valign = '', \
	width = ''):
    """Instantiates athe table_item object.
    The first parameter, data, is the visible text in the cell
    The other paramaters are HTML attributes"""

    self.align           = align
    self.abbr            = abbr
    self.axes            = axes
    self.background      = background
    self.bgcolor         = bgcolor
    self.bordercolor     = bordercolor
    self.bordercolordark = bordercolordark
    self.bordercolorlight= bordercolorlight
    self.char            = char
    self.charoff         = charoff
    self.styleclass      = styleclass
    self.colspan         = colspan
    self.id              = id
    self.nowrap          = nowrap
    self.rowspan         = rowspan
    self.style           = style
    self.title           = title
    self.valign          = valign
    self.width           = width
    self.header          = header
    self.data            = data


  def pr_item(self):
    """Returns an HTML representation of a table_item object
    It is typically used by the table_row.pr_row() procedure call"""
    if self.data is None:
      self.data = ''
    if self.header:
      cItem = '<TH'
    else:
      cItem = '<TD'
    if self.align != '':
      cItem += ' ALIGN="' + self.align + '"'
    if self.bgcolor != '':
      cItem += ' BGCOLOR="' + self.bgcolor + '"'
    if self.bordercolor != '':
      cItem += ' BORDERCOLOR="' + self.bordercolor + '"'
    if self.bordercolordark != '':
      cItem += ' BORDERCOLORDARK="' + self.bordercolordark + '"'
    if self.bordercolorlight != '':
      cItem += ' BORDERCOLORLIGHT="' + self.bordercolorlight + '"'
    if string.upper(self.align) == 'CHAR':
      if self.char != '':
        cItem += ' CHAR="' + self.char + '"'
      if self.charoff != '':
        cItem += ' CHAROFF="' + self.charoff + '"'
    if self.styleclass != '':
      cItem += ' CLASS="' + self.styleclass + '"'
    if self.colspan != '':
      cItem += ' COLSPAN="' + str(self.colspan) + '"'
    if self.id != '':
      cItem += ' ID="' + self.id + '"'
    if self.nowrap == 'Y':
      cItem += ' NOWRAP'
    if self.rowspan != '':
      cItem += ' ROWSPAN="' + str(self.rowspan) + '"'
    if self.style != '':
      cItem += ' STYLE="' + self.style + '"'
    if self.title != '':
      cItem += ' TITLE="' + self.title + '"'
    if self.valign != '':
      cItem += ' VALIGN="' + self.valign + '"'
    if self.width != '':
      cItem += ' WIDTH="' + str(self.width) + '"'

    cItem += '>' + self.data
    if self.header:
      cItem += '</TH>\n'
    else:
      cItem += '</TD>\n'

    return cItem

  def __str__(self):
    """Prints the table_item object as HTML"""
    return self.pr_item()

  def get_cols(self):
    """Returns integer number of display columns this element covers"""
    if str(self.colspan) == '':
      return 1
    else:
      return int(str(self.colspan))



##############################################################################
class table_colgroup:
  """ Abstracts the HTML4 colgroup tag structure
    the data attribute cols, is a list of table_col objects """
  def __init__(self, \
    align='', \
    char='', \
    charoff='', \
    id='', \
    span='', \
    style='', \
    title='', \
    width='', \
    valign='', \
    attribs=''):
    """All parameters are HTML attributes"""

    self.align = align
    self.char = char
    self.charoff = charoff
    self.id = id
    self.span = span
    self.style = style
    self.title = title
    self.width = width
    self.valign = valign
    self.attribs = attribs
    self.cols = []

  def pr_colgr(self):
    """Returns an HTML representation of the table_colgroup object"""
    cColgr = '<COLGROUP'
    if self.align != '':
      cColgr += ' ALIGN="' + self.align + '"'
      if string.upper(self.align) == 'CHAR':
        if self.char != '':
          cColgr += ' CHAR="' + self.char + '"'
        if self.charoff != '':
          cColgr += ' CHAROFF="' + self.charoff + '"'
    if self.id != '':
      cColgr += ' ID="' + self.id + '"'
    if self.span != '':
      cColgr += ' SPAN="' + self.span + '"'
    if self.style != '':
      cColgr += ' STYLE="' + self.style + '"'
    if self.title != '':
      cColgr += ' TITLE="' + self.title + '"'
    if self.valign != '':
      cColgr += ' VALIGN="' + self.valign + '"'
    if self.width != '':
      cColgr += ' WIDTH="' + self.width + '"'
    if self.attribs != '':
      cColgr += ' ' + self.attribs

    cColgr += '>\n'

    for col in self.cols:
      cColgr += col.pr_col()

    return cColgr

  def add_col(self, \
    align='', \
    char='', \
    charoff='', \
    id='', \
    span='', \
    style='', \
    title='', \
    width='', \
    valign='', \
    attribs=''):

    "Adds a table_col object to a colgroup"
    self.col = table_col(align, char, charoff, id, span, style, title, width,\
      valign, attribs)
    self.cols.append(self.col)
    return self.col


##############################################################################
class table_col:
  """ Abstracts the HTML4 col tag structure """
  def __init__(self, \
    align='', \
    char='', \
    charoff='', \
    id='', \
    span='', \
    style='', \
    title='', \
    width='', \
    valign='', \
    attribs=''):
    """Creates a table_col object"""
    self.align = align
    self.char = char
    self.charoff = charoff
    self.id = id
    self.span = span
    self.style = style
    self.title = title
    self.width = width
    self.valign = valign
    self.attribs = attribs

  def pr_col(self):
    """Returns HTML representation of the table_col object"""
    cCol = '<COL'
    if self.align != '':
      cCol += ' ALIGN="' + self.align + '"'
      if string.upper(self.align) == 'CHAR':
        if self.char != '':
          cCol += ' CHAR="' + self.char + '"'
        if self.charoff != '':
          cCol += ' CHAROFF="' + self.charoff + '"'
    if self.id != '':
      cCol += ' ID="' + self.id + '"'
    if self.span != '':
      cCol += ' SPAN="' + self.span + '"'
    if self.style != '':
      cCol += ' STYLE="' + self.style + '"'
    if self.title != '':
      cCol += ' TITLE="' + self.title + '"'
    if self.valign != '':
      cCol += ' VALIGN="' + self.valign + '"'
    if self.width != '':
      cCol += ' WIDTH="' + self.width + '"'
    if self.attribs != '':
      cCol += ' ' + self.attribs
    cCol += '>\n'
    
    return cCol

##############################################################################
class form_input:
  """Abstracts the input fields for a form"""
  def __init__(self, type, \
                     accept='', \
                     align='', \
                     checked=0, \
                     styleclass='', \
                     datafld='', \
                     datasrc='', \
                     disabled=0, \
                     maxlength=0, \
                     name='', \
                     notab=0, \
                     readonly=0, \
                     size=0, \
                     src='', \
                     style='', \
                     tabindex=0, \
                     title='', \
                     usemap='', \
                     value=''):

    """Instantiates a form_input object.
    If the mandatory parameter, type, is not valid, it is replaced by 'TEXT'"""
    self.type = type.upper()
    if self.type not in ('TEXT', 'PASSWORD', 'RADIO', 'CHECKBOX', 'SUBMIT', 'RESET', 'FILE', 'IMAGE', 'HIDDEN', 'BUTTON'):
      self.type = 'TEXT'
    self.accept = accept
    self.align = align
    self.checked = checked
    self.styleclass = styleclass
    self.datafld = datafld
    self.datasrc = datasrc
    self.disabled = disabled
    self.maxlength = maxlength
    self.name = name
    self.notab = notab
    self.readonly = readonly
    self.size = size
    self.src = src
    self.style = style
    self.tabindex = tabindex
    self.title = title
    self.usemap = usemap
    self.value = value

  def pr_input(self):
    """Returns HTML string representing the form_input object"""
    cInp = '<INPUT TYPE="%s" ' % self.type
    if self.name != '':
      cInp += 'NAME="%s" ' % self.name
    if self.value != '':
      cInp += 'VALUE="%s" ' % self.value
    if self.accept != '':
      cInp += 'ACCEPT=%s ' % self.accept
    if self.align != '':
      cInp += 'ALIGN=%s ' % self.align
    if self.styleclass != '':
      cInp += 'CLASS="%s" ' % self.styleclass
    if self.datafld != '':
      cInp += 'DATAFLD="%s" ' % self.datafld
    if self.datasrc != '':
      cInp += 'DATASRC="%s" ' % self.datasrc
    if self.disabled:
      cInp += 'DISABLED '
    if self.type in ('TEXT', 'PASSWORD'):
      if self.maxlength > 0:
        cInp += 'MAXLENGTH=%d ' % self.maxlength
      if self.size > 0:
        cInp += 'SIZE=%d ' % self.size
    if self.notab:
      cInp += 'NOTAB '
    if self.readonly:
      cInp += 'READONLY '
    if self.type=='IMAGE':
      if self.src != '':
        cInp += 'SRC="%s" ' % self.src
      if self.usemap != '':
        cInp += 'USEMAP="%s" ' % self.usemap
    if self.style != '':
      cInp += 'STYLE="%s" ' % self.style
    if self.tabindex:
      cInp += 'TABINDEX=%d ' % self.tabindex
    if self.title != '':
      cInp += 'TITLE="%s" ' % self.title

    cInp += '>'
    return cInp

##############################################################################
class form:
  """Abstracts the HTML form tag"""
  def __init__(self, action, \
                     form_body, \
                     method='POST', \
                     accept='', \
                     styleclass='', \
                     enctype='', \
                     id='', \
                     name='', \
                     style='', \
                     target='', \
                     title=''):
    """Instantiates the form object.
Parameters
  1. action - this is the action the form should take, usually a URL
  2. form_body - the HTML body of the form
  3. method - can be 'GET' or 'POST', defaults to 'POST'
A data attribute hidden_fld is created a an empty list. Any form_input objects in it will
    be added to the form when printed"""
    self.method = method.upper()
    if self.method not in ('POST', 'GET'):
      self.method = 'POST'
    self.action = action
    self.form_body = form_body
    self.accept = accept
    self.styleclass = styleclass
    self.enctype = enctype
    self.id = id
    self.name = name
    self.style = style
    self.target = target
    self.title = title
    self.hidden_fld = []

  def add_hidden(self, name, value):
    """Adds a 'hidden' input field to the hidden_fld list. 
    These will be inserted when the form is created"""
    self.hidden_fld.append(form_input("HIDDEN", name = name, value = value))

  def pr_form(self):
    """Returns HTML representation of the form"""
    cInp = '<FORM METHOD=%s ACTION="%s"' % (self.method, self.action)
    if self.name != '':
      cInp += 'NAME="%s" ' % self.name
    if self.accept != '':
      cInp += 'ACCEPT="%s" ' % self.accept
    if self.styleclass != '':
      cInp += 'CLASS="%s" ' % self.styleclass
    if self.enctype != '':
      cInp += 'ENCTYPE="%s" ' % self.enctype
    if self.id != '':
      cInp += 'ID="%s" ' % self.id
    if self.style != '':
      cInp += 'STYLE="%s" ' % self.style
    if self.target:
      cInp += 'TARGET="%s" ' % self.target
    if self.title != '':
      cInp += 'TITLE="%s" ' % self.title
    cInp += '>\n' + self.form_body
    for hf in self.hidden_fld:
      cInp += hf.pr_input() + '\n'

    cInp += '\n</FORM>'

    return cInp
  
  def __str__(self):
    """Prints the form"""
    return self.pr_form()

##############################################################################
class page:
  """ Abstracts a web page and returns it a a string for output
Parameters:
    Title - title of the page
    cookie - a text representation of a cookie to be set. This is for backwards compatability
        rather use the ocookie parameter
    ocookie - this expects a cookie as produced by the Cookie module
    css - a list of names of cascading style sheets to be used by the page

Data attributes
  meta - a list of meta data field created in the HTML header
  head - a list of strings that will be produced first
  data - a list of strings for the body of the page
  foot - a list of strings to be put at the end of the page"""
  def __init__(self, title = '', \
    cookie = '',\
    ocookie = None,\
    css = []):
    """Instantiates the page"""

    self.cookie = cookie
    self.ocookie = ocookie
    self.title = title
    self.css = css
    self.meta = []
    self.head = []
    self.data = []
    self.foot = []


  def pr_page(self):    
    """Returns a sting containing the full page contents"""
    self.str_page = "Content-type: text/html\n"
    if self.ocookie is not None:
      self.str_page += self.ocookie.output() + '\n'
      #self.head.append('Object Cookie set = %s \n' % self.ocookie.output())
    elif self.cookie is not None and self.cookie != '':
      self.str_page += self.cookie + '\n'
    else:
      #self.head.append('No cookie')
      pass

    self.str_page += '\n<HTML>\n<HEAD>\n<TITLE>%s</TITLE>\n' % self.title
    for c in self.css:
      self.str_page += '<LINK REL="stylesheet" TYPE="text/css" HREF="%s">\n' % c
    for m in self.meta:
      self.str_page += m + '\n'
    self.str_page += '</HEAD>\n<BODY>\n'
    for h in self.head:
      self.str_page += h + '\n'
    for d in self.data:
      self.str_page += d + '\n'
    if len(self.foot):
      for f in self.foot:
        self.str_page += f + '\n'
    else:
      self.str_page += '<ADDRESS><HR> Copyright Jim West 2003-2007</ADDRESS>\n</BODY>\n</HTML>\n'
    return self.str_page

  def __str__(self):
    """Prints the page to std output"""
    self.pr_page()
    return self.str_page

  def output(self):
    """Prints the page"""
    print self.pr_page()

  def test_output(self):
    tfn = '/tmp/outfile.web'
    tf = open(tfn, 'w')
    tf.write(self.pr_page())
    tf.close()
    return


##############################################################################

# OBSOLETE CODE beloe here


##############################################################################
def file_header(file, param, message = ''):
  """Obsolete page header"""
  f_print(file, ' ')
  f_print(file, "<html>")
  f_print(file, "<head>")
  f_print(file, tag('title', param.disp_name))
  if string.strip(param.css_file) != '':
    f_print(file, '<link rel="stylesheet" type="text/css" href="' + string.strip(param.css_file) + '">')
  f_print(file, "</head>")
  f_print(file, "<body>")
  oTable = table()
  oTable.cellpadding = '2'
  oTable.cellspacing = '0'
  oTable.width = '100%'
  oTable.cols = '3'
  oTable.border = '1'
  row = table_row()
  # Column 1, the logo if I get one
  item = table_item('Logo')
  item.width='100'
  item.rowspan='2'
  row.items.append(item)
  # Col 2, the Title
  item = table_item(tag('H1', param.disp_name))
  item.width = '*'
  item.rowspan='2'
  item.align = 'CENTER'
  row.items.append(item)
  oTable.rows.append(row)

  f_print(file, oTable.pr_table())

  if message is not None and message != "":
    f_print(file, tag('center', tag('h4', message + '<br>')))

##############################################################################
def table_html(inList, border=1, cellspacing=3, width='100%'):
  """Obsolete Table procedure"""
  cTable = ''
  for nRow in inList:
    cRow = ''
    for nElement in nRow:
      cRow = cRow + tag('td', nElement[0], 'Width = "' + nElement[1] + '"')
    cTable = cTable + tag('tr', cRow)
  cTable = tag('table', cTable, 'border="' +str(border) + '" cellspacing="' + str(cellspacing) + '" width="' + width + '"')
  return cTable

##############################################################################
def form_footer():
  """Obsolete page footer"""
  print tag('address', '<hr> Copyright Jim West 2003-2005')
  #print 'Env cookie = ' + os.environ.get("HTTP_COOKIE")
  print "</body>"
  print "</html>"

##############################################################################
def jw_header(param, conn, menu_item = 1, cCookie = '', message = ''):
  """Obsolete page header"""
  print "Content-type: text/html"
  if not cCookie == None:
    print cCookie
  print
  print "<html>"
  print "<head>"
  print tag('title', param.disp_name)
  if string.strip(param.css_file) != '':
    print '<link rel="stylesheet" type="text/css" href="' + string.strip(param.css_file) + '">'
  print "</head>"
  print "<body>"
  oTable = table()
  oTable.cellpadding = '2'
  oTable.cellspacing = '0'
  oTable.width = '100%'
  oTable.cols = '3'
  oTable.border = '1'
  row = table_row()
  # Column 1, the logo if I get one
  item = table_item('Logo')
  item.width='100'
  item.rowspan='2'
  row.items.append(item)
  # Col 2, the Title
  item = table_item(tag('H1', param.disp_name))
  item.width = '*'
  item.rowspan='2'
  item.align = 'CENTER'
  row.items.append(item)
  # Col 3, personal dets
  item = table_item("Profile")
  item.width = '10%'
  item.align = "CENTER"
  if menu_item == 20 and conn.user_id != '':
    item.bgcolor = "FFFF00"
    item.data = tag('a', 'Profile', 'href="photo.py?jw_action=profile"')
  else:
    item.data = '&nbsp;'
  row.items.append(item)
  oTable.rows.append(row)

  # Row 2 (only 3 col, the log out as 1st 2 rows use rowspan
  row = table_row()
  if conn.sign_in:
    item = table_item(tag('A', 'Sign Out', 'href="photo.py?jw_action=logout_form"'))
  else:
    item = table_item(tag('A', 'Sign In', 'href="photo.py?jw_action=login_form"'))
    if menu_item == 30:
      item.bgcolor = "FFFF00"
  item.align = "CENTER"
  row.items.append(item)
  oTable.rows.append(row)

  print oTable.pr_table()

  oTable = table()
  oTable.cellpadding = '3'
  oTable.cellspacing = '0'
  oTable.border = '1'
  row = table_row()

  # Display Home tag
  item = table_item(tag('A', 'Home', 'href="photo.py?jw_action=home_page"')) 
  if menu_item == 1:
    item.bgcolor = "#FFFF00"
    item.data = '<b>' + item.data + '</b>'
  row.items.append(item)

  # Display films tag
  item = table_item(tag('A', 'Films', 'href="photo.py?jw_action=film_disp"')) 
  if menu_item == 2:
    item.bgcolor = "#FFFF00"
    item.data = '<b>' + item.data + '</b>'
  row.items.append(item)


  # System maintenance tag
  if conn.sign_in:
    item = table_item(tag('A', "System Maintenance", 'href="photo.py?jw_action=prmf_edit"'))
    if menu_item == 21:
      item.bgcolor = "#FFFF00"
      item.data = '<b>' + item.data + '</b>'
    row.items.append(item)

  oTable.rows.append(row)
  print oTable.pr_table()

  if message is not None and message != "":
    print tag('center', tag('h4', message + '<br>'))
  print '<hr>'

##############################################################################
def prm_header(menu_item = 1):
  """OBSOLETE"""
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



