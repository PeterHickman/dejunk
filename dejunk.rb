#!/usr/bin/env ruby
# frozen_string_literal: true

require 'yaml'
require 'sequel'
require 'sinatra'

$LOAD_PATH << './lib'

require 'database_access'
require 'cycle'
require 'tags'

config = YAML.load_file('config.yaml')

da = DatabaseAccess.new(config['dcs'])

set :public_folder, File.dirname(__FILE__) + '/static'

helpers do
  def get_cycle(*args)
    Cycle.new(*args)
  end

  def human(size)
    # Human readable byte sizes

    if size < 1024
      # Is in the bytes range
      "#{size}b"
    elsif size < 1048576
      # Is in the Kb
      "#{(size / 1024.0).round(2)}Kb"
    elsif size < 1073741824
      # Is in the Mb
      "#{(size / 1048576.0).round(2)}Mb"
    elsif size < 1099511627776
      # Is in the Gb
      "#{(size / 1073741824.0).round(2)}Gb"
    else
      # Is in the Tb
      "#{(size / 1099511627776.0).round(2)}Tb"
    end
  end
end

def get_page
  if params[:page]
    params[:page].to_i
  else
    1
  end
end

get '/' do
  totals = da.status_information()
  erb :status, { locals: { totals: totals, selected_menu: 'status' } }
end

get '/dejunk' do
  page = get_page
  data = da.photos_with_status('unknown', config['images_a_page'], config['images_a_row'], page)
  erb :dejunk, { locals: { data: data, selected_menu: 'dejunk' } }
end

get '/tags' do
  if params[:query]
    page = get_page
    new_query = Tags.rewrite_query(params[:query])
    data = da.photos_by_tags(new_query, config['images_a_page'], config['images_a_row'], page)
    erb :selected_tags, { locals: { selected_menu: 'tags', data: data } }
  else
    query = da.all_tags_and_counts
    erb :tags, { locals: { selected_menu: 'tags', query: query } }
  end
end

post '/dejunk' do
  # {"commit"=>"Submit", "page"=>"1", "photo_642207"=>"ok"}

  ids = {}
  params.each do |k, v|
    next unless k.index('photo_') == 0
    ids[k.split('_').last] = v
  end

  da.classify_unknown(ids)

  redirect "/dejunk?page=#{get_page}"
end

get '/purge' do
  page = get_page
  data = da.photos_with_status('junk', config['images_a_page'], config['images_a_row'], page)
  erb :purge, { locals: { data: data, selected_menu: 'purge' } }
end

post '/purge' do
  # {"commit"=>"Submit", "page"=>"1", "photo_642207"=>"1", "photo_642328"=>"1"}

  ids = {}
  params.each do |k, v|
    next unless k.index('photo_') == 0
    ids[k.split('_').last] = v
  end

  da.photos_to_delete(ids)

  redirect "/purge?page=#{get_page}"
end

get '/picture' do
  data = {}
  data['page'] = get_page
  data['query'] = Tags.rewrite_query(params[:query])
  data['photo'] = da.get_picture(params[:photo_id])
  data['tags'] = da.all_tags_for_photo(params[:photo_id])

  erb :picture, { locals: { data: data, selected_menu: 'picture' } }
end

post '/add_tags' do
  photo_ids = params[:id].split(',')
  tags = params[:new_tag].split(',')

  da.add_tags_to_photos(photo_ids, tags)

  page = get_page

  query = Tags.rewrite_query(params[:query])

  if photo_ids.size > 1
    # Multiple images
    redirect "/tags?page=#{get_page}&query=#{query}"
  else
    # Single image
    redirect "/picture?photo_id=#{photo_ids.first}&query=#{query}&page=#{page}"
  end
end

get '/remove_tag' do
  photo_id = params[:photo_id]
  old_tag = params[:old_tag]

  da.remove_tag_from_photo(photo_id, old_tag)

  page = get_page

  query = Tags.rewrite_query(params[:query])

  redirect "/picture?photo_id=#{photo_id}&query=#{query}&page=#{page}"
end

get '/admin' do
  erb :admin, { locals: { selected_menu: 'admin', message: nil } }
end

get '/convert_junk' do
  count = da.convert_junk
  message = "#{count} photos have been converted to junk status"
  erb :admin, { locals: { selected_menu: 'admin', message: message } }
end

get '/remove_surplus' do
  count = da.remove_surplus
  message = "#{count} surplus untagged tags have been removed"
  erb :admin, { locals: { selected_menu: 'admin', message: message } }
end

get '/full_size/:photo_id' do
  data = {}
  data['photo'] = params[:photo_id]
  erb :full_size, { layout: nil, locals: { data: data, selected_menu: 'picture' } }
end