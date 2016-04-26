DROP TABLE section;
CREATE TABLE section (
  sect_cd	char(1) PRIMARY KEY,
  name		varchar(60),
  start_age	real,
  end_age	real,
  next_sect	char(1),
  collective	varchar(60),
  comments	text
);

GRANT SELECT,UPDATE,INSERT,DELETE ON section TO apache;

INSERT INTO section VALUES ('K', 'Kea', 6, 8, 'C', 'club');
INSERT INTO section VALUES ('C', 'Cubs', 8, 10.5, 'S', 'Pack');
INSERT INTO section VALUES ('S', 'Scouts', 10.5, 15, 'V', 'Troop');
INSERT INTO section VALUES ('V', 'Venturers', 15, 18, 'R', 'Troop');
INSERT INTO section VALUES ('R', 'Rovers', 18, 24, 'A', 'Troop');
INSERT INTO section VALUES ('A', 'Adults');
