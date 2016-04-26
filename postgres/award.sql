DROP TABLE achievesub;
DROP TABLE achieve;

DROP TABLE awardsub;
DROP TABLE award;

DROP SEQUENCE awd_seq;

CREATE TABLE award (
  award_id	integer PRIMARY KEY,
  ou_level	char(1),
  sect_cd	char(1),
  award_type	integer references award_type,
  name		varchar(80), 
  descr		text,
  prereq	integer DEFAULT 0,
  leader	integer DEFAULT 0,
  opt_needed	integer DEFAULT 0,
  status	char(1) DEFAULT 'C',
  yrs_valid	integer DEFAULT 0,
  mth_valid	integer DEFAULT 0
);

CREATE SEQUENCE awd_seq START 36;

CREATE TABLE awardsub (
  award_id	integer REFERENCES award ON DELETE cascade,
  sub_award_id	integer,
  name		varchar(80), 
  descr		text,
  optional	integer,
  num_req	integer DEFAULT 1,
  PRIMARY KEY (award_id, sub_award_id)
);

CREATE TABLE achieve (
  scout_id	integer REFERENCES scout ON DELETE cascade,
  award_id	integer REFERENCES award,
  dt_obtained	date,
  comments	text,
  status	char(1),
  awd_presented integer,
  ldr_notify    integer,
  PRIMARY KEY (scout_id, award_id)
);

CREATE TABLE achievesub (
  scout_id	integer REFERENCES scout ON DELETE cascade,
  award_id	integer REFERENCES award,
  sub_award_id  integer,
  sub_ach_id	integer,
  dt_obtained	date,
  comments	text,
  PRIMARY KEY (scout_id, award_id, sub_award_id, sub_ach_id)
);


GRANT SELECT,UPDATE,INSERT,DELETE ON award TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON awardsub TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON achieve TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON achievesub TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON awd_seq TO apache;

INSERT INTO award VALUES (1, 'N', 'C', 3, 'Swimmer stage 1 Badge');
INSERT INTO award VALUES (2, 'N', 'C', 3, 'Swimmer stage 2 Badge', '', 1);
INSERT INTO award VALUES (3, 'N', 'C', 3, 'Swimmer stage 3 Badge', '', 2);
INSERT INTO award VALUES (4, 'N', 'C', 3, 'First Aid Badge');
INSERT INTO award VALUES (5, 'N', 'C', 3, 'Computer Badge');
INSERT INTO award VALUES (6, 'N', 'C', 3, 'Athlete stage 1 Badge');
INSERT INTO award VALUES (7, 'N', 'C', 3, 'Athlete stage 2 Badge', '', 6);
INSERT INTO award VALUES (8, 'N', 'C', 3, 'Athlete stage 3 Badge', '', 7);
INSERT INTO award VALUES (9, 'N', 'C', 3, 'Artist Badge');
INSERT INTO award VALUES (10, 'N', 'C', 3, 'Book reader Badge');
INSERT INTO award VALUES (11, 'N', 'C', 3, 'Conservation Badge');
INSERT INTO award VALUES (12, 'N', 'C', 3, 'Cook Badge', '', 25);
INSERT INTO award VALUES (13, 'N', 'C', 3, 'Cub Badge');
INSERT INTO award VALUES (14, 'N', 'C', 3, 'Cub Camper Badge');
INSERT INTO award VALUES (15, 'N', 'C', 3, 'Cyclist Badge');
INSERT INTO award VALUES (16, 'N', 'C', 3, 'Entertainer Badge');
INSERT INTO award VALUES (17, 'N', 'C', 3, 'Explorer Badge');
INSERT INTO award VALUES (18, 'N', 'C', 3, 'Faith Awareness Stage 1 Badge');
INSERT INTO award VALUES (19, 'N', 'C', 3, 'Faith Awareness Stage 2 Badge', '', 18);
INSERT INTO award VALUES (20, 'N', 'C', 3, 'Photographer Aid Badge');
INSERT INTO award VALUES (21, 'N', 'C', 3, 'Fishing Badge');
INSERT INTO award VALUES (22, 'N', 'C', 3, 'Handy Badge');
UPDATE award SET leader = 0;
