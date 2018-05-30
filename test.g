
#import pappa //relative
#import projects/herp/herp //absolute
#import math //stdlib


#struct point
    x:byte
    y:byte
end


#struct player
    health :byte
    position:point
end

log player size: $size(player)
log total mem usage: $globals.mem_total
log mem used: $globals.mem_used
log first free memory: $globals.mem_free_first
log this is line $globals.line  in file $globals.file

%testfunc
    #instance players : player[4]
    log size of players: $size(players)
    loada players
end

%main
    #instance d : math_complex 
    log size of d: $size(d)
    loada testfunc
    loada pappa_main
    //loada projects_herp_herp_main
end




