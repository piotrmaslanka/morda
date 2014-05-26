As a member of a reliable company that develops reliable technologies, we dogfood.

We dogfood __a lot__.

That's why, as I'm developing y/OS, I've decided to dogfood. Not on my customers, but on myself.

# morda

_morda_ is a reimplementation of my home BMS as a y/OS app, utilizing it's y/Page runtime system.

Right now devices plugged in are:
* Heating controller, via RS232
* Electric power meter, via RS485
* Alarm system, via RS485
* Garden irrigation, via RS485
* Second floor temperature sensor, via RS485

## Modules rundown

All modules in this project contain a _run.py_ file that contains the entry-point tasklet. It's purpose is well-defined and understandable - just read the docs. So far there are:

* timesynced - time synchronization (irrigation, alarm and heating need that)
* serialTasklet - serial port communications server. Clients send serial port requests, and it rolls'em