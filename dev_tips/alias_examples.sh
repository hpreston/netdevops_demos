alias ll='ls -FGlAhp'

alias memHogsTop='top -l 1 -o rsize | head -20'
alias memHogsPs='ps wwaxm -o pid,stat,vsize,rss,time,command | head -10'
alias cpu_hogs='ps wwaxr -o pid,stat,%cpu,time,command | head -10'

alias flushDNS='dscacheutil -flushcache'
alias openPorts='sudo lsof -i | grep LISTEN'

alias docker_rm='docker rm -v $(docker ps -aq -f status=exited)'
