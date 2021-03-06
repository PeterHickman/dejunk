#!/usr/bin/env ruby
# frozen_string_literal: true

require 'yaml'
require 'sequel'

$LOAD_PATH << './lib'

require 'database_access'

def count_images(config, photo)
  exists = 0

  filename = "#{config['destination_root']}images/#{photo[:filename]}"
  exists += 1 if File.exist?(filename)

  filename = "#{config['destination_root']}medium/#{photo[:othername]}"
  exists += 1 if File.exist?(filename)

  filename = "#{config['destination_root']}thumbs/#{photo[:othername]}"
  exists += 1 if File.exist?(filename)

  exists
end

def has_no_tags(da, photo)
  number = da.all_tags_for_photo(photo[:id]).size

  puts("#{photo[:status]} #{photo[:id]} still has #{number} tags") unless number == 0
end

def has_no_images(config, photo)
  number = count_images(config, photo)

  puts("#{photo[:status]} #{photo[:id]} needs it's files removed") unless number == 0
end

def has_all_images(config, photo)
  number = count_images(config, photo)

  puts("#{photo[:status]} #{photo[:id]} is missing files. Has #{number}") if number != 3
end

def has_real_size(photo)
  puts("#{photo[:id]} #{photo[:filename]} has no size") if photo[:file_size].nil?
end

def has_some_tags(da, photo)
  number = da.all_tags_for_photo(photo[:id])

  puts("#{photo[:status]} #{photo[:id]} should have at least 1 tag") if number == 0
end

config = YAML.load_file('config.yaml')

da = DatabaseAccess.new(config['dcs'])

image_names = []
other_names = []

da.all_the_photos.each do |photo|
  case photo[:status]
  when 'deleted'
    has_no_tags(da, photo)
    has_no_images(config, photo)
  when 'junk'
    has_no_tags(da, photo)
    has_all_images(config, photo)
    image_names << photo[:filename]
    other_names << photo[:othername]
  when 'ok'
    has_some_tags(da, photo)
    has_all_images(config, photo)
    has_real_size(photo)
    image_names << photo[:filename]
    other_names << photo[:othername]
  when 'unknown'
    has_no_tags(da, photo)
    has_all_images(config, photo)
    image_names << photo[:filename]
    other_names << photo[:othername]
  end
end

Dir["#{config['destination_root']}images/*"].each do |filename|
  basename = File.basename(filename)

  puts("The image #{basename} is not in the database") unless image_names.include?(basename)
end

Dir["#{config['destination_root']}medium/*"].each do |filename|
  basename = File.basename(filename)

  puts("The medium #{basename} is not in the database") unless other_names.include?(basename)
end

Dir["#{config['destination_root']}thumbs/*"].each do |filename|
  basename = File.basename(filename)

  puts("The thumb #{basename} is not in the database") unless other_names.include?(basename)
end
