#!/bin/bash
nidaqmxconfig --import /home/evanp/Scripts/ni-temp.ini --eraseconfig
nidaqmxconfig --import /home/evanp/Scripts/ni-cfg.ini --eraseconfig
nilsdev --verbose
