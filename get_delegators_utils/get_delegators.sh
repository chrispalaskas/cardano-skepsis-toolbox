#!/bin/bash

# Timeslot start of epoch 327: 1647467719

let timeslot="($(date +%s) - 1647467719) / 86400 % 5"

date
if [ $timeslot -eq 1 ]
then

    python3 /home/chruskal/cardano-skepsis-toolbox/get_delegators_stake.py
else
    echo Not running today. Only once per epoch.
fi

