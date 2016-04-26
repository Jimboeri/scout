DROP TABLE area;
DROP SEQUENCE area_seq;

CREATE TABLE area (
  area_id	integer PRIMARY KEY,
  national_id	char(1) REFERENCES national,
  curr_memb	integer,
  name		varchar(60)
);

CREATE SEQUENCE area_seq START 3;

GRANT SELECT,UPDATE,INSERT,DELETE ON area TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON area_seq TO apache;

INSERT INTO area VALUES (1, '1', 'Mahurangi');
INSERT INTO area VALUES (2, '1', 'Northland');
