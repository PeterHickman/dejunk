#!/usr/bin/env python

import glob
import os
import sys
import shutil

from lib.database_wrapper import DatabaseWrapper
from lib.resize import resize

from settings import config

db = DatabaseWrapper(config.CONNECTION_STRING)

counter = 0
for filename in glob.glob(config.SOURCE_PATH + '*'):
    if os.path.isfile(filename):
        counter += 1

        basename = os.path.basename(filename)

        dest_name = config.DESTINATION_ROOT + 'images/' + basename
        if os.path.exists(dest_name):
            print('{}: File {} already found'.format(counter, basename))
        else:
            print('{}: Need to import {}'.format(counter, basename))

            (path, ext) = os.path.splitext(basename)
            othername = path + '.png'

            db.add_new_photo(basename, othername)

            # Create the medium image
            new_filename = config.DESTINATION_ROOT + 'medium/' + othername
            resize(filename, new_filename, 800)

            # Create the thumbnail
            new_filename = config.DESTINATION_ROOT + 'thumbs/' + othername
            resize(filename, new_filename, 125)

            # Copy the source image
            new_filename = config.DESTINATION_ROOT + 'images/' + basename
            shutil.copy2(filename, new_filename)

        # Remove the original
        os.remove(filename)
