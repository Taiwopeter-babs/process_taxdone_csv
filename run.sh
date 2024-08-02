#!/usr/bin/env bash
./setup.sh

echo ""
echo "Running program now"

if [ ! -f ./data/migration_data.xlsx ]; then
    echo -e "migration_data.xlsx does not exist in data directory"

else
    echo -e "PARSING EXCEL FILE NOW"

    python src/main.py
fi
