#!/usr/bin/env ruby
# frozen_string_literal: true

require 'yaml'
require 'sequel'
require 'fileutils'

$LOAD_PATH << './lib'

require 'database_access'
require 'resize'
require 'tags'

VALID_STATII = %w[ok unknown junk deleted].freeze

config = YAML.load_file('config.yaml')

da = DatabaseAccess.new(config['dcs'])

puts '== Images in image directory but not in the database'

Dir["#{config['destination_root']}images/*"].each do |filename|
  name = File.basename(filename)

  row = da.db['SELECT * FROM photos WHERE filename = ?', name].first
  if row
    next if VALID_STATII.include?(row[:status])

    p row
  else
    puts "-- #{name} move to import"
    new_file = "#{config['destination_root']}/import/#{name}"
    FileUtils.move filename, new_file
  end
end

puts '== Tags that reference unknown photos'

all_known_photos = da.db['SELECT id FROM photos'].map { |row| row[:id] }
all_photos_in_tags = da.db['SELECT DISTINCT(photo_id) FROM tags'].map { |row| row[:photo_id] }

all_photos_in_tags.each do |photo_id|
  next if all_known_photos.include?(photo_id)

  puts "-- #{photo_id} is unreferenced"
  da.db['DELETE FROM tags WHERE photo_id = ?', photo_id].first
end
