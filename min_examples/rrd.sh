rrdtool create temp_ctrl.rrd \
--start now \
--step 10 \
DS:temp:GAUGE:20:0:90 \
DS:hum:GAUGE:20:0:100 \
RRA:AVERAGE:0.5:1:10




rrdtool fetch temp_ctrl.rrd AVERAGE --start 1700224694   --end 1700224715


rrdtool graph temp.png --start 1700224694   --end 1700224715 DEF:mytemp=temp_ctrl.rrd:temp:AVERAGE DEF:myhum=temp_ctrl.rrd:hum:AVERAGE LINE2:mytemp#FF0000 LINE3:myhum#00FF00
