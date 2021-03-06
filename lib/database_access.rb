require 'tags'

class DatabaseAccess
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

  def add_new_photo(filename, othername, file_size)
    @db[:photos].insert(filename: filename, othername: othername, status: 'unknown', file_size: file_size)
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
end
