#!/usr/bin/env python

import os
import sys

from lib.database_wrapper import DatabaseWrapper

import settings as config

db = DatabaseWrapper(config.CONNECTION_STRING)

list_of_dups = sys.argv[1]

print("Read duplicates from {}".format(list_of_dups))


with open(list_of_dups) as fh:
    tag_index = 1

    for line in fh:
        tag = "Duplicates {}".format(tag_index)
        print(tag)

        line = line.strip()
        filenames = line.split(' ')
        for filename in filenames:
            photo = db.photo_by_filename(filename)
            db.add_tag_to_photo(photo[0], tag)

        tag_index += 1
