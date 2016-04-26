DROP TABLE national;
CREATE TABLE national (
  national_id	char(1) PRIMARY KEY,
  name		varchar(60)
);

GRANT SELECT,UPDATE ON national TO apache;

INSERT INTO national VALUES ('1', 'Scouting New Zealand');
