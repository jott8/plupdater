# plupdater

This is a program to copy your Liked Songs from Spotify to a separate playlist to make them publicly available.

### Usage

To access the API and make changes to your Spotify account, you have to create an App in the Spotify Developer Dashboard.
The plupdater needs the client id, client secret and the playlist id for the target playlist for each user. Those have to be provided in a file called users.csv (I'll add an example configuration).

For the first use, it's neccessary to copy the songs manually to the target playlist. If you don't to this, the order is messed up.

After scanning and editing the playlist(s), a changelog will be written to "logs/USERNAME.csv"

Run the script via "script.sh/DEBUG_MODE/PATH/REDIRECT_URI where DEBUG can either be 'TRUE' or 'FALSE', PATH is the path to the plupdater dir and REDIRECT_URI the URI the users provided in the Spotify dashboard app (has to be the same for all users).

### TODO
[] Generate HTML from changelog
