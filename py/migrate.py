#!/usr/bin/python
import pg
import ConfigParser

##############################################################################
def check_field (db, table, field):
  cSel = "SELECT c.oid, c.relname, a.attname, a.attrelid FROM pg_class c, pg_attribute a WHERE c.oid = a.attrelid AND c.relname = '%s' AND a.attname = '%s'" % (table, field)
  cQry = db.query(cSel).dictresult()
  return len(cQry)

##############################################################################
def check_table (db, table):
  cSel = "SELECT relname FROM pg_class WHERE relname = '%s'" % table
  cQry = db.query(cSel).dictresult()
  return len(cQry)


##############################################################################
# Initiate Confiog Parser
conf = ConfigParser.SafeConfigParser()

# work out file name
cfgfile = 'scout.conf'
conf.read([cfgfile])

# Prefine default values in case values are not defines in the config file
dbname = "scoutdev"
if conf.has_section('database'):
  if conf.has_option('database', 'name'):
    dbname = conf.get('database', 'name')
 
db = pg.connect(dbname)

if check_table(db, 'ou'):
  db.query("DROP TABLE ou;")
  db.query("DROP SEQUENCE ou_seq;")

if check_table(db, 'ou_disp'):
  db.query("DROP TABLE ou_disp;")

if check_table(db, 'ou_struct'):
  db.query("DROP TABLE ou_struct;")

db.query("CREATE TABLE ou_struct (\
  ou_struct	int	PRIMARY KEY,\
  parent_id	int,\
  s_name	varchar(60),\
  heirarchic	int,\
  s_def_name varchar(60),\
  s_mngt_str	int,\
  s_next_sect	int,\
  s_start_age	real,\
  s_end_age	real,\
  sec_inherit   int default 0,\
  mngt		int default 0\
);")

db.query("INSERT INTO ou_struct VALUES (1, 0, 'National', 1, 'National level', 201);")
db.query("INSERT INTO ou_struct VALUES (2, 1, 'Region', 1, 'XXX Region', 202);")
db.query("INSERT INTO ou_struct VALUES (3, 2, 'Zone', 1, 'XXX Zone', 203);")
db.query("INSERT INTO ou_struct VALUES (4, 3, 'Group', 1, 'XXX Group', 204);")
db.query("INSERT INTO ou_struct VALUES (5, 4, 'Kea club', 1, 'XXX Keas', 205, 6, 6, 8, 1);")
db.query("INSERT INTO ou_struct VALUES (6, 4, 'Cub pack', 1, 'XXX Cubs', 206, 7, 8, 10.5, 1);")
db.query("INSERT INTO ou_struct VALUES (7, 4, 'Scout troop', 1, 'XXX Scouts', 207, 8, 10.5, 14, 1);")
db.query("INSERT INTO ou_struct VALUES (8, 4, 'Venturers', 1, 'XXX Venturers', 208);")
db.query("UPDATE ou_struct SET sec_inherit = 1 WHERE ou_struct = 8")
db.query("INSERT INTO ou_struct VALUES (9, 5, 'Posse', 1, '');")
db.query("INSERT INTO ou_struct VALUES (10, 6, 'Six', 1, '');")
db.query("INSERT INTO ou_struct VALUES (11, 7, 'Patrol', 1, '');")
db.query("INSERT INTO ou_struct VALUES (101, 0, 'Committee', 0);")
db.query("INSERT INTO ou_struct VALUES (102, 101, 'Sub-committee', 1)")
db.query("INSERT INTO ou_struct VALUES (201, 1, 'National', 1, 'National executive');")
db.query("INSERT INTO ou_struct VALUES (202, 2, 'Region', 1, 'Regional executive');")
db.query("INSERT INTO ou_struct VALUES (203, 3, 'Zone', 1, 'Zone executive');")
db.query("INSERT INTO ou_struct VALUES (204, 4, 'Group', 1, 'Group committee');")
db.query("INSERT INTO ou_struct VALUES (205, 5, 'Kea club', 1, 'Kea leaders', 6, 6, 8, 1);")
db.query("INSERT INTO ou_struct VALUES (206, 6, 'Cub pack', 1, 'Cub leaders', 7, 8, 10.5, 1);")
db.query("INSERT INTO ou_struct VALUES (207, 7, 'Scout troop', 1, 'Scout leaders', 8, 10.5, 14, 1);")
db.query("INSERT INTO ou_struct VALUES (208, 8, 'Venturers', 1, 'Venturer leaders');")
db.query("UPDATE ou_struct SET mngt = 1 WHERE ou_struct > 200")

db.query("CREATE TABLE ou (\
  ou_id		int PRIMARY KEY,\
  ou_owner	int,\
  ou_struct	int REFERENCES ou_struct,\
  name		varchar(60),\
  curr_memb	int DEFAULT 0,\
  curr_child    int DEFAULT 0,\
  p_addr1	varchar(60),\
  p_addr2	varchar(60),\
  p_addr3	varchar(60),\
  p_code	varchar(10),\
  m_addr1	varchar(60),\
  m_addr2	varchar(60),\
  m_addr3	varchar(60),\
  m_code	varchar(10),\
  phone		varchar(60),\
  fax		varchar(60),\
  sect_cd	char(1),\
  meet_time	varchar(60),\
  start_age	real,\
  end_age	real,\
  award_remind  date,\
  mngt		int default 0,\
  access	int default 1\
);")

db.query("CREATE SEQUENCE ou_seq START 1;")

db.query("CREATE TABLE ou_disp (\
  ou_id	int,\
  conn_id int,\
  show_actions INTEGER DEFAULT 0,\
  expand_ou varchar(200),\
  all_members INTEGER DEFAULT 0,\
  PRIMARY KEY (ou_id, conn_id)\
);")


db.query("GRANT SELECT,UPDATE,INSERT,DELETE ON ou TO apache;")
db.query("GRANT SELECT,UPDATE,INSERT,DELETE ON ou_seq TO apache;")
db.query("GRANT SELECT,UPDATE,INSERT,DELETE ON ou_struct TO apache;")
db.query("GRANT SELECT,UPDATE,INSERT,DELETE ON ou_disp TO apache;")

# Update table structures
if check_field(db, 'national', 'ou_id'):
  cSel = "Update national SET ou_id = 0" 
else:
  cSel = "ALTER TABLE national ADD ou_id integer" 
db.query(cSel)

if check_field(db, 'area', 'ou_id'):
  cSel = "Update area SET ou_id = 0" 
else:
  cSel = "ALTER TABLE area ADD ou_id integer; Update area SET ou_id = 0" 
db.query(cSel)

if check_field(db, 'district', 'ou_id'):
  cSel = "Update district SET ou_id = 0" 
else:
  cSel = "ALTER TABLE district ADD ou_id integer; Update district SET ou_id = 0" 
db.query(cSel)

if check_field(db, 'groupdef', 'ou_id'):
  cSel = "Update groupdef SET ou_id = 0" 
else:
  cSel = "ALTER TABLE groupdef ADD ou_id integer; Update groupdef SET ou_id = 0" 
db.query(cSel)

if check_field(db, 'unit', 'ou_id'):
  cSel = "Update unit SET ou_id = 0" 
else:
  cSel = "ALTER TABLE unit ADD ou_id integer; Update unit SET ou_id = 0" 
db.query(cSel)

if not check_field(db, 'role', 'ou_id'):
  cSel = "ALTER TABLE role ADD ou_id integer"
  db.query(cSel)

if check_field(db, 'role', 'status'):
  cSel = "Update role SET status = ' '" 
else:
  cSel = "ALTER TABLE role ADD status char; Update role SET status = ' '" 
db.query(cSel)

if check_field(db, 'role', 'ou_order'):
  cSel = "Update role SET ou_order = 1" 
else:
  cSel = "ALTER TABLE role ADD ou_order integer; Update role SET ou_order = 1" 
db.query(cSel)

if not check_field(db, 'connection', 'last_ou_id'):
  cSel = "ALTER TABLE connection ADD last_ou_id integer; Update connection SET last_ou_id = 0" 
  db.query(cSel)

if not check_field(db, 'scout', 'home_ou_id'):
  cSel = "ALTER TABLE scout ADD home_ou_id integer; Update scout SET home_ou_id = 0" 
  db.query(cSel)

if not check_field(db, 'award_type', 'ou_struct'):
  cSel = "ALTER TABLE award_type ADD ou_struct integer"
  db.query(cSel)

db.query("Update award_type SET ou_struct = 5 WHERE sect_cd = 'K'")
db.query("Update award_type SET ou_struct = 6 WHERE sect_cd = 'C'")
db.query("Update award_type SET ou_struct = 7 WHERE sect_cd = 'S'")
db.query("Update award_type SET ou_struct = 8 WHERE sect_cd = 'V'")
db.query("Update award_type SET ou_struct = 1 WHERE sect_cd = 'A'")

db.close()
import dbobj
import olddbobj

db = dbobj.dbinstance(dbname)

############################################################################
# National record added
nat = olddbobj.nationalrec(db)

#Create nationalrec
natou = dbobj.ourec(db, 0)
natou.name = nat.name
natou.ou_owner = 0
natou.ou_struct = 1
natou.add()
natou = dbobj.ourec(db, 1)

nat.ou_id = natou.ou_id
nat.update()

natou.get_mngt()
natou.add_mngt()

roles = nat.role_list()
rCnt = 0
for r in roles:
  r.ou_id = natou.mngt_ou.ou_id
  r.ou_order = 10
  r.status = 'C'
  r.add_edit()
  rCnt += 1


print "National record updated"
print "%d national role records updated" % rCnt

############################################################################
# Area records
nat.area_list()

aCnt = 0
arCnt = 0
amCnt = 0

dCnt = 0
drCnt = 0
dmCnt = 0

gCnt = 0
grCnt = 0
gmCnt = 0

uCnt = 0
urCnt = 0
umCnt = 0

for a in nat.arealist:
  aCnt +=1
  #Create arearec
  aou = dbobj.ourec(db, 0)
  aou.name = a.name
  aou.ou_owner = natou.ou_id
  aou.ou_struct = 2
  aou.add()
  aou_id = aou.ou_id
  # Refresh area object
  aou = dbobj.ourec(db, aou_id)

  #Update orginal area record
  a.ou_id = aou.ou_id
  a.update()

  # Create area management ou
  aou.get_mngt()
  aou.add_mngt()

  roles = a.role_list()
  for r in roles:
    r.ou_id = aou.mngt_ou.ou_id
    r.ou_order = 10
    r.status = 'C'
    r.add_edit()
    arCnt += 1

  a.district_list()
  for d in a.districtlist:
    dCnt +=1
    dou = dbobj.ourec(db, 0)
    dou.name = d.name
    dou.curr_memb = d.curr_memb
    dou.ou_owner = aou.ou_id
    dou.ou_struct = 3
    dou.add()
    dou_id = dou.ou_id
    # Refresh dist ou rec
    dou = dbobj.ourec(db, dou_id)

    d.ou_id = dou.ou_id
    d.update()

    # Create area management ou
    dou.get_mngt()
    dou.add_mngt()

    roles = d.role_list()
    for r in roles:
      r.ou_id = dou.mngt_ou.ou_id
      r.ou_order = 10
      r.status = 'C'
      r.add_edit()
      drCnt += 1


    d.group_list()
    for g in d.grouplist:
      gCnt += 1
      gou = dbobj.ourec(db, 0)
      gou.name = g.name
      gou.curr_memb = g.curr_memb
      gou.ou_owner = dou.ou_id
      gou.ou_struct = 4
      gou.add()
      gou_id = gou.ou_id
      # Refresh dist ou rec
      gou = dbobj.ourec(db, gou_id)
  
      g.ou_id = gou.ou_id
      g.update()

      # Create area management ou
      gou.get_mngt()
      gou.add_mngt()

      roles = g.role_list()
      for r in roles:
        r.ou_id = gou.mngt_ou.ou_id
        r.ou_order = 10
        r.status = 'C'
        r.add_edit()
        grCnt += 1


      g.unit_list()
      for u in g.unitlist:
        uCnt += 1
        uou = dbobj.ourec(db, 0)
        uou.name = u.name
        uou.curr_memb = u.curr_memb
        uou.ou_owner = gou.ou_id
        if u.sect_cd == 'K':
          uou.ou_struct = 5
        elif u.sect_cd == 'C':
          uou.ou_struct = 6
        elif u.sect_cd == 'S':
          uou.ou_struct = 7
        elif u.sect_cd == 'V':
          uou.ou_struct = 8
        uou.add()
        uou_id = uou.ou_id
        # Refresh dist ou rec
        uou = dbobj.ourec(db, uou_id)
    
        u.ou_id = uou.ou_id
        u.update()
  
        # Create area management ou
        uou.get_mngt()
        uou.add_mngt()

        u.role_list()
        for r in u.rolelist:
          r.ou_id = uou.mngt_ou.ou_id
          r.ou_order = 10
          r.status = 'C'
          r.add_edit()
          urCnt +=1

        # Add role records for all scouting members
        u.scout_list(status='')
        for s in u.scoutlist:
          if s.status == 'C' or s.status == 'L':
            role = dbobj.rolerec(db, 0)
            role.scout_id = s.scout_id
            role.ou_id = uou_id
            role.status = s.status
            role.ou_order = 1
            role.add_edit()
            umCnt += 1

print "%d Area records updated" % aCnt
print "%d area role records updated" % arCnt
print "%d area member records updated" % amCnt
print "%d District records updated" % dCnt
print "%d district role records updated" % drCnt
print "%d district member records updated" % dmCnt
print "%d Group records updated" % gCnt
print "%d group role records updated" % grCnt
print "%d group member records updated" % gmCnt
print "%d Unit records updated" % uCnt
print "%d unit role records updated" % urCnt
print "%d unit member records updated" % umCnt

db.database.commit()
db.database.close()

