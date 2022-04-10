Open crontab scheduler:
    crontab -e
Edit the file by adding this line:
    0 22 * * * /home/XXXXXXX/cardano-skepsis-toolbox/get_delegators_utils/get_delegators.sh >> /home/XXXXXXX/logs/get_delegators.log 2>&1

get_delegators.sh will run only once every 5 days.
