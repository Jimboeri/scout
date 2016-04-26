DROP TABLE ou;
DROP SEQUENCE ou_seq;

DROP TABLE ou_struct;
CREATE TABLE ou_struct (
  ou_struct	int	PRIMARY KEY,
  parent_id	int,
  s_name	varchar(60),
  heirarchic	int
);

INSERT INTO ou_struct VALUES (1, 0, 'National', 1);
INSERT INTO ou_struct VALUES (2, 1, 'Area', 1);
INSERT INTO ou_struct VALUES (3, 2, 'District', 1);
INSERT INTO ou_struct VALUES (4, 3, 'Group', 1);
INSERT INTO ou_struct VALUES (5, 4, 'Unit', 1);
INSERT INTO ou_struct VALUES (101, 0, 'Committee', 0);

CREATE TABLE ou (
  ou_id		int PRIMARY KEY,
  ou_owner	int,
  ou_struct	int REFERENCES ou_struct,
  name		varchar(60),
  curr_memb	int DEFAULT 0,
  curr_child    int DEFAULT 0,
  p_addr1	varchar(60),
  p_addr2	varchar(60),
  p_addr3	varchar(60),
  p_code	varchar(10),
  m_addr1	varchar(60),
  m_addr2	varchar(60),
  m_addr3	varchar(60),
  m_code	varchar(10),
  phone		varchar(60),
  fax		varchar(60),
  sect_cd	char(1),
  meet_time	varchar(60),
  start_age	real,
  end_age	real,
  award_remind  date
);

CREATE SEQUENCE ou_seq START 1;

GRANT SELECT,UPDATE,INSERT,DELETE ON ou TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON ou_seq TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON ou_struct TO apache;

INSERT INTO ou VALUES (nextval('ou_seq'), 0, 1, 'Scouting New Zealand');
INSERT INTO ou VALUES (nextval('ou_seq'), 1, 2, 'Mahurangi');

