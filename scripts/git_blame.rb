#!/usr/bin/env ruby
# TODO use the current WIDTH of the output window to automatically wrap
#
# Based on the code of Rene Saarsoo, you can find the original here
# https://github.com/nene/config/blob/master/bin/git-praise

#################
# Configuration #
#################
FORMAT    = "%Ccommit%h%Cblue (%ad) %Cgreen%an%F%Cwhite%L %Ccommit%M%BCreset"
SEPARATOR = 100


# Variables
unless ARGV.length == 1
    puts "Usage: ruby git_blame.rb <path>"
    exit
end
path         = ARGV[0]
hash         = ""
commits      = {}
line_nb      = 1
commit_count = 0
last_hash    = ""

# Function that will print one line according to the selected format
def pretty_print(format, separator, hash, commit, line, line_nb, commit_count)
  desc = format.
    gsub(/%Ccommit/, commit[:color]).
    gsub(/%H/,       hash).
    gsub(/%h/,       hash[0,10]).
    gsub(/%an/,      commit[:author]).
    gsub(/%ae/,      commit[:author_mail]).
    gsub(/%ad/,      commit[:author_time].strftime("%d. %b %Y %R")).
    gsub(/%Cgreen/,  "\033[32m").
    gsub(/%Cblue/,   "\033[34m").
    gsub(/%L/,       line_nb.to_s).
    gsub(/%Cwhite/,  "\033[37m").
    gsub(/%BCreset/, "\033[0m")

  # Minus 4 for the characters "%L%M" that hasn't been replaced yet
  length = desc.length - 4

  desc = desc.
      gsub(/%F/, " "* (separator - length)).
      gsub(/%M/, line)

  # Every commit change switch the background
  if (commit_count % 2 == 0)
      puts "\033[40m" + desc
  else
      puts desc
  end
end

colors = [
    # "\033[30m", # Black // Can't see it
    "\033[31m",   # Red
    # "\033[32m", # Green // Used in format
    "\033[33m",   # Yellow
    # "\033[34m", # Blue  // Used in format
    "\033[35m",   # Magenta
    "\033[36m",   # Cyan
    # "\033[37m",   # White
]
color_count = 0


#TEST

# Main loop
`git blame -p #{path}`.split("\n").each do |line|
    if line =~ /^([0-9a-f]{39,40})\s.*/
        hash = $1
        unless commits[hash]
            commits[hash] = {}
            commits[hash][:color] = colors[color_count%colors.length]
            color_count = color_count + 1
        end
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
        unless last_hash == hash
            commit_count = commit_count + 1
            last_hash = hash
        end
        pretty_print(FORMAT, SEPARATOR, hash, commits[hash], $1, line_nb, commit_count)
        line_nb = line_nb + 1
    end
end
