#!/usr/bin/env ruby
# frozen_string_literal: true

require 'yaml'
require 'sequel'
require 'fileutils'

$LOAD_PATH << './lib'

require 'database_access'
require 'resize'
require 'tags'

config = YAML.load_file('config.yaml')

da = DatabaseAccess.new(config['dcs'])

##
# Look for files that have not been deleted
##

da.all_the_photos.each do |photo|
  if photo[:status] == 'deleted'
    filename = "#{config['destination_root']}images/#{photo[:filename]}"
    if File.exist?(filename)
      puts("Removing #{filename}")
      File.delete(filename)
    end

    filename = "#{config['destination_root']}medium/#{photo[:othername]}"
    if File.exist?(filename)
      puts("Removing #{filename}")
      File.delete(filename)
    end

    filename = "#{config['destination_root']}thumbs/#{photo[:othername]}"
    if File.exist?(filename)
      puts("Removing #{filename}")
      File.delete(filename)
    end

    da.remove_all_tags_from_photo(photo[:id])
  else
    source = "#{config['destination_root']}images/#{photo[:filename]}"

    if File.exist?(source)
      if photo[:file_size] == nil
        file_size = File.size(source)
        da.set_size(photo[:id], file_size)
        puts("Updated size #{source} to #{file_size}")
      end

      filename = "#{config['destination_root']}medium/#{photo[:othername]}"
      unless File.exist?(filename)
        resize(source, filename, 800)
      end

      filename = "#{config['destination_root']}thumbs/#{photo[:othername]}"
      unless File.exist?(filename)
        resize(source, filename, 125)
      end

      number = da.all_tags_for_photo(photo[:id]).size
      if number == 0
        puts("Added 'untagged' tag to #{photo[:id]}")
        da.add_tag_to_photo(photo[:id], 'untagged')
      end
    else
      puts("#{photo[:filename]} is missing, marked as deleted")
      da.set_to_deleted(photo[:id])
    end
  end
end
