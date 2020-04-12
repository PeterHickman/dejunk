#!/usr/bin/env python

import os
import sys

from lib.database_wrapper import DatabaseWrapper

import settings as config

db = DatabaseWrapper(config.CONNECTION_STRING)

##
# Look for files that have not been deleted
##
for photo in db.all_the_photos():
    if photo[2] == 'junk':
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

        db.remove_all_tags_from_photo(photo[0])
        db.set_to_deleted(photo[0])
