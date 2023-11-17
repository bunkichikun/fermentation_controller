import rrdtool
import time

RRD_DB_NAME = "temp_ctrl.rrd"
f=1.2

rrdtool.create(
    RRD_DB_NAME,
    "--start","now",
    "--step", "2",
    "DS:temp:GAUGE:4:0:90",
    "DS:hum:GAUGE:4:0:100",
    "RRA:AVERAGE:0.5:1:10")

print("creation time: " + str( int(time.time())))

for i in [n for n in range(1,22)]:
    print(f)
    rrdtool.update(RRD_DB_NAME,'N:%s:%s'% (f,f))
    f = (f+i)/2
    time.sleep(1)

print("end time: " + str( int(time.time())))
