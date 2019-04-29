# A few handy bash aliases

# Display file list with colors, sizes, and in list format
alias ll='ls -FGlAhp'

# Handy aliases to find resource hogs
alias memHogsTop='top -l 1 -o rsize | head -20'
alias memHogsPs='ps wwaxm -o pid,stat,vsize,rss,time,command | head -10'
alias cpu_hogs='ps wwaxr -o pid,stat,%cpu,time,command | head -10'

# Some networking aliases for macOS
alias flushDNS='dscacheutil -flushcache'
alias openPorts='sudo lsof -i | grep LISTEN'

# Remove all exited/stopped docker containers
alias docker_rm='docker rm -v $(docker ps -aq -f status=exited)'
