require 'set'

class Tags
  def self.format(text)
    clean_tag = text.gsub(/\s+/, ' ').downcase.strip

    name = clean_tag.gsub(' ', '_')
    display = display_name(clean_tag)

    [name, display]
  end

  def self.display_name(name)
    name.split(' ').map(&:capitalize).join(' ')
  end

  def self.rewrite_query(tags)
    includes, excludes = split_tags(tags)

    excludes.each do |tag|
      includes << "-#{tag}"
    end

    includes.to_a.join(' ')
  end

  def self.split_tags(tags)
    # Given a string of space separated tags, group them into includes and
    # excludes based on a '-' prefix for exclude

    includes = Set.new
    excludes = Set.new

    tags.split(/\s+/).each do |tag|
      if tag.index('-') == 0
        excludes << tag[1..-1]
      else
        includes << tag
      end
    end

    includes.each do |tag|
      if excludes.include?(tag)
        includes.delete(tag)
        excludes.delete(tag)
      end
    end

    [includes.to_a, excludes.to_a]
  end

  def self.describe(tags)
    includes, excludes = split_tags(tags)

    text = ''

    if includes.any?
      text += "Includes: #{includes.each { |name| display_name(name) }.join(', ')}"
    end

    if excludes.any?
      text += '. ' unless text == ''
      text += "Excludes: #{excludes.each { |name| display_name(name) }.join(', ')}"
    end

    text
  end

  def self.tagged_with(tags, counted)
    # Return the SQL required to get the photos matching the tag query

    includes, excludes = split_tags(tags)

    if counted
      select = 'COUNT(*)'
    else
      select = 'photo_id'
    end

    sql = ''

    if includes.any?
      sql += "SELECT #{select} FROM tags WHERE name IN ('#{includes.join("', '")}')"
      if excludes.any?
        sql += " AND photo_id NOT IN (SELECT photo_id FROM tags WHERE name IN ('#{excludes.join("', '")}'))"
      end
      if includes.size > 1
        sql += " GROUP BY photo_id HAVING COUNT(photo_id) = #{includes.size}"
      end
    elsif excludes.any?
      sql += "SELECT #{select} FROM tags WHERE photo_id NOT IN (SELECT photo_id FROM tags WHERE name IN ('#{excludes.join("', '")}'))"
    else
      sql += "SELECT #{select} FROM tags"
    end

    if counted == false
      sql += ' ORDER BY photo_id DESC'
    end

    sql
  end
end
