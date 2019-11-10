# A little image catalog

I collect images from Flickr by tag and them have to filter and classify them. This internal website was the tool I created to make my life easier

The original was in Ruby 1.8.7 and Rails 2.1. Very out of date and needing a cleanup. An attempt to convert it to a newer Ruby and Rails made the code even messier. Upgrading from Rails 2.1 to 5.0 was less than smooth. A rewrite was in order to clean up the code and add new features

So I rewrote it in Python and Flask. Because I could :P

## Database schema

```sql
CREATE TABLE photos (
    id serial PRIMARY KEY,
    filename text,
    status character varying(10) DEFAULT 'unknown'::character varying,
    othername text,
    file_size integer
);


CREATE TABLE tags (
    id serial PRIMARY KEY,
    name character varying(64),
    display character varying(64),
    photo_id integer NOT NULL
);

CREATE INDEX index_photos_on_filename ON photos USING btree (filename);

CREATE INDEX index_photos_on_status ON photos USING btree (status);

CREATE INDEX index_tags_on_name ON tags USING btree (name);

CREATE UNIQUE INDEX index_tags_on_name_and_photo_id ON tags USING btree (name, photo_id);

CREATE INDEX index_tags_on_photo_id ON tags USING btree (photo_id);
```

## Security

There is none. The site is internal, it does not connect to the internet and neither does the database. Knowing the contents of `settings.py` will not get you anything

## TODO

0. Reimplement autocomplete
