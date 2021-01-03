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
end

