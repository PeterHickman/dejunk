def paginate(total_number_of_records, page_size, page):
    """
    Create the pagination tabs for <total_number_of_records> paginated
    <page_size> per page. Focused around the <page>
    """

    if total_number_of_records == 0:
        return ([], 1)

    number_of_pages = total_number_of_records / page_size
    if total_number_of_records % page_size is not 0:
        number_of_pages += 1

    tabs = [None] * number_of_pages
    tabs[0] = 1
    tabs[-1] = number_of_pages

    if page > number_of_pages:
        page = number_of_pages

    for pos in range(page - 4, page + 5):
        if 0 <= pos and pos < number_of_pages:
            tabs[pos] = pos+1

    final_tabs = []
    last_was_none = False

    for tab in tabs:
        if tab is not None:
            final_tabs.append(tab)
            last_was_none = False
        else:
            if last_was_none is False:
                final_tabs.append('...')
                last_was_none = True

    return (final_tabs, page)


def group_by(rows, row_size):
    """
    Split a list of <rows> into a list of <row_size> lists
    """

    groups = []

    while len(rows) > 0:
        groups.append(rows[:row_size])
        rows = rows[row_size:]

    return groups
