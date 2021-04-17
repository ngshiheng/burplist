#!/bin/bash

# This bash script is written to be used along with Heroku Scheduler to run the spiders.

# Currently Heroku Scheduler only supports scheduling at every 10min/hour/day interval
# Reference: https://dashboard.heroku.com/apps/burplist/scheduler

# To run every Monday
# ./task.sh weekly 1

# To run now
# ./task.sh

if [[ "$1" == "weekly" ]]; then
    echo "Frequency: <Weekly> | Day of the week: <$2>"
    if [ "$(date +%u)" = "$2" ]; then
        echo "Starting 🕷 to get 🍻 data from the 🕸..."
        scrapy list | xargs -n 1 scrapy crawl
        echo "Finished running all 🕷."
    fi
else
    echo "Frequency: <Now>"
    echo "Starting 🕷 to get 🍻 data from the 🕸..."
    scrapy list | xargs -n 1 scrapy crawl
    echo "Finished running all 🕷."
fi
