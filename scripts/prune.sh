#!/bin/bash

# This bash script is written to be used along with Heroku Scheduler to run the spiders

# Currently Heroku Scheduler only supports scheduling at every 10min/hour/day interval
# Reference: https://dashboard.heroku.com/apps/burplist/scheduler

# To prune 365 days old stale data every Friday:
# ./prune.sh weekly 5 365

# To prune 90 days old stale data now:
# ./prune.sh

frequency="$1"
day_of_week="$2"
stale_days="${3:-90}"

if [[ "$frequency" == "weekly" ]]; then
    echo "Frequency: <Weekly> | Day of the week: <$day_of_week>"
    if [ "$(date +%u)" = "$day_of_week" ]; then
        echo "Pruning stale data."
        scrapy prune --days "$stale_days"
        echo "Finished pruning."
    fi
else
    echo "Frequency: <Now>"
    echo "Pruning 90 days old stale data."
    scrapy prune --days "$stale_days"
    echo "Finished pruning."
fi
