#!/usr/bin/env ruby
# frozen_string_literal: true

require 'yaml'
require 'sequel'
require 'fileutils'

$LOAD_PATH << './lib'

require 'database_access'
require 'resize'

config = YAML.load_file('config.yaml')

da = DatabaseAccess.new(config['dcs'])

counter = 0

now_is = Time.now

Dir["#{config['source_path']}*"].each do |filename|
  counter += 1

  basename = File.basename(filename)

  dest_name = "#{config['destination_root']}images/#{basename}"

  if File.exist?(dest_name)
    puts("#{counter}: File #{basename} already found")
  else
    puts("#{counter}: Need to import #{basename}")

    othername = basename.split('.')[0..-2].join('.') + '.png'

    file_size = File.size(filename)
    photo_id = da.add_new_photo(basename, othername, file_size, now_is)
    da.add_tag_to_photo(photo_id, 'untagged')

    # Create the medium image
    new_filename = "#{config['destination_root']}medium/#{othername}"
    resize(filename, new_filename, 800)

    # Create the thumbnail
    new_filename = "#{config['destination_root']}thumbs/#{othername}"
    resize(filename, new_filename, 125)

    # Copy the source image
    new_filename = "#{config['destination_root']}images/#{basename}"
    FileUtils.cp(filename, new_filename)
  end

  File.delete(filename)
end
