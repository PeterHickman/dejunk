#!/usr/bin/env python

import os
import sys

from lib.database_wrapper import DatabaseWrapper
from lib.resize import resize

import settings as config

db = DatabaseWrapper(config.CONNECTION_STRING)

##
# Look for files that have not been deleted
##
for photo in db.all_the_photos():
    if photo[2] == 'deleted':
        filename = config.DESTINATION_ROOT + 'images/' + photo[1]
        if os.path.exists(filename):
            print("Removing {}".format(filename))
            os.remove(filename)

        filename = config.DESTINATION_ROOT + 'medium/' + photo[3]
        if os.path.exists(filename):
            print("Removing {}".format(filename))
            os.remove(filename)

        filename = config.DESTINATION_ROOT + 'thumbs/' + photo[3]
        if os.path.exists(filename):
            print("Removing {}".format(filename))
            os.remove(filename)
    else:
        source = config.DESTINATION_ROOT + 'images/' + photo[1]

        filename = config.DESTINATION_ROOT + 'medium/' + photo[3]
        if not os.path.exists(filename):
            print("Resize {}".format(filename))
            resize(source, filename, 800)

        filename = config.DESTINATION_ROOT + 'thumbs/' + photo[3]
        if not os.path.exists(filename):
            print("Resize {}".format(filename))
            resize(source, filename, 125)

        number = len(db.all_tags_for_photo(photo[0]))
        if number == 0:
            print("Added 'untagged' tag to {}".format(photo[0]))
            db.add_tag_to_photo(photo[0], 'untagged')

