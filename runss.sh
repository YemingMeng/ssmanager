#!/bin/bash

filename="/tmp/shadowsocks-manager.sock"
if [ -e "$filename" ]; then
	rm "$filename"
fi
ssserver --manager-address $filename -c ss_config.json
