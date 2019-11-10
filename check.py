#!/usr/bin/env python

import glob
import os
import sys

from lib.database_wrapper import DatabaseWrapper

import settings as config

db = DatabaseWrapper(config.CONNECTION_STRING)


def count_images(photo):
    exists = 0

    filename = config.DESTINATION_ROOT + 'images/' + photo[1]
    if os.path.exists(filename):
        exists += 1

    filename = config.DESTINATION_ROOT + 'medium/' + photo[3]
    if os.path.exists(filename):
        exists += 1

    filename = config.DESTINATION_ROOT + 'thumbs/' + photo[3]
    if os.path.exists(filename):
        exists += 1

    return exists


def has_no_tags(photo):
    number = len(db.all_tags_for_photo(photo[0]))
    if number != 0:
        print("{} {} still has {} tags".format(photo[2], photo[0], number))


def has_some_tags(photo):
    number = len(db.all_tags_for_photo(photo[0]))
    if number == 0:
        print("{} {} should have at least 1 tag".format(photo[2], photo[0]))


def has_all_images(photo):
    number = count_images(photo)
    if number != 3:
        print("{} {} is missing files. Has {}".format(photo[2], photo[0], number))


def has_no_images(photo):
    number = count_images(photo)
    if number != 0:
        print("{} {} needs it's files removed".format(photo[2], photo[0]))

def has_real_size(photo):
    if photo[4] == None:
        print("{} {} has no size".format(photo[0], photo[1]))

##
# First we check the database against the filesystem
##

image_names = []
other_names = []

for photo in db.all_the_photos():
    if photo[2] == 'deleted':
        has_no_tags(photo)
        has_no_images(photo)

    elif photo[2] == 'junk':
        has_no_tags(photo)
        has_all_images(photo)
        image_names.append(photo[1])
        other_names.append(photo[3])

    elif photo[2] == 'ok':
        has_some_tags(photo)
        has_all_images(photo)
        has_real_size(photo)
        image_names.append(photo[1])
        other_names.append(photo[3])

    elif photo[2] == 'unknown':
        has_no_tags(photo)
        has_all_images(photo)
        image_names.append(photo[1])
        other_names.append(photo[3])

##
# Now check the filesystem
##

for filename in glob.glob(config.DESTINATION_ROOT + 'images/*'):
    basename = os.path.basename(filename)

    if basename not in image_names:
        print("The image {} is not in the database".format(basename))

for filename in glob.glob(config.DESTINATION_ROOT + 'medium/*'):
    basename = os.path.basename(filename)

    if basename not in other_names:
        print("The medium {} is not in the database".format(basename))

for filename in glob.glob(config.DESTINATION_ROOT + 'thumbs/*'):
    basename = os.path.basename(filename)

    if basename not in other_names:
        print("The thumbs {} is not in the database".format(basename))
