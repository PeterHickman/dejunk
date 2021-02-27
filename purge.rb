#!/usr/bin/env ruby
# frozen_string_literal: true

##
# Look for files that have not been deleted
##

require 'yaml'
require 'sequel'

$LOAD_PATH << './lib'

require 'database_access'

config = YAML.load_file('config.yaml')

da = DatabaseAccess.new(config['dcs'])

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
    da.set_to_deleted(photo[:id])
  end
end
