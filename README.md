# Day One Utilties

This repository contains Python scripts for working with [Day One](https://dayoneapp.com/web/). Hopefully, you find them useful.

The scripts included are:
- add_file_to_dayone.py: imports a text, image, or PDF file into Day One
- [parse_evernote.py](#parse-evernote): imports an Evernote export

Note: This code is in no way related to or endorsed by those Day One nor Evernote. I doubt if they even know this code exists.

## Installation

1. Install the Day One desktop application and [Day One CLI](https://dayoneapp.com/guides/tips-and-tutorials/command-line-interface-cli/).
2. Clone this repository.
3. (optional) Create a Python virtual environment.
4. `pip install -r requirements.txt`

## Usage

### Add File to Day One

This script adds a a text, image, or PDF file into Day One, using the details of the file for the journal entry. I wrote it because I had a lot of journal entries written in Notepad.

1. Create the destination journal in the Day One applicaiton. The script won't create the journal for you.
2. Run the script. There is a help page that will explain in more detail.
`./add_to_dayone.py -h`

You can wrap the script with a little BASH to load a lot of files. For example:
- You have a lot of files in your ~/Downloads directory.
- The file names are all formatted like: `20240830 My journal entry name.txt`
- You've created a Downloads journal in Day One.

You might run something like:
`for x in ~/Downloads/*; do y=$(basename "${x}"); dt="${y:0:8}120000"; tit=${y:9:100}; ./add_file_to_dayone.py -j Downloads --title "${tit%%.pdf}" --date ${dt} "${x}"; done`


### Parse Evernote

To be honest, I wrote this script a long time ago, so I don't remember all the details. I think the steps are:
1. Export from Evernote.
2. `./parse_evernote.py [-j destination_journal] your_evernote_export.enx`


## Trademarks
Evernote and Day One are trademarks of their respective owners.
