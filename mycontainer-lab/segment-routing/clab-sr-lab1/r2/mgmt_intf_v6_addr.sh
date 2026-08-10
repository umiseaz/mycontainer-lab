#!/bin/bash

source /pkg/bin/ztp_helper.sh

xrapply_string "interface MgmtEth0/RP0/CPU0/0\n no ipv6 address\nipv6 address 3fff:172:20:20::3/64\n"
