drop table connection;

create table connection (
  ref_id	char(10) PRIMARY KEY,
  scout_id	integer,
  auth_key	char(20),
  last_access	timestamp without time zone,
  last_level	char(1),
  last_level_id integer
);

GRANT SELECT,UPDATE,INSERT,DELETE ON connection TO apache;
