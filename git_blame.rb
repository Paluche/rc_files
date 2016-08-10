#!/usr/bin/env ruby
# TODO Do something better with the format adding a %L for the line and a %F for
# the filler.
# TODO use the current WIDTH of the output window to automatically wrap
# Based on the code of Rene Saarsoo, you can find the original here
# https://github.com/nene/config/blob/master/bin/git-praise

#################
# Configuration #
#################
FORMAT    = "%Cred%h%Cblue (%ad) %Cgreen%an"
SEPARATOR = 100


# Variables
path      = ARGV[0]
hash      = ""
commits   = {}
line_nb     = 0

# Function that will print one line according to the selected format
def pretty_print(format, separator, hash, commit, line, line_nb)
  desc = format.
    gsub(/%H/, hash).
    gsub(/%h/, hash[0,10]).
    gsub(/%an/, commit[:author]).
    gsub(/%ae/, commit[:author_mail]).
    gsub(/%ad/, commit[:author_time].strftime("%d. %b %Y %R")).
    gsub(/%Cred/, "\033[31m").
    gsub(/%Cgreen/, "\033[32m").
    gsub(/%Cblue/, "\033[34m").
    gsub(/%Ccyan/, "\033[36m").
    gsub(/%Cwhite/, "\033[37m").
    gsub(/%BCreset/, "\033[30m")

  length = desc.length + line_nb.to_s.length

  output = ""

  # One line out of 2 will have a black background
  if line_nb % 2 == 0
      output = "\033[40m"
  end

  output += desc + " "

  if (length < separator)
      output += (" "* (separator - length))
  end

  puts output + "\033[36m" + line_nb.to_s + " \033[37m" + line + "\033[0m"

end

# Main loop
`git blame -p #{path}`.split("\n").each do |line|
    if line =~ /^([0-9a-f]{39,40})\s.*/
        hash = $1
        commits[hash] = {} unless commits[hash]
    elsif line =~ /^author (.+)/
        commits[hash][:author] = $1.strip
    elsif line =~ /^author-mail (.+)/
        commits[hash][:author_mail] = $1.strip
    elsif line =~ /^author-time (.+)/
        commits[hash][:author_time] = Time.at($1.strip.to_i)
    elsif line =~ /^author-tz (.+)/
        commits[hash][:author_tz] = $1.strip
    elsif line =~ /^committer (.+)/
        commits[hash][:committer] = $1.strip
    elsif line =~ /^committer-mail (.+)/
        commits[hash][:committer_mail] = $1.strip
    elsif line =~ /^committer-time (.+)/
        commits[hash][:committer_time] = Time.at($1.strip.to_i)
    elsif line =~ /^committer-tz (.+)/
        commits[hash][:committer_tz] = $1.strip
    elsif line =~ /^summary (.+)/
        commits[hash][:summary] = $1.strip
    elsif line =~ /^previous (.+)/
        commits[hash][:previous] = $1.strip
    elsif line =~ /^filename (.+)/
        commits[hash][:filename] = $1.strip
    elsif line =~ /^\t(.*)/
        pretty_print(FORMAT, SEPARATOR, hash, commits[hash], $1, line_nb)
        line_nb = line_nb + 1
    end
end
