#!/usr/bin/python2
"""Provides all class definitions needed to access data structures"""
#import cgitb; cgitb.enable()
import pg
import string
import random
import os
import time
import procs
import Cookie
import ConfigParser
import datetime
import sha

from optparse import OptionParser
import pgdb

##############################################################################
class dbinstanceold:
    """OBSOLETE
    A Class to abstract the database connection"""
    def __init__(self, db_name):
        self.database = pg.connect(db_name)
#        self.database = pgdb.connect(database=db_name)
#
##############################################################################
class dbinstance:
  """This class abstracts a PostgresQL database and permits DB access
  Parameter - db_name - database name"""
  def __init__(self, db_name):
    """Instantiates the object by connecting to the database"""
    self.database = pgdb.connect(database=db_name)
    return

  def query(self, cQry):
    """This procedure executes an SQL query, and populates a dictionary
    (dictresult) with the results"""
    self.dictresult = []
    self.curs = self.database.cursor()
    self.curs.execute(cQry)
    try:
      lRes = self.curs.fetchall()
      for r in lRes:
        nCnt = 0
        Dict = {}
        for e in r:
          Dict[self.curs.description[nCnt][0]] = e
          nCnt += 1
        self.dictresult.append(Dict)
    except pg.DatabaseError:
      pass
    return  self.dictresult

  def commit(self):
    """This procedure issues a DB commit"""
    self.database.commit()
    return

  def close(self):
    """Closes the database connection"""
    self.database.close()
    return
 
##############################################################################
class paramrec:
  """ A class to abstract parameters to the system
  The parameters are read from the 'scout.conf' file if not otherwise stated"""
  def __init__(self, cfg_file=''):
    """Reads the file and instantiates the following data attributes:
    dbname
    title
    css_file
    logo
    age_variance
    baseurl
    pythondir
    extract_dir
    template_dir
    email_extract_msg
    email_account_create
    email_pw_hint
    email_header
    email_footer
    online_agreement
    smtpserver
    fromaddr
    ot_cellpad
    ot_cellspc
    ot_brdr
    it_cellpad
    it_cellspc
    it_brdr
    testing - def 0
    junior_age (15) - Defines age below which must have parent details
    group_ou_struct (4) - Defines OU struct of group level
"""
    # Initiate Confiog Parser
    conf = ConfigParser.SafeConfigParser()

    # work out file name
    if cfg_file == '':
      cfgfile = 'scout.conf'
    else:
      cfgfile = cfg_file
    conf.read([cfgfile])

    # Prefine default values in case values are not defines in the config file
    self.dbname = "scout"
    self.title = "Scout membership systems"
    self.css_file = ""
    self.logo = ""
    self.age_variance = 0.5
    self.baseurl = ""
    self.pythondir = "/py"
    self.extract_dir = "extract"
    self.template_dir = "template"
    self.email_extract_msg = "email-extract-msg.txt"
    self.email_account_create = "email_account_create.html"
    self.email_pw_hint = "email_pw_hint.html"
    self.email_header = "email_header.html"
    self.email_footer = "email_footer.html"
    self.online_agreement = "online_agreement.html"
    self.smtpserver = "localhost"
    self.fromaddr = ""
    self.ot_cellpad = '3'
    self.ot_cellspc = '0'
    self.ot_brdr = 1
    self.it_cellpad = '0'
    self.it_cellspc = '0'
    self.it_brdr = 0
    self.testing = 0
    self.junior_age = 15
    self.group_ou_struct = 4

    # Now update values from the config file
    if conf.has_section('database'):
      if conf.has_option('database', 'name'):
        self.dbname = conf.get('database', 'name')
    if conf.has_section('display'):
      if conf.has_option('display', 'title'):
        self.title = conf.get('display', 'title')
      if conf.has_option('display', 'css_file'):
        self.css_file = conf.get('display', 'css_file')
      if conf.has_option('display', 'logo'):
        self.logo = conf.get('display', 'logo')
    if conf.has_section('General'):
      if conf.has_option('General', 'age_variance'):
        self.age_variance = float(conf.get('General', 'age_variance'))
      if conf.has_option('General', 'baseurl'):
        self.baseurl = conf.get('General', 'baseurl')
      if conf.has_option('General', 'pythondir'):
        self.pythondir = conf.get('General', 'pythondir')
    if conf.has_section('Extract'):
      if conf.has_option('Extract', 'dir'):
        self.extract_dir = conf.get('Extract', 'dir')
    if conf.has_section('Templates'):
      if conf.has_option('Templates', 'dir'):
        self.template_dir = conf.get('Templates', 'dir')
      if conf.has_option('Templates', 'email-extract-msg'):
        self.email_extract_msg = conf.get('Templates', 'email-extract-msg')
      if conf.has_option('Templates', 'email_account_create'):
        self.email_account_create = conf.get('Templates', 'email_account_create')
      if conf.has_option('Templates', 'email_pw_hint'):
        self.email_pw_hint = conf.get('Templates', 'email_pw_hint')
      if conf.has_option('Templates', 'email_header'):
        self.email_header = conf.get('Templates', 'email_header')
      if conf.has_option('Templates', 'email_footer'):
        self.email_footer = conf.get('Templates', 'email_footer')
      if conf.has_option('Templates', 'online_agreement'):
        self.online_agreement = conf.get('Templates', 'online_agreement')
    if conf.has_section('Email'):
      if conf.has_option('Email', 'smptserver'):
        self.smtpserver = conf.get('Email', 'smtpserver')
      if conf.has_option('Email', 'fromaddr'):
        self.fromaddr = conf.get('Email', 'fromaddr')
    if conf.has_section('Dev'):
      if conf.has_option('Dev', 'testing'):
        self.testing = int(conf.get('Dev', 'testing'))
    return

##############################################################################
class ourec:
  " A class to abstract the organisational unit record"
  def __init__(self, db, nOu_id):
    """The procedure instantiates the ourec object:
Parameters:
  db - a database object
  nOu_id - the ou_id of the ou record that is sought
Data attributes:
  These come from the database record
    ou_id - the id of the org unit
    name - the name of the ou
    ou_owner - the ID of the 'parent' ou record
    ou_struct - a reference to the ou structure table, defining the struct of the ou
    curr_memb - number of current members
    curr_child - number of current children
    p_addr1 - Postal address
    p_addr2
    p_addr3
    p_code
    m_addr1 - mailing address
    m_addr2
    m_addr3
    m_code
    phone
    fax
    sect_cd - section code
    meet_time
    start_age
    end_age
    award_remind
    mngt

  These come from the structure record
    struct_name - Name of the structure
    str_def_name - Default structure name
    struct_parent - Parent record of structure record
    sec_inherit - flag to say is secuity is inherited

  These are general
    database - the database object
    found - set to 1 is seach for id is successful
    junior - Set to 1 if ou members are less than 14
    adult - Set to 1 if all members are adults
    childlist - Empty list, populated with ourec child records bu child_list() method
    heir_child_names - Empty list, populated in chld_list() method. Contains allowable child types
    memberlist - Empty list, populated with members of the ou by member_list() method. 
        Contains rolerec objects
    parentlist - Empty list, populated with parents of members by the parent_list() method
    mngt_ou - ourec of the management OU belonging to this OU set by get_mngt() method
    ouowners - list (initially empty) of all owners up to root OU. Initialised by ou_owners() method
    awards - list initiall empty of possible awards that can be obtained in this OU. Populated by award_list()
"""
    self.database = db
    self.ou_id = nOu_id
    self.name = ''
    self.ou_owner = 0
    self.ou_struct = 0
    self.struct_name = ''
    self.struct_parent = 0
    self.str_def_name = ''
    self.curr_memb = 0
    self.curr_child = 0
    self.p_addr1 = ''
    self.p_addr2 = ''
    self.p_addr3 = ''
    self.p_code = ''
    self.m_addr1 = ''
    self.m_addr2 = ''
    self.m_addr3 = ''
    self.m_code = ''
    self.phone = ''
    self.fax = ''
    self.sect_cd = ''
    self.meet_time = ''
    self.start_age = 0
    self.end_age = 0
    self.award_remind = ''
    self.mngt = 0
    self.junior = 0
    self.adult = 0
    self.found = 0
    self.mngt_ou = None
    self.childlist = []
    self.heir_child_names = []
    self.memberlist = []
    self.parentlist = []
    self.ouowners = []
    self.awards = []
    curs = db.database.cursor()
    curs.execute("SELECT o.ou_id, o.ou_owner, o.ou_struct, o.name, o.curr_memb,\
        o.curr_child, o.p_addr1, o.p_addr2, o.p_addr3, o.p_code, o.m_addr1, o.m_addr2,\
        o.m_addr3, o.m_code, o.phone, o.fax, o.sect_cd, o.meet_time, o.start_age,\
        o.end_age, o.award_remind, o.mngt, s.s_name, s.s_def_name, s.parent_id,\
        s.sec_inherit, s.s_start_age, s.s_end_age FROM ou o, ou_struct s\
        WHERE ou_id = %d AND o.ou_struct = s.ou_struct"\
        % nOu_id)
    if curs.rowcount > 0:
      self.found = 1
      lQry = curs.fetchone()
      self.ou_id = lQry[0]
      self.ou_owner = lQry[1]
      self.ou_struct = lQry[2]
      self.name = lQry[3]
      self.curr_memb = lQry[4]
      self.curr_child = lQry[5]
      self.p_addr1 = lQry[6]
      self.p_addr2 = lQry[7]
      self.p_addr3 = lQry[8]
      self.p_code = lQry[9]
      self.m_addr1 = lQry[10]
      self.m_addr2 = lQry[11]
      self.m_addr3 = lQry[12]
      self.m_code = lQry[13]
      self.phone = lQry[14]
      self.fax = lQry[15]
      self.sect_cd = lQry[16]
      self.meet_time = lQry[17]
      self.start_age = lQry[26]
      self.end_age = lQry[27]
      self.award_remind = lQry[20]
      self.mngt = lQry[21]
      self.struct_name = lQry[22]
      self.str_def_name = lQry[23]
      self.struct_parent = lQry[24]
      self.sec_inherit = lQry[25]
      if lQry[18] is not None and lQry[18] != 0:
        self.start_age = lQry[18]
      if lQry[19] is not None and lQry[19] != 0:
        self.end_age = lQry[19]
      if self.start_age is None:
        self.start_age = 0
      if self.end_age is None: self.end_age = 0
      self.found = 1
      if self.end_age is not None and self.end_age > 0 and self.end_age < 15:
        self.junior = 1
      if self.start_age is not None and self.start_age > 0 and self.start_age < 15:
        self.junior = 1
      if self.start_age is not None and self.start_age > 14:
        self.adult = 1
        self.junior = 0
      if self.mngt:
        self.adult = 1
        self.junior = 0
    return

  def update(self):
    """Updates OU record based on data attributes"""
    self.result = ''
    upd_string = "UPDATE ou SET name = '%s', curr_memb = %d, curr_child = %d,\
	p_addr1 = '%s', p_addr2 = '%s', p_addr3 = '%s', p_code = '%s',\
	m_addr1 = '%s', m_addr2 = '%s', m_addr3 = '%s', m_code = '%s',\
	phone = '%s', fax = '%s', sect_cd = '%s', meet_time = '%s',\
	start_age = %d, end_age = %d, mngt = %d WHERE ou_id = %d" % \
	(sql_str(self.name), self.curr_memb, self.curr_child, sql_str(self.p_addr1),\
	sql_str(self.p_addr2), sql_str(self.p_addr3), sql_str(self.p_code),\
	sql_str(self.m_addr1), sql_str(self.m_addr2), sql_str(self.m_addr3),\
	sql_str(self.m_code), sql_str(self.phone), sql_str(self.fax),\
	sql_str(self.sect_cd), sql_str(self.meet_time), self.start_age,\
	self.end_age, self.mngt, self.ou_id)
    self.database.query(upd_string)

    # Only update the last award reminder date if needed
    if self.award_remind is not None:
      self.database.query("UPDATE ou SET award_remind = '%s' WHERE ou_id = %d" %\
        (self.award_remind, self.ou_id))
    return

  def add(self):
    """Creates a new OU record in the OU table in the database"""
    self.result = ''

    # first we get the next ou_id from the dist_seq sequence
    qry = self.database.query("SELECT nextval('ou_seq')")
    self.ou_id = int(qry[0]['nextval'])

    upd_string = "INSERT INTO ou (ou_id, ou_owner, ou_struct, name, p_addr1, p_addr2,\
      p_addr3, p_code, m_addr1, m_addr2, m_addr3, m_code, phone, fax, sect_cd, meet_time,\
      start_age, end_age, mngt)\
      VALUES (%d, %d, %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',\
      '%s', '%s', '%s', %d, %d, %d)"\
      % (self.ou_id, self.ou_owner, self.ou_struct, sql_str(self.name),\
      sql_str(self.p_addr1), sql_str(self.p_addr2), sql_str(self.p_addr3),\
      sql_str(self.p_code), sql_str(self.m_addr1), sql_str(self.m_addr2),\
      sql_str(self.m_addr3), sql_str(self.m_code), sql_str(self.phone), sql_str(self.fax),\
      sql_str(self.sect_cd), sql_str(self.meet_time), self.start_age, self.end_age, self.mngt)
    #Add record
    self.database.query(upd_string)
    return

  def child_list(self):
    """Return a list of child OU's. This also updates the following data attributes:
    childlist - contains ourec objects
    heir_child_names - contains tuples with name and ou_struct id's"""
    self.childlist = []
    self.mngt_ou = ourec(self.database, 0)
    qry = self.database.query("SELECT ou_id FROM ou WHERE ou_owner = %d ORDER BY name" % self.ou_id)
    for d in qry:
      cou = ourec(self.database, d["ou_id"])
      self.childlist.append(cou)
      if cou.mngt:
        self.mngt_ou = cou
    # return list of allowable heirarchical child types
    self.heir_child_names = []
    qry = self.database.query("SELECT ou_struct, s_name FROM ou_struct WHERE parent_id = %d AND heirarchic = 1" % self.ou_struct)
    for d in qry:
      self.heir_child_names.append([d["s_name"], d["ou_struct"]])
    return self.childlist

  def delete(self):
    """Deletes an OU from the database"""
    self.result = ''
    upd_string = "DELETE FROM ou WHERE ou_id = %d" % self.ou_id
    self.database.query(upd_string)
    return

  def member_list(self, status = ''):
    """Returns a list of member role records and also updates the data attribute memberlist
    memberlist contains rolerec records"""
    #Return a list of membership roles for the OU
    self.memberlist = []
    curs = self.database.database.cursor()
    if status == '' or status is None:
      curs.execute("SELECT role_id FROM role WHERE ou_id = %d" % self.ou_id)
    else:
      curs.execute("SELECT role_id FROM role WHERE ou_id = %d AND status = '%s'" % (self.ou_id, status))
    qry = curs.fetchall()
    for r in qry:
      self.memberlist.append(rolerec(self.database, r[0]))
    return self.memberlist

  def parent_list(self, surname=''):
    """Populates the parentlist list with adultrec objects and returns the list.
  If the optional parameter surname is provided, the list will only be populated with
  adult records if the child surname is equal OR if the adult surname is equal"""
    self.parentlist = []
    curs = self.database.database.cursor()
    if surname == '':
      cQry = 'SELECT s2.scout_id, s2.forename, s2.surname\
        FROM scout s1, scout s2, role r\
        WHERE r.ou_id = %d\
        AND s1.scout_id = r.scout_id\
        AND s1.parent1 = s2.scout_id\
        ORDER BY s2.surname, s2.forename' % self.ou_id
    else:
      # This returns those recs where child name = surname
      cQry = "SELECT s2.scout_id, s2.forename, s2.surname\
        FROM scout s1, scout s2, role r\
        WHERE r.ou_id = %d\
        AND s1.scout_id = r.scout_id\
        AND s1.parent1 = s2.scout_id\
        AND (s1.surname = '%s' OR s2.surname = '%s')" % (self.ou_id, surname, surname)

    curs.execute(cQry)
    lPar = curs.fetchall()
    for p in lPar:
      self.parentlist.append(adultrec(self.database, p[0])) 
    return self.parentlist

  def update_num(self):
    """Updates the number of current children OU's and members"""
    curs = self.database.database.cursor()
    curs.execute("SELECT role_id FROM role WHERE ou_id = %d AND status = 'C'" % self.ou_id)
    nMemb = curs.rowcount
    curs.execute("SELECT ou_id FROM ou WHERE ou_owner = %d" % self.ou_id)
    nChild = curs.rowcount
    curs.execute("UPDATE ou SET curr_memb = %d, curr_child = %d WHERE ou_id = %d" % (nMemb, nChild, self.ou_id))
    return

  def get_mngt(self):
    """Gets the ourec of the management OU for this OU and returns it"""
    curs = self.database.database.cursor()
    curs.execute("SELECT ou_id FROM ou WHERE ou_owner = %d AND mngt = 1" % self.ou_id)
    nMngt_ou = 0
    if curs.rowcount:
      # if the mngt_ou id is found, store it
      m = curs.fetchone()
      nMngt_ou = m[0]
    # get the management ou record
    self.mngt_ou = ourec(self.database, nMngt_ou)
    return self.mngt_ou

  def add_mngt(self):
    """Creates a management OU for this OU"""
    curs = self.database.database.cursor()
    curs.execute("SELECT ou_struct FROM ou_struct WHERE parent_id = %d AND mngt = 1" % self.ou_struct)
    if curs.rowcount:
      m = curs.fetchone()
      mngt_str = ou_structrec(self.database, m[0])
      if mngt_str.found:
        self.mngt_ou.name = mngt_str.s_def_name
        self.mngt_ou.ou_owner = self.ou_id
        self.mngt_ou.ou_struct = mngt_str.ou_struct
        self.mngt_ou.mngt = 1
        self.mngt_ou.add()
    return

  def __str__(self):
    """Prints ou the ou attributes"""
    return "<OU DETAILS>\nou_id = %d\nName = %s\nOu_owner = %d\nou_struct = %d\
      \ncurr_child = %d\ncurr_memb = %d\np_addr1 = %s\np_addr2 = %s\np_addr3 = %s\
      \np_code = %s\nm_addr1 = %s\nm_addr2 = %s\nm_addr3 = %s\nm_code = %s\
      \nphone = %s\nfax = %s\nmeet_time = %s\nstart_age = %d\nend_age = %d\
      \naward_remind = %s\nmngt = %d\njunior = %d\
      \n<END OF OU DETAILS>\n" %\
      (self.ou_id, self.name, self.ou_owner, self.ou_struct, self.curr_child, self.curr_memb,\
      self.p_addr1, self.p_addr2, self.p_addr3, self.p_code, self.m_addr1, self.m_addr2,\
      self.m_addr3, self.m_code, self.phone, self.fax, self.meet_time,\
      self.start_age, self.end_age, self.award_remind, self.mngt, self.junior)
    
  def ou_owners(self):
    """Populates the ouowners list woth ourec instances of ou owners going up the heirarcic tree.
    Starts with immediate owner, ends with root OU"""
    self.ouowners = []
    ou_up = ourec(self.database, self.ou_owner)
    while ou_up.ou_owner:
      self.ouowners.append(ou_up)
      ou_up = ourec(self.database, ou_up.ou_owner)
    return

  def award_list(self):
    """Populated the awards lists with award instances that can be obtained in this OU"""
    # Initialise the list
    self.awards = []

    # Need to go up the heirarchy, so get the heirarchy
    self.ou_owners()

    curs = self.database.database.cursor()
    # Start with awards for this OU
    if self.mngt:
      # just get management awards
      curs.execute("SELECT a.award_id FROM award a WHERE a.award_typeder = 1")
      as = curs.fetchall()
      for a in as:
        self.awards.append(awardrec(self.database, a[0]))

    else:
      curs.execute("SELECT a.award_id FROM award a, award_type t WHERE\
          a.award_type = t.award_type AND t.ou_struct = %d" % self.ou_struct)
      as = curs.fetchall()
      for a in as:
        self.awards.append(awardrec(self.database, a[0]))

      for o in self.ouowners:
        curs.execute("SELECT a.award_id FROM award a, award_type t WHERE\
            a.award_type = t.award_type AND t.ou_struct = %d" % o.ou_struct)
        as = curs.fetchall()
        for a in as:
          self.awards.append(awardrec(self.database, a[0]))

    return self.awards


##############################################################################
class ou_structrec:
  " A class to abstract the organisational unit structure record"
  def __init__(self, db, nOu_struct):
    """Instantiates the ou_structrec and sets the following data attributes:
From the database
    ou_struct - id of record
    s_name - Name of structure, e.g. "Zone"
    s_def_name - A default name for ou's relating to this structure
    hierarchic - Set to 1 if this structure is dependant on a heirarchy
                 and forms part of that heirarchy
    next_sect - In age based progression, defines the next age group structure up
    start_age - Starting age for members of the OU's created off this structure
    end_age - Ending age for members of the OU's created off this structure
    sec_inherit - Set to 1 if this OU inherits security from owner OU
    s_mngt_str - Hold the ou_struct id of the ou_struct record to be used for
                 mngt OU's for this struct
    mngt - Set to 1 if OU's with this struct are managemet OU's
 
General
    database - database object record
    children - empty list of children ou_structrec objects. Instantiated by sub_ou_list()
    generic_list - empty list of available generic ou_structrec objects.
       Instantiated by sub_ou_list()
    awardlist = []
    awardtypes = []
    found - def 0, 1 if record found
 
"""
    self.database = db
    self.ou_struct = nOu_struct
    self.s_name = ''
    self.s_def_name = ''
    self.hierarchic = 0
    self.next_sect = 0
    self.start_age = 0
    self.end_age = 0
    self.sec_inherit = 0
    self.s_mngt_str = 0
    self.mngt = 0
    self.children = []
    self.generic_list = []
    self.awardlist = []
    self.awardtypes = []
    self.found = 0
    try:
      qry = self.database.query("SELECT * FROM ou_struct WHERE ou_struct = %d " % nOu_struct)
    except ValueError:
      self.ou_id = 0
    if len(qry) > 0:
      self.s_name 	= qry[0]['s_name']
      self.s_def_name 	= qry[0]['s_def_name']
      self.heirarchic 	= qry[0]['heirarchic']
      self.next_sect 	= qry[0]['s_next_sect']
      self.start_age 	= qry[0]['s_start_age']
      self.end_age	= qry[0]['s_end_age']
      self.sec_inherit 	= qry[0]['sec_inherit']
      self.s_mngt_str	= qry[0]['s_mngt_str']
      self.mngt		= qry[0]['mngt']
      self.found = 1
    return

  def sub_ou_list(self):
    """Return a list of ou_structrec objects that are children of this ou_struct instance.
    Also instantiates the genericlist with ou_structrec objects.
      These are generic ou_structrec objects that can be children"""
    self.children = []
    self.genericlist = []
    qry = self.database.query("SELECT ou_struct FROM ou_struct WHERE parent_id = %d" %\
      self.ou_struct)
    for r in qry:
      self.children.append(ou_structrec(self.database, r["ou_struct"]))

    qry = self.database.query("SELECT ou_struct FROM ou_struct WHERE heirarchic = 0")
    for r in qry:
      self.generic_list.append(ou_structrec(self.database, r["ou_struct"]))

    return self.children

  def award_list(self):
    """Return a list of awardrec objects relevant to this struct type.
    Instantiates the awardlist data attribute and sorts it by name"""
    curs = self.database.database.cursor()
    curs.execute("SELECT a.award_id FROM award a, award_type t WHERE t.ou_struct = %d AND a.award_type = t.award_type" % self.ou_struct)
 
    self.awardlist = []
    qry = curs.fetchall()
    for r in qry:
      self.awardlist.append(awardrec(self.database, r[0]))

    self.awardlist = sort_by_attr(self.awardlist, 'name')
    return self.awardlist

  def award_types_list(self):
    """Instantiates the awardtypes list with awardtyperec objects and returns it"""
    self.awardtypes = []
    curs = self.database.database.cursor()
    curs.execute("SELECT award_type FROM award_type WHERE ou_struct = %d" % self.ou_struct)
    qry = curs.fetchall()
    for t in qry:
      self.awardtypes.append(awardtyperec(self.database, t[0]))
    return self.awardtypes


##############################################################################
class ou_disprec:
  """A class to abstract the ou_disp database record.
  This record stores display information about an ourec that is relevant to a person
  that is logged in as indicated by the connectrec"""
  def __init__(self, db, nOu_id, nConn_id):
    """Instantiates the ou_disprec with the data attributes as follows:
    database  database object
    ou_id - ID of relevant OU
    conn_id ID of connectrec
    show_actions
    expand_ou
    all_members
    found
    exp_ou - Empty list

"""
    self.database = db
    self.ou_id = nOu_id
    self.conn_id = nConn_id
    self.show_actions = 0
    self.expand_ou = ''
    self.all_members = 0
    self.found = 0
    self.exp_ou = []
    curs = db.database.cursor()
    curs.execute("SELECT ou_id, conn_id, show_actions, expand_ou, all_members FROM ou_disp\
      WHERE ou_id = %d AND conn_id = %d" % (self.ou_id, self.conn_id))

    if curs.rowcount:
      lRow = curs.fetchone()
      self.show_actions = lRow[2]
      self.expand_ou = lRow[3]
      self.all_members = lRow[4]
      self.exp_ou = eval(self.expand_ou)
    return

  def update(self):
    """Updates the database record for this ourec and connectrec"""
    self.expand_ou = self.exp_ou.__repr__()
    # Check if the record exists
    curs = self.database.database.cursor()
    curs.execute("SELECT ou_id FROM ou_disp WHERE ou_id = %d AND conn_id = %d" %\
        (self.ou_id, self.conn_id))
    if curs.rowcount:
      curs.execute("UPDATE ou_disp SET show_actions = %d, expand_ou = '%s',\
           all_members = %d WHERE ou_id = %d AND conn_id = %d" %\
          (self.show_actions, self.expand_ou, self.all_members, self.ou_id, self.conn_id))
    else:
      #Record does not exist
      curs.execute("INSERT INTO ou_disp (ou_id, conn_id, show_actions, expand_ou,\
          all_members) VALUES (%d, %d, %d, '%s', %d)" %\
          (self.ou_id, self.conn_id, self.show_actions, self.expand_ou, self.all_members))
    self.database.database.commit()
    return

  def delete(self):
    """Deletes accociated ou_disprec"""
    curs = self.database.database.cursor()
    curs.execute("DELETE FROM ou_disp WHERE ou_id = %d AND conn_id = %d" %\
        (self.ou_id, self.conn_id))
    self.database.database.commit()
    return 

##############################################################################
class personrec:
  """Base class for people records. This class is extended by scoutrec and
 adultrec clases"""
  def __init__(self, db, nScout_id):
    """Instantiates the object.
Parameter
  nScout_id - ID of the person (scout table) record to be accessed
Data attributes
  From database record
    scout_id
    forename
    initials
    surname
    addr1
    addr2
    addr3
    p_code
    telephone_h
    telephone_w
    fax
    mobile
    email
    on_line_id = ''
    scout_name = ''
    gender = ''
    add_info = ''
    date_of_birth = ''
    status = ''
 

  Other
    years = 0
    months = 0
    age = 0.0
    dob = datetime.date(1990, 1, 1)
    achievelist - Empty list of associated achieverec objects. set by achieve_list() method
    achieve_wiplist - Empty list of associated achieverec objects. set by achieve_wip_list() method
    award_todolist - Empty list of associated awardrec objects. set by all_award_info() method
    rolelist - Empty list of associated rolerec objects. set by role_list() method
    found - set to 1 if record found
    junior - set by check_junior() method, is 1 if person should be treated as a junior
"""
    self.database = db
    self.scout_id = nScout_id
    self.forename = ''
    self.initials = ''
    self.surname = ''
    self.addr1 = ''
    self.addr2 = ''
    self.addr3 = ''
    self.p_code = ''
    self.telephone_h = ''
    self.telephone_w = ''
    self.fax = ''
    self.mobile = ''
    self.email = ''
    self.on_line_id = ''
    self.scout_name = ''
    self.gender = ''
    self.add_info = ''
    self.years = 0
    self.months = 0
    self.age = 0.0
    self.date_of_birth = ''
    self.dob = datetime.date(1990, 1, 1)
    self.status = ''
    self.achievelist = []
    self.achieve_wiplist = []
    self.award_todolist = []
    self.rolelist = []
    dToday = datetime.date(1990, 1, 1).today()
    self.found = 0
    qry = self.database.query("SELECT * FROM scout WHERE scout_id = %d" % nScout_id)
    if len(qry):
      self.found = 1
      self.forename 	= qry[0]['forename']
      self.initials 	= qry[0]['initials']
      self.surname 	= qry[0]['surname']
      self.mobile 	= qry[0]['mobile']
      self.email 	= qry[0]['email']
      self.on_line_id	= qry[0]['on_line_id']
      self.date_of_birth = qry[0]['date_of_birth']
      self.scout_name   = qry[0]['scout_name']
      self.add_info     = qry[0]['add_info']
      self.gender       = qry[0]['gender']
      self.status       = qry[0]['status']
      if self.date_of_birth is not None:
        sDate 		= self.date_of_birth.split('-')
        self.dob 	= datetime.date(int(sDate[0]), int(sDate[1]), int(sDate[2]))
        tempage = dToday - self.dob
        self.years = int(tempage.days/365)
        self.months = (tempage.days - (self.years * 365)) / 30
        self.age = tempage.days / 365.0
    return

  def role_list(self, status=''):
    """Populates the rolelist data attribute with rolerec objects"""
    self.rolelist = []
    curs = self.database.database.cursor()
    curs.execute("SELECT role_id, ou_id, status FROM role\
      WHERE scout_id = %d ORDER BY ou_order" % (self.scout_id))
    #Check if any records returned
    if curs.rowcount:
      #Get the rows returned
      rows = curs.fetchall()
      for row in rows:
        #if the status is blank, return all records
        if status == '' or status is None:
          self.rolelist.append(rolerec(self.database, row[0]))
        elif status == row[2]:
          #otherwise just those with the same status
          self.rolelist.append(rolerec(self.database, row[0]))
    return self.rolelist

  def role_by_ou(self, ou_id):
    """Returns a role record for an ou and a person if it exists"""
    nRole = 0
    curs = self.database.database.cursor()
    curs.execute("SELECT role_id FROM role\
      WHERE scout_id = %d AND ou_id = %d" % (self.scout_id, ou_id))
    if curs.rowcount:
      value = curs.fetchone()
      nRole = value[0]
    return rolerec(self.database, nRole)
 
  def achieve_list(self):
    """Returns a list of achievements"""
    curs = self.database.database.cursor()
    self.achievelist = []
    # If the rolelist is not populated we must do so
    #if not len(self.rolelist):
    #  self.rolelist()
    curs.execute("SELECT * FROM achieve where scout_id = %d AND status = 'H'"\
        % self.scout_id)
    dQry = curs.fetchall()
    for a in dQry:
      ach = achieverec(self.database, self.scout_id, a[1])
      self.achievelist.append(ach)

    self.achievelist = sort_by_attr(self.achievelist, 'name')
    return self.achievelist

  def achieve_wip_list(self):
    """Returns list of achievements in WIP status """

    self.achieve_wiplist = []
    self.cStr = "SELECT * FROM achieve where scout_id = %d AND status = 'W'" % self.scout_id
    dQry = self.database.query(self.cStr)
    for a in dQry:
      self.achieve_wiplist.append(achieverec(self.database, self.scout_id, a['award_id']))
    return self.achieve_wiplist

  def all_award_info(self):
    """Collates all award and achievement info """

    curs = self.database.database.cursor()
    #populate achievement lists
    self.achieve_list()
    self.achieve_wip_list()
    self.role_list(status = 'C')

    # Need awards for all current roles
    for role in self.rolelist:
      #First check the ou the role is in
      ou_rec = ourec(self.database, role.ou_id)
      self.award_tbd(ou_rec, curs, self.achievelist, self.achieve_wiplist,\
          self.award_todolist)

      # Then get the ou heirarchy and check all senior OU's
      if not ou_rec.mngt:
        # Check upper level hioerarchy, but only if not a mngt ou
        ou_rec.ou_owners()
        for o in ou_rec.ouowners:
          self.award_tbd(o, curs, self.achievelist, self.achieve_wiplist,\
              self.award_todolist)

    return 

##########################################################################
  def award_tbd(self, ou, curs, ach_list, ach_wiplist, awd_todolist):
    """Checks for awards available to the ou that have not been achieved or worked on"""

    # 
    curs.execute("SELECT a.award_id, a.name, a.prereq FROM\
        award a, award_type t WHERE\
        a.award_type = t.award_type AND t.ou_struct = %d ORDER BY name"\
        % ou.ou_struct)

    dQry = curs.fetchall()

    for a in dQry:
      add_award = 1 
      prereq = 1
      if a[2] > 0:
        #set prereq flag off
        prereq = 0

      # dont add if award already achieved
      for b in ach_list:
        if b.award_id == a[0]:
          add_award = 0
          break
        # if the achived award is a pre requisite set the flag
        if a[2] == b.award_id:
          prereq = 1

      # dont add if it is work in progress
      for b in ach_wiplist:
        if b.award_id == a[0]:
          add_award = 0
          break

      if add_award and prereq:
        awd_todolist.append(awardrec(self.database, a[0]))
    return


##############################################################################
  def check_junior(self, ourec, param):
    """This procedure determines if a persn should be treated as a junior, i.e. needs guardians
It requires the ou instance to see if this is only for juniors
and also the param object to check which age someone should be a junior"""

    # Let's work out if this is a junior or an adult
    # Start off assuming the scout is an adult
    self.junior = 0
    if ourec.junior:
      # if the ourec is only for juniors this person must be a junior
      self.junior = 1

    if self.years:
      if self.years < param.junior_age:
        # age is less than an adult
        self.junior = 1
    return

##############################################################################
class scoutrec(personrec):
  " A class to abstract the scout record"
  def __init__(self, db, nScout_id):
    """Instantiates the scout record and sets the following data attributes that are in addition to the personrec instance
  
    parent1 - ID of adultrec, first parent of the scout
    parent1_forename - Name from the above adultrec
    parent1_surname - Ditto
    parent2 - ID of adultrec, second parent, if they exist
    parent2_forename - Name from the above adultrec
    parent2_surname - Ditto
    school ('') - School attended
  Obsolete entries not to be used
    unit_id = 0
    unit_sect = ''
    sect_cd = ''
    ou_id = 0
 
"""
    self.database = db
    self.scout_id = nScout_id
    self.forename = ''
    self.initials = ''
    self.surname = ''
    self.unit_id = 0
    self.unit_sect = ''
    self.addr1 = ''
    self.addr2 = ''
    self.addr3 = ''
    self.p_code = ''
    self.telephone_h = ''
    self.telephone_w = ''
    self.fax = ''
    self.mobile = ''
    self.email = ''
    self.parent1 = 0
    self.parent1_forename = ''
    self.parent1_surname = ''
    self.parent2 = 0
    self.parent2_forename = ''
    self.parent2_surname = ''
    self.on_line_id = ''
    self.scout_name = ''
    self.school = ''
    self.gender = ''
    self.add_info = ''
    self.years = 0
    self.months = 0
    self.age = 0.0
    self.date_of_birth = ''
    self.dob = datetime.date(1990, 1, 1)
    self.status = ''
    self.sect_cd = ''
    self.ou_id = 0
    self.achievelist = []
    self.achieve_wiplist = []
    self.award_todolist = []
    self.rolelist = []
    dToday = datetime.date(1990, 1, 1).today()
    qry = self.database.query("SELECT * FROM scout WHERE scout_id = %d" % nScout_id)
    if len(qry) == 0:
      self.found = 0
    else:
      self.found = 1
      self.forename 	= qry[0]['forename']
      self.initials 	= qry[0]['initials']
      self.surname 	= qry[0]['surname']
      self.unit_id	= qry[0]['unit_id']
      self.mobile 	= qry[0]['mobile']
      self.email 	= qry[0]['email']
      self.parent1 	= qry[0]['parent1']
      self.parent2	= qry[0]['parent2']
      self.on_line_id	= qry[0]['on_line_id']
      self.date_of_birth = qry[0]['date_of_birth']
      self.scout_name   = qry[0]['scout_name']
      self.add_info     = qry[0]['add_info']
      self.school       = qry[0]['school']
      self.gender       = qry[0]['gender']
      self.status       = qry[0]['status']
      self.addr1        = qry[0]['addr1']
      self.addr2        = qry[0]['addr2']
      self.addr3        = qry[0]['addr3']
      self.p_code       = qry[0]['p_code']
      self.telephone_w  = qry[0]['telephone_w']
      self.telephone_h  = qry[0]['telephone_h']
      self.fax		= qry[0]['fax']
      if self.date_of_birth is not None:
        sDate 		= self.date_of_birth.split('-')
        self.dob 	= datetime.date(int(sDate[0]), int(sDate[1]), int(sDate[2]))
        tempage = dToday - self.dob
        self.years = int(tempage.days/365)
        self.months = (tempage.days - (self.years * 365)) / 30
        self.age = tempage.days / 365.0

      #Get primary org unit details
      qry = self.database.query("SELECT * FROM role WHERE scout_id = %d AND status = 'C' ORDER BY ou_order LIMIT 1" % nScout_id)
      #if len(qry):


      # get parent details
      if self.parent1 is not None:
        pqry = self.database.query("SELECT * FROM scout WHERE scout_id = " + str(self.parent1))
        if len(pqry) > 0:
          self.addr1 		= pqry[0]['addr1']
          self.addr2 		= pqry[0]['addr2']
          self.addr3 		= pqry[0]['addr3']
          self.p_code		= pqry[0]['p_code']
          self.telephone_h 	= pqry[0]['telephone_h']
          self.telephone_w 	= pqry[0]['telephone_w']
          self.fax 		= pqry[0]['fax']
          self.parent1_forename = pqry[0]['forename']
          self.parent1_surname  = pqry[0]['surname']

      # Secondary parent details
      if self.parent2 is not None:
        pqry = self.database.query("SELECT * FROM scout WHERE scout_id = " + str(self.parent2))
        if len(pqry) > 0:
          self.parent2_forename 	= pqry[0]['forename']
          self.parent2_surname  	= pqry[0]['surname']

      pqry = self.database.query("SELECT ou_id FROM role WHERE scout_id = %d AND ou_order = 1" % self.scout_id)
      if len(pqry):
        self.ou_id = pqry[0]['ou_id']
    return

  def update(self):
    """Method to update scout record"""
    curs = self.database.database.cursor()
    dToday = datetime.date(1990, 1, 1).today()
    # Validate gender field
    self.gender = self.gender.upper()
    if string.find('MF', self.gender) == -1:
      self.gender = ''
    self.result = ''
    upd = "UPDATE scout SET forename = '%s', initials = '%s', surname = '%s', mobile = '%s',\
        email = '%s', addr1 = '%s', addr2 = '%s', addr3 = '%s', p_code = '%s',\
        on_line_id = '%s', add_info = '%s', school = '%s', gender = '%s'" %\
        (sql_str(self.forename), sql_str(self.initials), sql_str(self.surname),\
        sql_str(self.mobile), sql_str(self.email), sql_str(self.addr1), sql_str(self.addr2),\
        sql_str(self.addr3), sql_str(self.p_code), sql_str(self.on_line_id),\
        sql_str(self.add_info), sql_str(self.school), sql_str(self.gender))
    if self.parent1 is not None:
      upd += ", parent1 = %d" % self.parent1
    if self.parent2 is not None:
      upd += ", parent2 = %d" % self.parent2
    if self.unit_id is not None and self.unit_id != 0:
      upd += ", unit_id = %d" % str(self.unit_id)

    if sql_str(self.date_of_birth) != '':
      upd += ", date_of_birth = '%s'" % sql_str(self.date_of_birth)
      # split the field in to yyyy, mm, dd components
      sDate 		= self.date_of_birth.split('-')
      # create datetime.date field
      self.dob 	= datetime.date(int(sDate[0]), int(sDate[1]), int(sDate[2]))
      temp_age = dToday - self.dob
      # calculate age in differing forms
      self.years = int(temp_age.days/365)
      self.months = (temp_age.days - (self.years * 365)) / 30
      self.age = temp_age.days / 365
    upd += " WHERE scout_id = " + str(self.scout_id)

    curs.execute(upd)

    #log_action(self.database, 21, cMnf, cProd)

  def add(self):
    """Creates a new scout record """
    dToday = datetime.date(1990, 1, 1).today()
    # Validate gender field
    if self.gender is None:
      self.gender = ' '
    self.gender = self.gender.upper()
    if string.find('MF', self.gender) == -1:
      self.gender = ''

    # first we get the next scout_id from the scout_seq sequence
    qry = self.database.query("SELECT nextval('scout_seq')")
    self.scout_id = int(qry[0]['nextval'])
    # Now build the insert query
    cInsert_str = "INSERT INTO scout (scout_id, forename, initials, surname, unit_id, unit_since, mobile, email, date_of_birth, school, gender, parent1, parent2, add_info, status) VALUES ("
    cInsert_str += str(self.scout_id) + ", '"
    cInsert_str += sql_str(self.forename) + "', '"
    cInsert_str += sql_str(self.initials) + "', '"
    cInsert_str += sql_str(self.surname) + "', "
    cInsert_str += str(self.unit_id) + ", '"
    cInsert_str += str(dToday) + "', '"
    cInsert_str += sql_str(self.mobile) + "', '"
    cInsert_str += sql_str(self.email) + "', '"
    cInsert_str += sql_str(self.date_of_birth) + "', '"
    cInsert_str += sql_str(self.school) + "', '"
    cInsert_str += sql_str(self.gender) + "', "
    cInsert_str += procs.pr_str(self.parent1) + ", "
    if self.parent2 is not None:
      cInsert_str += procs.pr_str(self.parent2) + ", '"
    else:
      cInsert_str += "0, '"
    cInsert_str += sql_str(self.add_info) + "', 'C')"
    self.database.query(cInsert_str)

  def find_on_line_id(self, cOn_line_id):
    """Returns of scout id if on-line_id found, otherwise 0 """
    self.scout_id = 0
    try:
      qry = self.database.query("SELECT * FROM scout WHERE on_line_id = '" + cOn_line_id + "'")
    except ValueError:
      self.scout_id = 0
    if len(qry) == 0:
      self.scout_id = 0
    else:
      self.scout_id = qry[0]['scout_id']
    return self.scout_id

  def ch_status(self, new_status):
    """Changes status of scout and updated the status change date """
    dToday = datetime.date(1990, 1, 1).today()
    if string.find('CL', new_status) != -1:
      cQry = "UPDATE scout SET status = '" + new_status + "', status_dt = '" + str(dToday) + "' WHERE scout_id = " + str(self.scout_id) 
      self.database.query(cQry)

  def set_unit(self, new_unit):
    """Sets the unit connection for a scout record """
    dToday = datetime.date(1990, 1, 1).today()
    unit = unitrec(self.database, new_unit)
    if unit.found:
      cQry = "UPDATE scout SET unit_id = '" + str(new_unit) + "', unit_since = '" + str(dToday) + "' WHERE scout_id = " + str(self.scout_id) 
      self.database.query(cQry)


##############################################################################
class adultrec(personrec):
  " A class to abstract an adult record"
  def __init__(self, db, nScout_id):
    """Instatiates the instance and populates the following data attributes IN ADDITION
  to those populated by personrec.
Data Attributes
    passwd - Password (hashed)
    oldpasswd - Previous password (hashed)
    pw_hint - Password hint
    online_agree_dt Date of online agreement
    partner_id (0) - ID of partner if defined
    partner_forename - Forename of partner (if defined)
    partner_initials = Partner initials
    partner_surname - Partner surname
    home_level - No longer used
    home_id - No longer used
    home_ou_id - ID of home OU
    superuser (0) - Set to 1 if a superuser
    email_bounce - Not yet used
    kidlist = [] - List of children of this adult, populated by kids_list()

"""
    self.database = db
    self.scout_id = nScout_id
    self.forename = ''
    self.initials = ''
    self.surname = ''
    self.addr1 = ''
    self.addr2 = ''
    self.addr3 = ''
    self.p_code = ''
    self.date_of_birth = ''
    self.telephone_h = ''
    self.telephone_w = ''
    self.fax = ''
    self.mobile = ''
    self.email = ''
    self.email_bounce = 0
    self.on_line_id = ''
    self.passwd = ''
    self.oldpasswd = ''
    self.pw_hint = ''
    self.online_agree_dt = ''
    self.scout_name = ''
    self.gender = ''
    self.add_info = ''
    self.partner_id = 0
    self.partner_forename = ''
    self.partner_initials = ''
    self.partner_surname = ''
    self.found = 0
    self.home_level = ''
    self.home_id = 0
    self.home_ou_id = 0
    self.superuser = 0
    self.achievelist = []
    self.achieve_wiplist = []
    self.award_todolist = []
    self.kidlist = []
    if nScout_id is None:
      return
    try:
      qry = self.database.query("SELECT * FROM scout WHERE scout_id = " + str(nScout_id))
      self.found = 1
    except ValueError:
      self.found = 0
    if len(qry) == 0:
      self.found = 0
    else:
      self.found = 1
      self.forename 	= qry[0]['forename']
      self.initials 	= qry[0]['initials']
      self.surname 	= qry[0]['surname']
      self.mobile 	= qry[0]['mobile']
      self.email 	= qry[0]['email']
      self.addr1 	= qry[0]['addr1']
      self.addr2 	= qry[0]['addr2']
      self.addr3 	= qry[0]['addr3']
      self.p_code 	= qry[0]['p_code']
      self.date_of_birth= qry[0]['date_of_birth']
      self.telephone_h 	= qry[0]['telephone_h']
      self.telephone_w 	= qry[0]['telephone_w']
      self.fax	 	= qry[0]['fax']
      self.on_line_id	= qry[0]['on_line_id']
      self.date_of_birth = qry[0]['date_of_birth']
      self.scout_name   = qry[0]['scout_name']
      self.partner_id   = qry[0]['partner_id']
      self.gender       = qry[0]['gender']
      self.add_info     = qry[0]['add_info']
      self.passwd 	= qry[0]["passwd"]
      self.oldpasswd 	= qry[0]["oldpasswd"]
      self.pw_hint 	= qry[0]["pw_hint"]
      self.online_agree_dt = qry[0]["online_agree_dt"]
      self.home_level 	= qry[0]["home_level"]
      self.email_bounce	= qry[0]["email_bounce"]
      if qry[0]["home_id"] is not None:
        self.home_id 	= int(qry[0]["home_id"])
      else:
        self.home_id = 0
      if qry[0]["home_ou_id"] is not None:
        self.home_ou_id 	= int(qry[0]["home_ou_id"])

      if qry[0]['superuser'] == 't':
        self.superuser = 1

      if self.partner_id is not None and self.partner_id > 0:
        qry = self.database.query("SELECT * FROM scout WHERE scout_id = " + str(self.partner_id))
        if len(qry) > 0:
          self.partner_forename	= qry[0]['forename']
          self.partner_initials	= qry[0]['initials']
          self.partner_surname 	= qry[0]['surname']
 
    return

  def update(self):
    """Method to update adult scout record"""
    if self.gender is not None:
      self.gender = self.gender.upper()
    else:
      self.gender = ''
    if string.find('MF', self.gender) == -1:
      self.gender = ''
    self.result = ''
    upd_string = "UPDATE scout SET forename = '" + sql_str(self.forename)
    upd_string += "', initials = '" + sql_str(self.initials)
    upd_string += "', surname = '" + sql_str(self.surname)
    upd_string += "', addr1 = '" + sql_str(self.addr1)
    upd_string += "', addr2 = '" + sql_str(self.addr2)
    upd_string += "', addr3 = '" + sql_str(self.addr3)
    upd_string += "', p_code = '" + sql_str(self.p_code)
    upd_string += "', telephone_h = '" + sql_str(self.telephone_h)
    upd_string += "', telephone_w = '" + sql_str(self.telephone_w)
    upd_string += "', fax = '" + sql_str(self.fax)
    upd_string += "', mobile = '" + sql_str(self.mobile)
    upd_string += "', email_bounce = " + str(self.email_bounce)
    upd_string += ", email = '" + sql_str(self.email)
    if sql_str(self.date_of_birth) != '':
      upd_string += "', date_of_birth = '" + sql_str(self.date_of_birth)
    upd_string += "', on_line_id = '" + sql_str(self.on_line_id)
    upd_string += "', partner_id = " + sql_int_str(self.partner_id)
    upd_string += ", gender = '" + sql_str(self.gender)
    upd_string += "', pw_hint = '" + sql_str(self.pw_hint)
    upd_string += "', home_level = '" + sql_str(self.home_level)
    upd_string += "', home_id = " + sql_int_str(self.home_id)
    upd_string += ", home_ou_id = " + sql_int_str(self.home_ou_id)
    upd_string += ", add_info = '" + sql_str(self.add_info)
    if sql_str(self.online_agree_dt) != '':
      upd_string += "', online_agree_dt = '" + sql_str(self.online_agree_dt)
    upd_string += "', status = 'A' WHERE scout_id = " + str(self.scout_id)
    self.database.query(upd_string)
    #log_action(self.database, 21, cMnf, cProd)

  def add(self):
    """Creates a new adult scout / parent record """

    # first we get the next scout_id from the scout_seq sequence
    qry = self.database.query("SELECT nextval('scout_seq')")
    self.scout_id = int(qry[0]['nextval'])
    # Now build the insert query
    self.gender = self.gender.upper()
    if string.find('MF', self.gender) == -1:
      self.gender = ''
    cInsert_str = "INSERT INTO scout (scout_id, forename, initials, surname, addr1, addr2, addr3, p_code, telephone_h, telephone_w, mobile, email, partner_id, gender, add_info, status, home_ou_id) VALUES ("
    cInsert_str += str(self.scout_id) + ", '"
    cInsert_str += sql_str(self.forename) + "', '"
    cInsert_str += sql_str(self.initials) + "', '"
    cInsert_str += sql_str(self.surname) + "', '"
    cInsert_str += sql_str(self.addr1) + "', '"
    cInsert_str += sql_str(self.addr2) + "', '"
    cInsert_str += sql_str(self.addr3) + "', '"
    cInsert_str += sql_str(self.p_code) + "', '"
    cInsert_str += sql_str(self.telephone_h) + "', '"
    cInsert_str += sql_str(self.telephone_w) + "', '"
    cInsert_str += sql_str(self.mobile) + "', '"
    cInsert_str += sql_str(self.email) + "', "
    cInsert_str += sql_int_str(self.partner_id) + ", '"
    cInsert_str += sql_int_str(self.gender) + "', '"
    cInsert_str += sql_str(self.add_info) + "', 'A', 0)"

    self.database.query(cInsert_str)


  def find_on_line_id(self, cOn_line_id):
    """Returns of scout id if on-line_id found, otherwise 0 """
    self.scout_id = 0
    try:
      qry = self.database.query("SELECT * FROM scout WHERE on_line_id = '" + cOn_line_id + "'")
    except ValueError:
      self.scout_id = 0
    if len(qry) == 0:
      self.scout_id = 0
    else:
      self.scout_id = qry[0]['scout_id']
    return self.scout_id

  def find_email(self, cEmail):
    """Returns of scout id if email address is found, otherwise 0 """
    self.scout_id = 0
    try:
      qry = self.database.query("SELECT * FROM scout WHERE email = '" + cEmail + "'")
    except ValueError:
      self.scout_id = 0
    if len(qry) == 0:
      self.scout_id = 0
    else:
      self.scout_id = qry[0]['scout_id']
    return self.scout_id

  def kids_list(self):
    """Returns a list of scoutrec instances that list this adultrec as a parent"""
    cQry = "SELECT scout_id FROM scout WHERE parent1 = " + str(self.scout_id)+ " OR parent2 = " + str(self.scout_id)
    self.kidlist = []
    qry = self.database.query(cQry)
    for k in qry:
      self.kidlist.append(scoutrec(self.database, k["scout_id"]))
    return self.kidlist

  def check_pw(self, passwd):
    """Checks if password matches hash value"""
    hash = sha.new(string.strip(passwd))

    if self.passwd is None or self.passwd == '':
      if string.strip(passwd) == '':
        return 1

    if hash.hexdigest() == self.passwd:
      return 1
    else:
      return 0

  def update_pw(self, passwd, oldpasswd, superuser):
    """Updates password related fields"""
    pw = string.strip(passwd)
    oldpw = string.strip(oldpasswd)

    hash = sha.new(pw)
    oldhash = sha.new(oldpw)
    update = 0

    # Must change the password
    #if passwd == oldpasswd:
    #  return 2

    # Password must not be current or most recent password
    #if hash.hexdigest() == self.passwd or hash.hexdigest() == self.oldpasswd:
    #  return 3

    # If a password previously existed
    if self.passwd is None or self.passwd != '':
      update = 1
    else:
      # Old password must be the current PW
      if oldhash.hexdigest() == self.passwd:
        update = 1

    # If superuser doing the change, previous checks not needed
    if superuser:
      update = 1

    if update:
      upd_string = "UPDATE scout SET passwd = '"
      upd_string += hash.hexdigest() + "', oldpasswd = '"
      upd_string += oldhash.hexdigest() 
      upd_string += "' WHERE scout_id = " + str(self.scout_id)
      self.database.query(upd_string)
      self.oldpasswd = self.passwd
      self.passwd = hash.hexdigest()

    return update


#############################################################################
class rolerec:
  " A class to abstract the role record"
  def __init__(self, db, nRole_id):
    """Instantiates the object and sets the following data attributes
Database
    role_id (nRole_id from params) - Role ID
    scout_id (0) - Scout ID associated with the role
    ou_id (0) - OU id this role references
    security (0) - Integer indicatng level of security available
                   Need further documentation
    title ('') - Display title
    last_update - Date
    dt_appt - Creation date
    role_ref (0) - Integer
                   Needs furter documentation
    forename ('') - Obtained from scout table
    initials ('') - Obtained from scout table
    surname ('') - Obtained from scout table
    status ('') - Role status. Allowed values are ???
    ou_order = 1

Other
    database - DB instance from params
    found (0) - Set to 1 if record found
    result = ''
 
 """
    self.database = db
    self.role_id = nRole_id
    self.scout_id = 0
    self.security = 0
    self.title = ''
    self.last_update = ''
    self.dt_appt = ''
    self.role_ref = 0
    self.forename = ''
    self.initials = ''
    self.surname = ''
    self.status = ''
    self.ou_id = 0
    self.ou_order = 1
    self.found = 0
    self.result = ''
    
    qry = self.database.query("SELECT * FROM role WHERE role_id = " + str(nRole_id))
    if len(qry) == 0:
      self.found = 0
    else:
      self.found 	= 1
      self.role_id 	= qry[0]['role_id']
      self.scout_id 	= qry[0]['scout_id']
      self.security 	= qry[0]['security']
      self.title 	= qry[0]['title']
      self.last_update 	= qry[0]['last_update']
      self.dt_appt 	= qry[0]['dt_appt']
      self.ou_id        = qry[0]['ou_id']
      self.ou_order     = qry[0]['ou_order']
      self.status       = qry[0]['status']

      # get scout details
      uqry = self.database.query("SELECT forename, initials, surname, email, email_bounce FROM scout WHERE scout_id = " + str(self.scout_id))
      if len(uqry) > 0:
        self.forename = uqry[0]['forename']
        self.initials = uqry[0]['initials']
        self.surname = uqry[0]['surname']
        self.email = uqry[0]['email']
        self.email_bounce = uqry[0]['email_bounce']
    return

  def find_role(self, ou_id, scout_id):
    """This function searches the database for the role record for this scout_id and ou_id
The usual attributes are set as in __init__()"""
    qry = self.database.query("SELECT * FROM role WHERE ou_id = %d AND scout_id = %d" % (ou_id, scout_id))
    if len(qry) == 0:
      self.found = 0
    else:
      self.found 	= 1
      self.role_id 	= qry[0]['role_id']
      self.scout_id 	= qry[0]['scout_id']
      self.security 	= qry[0]['security']
      self.title 	= qry[0]['title']
      self.last_update 	= qry[0]['last_update']
      self.dt_appt 	= qry[0]['dt_appt']
      self.status 	= qry[0]['status']
      self.ou_id	= qry[0]['ou_id']
      self.ou_order	= qry[0]['ou_order']

      # get scout details
      uqry = self.database.query("SELECT forename, initials, surname FROM scout WHERE scout_id = " + str(self.scout_id))
      if len(uqry) > 0:
        self.found = 1
        self.forename = uqry[0]['forename']
        self.initials = uqry[0]['initials']
        self.surname = uqry[0]['surname']
    return


  def update(self):
    """Here for legacy reasons, simply calls add_update()"""
    self.add_edit()

  def add(self):
    """Here for legacy reasons, simply calls add_update()"""
    self.add_edit()

  def add_edit(self):
    role_id = 0
    order = 0
    orig_exists = 0		# set if original record exists
    ou_id_exists = 0
    change_ou = 0		# Set to one if a ou_id change occurs
    ou_id_role_id = 0		# store role_id of existing record for that ou_id
    curs = self.database.database.cursor()
    # Get original values
    curs.execute("SELECT role_id, ou_id, scout_id, ou_order, status FROM role WHERE role_id = %d" %\
        self.role_id)
    if curs.rowcount:
      orig_exists = 1
      original = curs.fetchone()
      if self.ou_id != original[1]:
        change_ou = 1


    curs.execute("SELECT role_id, ou_order FROM role WHERE ou_id = %d AND scout_id = %d" %\
        (self.ou_id, self.scout_id))
    # If ou_id and scout_id exists
    if curs.rowcount:
      row = curs.fetchone()
      role_id = row[0]
      order = row[1]

    #Now get all role records for the person
    curs.execute("SELECT role_id, ou_id, ou_order, status FROM role WHERE scout_id = %d ORDER BY ou_order" %\
        self.scout_id)
    # Does our order number already exist?
    roles = curs.fetchall()
    nCnt = 0
    nConflict = 0
    order_conflict = 0
    ou_id_conflict = 0
    for role in roles:
      #Check to see if that order number exists
      if role[2] == self.ou_order:
        # store conflicting role_id
        order_conflict = role[0]
        nConflict = nCnt
      nCnt += 1
      # check to see if a record for that ou_id exists
      if role[1] == self.ou_id:
        ou_id_role_id = role[0]


    if nConflict:
      # some fancy processing here as we need to shuffle the ou_order values
      next_order = self.ou_order + 10
      for x in range(nConflict, len(roles)):
        # all roles after this one will be incremented by 10
        curs.execute("UPDATE role SET ou_order = %d WHERE role_id = %d" % (next_order, roles[x][0]))
        next_order = next_order + 10

    #If original record exists
    if orig_exists:
      # Ahah, but has the ou_id changed?
      if change_ou:
        #does this scout have a role record for this ou_id, if so update it
        if ou_id_role_id:
          # delete the old one then
          curs.execute("DELETE FROM role WHERE role_id = %d" % self.role_id)
          # and update the existing one
          upd_string = "UPDATE role SET ou_order = %d, security = %d,\
            title = '%s', last_update = '%s', status = '%s' WHERE role_id = %d" %\
            (self.ou_order, self.security, sql_str(self.title),\
            time.strftime("%Y%m%d %H:%M:%S", time.localtime()), self.status, ou_id_role_id)
          curs.execute(upd_string)
          self.role_id = ou_id_role_id
        else:
          # Change the ou_id and the other fields
          upd_string = "UPDATE role SET ou_id = %d, ou_order = %d, security = %d,\
            title = '%s', last_update = '%s', status = '%s' WHERE role_id = %d" %\
            (self.ou_id, self.ou_order, self.security, sql_str(self.title),\
            time.strftime("%Y%m%d %H:%M:%S", time.localtime()), self.status, self.role_id)
          curs.execute(upd_string)
      else:
        #record exists and ou_id stays the same, update the other fields
        upd_string = "UPDATE role SET ou_order = %d, security = %d,\
          title = '%s', last_update = '%s', status = '%s' WHERE role_id = %d" %\
          (self.ou_order, self.security, sql_str(self.title),\
          time.strftime("%Y%m%d %H:%M:%S", time.localtime()), self.status, self.role_id)
        curs.execute(upd_string)

    else:
      #OK, the original record does not exist, this is something new, or is it
      if ou_id_role_id:
        #Does the person have another role rec with the right ou_id?, update it then
        upd_string = "UPDATE role SET ou_order = %d, security = %d,\
          title = '%s', last_update = '%s', status = '%s' WHERE role_id = %d" %\
          (self.ou_order, self.security, sql_str(self.title),\
          time.strftime("%Y%m%d %H:%M:%S", time.localtime()), self.status, ou_id_role_id)
        curs.execute(upd_string)
        self.role_id = ou_id_role_id
      else:
        # OK this is really new then?  
        upd_string = "INSERT INTO role (role_id, ou_id, ou_order, scout_id, security,\
          title, last_update, dt_appt, status)\
          VALUES (nextval('role_seq'), %d, %d, %d, %d, '%s', '%s', '%s', '%s')"\
          % (self.ou_id, self.ou_order, self.scout_id,\
          self.security, sql_str(self.title), time.strftime("%Y%m%d %H:%M:%S", time.localtime()),\
          time.strftime("%Y%m%d %H:%M:%S", time.localtime()), self.status)
        curs.execute(upd_string)

    # Now lets write all these changes to the database
    self.database.database.commit()

  def delete(self):
    """Deletes the role records from the database"""
    upd_string = "DELETE FROM role WHERE role_id = " + str(self.role_id)
    self.database.query(upd_string)
    #log_action(self.database, 21, cMnf, cProd)


    """
  def scout_list(self):
    self.scoutlist = []
    qry = self.database.query("SELECT scout_id FROM scout WHERE unit_id = " + str(self.unit_id) + " AND status = 'C' ORDER BY date_of_birth")
    for s in qry:
      self.scoutlist.append(scoutrec(self.database, s["scout_id"]))
    return self.scoutlist
    """

  def __str__(self):
    """Returns a string of attributes for printing"""
    return "<ROLE RECORD INFO>\nrole_id = %d\nscout_id = %d\nou_id = %d\
      \nsecurity = %d\ntitle = %s\nlast_update = %s\ndt_appt = %s\
      \nrole_ref = %d\nstatus = %s\nou_order = %d\nforename = %s\
      \ninitials = %s\nSurname = %s" %\
      (self.role_id, self.scout_id, self.ou_id, self.security, self.title,\
      self.last_update, self.dt_appt, self.role_ref, self.status, self.ou_order,\
      self.forename, self.initials, self.surname)


##############################################################################
class sectionrec:
  " A class to abstract the section record"
  def __init__(self, db, cSect_cd):
    self.database = db
    self.sect_cd = cSect_cd
    self.name = ''
    self.next_sect = ''
    self.start_age = 0
    self.end_age = 0
    self.collective = ''
    try:
      uqry = self.database.query("SELECT * FROM section WHERE sect_cd = '" + self.sect_cd + "'")
      self.found = 1
      self.name = uqry[0]['name']
      self.next_sect = uqry[0]['next_sect']
      self.start_age = uqry[0]['start_age']
      self.end_age = uqry[0]['end_age']
      self.collective = uqry[0]['collective']
    except ValueError:
      xx = 0
    return



##############################################################################
class connectrec:
  """Abstracts connection """
  def __init__(self, db):
    """Instantiates the connection record and sets the following data attributes
    database - DB instance from params
    found = connection record fouund in DB
    ref_id = reference Id
    auth_key = authentication key
    scout_id = scout ID
    last_access - last access time of connect 
    new_conn - set to 1 if this is a new connection
    sign_in - set to 1 if user is signed in
    last_level - Obsolete
    last_level_id - Obsolete
    home_level - Obsolete
    home_id - Obsolete
    last_ou_id = last ou page dealt with
    home_ou_id = ou_id of home page
    superuser - set to 1 if a superuser
    online_agree - set to 1 if online agreement agreed to
    name - fore name and surname
    write - allowed to write to this OU. Set in ou_security()
    read - allowed to read this OU, set as above
    add - allowed to add to this ou, set as above
    """
    self.database = db
    sCookie = os.environ.get("HTTP_COOKIE")
    self.found = 0
    self.ref_id = ''
    self.scout_id = 0
    self.last_access = ''
    self.auth_key = ''
    self.new_conn = 0
    self.sign_in = 0
    self.last_level = ' '
    self.last_level_id = 0
    self.home_level = ' '
    self.home_id = 0
    self.last_ou_id = 0
    self.home_ou_id = 0
    self.superuser = 0
    self.online_agree = 0
    self.name = ''
    self.write = 0
    self.read = 0
    self.add = 0
    self.display = ''

    dRef_dt = datetime.date(2004, 8,1) 
    curs = self.database.database.cursor()

##################
    if sCookie != None:
      # Get a list of cookies issued
      lCookies = string.split(sCookie, ';')
      for lC in lCookies:
        nlen = len(lCookies) - 1
        # Check last cookie
        lCook = string.split(lC, "=")
        self.ref_id = string.strip(lCook[0]) 
        self.auth_key = string.strip(lCook[1])
        # Get the connection record
        qstr = "SELECT ref_id, scout_id, auth_key, last_access, last_level,\
            last_level_id, last_ou_id FROM connection WHERE ref_id = '%s'" % self.ref_id
        curs.execute(qstr)
        if curs.rowcount:
          qry = curs.fetchone()
          if  qry[2] == self.auth_key:
            self.found = 1
            self.scout_id = qry[1]
            self.last_access = qry[3]
            self.last_level = qry[4]
            self.last_level_id = qry[5]
            self.last_ou_id = qry[6]
            if self.scout_id is not None:
              if self.scout_id > 0:
                self.sign_in = 1
          break

    if not self.found:
      self.new_conn = 1
      self.ref_id = rand_string(10)
      self.auth_key = rand_string(20)
      qstr = "INSERT INTO connection (ref_id, auth_key, scout_id) VALUES ('" + self.ref_id + "', '" + self.auth_key + "', 0)"
      try:
        self.database.query(qstr)
      except ValueError: 
        self.result = "Create error"

    # Update last access time
    qstr = "UPDATE connection SET last_access = '%s' WHERE ref_id = '%s' AND auth_key = '%s'" %\
      (time.strftime("%Y%m%d %H:%M:%S", time.localtime()), self.ref_id, self.auth_key)
    try:
      qry = self.database.query(qstr)
    except ValueError: 
      self.result = "Update Error"

    # Get the scout record if it exists so we can set security levels
    if self.scout_id > 0:
      qry = self.database.query("SELECT scout_id, superuser, home_level, home_id, home_ou_id,\
        online_agree_dt, forename, surname FROM scout WHERE scout_id = '"\
        + str(self.scout_id) + "'")
      if len(qry) > 0:
        self.name = qry[0]['forename'] + ' ' + qry[0]['surname']
	# Scout record found
        self.superuser = qry[0]['superuser']
        # get scouts home page
        if qry[0]["home_level"] is not None and qry[0]["home_id"] is not None:
          self.home_level = qry[0]["home_level"]
          self.home_id    = qry[0]["home_id"]
        if qry[0]["home_ou_id"] is not None:
          self.home_ou_id = qry[0]["home_ou_id"]
        if qry[0]["online_agree_dt"] is not None:
          sAgree = qry[0]["online_agree_dt"].split('-')
          dAgree = datetime.date(int(sAgree[0]), int(sAgree[1]), int(sAgree[2]))
          if dAgree > dRef_dt:
            self.online_agree = 1

  def logout(self):
    """ Method to update connection with the Logout sign """
    upd_string = "UPDATE connection SET scout_id = 0 WHERE ref_id = '" + self.ref_id + "'"
    self.sign_in = 0
    self.database.query(upd_string)

  def update(self):
    """ Method to update connection with the last accessed time """
    if self.last_level_id is None:
      self.last_level_id = 0
    upd_str = "UPDATE connection SET scout_id = %d, last_access = '%s', last_level = '%s',\
      last_level_id = %d, last_ou_id = %d WHERE ref_id = '%s'" % (self.scout_id,\
      curr_time(), self.last_level, self.last_level_id, self.last_ou_id, self.ref_id)
    if self.scout_id > 0:
      self.sign_in = 1
    else:
      self.sign_in = 0 
    self.database.query(upd_str)
    self.database.commit()

  def char_disp(self):
    cStr = "Conn_id: %d\n last_ou_id: %d\nSuperuser: %d" % (self.scout_id, self.last_ou_id, self.superuser)
    return cStr

  def ou_security(self, ou_id):
    "Checks on security access rights for a user for this OU"
    self.read = 0
    self.write = 0
    self.add = 0
    self.display = ''
    if self.superuser:
      self.read = self.write = self.add = 1

    #if scout_id exists (we're logged in)
    if self.scout_id:
      self.read = 1
    else:
      return
    self.display = 'Connection logged in, scout id = %d<BR>OU being initially interrogated = %d<BR>' % (self.scout_id, ou_id)
    curs = self.database.database.cursor()
   # we're going up the tree until we get an answer
    lTree = 1
    nCurr_ou = ou_id
    while lTree:
      curs.execute("SELECT o.ou_id, o.ou_owner, s.sec_inherit, o.ou_struct FROM ou o, ou_struct s\
          WHERE o.ou_id=%d AND o.ou_struct = s.ou_struct" % (nCurr_ou))
      if curs.rowcount:
        # get the ou details
        oqry = curs.fetchone()
        self.display += "Process OU %d, Owner = %d, Struct = %d, sec_inherit = %d<BR>"\
            % (nCurr_ou, oqry[1], oqry[3], oqry[2])
        curs.execute("SELECT ou_id, scout_id, security, status FROM role WHERE ou_id = %d AND\
            scout_id = %d" % (ou_id, self.scout_id))
        # is there a role record
        if curs.rowcount:
          rqry = curs.fetchone()
          self.display += "Role record found for %d, security = %d, Status = %s<BR>" % (nCurr_ou, rqry[2], rqry[3])
          # security > 1 and current
          if rqry[2] and rqry[3] == 'C':
            self.write = 1
            self.add = 1
            return
        else:
          # role record not found, lets check for a management record
          self.display += "No role record for %d, check for management OU<BR>" % nCurr_ou
          curs.execute("SELECT ou_id, ou_owner, ou_struct FROM ou WHERE ou_owner=%d AND mngt = 1" % (nCurr_ou))
          if curs.rowcount:
            mqry = curs.fetchone()
            mOu = mqry[0]
            self.display += "Management OU for %d is %d<BR>" % (nCurr_ou, mOu)
            curs.execute("SELECT ou_id, scout_id, security, status FROM role WHERE ou_id = %d AND\
                scout_id = %d" % (mOu, self.scout_id))
            if curs.rowcount:
              rqry = curs.fetchone()
              self.display += "Role record found for mngt %d, security = %d, Status = %s<BR>"\
                  % (mOu, rqry[2], rqry[3])
              # security > 1 and current
              if rqry[2] and rqry[3] == 'C':
                self.write = 1
                self.add = 1
                return        
            else:            
              self.display += "No role for Management OU %d<BR>" % (mOu)

        if oqry[2]:
          # sec_inherit set for this ou
          nCurr_ou = oqry[1]
        else:
          #no heirarchy, just return
          break
      else:
        # could not find the OU, an error, no access
        self.display += "No OU record for %d, ERROR<BR>" % nCurr_ou
        break
      # Check out owner record

  def pers_security(self, scout):
    """This procedure checks to see if read and / or write access is enabled for\
       a scout by this connection. It does this by checking all ou security for each\
       role record held for the scout"""

    self.read = 0
    self.write = 0
    self.display = ''
    if self.superuser:
      self.read = self.write = 1
      return

    roles = scout.role_list()
    for r in roles:
      self.ou_security(r.ou_id)
      if self.write:
        break

    return


  def __str__(self):
    """Prints out the connection attributes"""
    return "[CONNECT DETAILS]\nscout_id = %d\nName = %s\n write = %d\n Display = %s\
      \n[END OF CONNECT DETAILS]\n" %\
      (self.scout_id, self.name, self.write, self.display)
 

###############################################################################
class histrec:
  """Class used for storing and retrieving history (log / audit) records """
  def __init__(self, db, hist_id =0):
    self.database = db
    self.found = 0
    self.conn_id = ''
    self.hist_id = 0
    self.action = 0
    self.update_tm = ''
    self.scout_id = 0
    self.id1 = 0
    self.id2 = 0
    self.id3 = 0

  def add(self): 
    self.result = ''
    upd_string = "INSERT INTO history (hist_id, conn_id, action, update_tm, scout_id, id1, id2, id3) VALUES (nextval('hist_seq'), "
    upd_string += str(self.conn_id) + ", "
    upd_string += str(self.action) + ", '"
    upd_string += time.strftime("%Y%m%d %H:%M:%S", time.localtime()) + "', "
    upd_string += str(self.scout_id) + ", "
    upd_string += str(self.id1) + ", "
    upd_string += str(self.id2) + ", "
    upd_string += str(self.id3) + ")"
    try:
      self.database.query(upd_string)
    except ValueError: 
      self.result = "Create error"

##############################################################################
class awardrec:
  """A class to abstract the award definition record
The following data attributes are available:
  From the database
    award_id
    award_type (0)
    ou_struct (0) _ From award_type table
    name ('')
    descr ('')
    opt_needed (0)
    prereq (0)
    leader (0)
    status ('')
    current (0)
    yrs_valid (0)
    mth_valid (0)
    expires (0)
    collective (0)

    database (Database fom initialisation)
    sublevel [] - Populated with award_sublevel instances when this is instantiated
    found (0) - Set to 1 if record found

Methods
  update()
  add()
  """
  def __init__(self, db, in_awd_id = 0):
    self.database = db
    self.award_id = in_awd_id
    self.award_type = 0
    self.ou_struct = 0
    self.name = ''
    self.descr = ''
    self.sublevel = []
    self.opt_needed = 0
    self.prereq = 0
    self.leader = 0
    self.status = ''
    self.current = 0
    self.yrs_valid = 0
    self.mth_valid = 0
    self.expires = 0
    self.collective = 0
    self.found = 0
    uqry = self.database.query("SELECT a.award_type, a.name, a.descr, a.opt_needed, a.prereq,\
        a.leader, a.status, a.yrs_valid, a.mth_valid, a.collective, t.ou_struct FROM\
        award a, award_type t WHERE a.award_id = %d AND a.award_type = t.award_type" % self.award_id)
    if len(uqry) > 0:
      self.found = 1
      self.award_type = uqry[0]['award_type']
      self.name = uqry[0]['name']
      self.descr = uqry[0]['descr']
      self.opt_needed = uqry[0]['opt_needed']
      self.prereq = uqry[0]['prereq']
      self.leader = uqry[0]['leader']
      self.status = uqry[0]['status']
      if self.status == 'C':
        self.current = 1
      self.yrs_valid = uqry[0]['yrs_valid']
      self.mth_valid = uqry[0]['mth_valid']
      if self.yrs_valid > 0 or self.mth_valid > 0:
        self.expires = 0
      self.collective = uqry[0]['collective']
      self.ou_struct = uqry[0]['ou_struct']
 
      uqry = self.database.query("SELECT * FROM awardsub WHERE award_id = " + str(self.award_id))
      for sub in uqry:
        sl = award_sublevel(db, self.award_id, int(sub['sub_award_id']))
        if sl.found:
          self.sublevel.append(sl)

  def update(self):
    """ Method to update an award record  """
    self.result = ''
    upd_string = "UPDATE award SET status = '%s', name = '%s', descr = '%s',\
      prereq = %d, opt_needed = %d, yrs_valid = %d, mth_valid = %d,\
      collective = %d, award_type = %d WHERE award_id = %d" %\
      (self.status, sql_str(self.name), sql_str(self.descr), self.prereq, self.opt_needed,\
      self.yrs_valid, self.mth_valid, self.collective, self.award_type, self.award_id)
    self.database.query(upd_string)

  def add(self):
    """ Method to create a new award record  """
    self.result = 0
    curs = self.database.database.cursor()
    # Check that the award_type is valid
    curs.execute("SELECT award_type FROM award_type WHERE award_type = %d" % self.award_type)
    if not curs.rowcount:
      self.result = -1
      return

    #Check that a name is entered
    if self.name is None or self.name == '':
      self.result = -1
      return

    self.status = 'C'
    upd_string = "INSERT INTO award (award_id, award_type, name, descr,\
      prereq, leader, opt_needed, status, yrs_valid, mth_valid, collective) VALUES\
      (nextval('awd_seq'), %d, '%s', '%s', %d, %d, 0, 'C', %d, %d, %d)" %\
      (self.award_type, sql_str(self.name), sql_str(self.descr),\
      self.prereq, self.leader, self.yrs_valid, self.mth_valid, self.collective)
    self.database.query(upd_string)
    return

##############################################################################
class award_sublevel:
  """A class to abstract the award sub level definition record
Data attributes
  Fromdatabase
    award_id (Input - in_awd_id)
    sub_award_id (Input - in_sub_award_id)
    name ('')
    descr ('')
    optional (0)
    num_req (1)
  Other
    database (Input database)
    found (0)

"""
  def __init__(self, db, in_awd_id = 0, in_sub_award_id = 0):
    """Initialiases the award_sublevel instance if the record is found in the table"""
    self.database = db
    self.award_id = in_awd_id
    self.sub_award_id = in_sub_award_id
    self.name = ''
    self.descr = ''
    self.optional = 0
    self.num_req = 1
    self.found = 0
    uqry = self.database.query("SELECT * FROM awardsub WHERE award_id = " + str(self.award_id) + " AND sub_award_id = " + str(self.sub_award_id))
    if len(uqry) > 0:
      self.found = 1
      self.name = uqry[0]['name']
      self.descr = uqry[0]['descr']
      self.optional = uqry[0]['optional']
      self.num_req = uqry[0]['num_req']
    return

  def update(self):
    """Method to update a sub award record"""
    self.result = ''
    upd_string = "UPDATE awardsub SET  name = '%s', descr = '%s',\
      num_req = %d, optional = %d WHERE award_id = %d AND sub_award_id = %d"\
      % (sql_str(self.name), sql_str(self.descr), self.num_req, self.optional,\
      self.award_id, self.sub_award_id)
    self.database.query(upd_string)

  def add(self):
    """ Method to create a new sub level of award record  """
    self.result = 0
    if self.name is None or self.name == '':
      self.result = -1
      return
    self.status = 'C'

    # need to calculate next sub level id number
    qry = self.database.query('SELECT sub_award_id FROM awardsub WHERE award_id = %d' % (self.award_id))
    self.sub_award_id = 1
    for s in qry:
      if int(s['sub_award_id']) >= self.sub_award_id:
        self.sub_award_id = int(s['sub_award_id']) + 1

    upd_string = "INSERT INTO awardsub (award_id, sub_award_id, name, descr,\
      optional, num_req) VALUES (%d, %d, '%s', '%s', %d, %d)" %\
      (self.award_id, self.sub_award_id, sql_str(self.name),\
      sql_str(self.descr), self.optional, self.num_req)
    self.database.query(upd_string)
    return


##############################################################################
class achieverec:
  """A class to abstract individual achievements
Each achievement is linked to an awardrec instance and a personrec instance.
The award_id and person (scout_id) for the primary key for this instance"""
  def __init__(self, db, in_scout_id, in_awd_id):
    """This initialises the instance and sets the following data attributes:
  From the Database
    scout_id (in_scout_id from parameter list)
    award_id (in_awd_id from parameter list)
    dt_obtained ('')
    name ('')
    comments ('')
    status ('') - 'H' if the award is achieved, 'W' if the acheivement is 'W'ork in progress
    done (0) - Set to 1 if achievement is held - related to status field above
    awd_presented (0)
    ldr_notify (0)

  Other
    database (database from the parameter list)
    sublevel (Empty list) List of achievesubrec instances populated by sublevels() method
    found - Set to one if record found
    result - Set by add/update operations
    current -Initially 0, set by some operations to show if currntly appropriate achievement
"""
    self.database = db
    self.scout_id = in_scout_id
    self.award_id = in_awd_id
    self.dt_obtained = ''
    self.name = ''
    self.comments = ''
    self.status = ''
    self.awd_presented = 0
    self.ldr_notify = 0
    self.done = 0
    self.sublevel = []
    self.found = 0
    self.current = 0
    uqry = self.database.query("SELECT * FROM achieve WHERE scout_id = %d AND award_id = %d" % (self.scout_id, self.award_id))
    if len(uqry) > 0:
      self.found = 1
      self.dt_obtained   = uqry[0]['dt_obtained']
      self.comments      = uqry[0]['comments']
      self.status        = uqry[0]['status']
      self.awd_presented = uqry[0]['awd_presented']
      self.ldr_notify    = uqry[0]['ldr_notify']
      if self.status is not None:
        if self.status.upper() == 'H':
          self.done = 1    
      else:
        self.status = 'W'
      if self.awd_presented is None:
        self.awd_presented = 0
      if self.ldr_notify is None:
        self.ldr_notify = 0



      aqry = self.database.query("SELECT * FROM award WHERE award_id = " + str(self.award_id))
      if len(aqry) > 0:
        self.name = aqry[0]['name']
        self.descr = aqry[0]['descr']

    return

  def add(self):
    """Adds an achievement record
  First validates that the scout_id and award_id are valid
  Then checks if the record already exists, does nothing if it does
  Then inserts the record"""
    self.result = 0
 
    # Check the scout exists
    qry = self.database.query("SELECT scout_id FROM scout WHERE scout_id = '%d'" %\
        (self.scout_id))
    #If no scout record quit
    if len(qry) == 0:
      return

    # Check the award exists
    qry = self.database.query("SELECT award_id FROM award WHERE award_id = '%d'" %\
        (self.award_id))
    #If no scout record quit
    if len(qry) == 0:
      return

    # Check the iachievement does not exist
    qry = self.database.query("SELECT award_id FROM achieve WHERE scout_id = '%d' AND award_id = '%d'" %\
      (self.scout_id, self.award_id))
    #If no scout record quit
    if len(qry) > 0:
      return

    upd_string = "INSERT INTO achieve (scout_id, award_id, comments, status, awd_presented, \
      ldr_notify) VALUES (%d, %d, '%s', '%s', %d, %d)" % \
      (self.scout_id, self.award_id, sql_str(self.comments), sql_str(self.status), \
       self.awd_presented, self.ldr_notify)
    if self.status.upper() == 'H':
      self.done = 1    
    self.database.query(upd_string)
    if self.dt_obtained is not None and self.dt_obtained != '':
      self.database.query("UPDATE achieve SET dt_obtained = '%s' WHERE scout_id = %d and award_id = %d"\
          % (self.dt_obtained, self.scout_id, self.award_id))  
    return

  def update(self):
    """ Method to update an achievement record"""
    self.result = ''
    upd_string = "UPDATE achieve SET status = '%s', dt_obtained = '%s', comments = '%s',\
      awd_presented = %d, ldr_notify = %d WHERE scout_id = %d AND award_id = %d" %\
      (self.status, self.dt_obtained, sql_str(self.comments), self.awd_presented, self.ldr_notify,\
      self.scout_id, self.award_id)
    if self.status.upper() == 'H':
      self.done = 1    

    self.database.query(upd_string)
    return

  def delete(self):
    """This method currently does nothing"""
    pass

  def sublevels(self):
    """ Populates data attibute sublevel with achievesubrec instances"""
    self.sublevel = []
    qry = self.database.query("SELECT sub_award_id FROM achievesub\
        WHERE award_id = %d AND scout_id = %d" %\
        (self.award_id, self.scout_id))
    for q in qry:
      sl = achievesubrec(self.database, self.scout_id, self.award_id, q['sub_award_id'])
      if sl.found:
        self.sublevel.append(sl)

    return

  def check_complete(self):
    """Check all sub levels to see if the award has been achieved
  Obtains award record, no action if not found, should never be the case
  Populates the sublevels list data attribute
  Iterate through the award sublevel list to see if all mandatory steps have been acheived
  Then checks option steps
  If all completed, returns 1, otherwise returns 0
"""
    # Get the owning award record
    self.award = awardrec(self.database, self.award_id)
    if self.award.found:
      # Populate the achievement sub levels
      self.sublevels()
      bMandatory = 1
      # Lets check the mandatory items
      for sl in self.award.sublevel:
        if not sl.optional:
          # This in mandatory, now find the sub achievement record
          ntx = self.find_sa(sl.sub_award_id)
          if ntx < 0 or not (self.sublevel[ntx].complete):
            # if the record is missing or incomplete
            bMandatory = 0
      # Now check optional items
      nOpt = 0
      for sl in self.award.sublevel:
        if sl.optional:
          # Now find the sub achievement record
          ntx = self.find_sa(sl.sub_award_id)
          if ntx > -1 and (self.sublevel[ntx].complete):
            nOpt += 1
      # Let return the answer
      if bMandatory and nOpt >= self.award.opt_needed:
        self.done = 1
        return 1
    return 0
          

  def find_sa(self, in_sub_award_id):
    """ find the sub achievement record in the existing sublevel list"""
    ntx = 0
    for sa in self.sublevel:
      if sa.sub_award_id == in_sub_award_id:
        return ntx
      else:
        ntx += 1
    return -1

##############################################################################
class achievesubrec:
  """A class to abstract individual achievement sub records. These are the steps
needed to complete the achjievement."""
  def __init__(self, db, in_scout_id, in_awd_id, in_sub_awd_id):
    """Initialises the achievesubrec instance and sets the following data attributes:
  From database

    scout_id (in_scout_id from params)
    award_id (in_awd_id from params)
    sub_award_id (in_sub_awd_id from params)
    dt_obtained ('')
    name ('')
    descr ('')
    comments ('')
  Other
    found (0) - Set to 1 if record found
    units - List of achievesubunitrec instances
    complete - Set to 1 if achieve step is completed
    num_req - From awardsub table - number of steps to be completed
"""
    self.database = db
    self.scout_id = in_scout_id
    self.award_id = in_awd_id
    self.sub_award_id = in_sub_awd_id
    self.dt_obtained = ''
    self.name = ''
    self.descr = ''
    self.comments = ''
    self.found = 0
    self.units = []
    self.complete = 0
    self.num_req = 0
    uqry = self.database.query("SELECT * FROM achievesub WHERE scout_id = %d AND\
      award_id = %d AND sub_award_id = %d" %\
      (self.scout_id, self.award_id, self.sub_award_id))
    if len(uqry) > 0:
      self.found = 1
      self.dt_obtained   = uqry[0]['dt_obtained']
      self.comments      = uqry[0]['comments']
  
      aqry = self.database.query("SELECT * FROM awardsub WHERE award_id = %d AND sub_award_id = %d" %\
        (self.award_id, self.sub_award_id))
      if len(aqry) > 0:
        self.name = aqry[0]['name']
        self.descr = aqry[0]['descr']
        self.num_req = aqry[0]['num_req']

      for uq in uqry:
        asu = achievesubunitrec(self.database, self.scout_id, self.award_id,\
          self.sub_award_id, uq['sub_ach_id'])
        if asu.found:
          self.units.append(asu)
      if len(self.units) >= aqry[0]['num_req']:
        self.complete = 1

    return

  def add(self):
    """Adds a sub award record.
  Validates that scout and sub award exist first"""
    self.result = 0
 
    curs = self.database.database.cursor()

    # Check the scout exists
    curs.execute("SELECT scout_id FROM scout WHERE scout_id = '%d'" %\
        (self.scout_id))
    #If no scout record quit
    if curs.rowcount == 0:
      return

    # Check the sub award exists
    sub_award = award_sublevel(self.database, self.award_id, self.sub_award_id)
    #If no scout record quit
    if not sub_award.found:
      return

    # we do different things if num_req > 1
    next_no = 1
    if sub_award.num_req > 1:
      # Check thei sub achievement quantities
      qry = self.database.query("SELECT * FROM achievesub WHERE scout_id = %d\
        AND award_id = %d AND sub_award_id = %d" %\
        (self.scout_id, self.award_id, self.sub_award_id))
      #If no scout record quit
      for q in qry:
        if q['sub_ach_id'] >= next_no:
          next_no = q['sub_ach_id'] + 1

    # Add the achieve sub record
    upd_string = "INSERT INTO achievesub (scout_id, award_id, sub_award_id, sub_ach_id,\
      dt_obtained, comments) VALUES (%d, %d, %d, %d, '%s', '%s')" % \
      (self.scout_id, self.award_id, self.sub_award_id, next_no, sql_str(self.dt_obtained),\
      sql_str(self.comments))
    curs.execute(upd_string)

    # If there is no 'owning' achievemment record, add one now
    curs.execute("SELECT * FROM achieve WHERE scout_id = %d AND award_id = %d" %\
        (self.scout_id, self.award_id))
    if curs.rowcount == 0:
      curs.execute("INSERT INTO achieve (scout_id, award_id, status, awd_presented,\
           ldr_notify) VALUES (%d, %d, 'W', 0, 0)" %\
           (self.scout_id, self.award_id))

    asu = achievesubunitrec(self.database, self.scout_id, self.award_id,\
      self.sub_award_id, next_no)
    if asu.found:
      self.units.append(asu)
    if len(self.units) >= self.num_req:
      self.complete = 1
    return

##############################################################################
class achievesubunitrec:
  " A class to abstract individual achievement sub records where they are split into multiple options"
  def __init__(self, db, in_scout_id, in_awd_id, in_sub_awd_id, in_sub_ach_id):
    """Initiates the achievesubunitrec and sets the following data attributes:
  Database
    scout_id (in_scout_id from parameters)
    award_id (in_awd_id from parameters)
    sub_award_id (in_sub_awd_id from parameters)
    sub_ach_id (in_sub_ach_id from parameters)
    dt_obtained ('')
    comments ('')
  Other
    database - From params
    found (0) Set to 1 is found
"""
    self.database = db
    self.scout_id = in_scout_id
    self.award_id = in_awd_id
    self.sub_award_id = in_sub_awd_id
    self.sub_ach_id = in_sub_ach_id
    self.dt_obtained = ''
    self.comments = ''
    self.found = 0
    uqry = self.database.query("SELECT * FROM achievesub WHERE scout_id = %d AND\
      award_id = %d AND sub_award_id = %d AND sub_ach_id = %d" %\
      (self.scout_id, self.award_id, self.sub_award_id, self.sub_ach_id))
    if len(uqry) > 0:
      self.found = 1
      self.dt_obtained   = uqry[0]['dt_obtained']
      self.comments      = uqry[0]['comments']

    return


##############################################################################
class awardtyperec:
  " A class to abstract award types database objects"
  def __init__(self, db, in_award_type):
    """Instantiates the object from the database information.
Parameter:
  in_award_type - mandatory
Data attributes set
    database - Database object
    aws per in_award_type 
    sect_cd
    name
    ou_struct
    found - 1 if found, otherwise 0
 
"""
    self.database = db
    self.award_type = in_award_type
    self.sect_cd = ''
    self.name = ''
    self.ou_struct = 0
    self.found = 0
    uqry = self.database.query("SELECT * FROM award_type WHERE award_type = %d" %\
      (self.award_type))
    if len(uqry) > 0:
      self.found = 1
      self.sect_cd   = uqry[0]['sect_cd']
      self.name      = uqry[0]['name']
      self.ou_struct = uqry[0]['ou_struct']
    return


##############################################################################
class messagerec:
  """A class to abstract the message record
This object is used to pass messages between users and to the sys admin"""
  def __init__(self, db, in_msg_id = 0):
    """This instantiates the object and set the following data attributes:
  From database
    msg_id (in_msg_id from params) - ID of message
    create_tm ('') - Timestamp
    from_id (0) - ID of user who created the message
    to_id (0) - Recipient's ID
    for_sysadmin (0) - Set to 1 if this is for a sysadmin
    for_developer (0) - Set to 1 if this is for a developer
    status ('') - Status. Options are ???
    notify (0) - Notification flag
    name ('')
    email ('')
    telephone ('')
    subject ('')
    body ('') - Body of message
    last_update - Timestamp
    msg_response ('') - Text for response
  Other
    database - database object
    found (0) - Set to 1 if found

"""
    self.database = db
    self.msg_id = in_msg_id
    self.create_tm = ''
    self.from_id = 0
    self.to_id = 0
    self.for_sysadmin = 0
    self.for_developer = 0
    self.status = ''
    self.notify = 0
    self.name = ''
    self.email = ''
    self.telephone = ''
    self.subject = ''
    self.body = ''
    self.last_update = ''
    self.msg_response = ''
    self.found = 0
    curs = db.database.cursor()
    str = "SELECT create_tm, from_id, to_id, for_sysadmin, for_developer,\
      status, notify, name, email, telephone, subject, body, last_update,\
      msg_response FROM message WHERE msg_id = %d" % self.msg_id
    curs.execute(str)
    if curs.rowcount:
      qry = curs.fetchone()
      self.found = 1
      self.create_tm = qry[0]
      self.from_id = qry[1]
      self.to_id = qry[2]
      self.for_sysadmin = qry[3]
      self.for_developer = qry[4]
      self.status = qry[5]
      self.notify = qry[6]
      self.name = qry[7]
      self.email = qry[8]
      self.telephone = qry[9]
      self.subject = qry[10]
      self.body = qry[11]
      self.last_update = qry[12]
      self.msg_response = qry[13]
    return

  def add(self): 
    """Adds a new message record to the table based on data attributes set."""
    curs = self.database.database.cursor()
    curs.execute("SELECT nextval('ou_seq')")
    qry = curs.fetchone()
    self.msg_id = qry[0]
    if self.to_id is None:
      self.to_id = 0
    if self.for_sysadmin is None:
      self.for_sysadmin = 0
    if self.for_developer is None:
      self.for_developer = 0
    if self.notify is None:
      self.notify = 0

    upd_string = "INSERT INTO message (msg_id, create_tm, from_id, to_id,\
        for_sysadmin, for_developer, status, notify, name, email, telephone,\
        subject, body, last_update, msg_response) VALUES (%d, '%s', %d, %d,\
        %d, %d, 'N', %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %\
        (self.msg_id, curr_time(), self.from_id, self.to_id, self.for_sysadmin,\
        self.for_developer, self.notify, self.name, self.email, self.telephone,\
        self.subject, self.body, curr_time(), self.msg_response)
    curs.execute(upd_string)
    return

  def update(self):
    """Method to update a message record"""
    curs = self.database.database.cursor()
    str = "UPDATE message SET status = '%s', last_update = '%s',\
        msg_response = '%s' WHERE msg_id = %d" % (self.status, curr_time(),\
        self.msg_response, self.msg_id)
    curs.execute(str)
    return

  def ntfy_update(self):
    """Method to update a notification details"""
    curs = self.database.database.cursor()
    str = "UPDATE message SET notify = %d WHERE msg_id = %d" %\
        (self.notify, self.msg_id)
    curs.execute(str)
    return


##############################################################################
class person_list:
  def __init__(self, db, search_str, type):
    """This class returns a dictionary of personal details with similiar surnames """
    self.cStr = "SELECT scout_id, surname, forename, initials FROM scout WHERE substring(upper(surname) FOR " + str(len(search_str)) + ") = '"
    self.cStr += sql_str(search_str.upper()) + "' AND status = '" + type + "'"
    self.list = db.query(self.cStr)
    return

##############################################################################
def person_search(db, surname, forename=''):
  """Returns list of person records with the same name and surname """ 
  persons = []
  curs = db.database.cursor()
  cStr = "SELECT scout_id FROM scout WHERE substring(upper(surname) FOR %d) = '%s'" %\
      (len(surname.rstrip()), surname.upper())
  if len(forename) > 0:
    cStr += " AND substring(upper(forename) FOR %d) = '%s'" %\
      (len(forename.rstrip()), forename.upper())
  curs.execute(cStr)
  pl = curs.fetchall()
  for p in pl:
    persons.append(personrec(db, p[0]))
  return persons


##############################################################################
class section_list:
  def __init__(self, db):
    """This class returns a list of available section records """
    self.sectionlist = []
    self.cStr = "SELECT sect_cd FROM section"
    cQry = db.query(self.cStr)
    for s in cQry:
      self.sectionlist.append(sectionrec(db, s['sect_cd']))
    return

##############################################################################
def struct_list(db, no_mngt = 0, no_heir = 0):
  """Returns list of available OU struct records"""
  struct_list = []
  if no_mngt:
    if no_heir:
      cSel = "SELECT ou_struct FROM ou_struct WHERE mngt != 1 AND heirarchic != 1 ORDER BY ou_struct"
    else:
      cSel = "SELECT ou_struct FROM ou_struct WHERE mngt != 1 AND heirarchic = 1 ORDER BY ou_struct"
  else:
    if no_heir:
      cSel = "SELECT ou_struct FROM ou_struct WHERE mngt = 1 AND heirarchic != 1 ORDER BY ou_struct"
    else:
      cSel = "SELECT ou_struct FROM ou_struct WHERE mngt = 1 AND heirarchic = 1 ORDER BY ou_struct"

  curs = db.database.cursor()
  curs.execute(cSel)
  sl = curs.fetchall()
  for s in sl:
    struct_list.append(ou_structrec(db, s[0]))

  return struct_list

##############################################################################
def subach_list(db, nScout):
  """Returns a list of sub achievement unit instances. Default order is date obtained"""
  aclist = []
  curs = db.database.cursor()
  curs.execute("SELECT award_id, sub_award_id, sub_ach_id FROM achievesub WHERE scout_id = %d ORDER BY dt_obtained" % nScout)
  ac = curs.fetchall()
  for a in ac:
    acrec = achievesubunitrec(db, nScout, a[0], a[1], a[2])
    if acrec.found:
      aclist.append(acrec)
  return aclist


##############################################################################
class sys_admin_msg_list:
  def __init__(self, db, status = 'N'):
    """This class returns a list of messages for system administrators """
    self.messagelist = []
    if status == '*':
      self.cStr = "SELECT msg_id FROM message WHERE for_sysadmin=1 ORDER by create_tm DESC"
    else:
      self.cStr = "SELECT msg_id FROM message WHERE for_sysadmin=1 AND status='" + status + "' ORDER by create_tm DESC"
    cQry = db.query(self.cStr)
    for m in cQry:
      self.messagelist.append(messagerec(db, m['msg_id']))
    return

##############################################################################
def sys_admin_list(db):
  """This function returns a list of system administrators"""
  sysadminlist = []
  curs = db.database.cursor()
  curs.execute("SELECT scout_id FROM scout WHERE superuser=true")
  cQry = curs.fetchall()
  for m in cQry:
    sysadminlist.append(adultrec(db, m[0]))
  return sysadminlist

##############################################################################
def award_list(db, type):
  """This procedure returns a list of awardrec instances for an awardtyperec"""
  award_list = []
  # return awards id's
  cStr = "SELECT award_id FROM award WHERE award_type = %d ORDER BY name" % type
  curs = db.database.cursor()
  curs.execute(cStr)
  al = curs.fetchall()
  for a in al:
    award_list.append(awardrec(db, a[0]))

  return award_list

##############################################################################
class dt_time:
  """Class to abstract date and time and perform calculations """
  def __init__(self, inp_gmtime):
    self.gmtime = inp_gmtime
    self.seconds = time.mktime(self.gmtime)
    self.full_time = time.strftime("%Y-%m-%d %H:%M:%S", self.gmtime)
    self.date = time.strftime("%Y-%m-%d", self.gmtime)

  def sql_time(self, inp_string):
    self.gmtime = time.strptime(inp_string, "%Y-%m-%d %H:%M:%S")
    self.seconds = time.mktime(self.gmtime)
    self.full_time = time.strftime("%Y-%m-%d %H:%M:%S", self.gmtime)

  def add(self, inp_seconds):
    self.seconds = self.seconds + inp_seconds
    self.gmtime = time.localtime(self.seconds)
    self.full_time = time.strftime("%Y-%m-%d %H:%M:%S", self.gmtime)
        
##############################################################################
def curr_time():
  """Returns the current time formatted for input into the database"""
  return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
 
##############################################################################
def sql_str(cString):
  cStr = cString
  if cStr is None:
    cStr = ''
  cStr = string.replace(cStr, "'", "' || chr(39) || '")
  return cStr


##############################################################################
def rand_string(nSize=20):
  cString = ''
  while len(cString) < nSize:
    cString = cString + str(random.randint(1,9))
  return cString

##############################################################################
def sql_int_str(nInt):
  """Always returns a character integer """
  Num = nInt
  if Num is None:
    Num = 0
  try:
    cNum = str(Num)
  except:
    cNum = '0'
  return cNum
 
###############################################################################
def log_action(db, conn_id, action, scout_id=0, id1=0, id2=0, id3=0):
  Hist = histrec(db)
  Hist.conn_id = conn_id
  Hist.action = action
  Hist.scout_id = scout_id
  Hist.id1 = id1
  Hist.id2 = id2
  Hist.id3 = id3
  Hist.add()
  return

###############################################################################
def sort_by_attr(seq, attr):
  """This sort sequence was obtained from the python cookbook, 1st edition, 'recipe' no 2.6
     Credit Yakov Markovich, Nick Perkins """
  import operator
  intermed = map(None, map(getattr, seq, (attr,)*len(seq)), xrange(len(seq)), seq )
  intermed.sort()
  return map(operator.getitem, intermed, (-1,)*len(intermed))

##############################################################################
def scout_in_list(list, in_scout_id):
  for x in list:
    if x.scout_id == in_scout_id:
      return 1
  return 0



##############################################################################
def main():

  usage = "usage: %prog [-test]"
  opt = OptionParser()
  opt.set_defaults(testing=False) 
  opt.add_option("-t", "--test", action='store_true', dest="testing")
  (options, args) = opt.parse_args()

  if options.testing:

    param = paramrec()
    #  #db = dbinstance(param.dbname)
    db = dbinstance(param.dbname)
    print "testing"

    o = ourec(db, 17)
    #print o

    o.award_list()

    for p in o.awards:
      print p.name

    db.commit()
  return



#Call the main program
if __name__ == "__main__":
  main()


