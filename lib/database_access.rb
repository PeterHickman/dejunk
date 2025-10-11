require 'tags'
require 'paginate'

class DatabaseAccess
  attr :db

  def initialize(dcs)
    @db = Sequel.connect(dcs)
  end

  def all_the_photos
    @db[:photos].order(:id).all
  end

  def all_tags_for_photo(photo_id)
    @db[:tags].where(photo_id: photo_id).all
  end

  def remove_all_tags_from_photo(photo_id)
    @db[:tags].where(photo_id: photo_id).delete
  end

  def set_to_deleted(photo_id)
    @db[:photos].where(id: photo_id).update(status: 'deleted')
  end

  def add_new_photo(filename, othername, file_size, now)
    existing = @db[:photos].where(filename: filename).first

    if existing
      @db[:photos].where(id: existing[:id]).update(othername: othername, status: 'unknown', file_size: file_size, imported_at: now)
      return existing[:id]
    else
      @db[:photos].insert(filename: filename, othername: othername, status: 'unknown', file_size: file_size, imported_at: now)
    end
  end

  def set_size(photo_id, file_size)
    @db[:photos].where(id: photo_id).update(file_size: file_size)
  end

  def add_tag_to_photo(photo_id, tag)
    name, display = Tags.format(tag)

    row = @db[:tags].where(photo_id: photo_id, name: name).first

    return if row

    @db[:tags].insert(photo_id: photo_id, name: name, display: display)
  end

  def status_information
    data = { 'ok' => 0, 'junk' => 0, 'unknown' => 0, 'total' => 0 }

    rows = @db['SELECT status, count(*) AS count FROM photos GROUP BY status']

    rows.each do |row|
      next if row[:status] == 'deleted'

      data[row[:status]] += row[:count]
      data['total'] += row[:count]
    end

    data
  end

  def photos_with_status(status, page_size, row_length, page)
    ##
    # 'data' holds the values used when we call the database
    ##
    data = { limit: page_size, status: status }

    ##
    # This is the information we will be returning
    ##
    results = {}

    ##
    # Total number of records
    ##
    total_records = @db[:photos].where(status: status).count
    results['total_records'] = total_records

    ##
    # The tabs for pagination and the revised 'page'
    ##
    tabs, page = paginate(results['total_records'], page_size, page)

    results['tabs'] = tabs
    results['page'] = page

    data['offset'] = (page - 1) * page_size

    ##
    # The data for the page we are looking at
    ##
    rows = @db[:photos].select(:id, :othername).where(status: status).order(:id).limit(page_size, data['offset']).all
    results['rows'] = group_by(rows, row_length)

    return results
  end

  def all_tags_and_counts
    @db['SELECT DISTINCT(display), name, COUNT(*) AS count FROM tags GROUP BY display, name ORDER BY display'].all
  end

  def photos_by_tags(query, page_size, row_length, page)
    ##
    # This is the information we will be returning
    ##
    results = {}
    results['query'] = Tags.rewrite_query(query)
    results['describe'] = Tags.describe(query)

    ##
    # Total number of records
    ##
    sql = Tags.tagged_with(query, true)
    row = @db[sql].first
    results['total_records'] = row[:count]

    ##
    # The tabs for pagination and the revised 'page'
    ##
    tabs, page = paginate(results['total_records'], page_size, page)
    results['tabs'] = tabs
    results['page'] = page

    ##
    # Get all the photos that this query matches
    ##
    sql = Tags.tagged_with(query, false)
    rows = @db[sql].all
    photo_ids = rows.map { |cell| cell[:photo_id] }

    ##
    # Get all the tags associated with the photos
    ##
    includes, excludes = Tags.split_tags(query)

    results['used_tags'] = []

    if photo_ids.any?
      sql = "SELECT DISTINCT(name) FROM tags WHERE photo_id IN (#{photo_ids.join(',')})"
      rows = @db[sql].all
      rows.each do |row|
        name, display = Tags.format(row[:name])
        can_add = true
        can_remove = true
        if includes.include?(name)
          can_add = false
          if includes.size == 1
            can_remove = false
          end
        end

        results['used_tags'] << [name, display, can_add, can_remove]
      end
    end

    ##
    # Get the photos just on this page
    ##
    if photo_ids.any?
      page_start = (page - 1) * page_size
      page_end = page_start + page_size

      photo_ids_on_page = photo_ids[page_start ... page_end]

      sql = "SELECT * FROM photos WHERE id IN (#{photo_ids_on_page.join(',')}) ORDER BY id DESC"

      rows = @db[sql].all
    else
      rows = []
    end

    results['rows'] = group_by(rows, row_length)

    results
  end

  def classify_unknown(photo_ids)
    photo_ids.each do |photo_id, status|
      @db[:photos].where(id: photo_id).update(status: status)
      add_tag_to_photo(photo_id, 'untagged') if status == 'ok'
    end
  end

  def photos_to_delete(photo_ids)
    photo_ids.each do |photo_id, status|
      @db[:photos].where(id: photo_id).update(status: 'deleted')
      @db[:tags].where(photo_id: photo_id).delete
    end
  end

  def get_picture(photo_id)
    @db[:photos].where(id: photo_id).first
  end

  def add_tags_to_photos(photo_ids, tags)
    photo_ids.each do |photo_id|
      tags.each do |tag|
        add_tag_to_photo(photo_id, tag)
      end
    end
  end

  def remove_tag_from_photo(photo_id, tag)
    name, display = Tags.format(tag)

    @db[:tags].where(photo_id: photo_id, name: name).delete
  end

  def photos_by_one_tag(name)
    @db[:tags].where(name: name).select(:photo_id).all
  end

  def convert_junk
    photo_ids = photos_by_one_tag('junk').map { |p| p[:photo_id] }

    @db[:photos].where(id: photo_ids).update(status: 'junk')
    @db[:tags].where(photo_id: photo_ids).delete

    photo_ids.size
  end

  def remove_surplus
    photo_ids = photos_by_one_tag('untagged').map { |p| p[:photo_id] }

    counter = 0

    photo_ids.each do |photo_id|
      tags = all_tags_for_photo(photo_id)
      if tags.size > 1
        @db[:tags].where(name: 'untagged', photo_id: photo_id).delete
        counter += 1
      end
    end

    counter
  end
end
