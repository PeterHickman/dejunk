def resize(source, destination, pixels)
  s1 = "#{pixels}x#{pixels}"
  s2 = "#{pixels * 2}x#{pixels * 2}"

  puts("Resizing to create #{destination} at #{s1}")
  cmd = "convert -define jpeg:size=#{s2} -auto-orient #{source}'[0]' -thumbnail '#{s1}>' -background transparent -gravity center -extent #{s1} #{destination}"

  system(cmd)
end
