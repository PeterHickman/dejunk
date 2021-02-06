def group_by(rows, row_size)
  # Split a list of <rows> into a list of <row_size> lists

  groups = []

  while rows.any?
    groups << rows.shift(row_size)
  end

  groups
end

def paginate(total_number_of_records, page_size, page)
  # Create the pagination tabs for <total_number_of_records> paginated
  # <page_size> per page. Focused around the <page>

  return [[], 1] if total_number_of_records == 0

  number_of_pages = total_number_of_records / page_size
  number_of_pages += 1 if total_number_of_records % page_size != 0

  tabs = Array.new(number_of_pages, nil)
  tabs[0] = 1
  tabs[-1] = number_of_pages

  page = number_of_pages if page > number_of_pages

  ((page - 4)..(page + 4)).each do |pos|
    tabs[pos] = pos + 1 if 0 <= pos && pos < number_of_pages
  end

  final_tabs = []
  last_was_none = false

  tabs.each do |tab|
    if tab != nil
      final_tabs << tab
      last_was_none = false
    else
      if last_was_none == false
        final_tabs << '...'
        last_was_none = true
      end
    end
  end

  [final_tabs, page]
end
