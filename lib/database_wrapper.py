import psycopg2
import psycopg2.extras
import humanize

from paginate import paginate, group_by
import tags


class DatabaseWrapper(object):
    def __init__(self, connection_string):
        self._connection_string = connection_string
        self._cursor = self._make_connection()

    def _make_connection(self):
        try:
            conn = psycopg2.connect(self._connection_string)
        except psycopg2.Error, e:
            raise RuntimeError("Unable to connect to the database with [{}] {}".format(self._connection_string, e.diag.message_primary))

        conn.autocommit = True
        return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def _photos_by_one_tag(self, name):
        sql = "SELECT photo_id FROM tags WHERE name = %(name)s"
        self._cursor.execute(sql, {'name': name})
        photo_ids = [row[0] for row in self._cursor.fetchall()]

        return photo_ids


    def purged_photos():
        sql = "SELECT id,  FROM photos WHERE status = %(status)s ORDER BY id DESC"
        self._cursor.execute(sql, ('junk',))
        return self._cursor.fetchall()

    def photos_to_delete(self, form):
        page = int(form['page'])

        for arg in form:
            if arg.startswith('photo_'):
                photo_id = int(arg[6:])

                sql = "UPDATE photos SET status = %(status)s WHERE id = %(photo_id)s"
                self._cursor.execute(sql, {'status': 'deleted', 'photo_id': photo_id})

                sql = "DELETE FROM tags where photo_id = %(photo_id)s"
                self._cursor.execute(sql, {'photo_id': photo_id})

        return page

    def remove_old_duplicate_tags(self):
        sql = "DELETE FROM tags WHERE name like 'duplicates_%'"
        self._cursor.execute(sql, {})


    def remove_tag_from_photo(self, photo_id, tag):
        name, display = tags.format(tag)

        sql = "DELETE FROM tags WHERE photo_id = %(photo_id)s AND name = %(name)s"
        self._cursor.execute(sql, {'photo_id': photo_id, 'name': name})

    def add_tags_to_photos(self, req):
        photo_ids = [int(x) for x in req['id'].split(',')]
        tags = req['new_tag'].split(',')

        for photo_id in photo_ids:
            for new_tag in tags:
                if new_tag != '':
                    self.add_tag_to_photo(photo_id, new_tag)

    def photo_by_filename(self, filename):
        data = {'filename': filename}
        sql = "SELECT * FROM photos WHERE filename = %(filename)s"
        self._cursor.execute(sql, data)

        return self._cursor.fetchone()

    def get_picture(self, photo_id):
        sql = "SELECT * FROM photos WHERE id = %(photo_id)s"
        self._cursor.execute(sql, {'photo_id': photo_id})

        picture = self._cursor.fetchone()
        return picture

    def convert_junk(self):
        photo_ids = self._photos_by_one_tag('junk')

        counter = 0

        for photo_id in photo_ids:
            sql = "UPDATE photos SET status = 'junk' WHERE id = %(photo_id)s"
            self._cursor.execute(sql, {'photo_id': photo_id})

            sql = "DELETE FROM tags WHERE photo_id = %(photo_id)s"
            self._cursor.execute(sql, {'photo_id': photo_id})

            counter += 1

        return counter

    def remove_surplus(self):
        photo_ids = self._photos_by_one_tag('untagged')

        counter = 0

        for photo_id in photo_ids:
            tags = self.all_tags_for_photo(photo_id)
            if len(tags) > 1:
                sql = "DELETE FROM tags WHERE name = 'untagged' AND photo_id = %(photo_id)s"
                self._cursor.execute(sql, {'photo_id': photo_id})

                counter += 1

        return counter
