import re


def format(text):
    clean_tag = re.sub("\s+", " ", text.lower().strip())

    name = clean_tag.replace(' ', '_')
    display = display_name(clean_tag)

    return name, display

def display_name(name):
    return name.title().replace('_', ' ')

def split_tags(tags):
    """
    Given a string of space separated tags, group them into includes and
    excludes based on a '-' prefix for exclude
    """

    includes = []
    excludes = []

    for tag in tags.split():
        if tag.startswith('-'):
            if tag[1:] not in excludes:
                excludes.append(tag[1:])
        else:
            if tag not in includes:
                includes.append(tag)

    for tag in includes:
        if tag in excludes:
            excludes.remove(tag)
            includes.remove(tag)

    return includes, excludes


def rewrite_query(tags):
    includes, excludes = split_tags(tags)

    for tag in excludes:
        includes.append("-{}".format(tag))

    return " ".join(includes)


def describe(tags):
    includes, excludes = split_tags(tags)

    text = ''
    if len(includes) > 0:
        text += "Includes: {}".format(', '.join([display_name(name) for name in includes]))

    if len(excludes) > 0:
        if len(text) > 0:
            text += ". "

        text += "Excludes: {}".format(', '.join([display_name(name) for name in excludes]))

    return text


def tagged_with(tags, counted):
    """
    Return the SQL required to get the photos matching the tag query
    """

    includes, excludes = split_tags(tags)

    if counted:
        select = 'COUNT(*)'
    else:
        select = 'photo_id'

    sql = ''

    if len(includes) > 0:
        sql += "SELECT {} FROM tags WHERE name IN ('{}')".format(select, "', '".join(includes))

        if len(excludes) > 0:
            sql += " AND photo_id NOT IN (SELECT photo_id FROM tags WHERE name IN ('{}'))".format("', '".join(excludes))

        if len(includes) > 1:
            sql += " GROUP BY photo_id HAVING COUNT(photo_id) = {}".format(len(includes))

    elif len(excludes) > 0:
        sql += "SELECT {} FROM tags WHERE photo_id NOT IN (SELECT photo_id FROM tags WHERE name IN ('{}'))".format(select, "', '".join(excludes))

    else:
        sql += "SELECT {} FROM tags".format(select)

    if counted is False:
        sql += " ORDER BY photo_id DESC"

    return sql
