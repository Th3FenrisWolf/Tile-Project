#!/bin/sh

openocd -f ./jlink.cfg -c "transport select swd" -f ./nrf52.cfg -c "init;nrf52_check_ap_lock"
