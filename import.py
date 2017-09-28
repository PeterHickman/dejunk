import glob
import os
import sys
import shutil

from flask import Flask

from lib.database_wrapper import DatabaseWrapper
from lib.resize import resize

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

db = DatabaseWrapper(app.config.get_namespace('DATABASE_'))

config = app.config.get_namespace('IMAGES_')

counter = 0
for filename in glob.glob(config['source_path'] + '*'):
    if os.path.isfile(filename):
        counter += 1

        basename = os.path.basename(filename)

        dest_name = config['destination_root'] + 'images/' + basename
        if os.path.exists(dest_name):
            print('{}: File {} already found'.format(counter, basename))
        else:
            print('{}: Need to import {}'.format(counter, basename))

            (path, ext) = os.path.splitext(basename)
            othername = path + '.png'

            db.add_new_photo(basename, othername)

            # Create the medium image
            new_filename = config['destination_root'] + 'medium/' + othername
            resize(filename, new_filename, 800)

            # Create the thumbnail
            new_filename = config['destination_root'] + 'thumbs/' + othername
            resize(filename, new_filename, 125)

            # Copy the source image
            new_filename = config['destination_root'] + 'images/' + basename
            shutil.copy2(filename, new_filename)

        # Remove the original
        os.remove(filename)

sys.exit(0)
