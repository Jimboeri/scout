class dbinstance:
  def get_field(self, cursor, cField):
    self.posn = 0
    nCnt = 0
    for x in cursor.description:
      if cField == x[0]:
        self.posn = nCnt
        return nCnt
      else:
        ncnt += 1
    return 0

##############################################################################
class nationalrec:
  """ A class to abstract the national record"""
  def __init__(self, db):
    """National record always has ID of '1' """
    self.database = db
    self.name = ''
    self.ou_id = 0
    try:
      qry = self.database.query("SELECT * FROM national WHERE national_id = '1'")
      self.found = 1
    except ValueError:
      self.found = 0
    if len(qry) == 0:
      self.found = 0
    else:
      self.name = qry[0]['name']
      self.ou_id = qry[0]['ou_id']
    return

  def update(self):
    """ Method to update national record  """
    self.result = ''
    upd_string = "UPDATE national SET name = '" + sql_str(self.name)
    upd_string += "', ou_id = %d WHERE national_id = '1'" % self.ou_id
    self.database.query(upd_string)
    upd_string = "UPDATE ou SET name = '%s' WHERE ou_id = %d" % (sql_str(self.name), self.ou_id)
    self.database.query(upd_string)

    #log_action(self.database, 21, cMnf, cProd)

  def area_list(self):
    """Return a list of areas for the nation """
    self.arealist = []
    qry = self.database.query("SELECT area_id FROM area Order By name")
    for a in qry:
      self.arealist.append(arearec(self.database, a["area_id"]))
    return self.arealist

  def role_list(self):
    """Return a list of adult roles for the Nation """
    self.rolelist = []
    qry = self.database.query("SELECT role_id FROM role WHERE level_ref = 'N' AND level_id = 1")
    for r in qry:
      self.rolelist.append(rolerec(self.database, r["role_id"]))
    return self.rolelist


##############################################################################
class arearec:
  " A class to abstract the area record"
  def __init__(self, db, nArea_id):
    self.database = db
    self.area_id = nArea_id
    self.name = ''
    self.national_id = '1'
    self.curr_memb = 0
    self.ou_id = 0
    try:
      qry = self.database.query("SELECT * FROM area WHERE area_id = " + str(nArea_id))
      self.found = 1
    except ValueError:
      self.found = 0
      self.area_id = 0
    if len(qry) == 0:
      self.found = 0
      self.area_id = 0
    else:
      self.name = qry[0]['name']
      self.curr_memb = qry[0]['curr_memb']
      self.national_id = qry[0]['national_id']
      self.ou_id = qry[0]["ou_id"]
    return

  def update(self):
    """ Method to update area record  """
    self.result = ''
    upd_string = "UPDATE area SET name = '%s', curr_memb = %d, ou_id = %d WHERE area_id = %d" % (sql_str(self.name), self.curr_memb, self.ou_id, self.area_id)
    self.database.query(upd_string)
    upd_string = "UPDATE ou SET name = '%s', curr_memb = %d WHERE ou_id = %d" % (sql_str(self.name), self.curr_memb, self.ou_id)
    self.database.query(upd_string)

  def add(self):
    self.result = ''

    # first we get the next dist_id from the dist_seq sequence
    qry = self.database.query("SELECT nextval('area_seq')")
    self.area_id = int(qry[0]['nextval'])

    #Add record
    upd_string = "INSERT INTO area (area_id, name, national_id, curr_memb) VALUES ("
    upd_string += str(self.area_id) + ", '"
    upd_string += sql_str(self.name) + "', 1, 0)"
    self.database.query(upd_string)

  def delete(self):
    self.result = ''
    upd_string = "DELETE FROM area WHERE area_id = " + str(self.area_id)
    self.database.query(upd_string)

  def district_list(self):
    """Return a list of districts for the area """
    self.districtlist = []
    qry = self.database.query("SELECT dist_id FROM district WHERE area_id = " + str(self.area_id) + " ORDER BY name")
    for d in qry:
      self.districtlist.append(districtrec(self.database, d["dist_id"]))
    return self.districtlist

  def role_list(self):
    """Return a list of adult roles for the Area """
    self.rolelist = []
    qry = self.database.query("SELECT role_id FROM role WHERE level_ref = 'A' AND level_id = " + str(self.area_id))
    for r in qry:
      self.rolelist.append(rolerec(self.database, r["role_id"]))
    return self.rolelist



##############################################################################
class districtrec:
  " A class to abstract the district record"
  def __init__(self, db, nDist_id):
    self.database = db
    self.dist_id = nDist_id
    self.name = ''
    self.area_id = 0
    self.curr_memb = 0
    self.ou_id = 0
    try:
      qry = self.database.query("SELECT * FROM district WHERE dist_id = " + str(nDist_id))
      self.found = 1
    except ValueError:
      self.found = 0
      self.dist_id = 0
    if len(qry) == 0:
      self.found = 0
      self.dist_id = 0
    else:
      self.name = qry[0]['name']
      self.area_id = qry[0]['area_id']
      self.curr_memb = qry[0]['curr_memb']
      self.ou_id = qry[0]["ou_id"]
    return

  def update(self):
    """ Method to update district record  """
    self.result = ''
    upd_string = "UPDATE district SET name = '%s', curr_memb = %d, ou_id = %d WHERE dist_id = %d" % (sql_str(self.name), self.curr_memb, self.ou_id, self.dist_id)
    self.database.query(upd_string)
    upd_string = "UPDATE ou SET name = '%s', curr_memb = %d WHERE ou_id = %d" % (sql_str(self.name), self.curr_memb, self.ou_id)
    self.database.query(upd_string)

    #log_action(self.database, 21, cMnf, cProd)

  def add(self):
    self.result = ''

    # first we get the next dist_id from the dist_seq sequence
    qry = self.database.query("SELECT nextval('dist_seq')")
    self.dist_id = int(qry[0]['nextval'])

    #Add record
    upd_string = "INSERT INTO district (dist_id, area_id, name, curr_memb) VALUES ("
    upd_string += str(self.dist_id) + ", "
    upd_string += str(self.area_id) + ", '"
    upd_string += sql_str(self.name) + "', 0)"
    self.database.query(upd_string)

  def delete(self):
    self.result = ''
    upd_string = "DELETE FROM district WHERE dist_id = " + str(self.dist_id)
    self.database.query(upd_string)


  def group_list(self):
    """Return a list of groups for the district """
    self.grouplist = []
    qry = self.database.query("SELECT group_id FROM groupdef WHERE dist_id = " + str(self.dist_id) + " ORDER BY name")
    for g in qry:
      self.grouplist.append(grouprec(self.database, g["group_id"]))
    return self.grouplist

  def role_list(self):
    """Return a list of adult roles for the District """
    self.rolelist = []
    qry = self.database.query("SELECT role_id FROM role WHERE level_ref = 'D' AND level_id = " + str(self.dist_id))
    for r in qry:
      self.rolelist.append(rolerec(self.database, r["role_id"]))
    return self.rolelist



##############################################################################
class grouprec:
  " A class to abstract the group record"
  def __init__(self, db, nGroup_id):
    self.database = db
    self.group_id = nGroup_id
    self.name = ''
    self.addr1 = ''
    self.addr2 = ''
    self.addr3 = ''
    self.p_code = ''
    self.telephone = ''
    self.dist_id = 0
    self.curr_memb = 0
    self.ou_id = 0
    try:
      qry = self.database.query("SELECT * FROM groupdef WHERE group_id = " + str(nGroup_id))
      self.found = 1
    except ValueError:
      self.found = 0
      self.group_id = 0
    if len(qry) == 0:
      self.found = 0
      self.group_id = 0
    else:
      self.name = qry[0]['name']
      self.dist_id = qry[0]['dist_id']
      self.addr1 = qry[0]['addr1']
      self.addr2 = qry[0]['addr2']
      self.addr3 = qry[0]['addr3']
      self.p_code = qry[0]['p_code']
      self.telephone = qry[0]['telephone']
      self.curr_memb = qry[0]['curr_memb']
      self.ou_id = qry[0]['ou_id']
    return

  def update(self):
    """ Method to update group record  """
    self.result = ''
    upd_string = "UPDATE groupdef SET name = '" + sql_str(self.name)
    upd_string += "', addr1 = '" + sql_str(self.addr1)
    upd_string += "', addr2 = '" + sql_str(self.addr2)
    upd_string += "', addr3 = '" + sql_str(self.addr3)
    upd_string += "', p_code = '" + sql_str(self.p_code)
    upd_string += "', telephone = '" + sql_str(self.telephone)
    upd_string += "', curr_memb = " + str(self.curr_memb)
    upd_string += ", ou_id = " + str(self.ou_id)
    upd_string += " WHERE group_id = " + str(self.group_id)
    self.database.query(upd_string)

  def add(self):
    self.result = ''

    # first we get the next unit_id from the unit_seq sequence
    qry = self.database.query("SELECT nextval('group_seq')")
    self.group_id = int(qry[0]['nextval'])

    #Add record
    upd_string = "INSERT INTO groupdef (group_id, dist_id, name, addr1, addr2, addr3, p_code, telephone, curr_memb) VALUES ("
    upd_string += str(self.group_id) + ", "
    upd_string += str(self.dist_id) + ", '"
    upd_string += sql_str(self.name) + "', '"
    upd_string += sql_str(self.addr1) + "', '"
    upd_string += sql_str(self.addr2) + "', '"
    upd_string += sql_str(self.addr3) + "', '"
    upd_string += sql_str(self.p_code) + "', '"
    upd_string += sql_str(self.telephone) + "', 0)"
    self.database.query(upd_string)

  def delete(self):
    self.result = ''
    upd_string = "DELETE FROM groupdef WHERE group_id = " + str(self.group_id)
    self.database.query(upd_string)


  def unit_list(self, section = ''):
    """Return a list of units for the group """
    self.unitlist = []
    if section == '':
      qry = self.database.query("SELECT unit_id FROM unit WHERE group_id = " + str(self.group_id) + " ORDER BY start_age")
    else:
      qry = self.database.query("SELECT unit_id FROM unit WHERE group_id = " + str(self.group_id) + " and sect_cd = '" + section + "'")
    for u in qry:
      self.unitlist.append(unitrec(self.database, u["unit_id"]))
    return self.unitlist

  def parent_list(self):
    """Return a list of primary parents for all members of the group """
    self.parentlist = []
    cQry = 'SELECT DISTINCT s2.scout_id, s2.forename, s2.surname FROM unit u, scout s1, scout s2 WHERE s1.parent1 = s2.scout_id AND s1.unit_id = u.unit_id AND u.group_id = ' + str(self.group_id) + ' ORDER BY s2.surname, s2.forename'
    qry = self.database.query(cQry)
    for p in qry:
      self.parentlist.append(adultrec(self.database, p["scout_id"]))
    return self.parentlist

  def all_scout_list(self, status ='C'):
    """Return a list of all scouts in units in the group"""
    self.scoutlist = []
    cQry = 'SELECT s.scout_id, s.forename, s.surname FROM unit u, scout s WHERE s.unit_id = u.unit_id AND u.group_id = ' + str(self.group_id) + ' ORDER BY s.surname, s.forename'
    qry = self.database.query(cQry)
    for s in qry:
      self.scoutlist.append(scoutrec(self.database, s["scout_id"]))
    return self.scoutlist

  def role_list(self):
    """Return a list of adult roles for the Group """
    self.rolelist = []
    qry = self.database.query("SELECT role_id FROM role WHERE level_ref = 'G' AND level_id = " + str(self.group_id))
    for r in qry:
      self.rolelist.append(rolerec(self.database, r["role_id"]))
    return self.rolelist



##############################################################################
class unitrec:
  " A class to abstract the unit record"
  def __init__(self, db, nUnit_id):
    self.database = db
    self.unit_id = 0
    if nUnit_id is not None:
      self.unit_id = nUnit_id
    self.name = ''
    self.sect_cd = ''
    self.group_id = 0
    self.sect_name = ''
    self.meet_time = ''
    self.next_sect = ''
    self.start_age = 0
    self.end_age = 0
    self.curr_memb = 0
    self.award_remind = ''
    self.next_sect_name = ''
    self.ou_id = 0
    try:
      qry = self.database.query("SELECT * FROM unit WHERE unit_id = %d" % self.unit_id)
      self.found = 1
    except ValueError:
      self.found = 0
    if len(qry) == 0:
      self.found = 0
    else:
      self.name = qry[0]['name']
      self.sect_cd = qry[0]['sect_cd']
      self.meet_time = qry[0]['meet_time']
      self.group_id = qry[0]['group_id']
      self.curr_memb = qry[0]['curr_memb']
      self.award_remind = qry[0]['award_remind']
      self.ou_id = qry[0]['ou_id']
      # get section details
      try:
        uqry = self.database.query("SELECT * FROM section WHERE sect_cd = '" + self.sect_cd + "'")
        self.found = 1
        self.sect_name = uqry[0]['name']
        self.next_sect = uqry[0]['next_sect']
        self.start_age = uqry[0]['start_age']
        self.end_age = uqry[0]['end_age']
        nqry = self.database.query("SELECT * FROM section WHERE sect_cd = '" + self.next_sect + "'")
        if len(nqry) > 0:
          self.next_sect_name = nqry[0]["name"]
      except ValueError:
        self.found = 0

    return

  def update(self):
    """ Method to update unit record  """
    self.result = ''
    upd_string = "UPDATE unit SET name = '" + sql_str(self.name)
    upd_string += "', meet_time = '" + sql_str(self.meet_time)
    if self.award_remind is not None and self.award_remind != '':
      upd_string += "', award_remind = '" + sql_str(self.award_remind)
    upd_string += "', curr_memb = " + str(self.curr_memb)
    upd_string += ", ou_id = %d" % self.ou_id
    upd_string += " WHERE unit_id = " + str(self.unit_id)
    self.database.query(upd_string)
    #log_action(self.database, 21, cMnf, cProd)

  def scout_list(self, status='C'):
    """Return a list of current scouts in the unit """
    self.scoutlist = []
    if status is None or status == '':
      qry = self.database.query("SELECT scout_id FROM scout WHERE unit_id = " + str(self.unit_id) + " ORDER BY date_of_birth")
    else:
      qry = self.database.query("SELECT scout_id FROM scout WHERE unit_id = " + str(self.unit_id) + " AND status = '%s' ORDER BY date_of_birth" % status.upper())
    for s in qry:
      self.scoutlist.append(scoutrec(self.database, s["scout_id"]))
    return self.scoutlist

  def role_list(self):
    """Return a list of adult roles for the unit """
    self.rolelist = []
    qry = self.database.query("SELECT role_id FROM role WHERE level_ref = 'U' AND level_id = " + str(self.unit_id))
    for r in qry:
      self.rolelist.append(rolerec(self.database, r["role_id"]))
    return self.rolelist

  def add(self):
    self.result = ''

    # first we get the next unit_id from the unit_seq sequence
    qry = self.database.query("SELECT nextval('unit_seq')")
    self.unit_id = int(qry[0]['nextval'])

    #Add record
    upd_string = "INSERT INTO unit (unit_id, group_id, name, sect_cd, meet_time)\
      VALUES (%d, %d, '%s', '%s', '%s')" % (self.unit_id, self.group_id, sql_str(self.name), \
      self.sect_cd, sql_str(self.meet_time))
    self.database.query(upd_string)
    #log_action(self.database, 21, cMnf, cProd)

  def delete(self):
    self.result = ''
    upd_string = "DELETE FROM unit WHERE unit_id = " + str(self.unit_id)
    self.database.query(upd_string)
    #log_action(self.database, 21, cMnf, cProd)

  def award_list(self):
    """Returns a list of awards suitable for collective achievement. Currently does all interest badges """
    self.award_list = []
    cStr = "SELECT * FROM award where (sect_cd = '%s' OR sect_cd = 'A') AND collective = 1 ORDER BY name" % self.sect_cd
    dQry = self.database.query(cStr)

    for a in dQry:
      self.award_list.append(awardrec(self.database, a['award_id']))

    return self.award_list



