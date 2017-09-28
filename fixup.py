import os
import sys

from flask import Flask

from lib.database_wrapper import DatabaseWrapper
from lib.resize import resize

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

db = DatabaseWrapper(app.config.get_namespace('DATABASE_'))

config = app.config.get_namespace('IMAGES_')

##
# Look for files that have not been deleted
##
for photo in db.all_the_photos():
    if photo[2] == 'deleted':
        filename = config['destination_root'] + 'images/' + photo[1]
        if os.path.exists(filename):
            print("Removing {}".format(filename))
            os.remove(filename)

        filename = config['destination_root'] + 'medium/' + photo[3]
        if os.path.exists(filename):
            print("Removing {}".format(filename))
            os.remove(filename)

        filename = config['destination_root'] + 'thumbs/' + photo[3]
        if os.path.exists(filename):
            print("Removing {}".format(filename))
            os.remove(filename)
    else:
        source = config['destination_root'] + 'images/' + photo[1]

        filename = config['destination_root'] + 'medium/' + photo[3]
        if not os.path.exists(filename):
            print("Resize {}".format(filename))
            resize(source, filename, 800)

        filename = config['destination_root'] + 'thumbs/' + photo[3]
        if not os.path.exists(filename):
            print("Resize {}".format(filename))
            resize(source, filename, 125)

        number = len(db.all_tags_for_photo(photo[0]))
        if number == 0:
            print("Added 'untagged' tag to {}".format(photo[0]))
            db.add_tag_to_photo(photo[0], 'untagged')


sys.exit(0)
