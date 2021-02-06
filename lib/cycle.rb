class Cycle
  def initialize(*pattern)
    @pattern = pattern

    @pos = 0
  end

  def get
    @pos = 0 if @pos >= @pattern.size
    x = @pattern[@pos]
    @pos += 1
    x
  end

  def reset
    @pos = 0
  end
end
