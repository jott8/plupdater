#!/bin/bash

DEBUG=$1
DIR=$2
REDIRECT_URI=$3

echo "Starting plupdater"
echo "Debug: $DEBUG"
echo "Directory: $DIR"
echo "Redirect URI: $REDIRECT_URI"
echo ""

while IFS="," read -r username client_id client_secret copy_playlist_id
do
		echo "Current user: $username"

		$DIR/.venv/bin/python3.11 $DIR/main.py $DEBUG $username $copy_playlist_id $client_id $client_secret $REDIRECT_URI

		unset SPOTIPY_CLIENT_ID
		unset SPOTIPY_CLIENT_SECRET

		echo "----------------------------------------"

done < <(tail -n +2 $DIR/users.csv)

echo "Done"
