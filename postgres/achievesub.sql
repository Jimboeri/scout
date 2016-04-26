DROP TABLE achievesub;

CREATE TABLE achievesub (
  scout_id	integer REFERENCES scout ON DELETE cascade,
  award_id	integer REFERENCES award,
  sub_award_id  integer,
  sub_ach_id	integer,
  dt_obtained	date,
  comments	text,
  PRIMARY KEY (scout_id, award_id, sub_award_id, sub_ach_id)
);

GRANT SELECT,UPDATE,INSERT,DELETE ON achievesub TO apache;


