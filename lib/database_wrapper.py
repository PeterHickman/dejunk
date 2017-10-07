import psycopg2
import psycopg2.extras

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

    def status_information(self):
        data = {'ok': 0, 'junk': 0, 'unknown': 0, 'total': 0}

        self._cursor.execute("SELECT status, count(*) FROM photos GROUP BY status")
        rows = self._cursor.fetchall()

        for row in rows:
            if row[0] in data:
                data[row[0]] = row[1]
                data['total'] += row[1]

        return data

    def add_new_photo(self, filename, othername):
        data = {'filename': filename, 'othername': othername, 'status': 'unknown'}

        sql = "INSERT INTO photos (filename, othername, status) VALUES (%(filename)s, %(othername)s, %(status)s);"
        self._cursor.execute(sql, data)

    def photos_with_status(self, status, page_size, row_length, page):
        ##
        # 'data' holds the values used when we call the database
        ##
        data = {}
        data['limit'] = page_size
        data['status'] = status

        ##
        # This is the information we will be returning
        ##
        results = {}

        ##
        # Total number of records
        ##
        sql = "SELECT COUNT(*) FROM photos WHERE status = %(status)s"
        self._cursor.execute(sql, data)
        results['total_records'] = int(self._cursor.fetchone()[0])

        ##
        # The tabs for pagination and the revised 'page'
        ##
        (tabs, page) = paginate(results['total_records'], page_size, page)
        results['tabs'] = tabs
        results['page'] = page

        data['offset'] = (page - 1) * page_size

        ##
        # The data for the page we are looking at
        ##
        sql = "SELECT id, othername FROM photos WHERE status = %(status)s ORDER BY id DESC OFFSET %(offset)s LIMIT %(limit)s"
        self._cursor.execute(sql, data)
        rows = self._cursor.fetchall()
        results['rows'] = group_by(rows, row_length)

        return results

    def classify_unknown(self, form):
        page = int(form['page'])

        for arg in form:
            if arg.startswith('photo_'):
                photo_id = int(arg[6:])
                status = form[arg]

                sql = "UPDATE photos SET status = %(status)s WHERE id = %(photo_id)s"
                self._cursor.execute(sql, {'status': status, 'photo_id': photo_id})

                if status == 'ok':
                    self.add_tag_to_photo(photo_id, 'untagged')

        return page

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

    def all_the_photos(self):
        sql = "SELECT * FROM photos ORDER BY id DESC"
        self._cursor.execute(sql)

        return self._cursor.fetchall()

    def all_tags_for_photo(self, photo_id):
        sql = "SELECT * FROM tags WHERE photo_id = %(photo_id)s"
        self._cursor.execute(sql, {'photo_id': photo_id})

        return self._cursor.fetchall()

    def add_tag_to_photo(self, photo_id, tag):
        name, display = tags.format(tag)

        sql = "SELECT * FROM tags WHERE photo_id = %(photo_id)s AND name = %(name)s"
        self._cursor.execute(sql, {'photo_id': photo_id, 'name': name})
        row = self._cursor.fetchone()

        if row is None:
            sql = "INSERT INTO tags (photo_id, name, display) VALUES (%(photo_id)s, %(name)s, %(display)s)"
            self._cursor.execute(sql, {'photo_id': photo_id, 'name': name, 'display': display})

    def remove_tag_from_photo(self, photo_id, tag):
        name, display = tags.format(tag)

        sql = "DELETE FROM tags WHERE photo_id = %(photo_id)s AND name = %(name)s"
        self._cursor.execute(sql, {'photo_id': photo_id, 'name': name})

    def remove_all_tags_from_photo(self, photo_id):
        sql = "DELETE FROM tags WHERE photo_id = %(photo_id)s"
        self._cursor.execute(sql, {'photo_id': photo_id})

    def add_tags_to_photos(self, req):
        photo_ids = [int(x) for x in req['id'].split(',')]
        tags = req['new_tag'].split(',')

        for photo_id in photo_ids:
            for new_tag in tags:
                if new_tag != '':
                    self.add_tag_to_photo(photo_id, new_tag)

    def all_tags_and_counts(self):
        sql = "SELECT DISTINCT(display), name, COUNT(*) FROM tags GROUP BY display, name ORDER BY display"
        self._cursor.execute(sql)

        return self._cursor.fetchall()

    def photos_by_tags(self, query, page_size, row_length, page):
        ##
        # This is the information we will be returning
        ##
        results = {}
        results['query'] = tags.rewrite_query(query)
        results['describe'] = tags.describe(query)

        ##
        # Total number of records
        ##
        sql = tags.tagged_with(query, True)
        self._cursor.execute(sql)

        row = self._cursor.fetchone()
        if row is None:
            results['total_records'] = 0
        else:
            results['total_records'] = int(row[0])

        ##
        # The tabs for pagination and the revised 'page'
        ##
        (tabs, page) = paginate(results['total_records'], page_size, page)
        results['tabs'] = tabs
        results['page'] = page

        ##
        # Get all the photos that this query matches
        ##
        sql = tags.tagged_with(query, False)
        self._cursor.execute(sql)
        photo_ids = [str(cell[0]) for cell in self._cursor.fetchall()]

        ##
        # Get all the tags associated with the photos
        ##
        if len(photo_ids) > 0:
            sql = "SELECT DISTINCT(name) FROM tags WHERE photo_id IN ({})".format(", ".join(photo_ids))
            self._cursor.execute(sql)
            results['used_tags'] = [list(tags.format(row[0])) for row in self._cursor.fetchall()]
        else:
            results['used_tags'] = []

        ##
        # Get the photos just on this page
        ##
        page_start = (page - 1) * page_size
        page_end = page_start + page_size

        photo_ids_on_page = photo_ids[page_start:page_end]

        if len(photo_ids) > 0:
            sql = "SELECT * FROM photos WHERE id IN ({}) ORDER BY id DESC".format(", ".join(photo_ids_on_page))
            self._cursor.execute(sql)
            rows = self._cursor.fetchall()
        else:
            rows = []

        results['rows'] = group_by(rows, row_length)

        return results

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
