DROP TABLE scout;
DROP SEQUENCE scout_seq;

CREATE TABLE scout (
  scout_id	integer PRIMARY KEY,
  forename	varchar(60),
  initials	varchar(20),
  surname	varchar(80),
  unit_id	integer,
  unit_since	date,
  status	char(1),
  status_dt	date,
  addr1		varchar(60),
  addr2		varchar(60),
  addr3		varchar(60),
  p_code	char(4),
  telephone_h	varchar(40),
  telephone_w	varchar(40),
  fax		varchar(40),
  mobile	varchar(40),
  email		varchar(80),
  parent1	integer,
  parent2	integer,
  partner_id	integer,
  on_line_id	varchar(40),
  passwd	char(40),
  oldpasswd	char(40),
  pw_expire	date,
  pw_hint	varchar(40),
  on_line_disable	boolean,
  online_agree_dt date,
  date_of_birth	date,
  scout_name	varchar(40),
  home_level	char(1),
  home_id	integer,
  school	varchar(60),
  gender	char(1),
  add_info	text,
  superuser	boolean		DEFAULT FALSE
);

CREATE INDEX scout_unit_idx ON scout (unit_id);
CREATE INDEX scout_parent1_idx ON scout (parent1);

CREATE SEQUENCE scout_seq start 1;

GRANT SELECT,UPDATE,INSERT,DELETE ON scout TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON scout_seq TO apache;

INSERT INTO scout (scout_id, forename, initials, surname, on_line_id, scout_name, superuser, addr1, addr2, addr3, p_code, telephone_h, telephone_w, fax, mobile, email, partner_id, add_info) VALUES (nextval('scout_seq'), 'Jim', '', 'West', 'weka', 'Weka', TRUE, '171 Glamorgan drive', 'Torbay', 'NSC', '1030', '09 473 2434', '09 355 2157', '021 blah', '021 466 721', 'jim@west.net.nz', 4, 'Additional text info here');
INSERT INTO scout (scout_id, forename, initials, surname, unit_id, parent1, parent2, date_of_birth, status) VALUES (nextval('scout_seq'), 'Duncan', '', 'West', 1, 1, 4, '1997-07-19', 'C');
INSERT INTO scout (scout_id, forename, initials, surname, unit_id, date_of_birth, parent1, status) VALUES (nextval('scout_seq'), 'Luke', '', 'Wright', 1, '1997-12-29', 6, 'C');

INSERT INTO scout (scout_id, forename, initials, surname, on_line_id, addr1, addr2, addr3, p_code, telephone_h, telephone_w, fax, mobile, email, add_info) VALUES (nextval('scout_seq'), 'Alison', '', 'West', 'fats', '171 Glamorgan drive', 'Torbay', 'NSC', '1030', '09 473 2434', '', '', '021 618 516', 'alison@west.net.nz', 'Additional text info here');
INSERT INTO scout (scout_id, forename, initials, surname, unit_id, date_of_birth, parent1, status) VALUES (nextval('scout_seq'), 'John', '', 'Wright', 2, '1994-12-29', 6, 'C');
INSERT INTO scout (scout_id, forename, initials, surname, date_of_birth) VALUES (nextval('scout_seq'), 'Bruce', '', 'Wright', '1964-12-29');
