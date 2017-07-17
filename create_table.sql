create table status(
  id integer NOT NULL,
  text text NOT NULL,
  in_reply_to_status_id integer default 0,
  user_id integer NOT NULL,
  is_quote_status integer NOT NULL,
  created_at integer NOT NULL,
  CONSTRAINT status_id PRIMARY KEY (id)
);

CREATE INDEX in_reply_to_status_id ON status (in_reply_to_status_id);

create table user(
  id integer NOT NULL,
  screen_name varchar(128) UNIQUE,
  name text NOT NULL,
  description text,
  CONSTRAINT user_id PRIMARY KEY (id)
);
