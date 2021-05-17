#!/usr/bin/env bash

for i in boot.py webrepl_cfg.py main.py blynklib_mp.py blynklib_mp_ssl.py secret.py
do
	echo -n "$i "
	ampy --port $1 put $i
	echo "OK"
done

