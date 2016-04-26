DROP TABLE award_type;

CREATE TABLE award_type (
  award_type	integer primary key,
  sect_cd	char(1),
  name		varchar(40)
);

GRANT SELECT,UPDATE,INSERT,DELETE ON award_type TO apache;

INSERT INTO award_type VALUES (1, 'C', 'Wero badge');
INSERT INTO award_type VALUES (2, 'C', 'Kiwi badge');
INSERT INTO award_type VALUES (3, 'C', 'Interest badge');
INSERT INTO award_type VALUES (4, 'C', 'General');
INSERT INTO award_type VALUES (5, 'K', 'General');
INSERT INTO award_type VALUES (6, 'S', 'General');
INSERT INTO award_type VALUES (7, 'V', 'General');
INSERT INTO award_type VALUES (8, 'R', 'General');
INSERT INTO award_type VALUES (9, 'L', 'General');


