#!/bin/bash

# This bash script is written to be used along with Heroku Scheduler to run the spiders

# Currently Heroku Scheduler only supports scheduling at every 10min/hour/day interval
# Reference: https://dashboard.heroku.com/apps/burplist/scheduler

# To run every Friday
# ./prune.sh weekly 5

# To run now
# ./prune.sh

if [[ "$1" == "weekly" ]]; then
    echo "Frequency: <Weekly> | Day of the week: <$2>"
    if [ "$(date +%u)" = "$2" ]; then
        echo "Pruning stale data."
        scrapy prune --days 21
        echo "Finished pruning all."
    fi
else
    echo "Frequency: <Now>"
    echo "Pruning stale data."
    scrapy prune --days 21
    echo "Finished pruning all."
fi
