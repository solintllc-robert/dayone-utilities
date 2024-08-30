#!/usr/bin/env python3
import logging
import re
import argparse # to read command line args
from subprocess import Popen, PIPE, STDOUT
from io import StringIO
import xml.etree.ElementTree as ET


# name of the day one journal which imported notes are written by default
DEFAULT_JOURNAL='Evernote'


class Note:

    def __init__(self, xml_node):
        self.title=xml_node.find('title').text
        if not self.title:
            self.title = 'Untitled'

        self.created=Note.convertDate(xml_node.find('created').text)
        self.updated=Note.convertDate(xml_node.find('updated').text)
        self.note_attributes=xml_node.find('note-attributes').text
        self.content=Note.parseContent(xml_node.find('content').text)


    def __str__(self):
        return f"TITLE:   {self.title}\nCREATED: {self.created}\nUPDATED: {self.updated}\nATTRIBS: {self.note_attributes}\nCONTENT: {self.content}\n"


    @staticmethod
    def convertDate(evernote_date):
        """Convert evernote format into the iso date format day one wants."""
        return f"{evernote_date[0:4]}-{evernote_date[4:6]}-{evernote_date[6:11]}:{evernote_date[11:13]}:{evernote_date[13:]}"


    @staticmethod
    def parseContent(content):
        """Parses the XML content of an evernote note"""

        first_part_stripped = re.sub(r".*<en-note[^>]*>", "", content.strip()) # strips off everytyhing from the front up to and including the <en-note>
        all_stripped = re.sub("</en-note.*","", first_part_stripped[54:] )
        formatted_string = re.sub(r"( *</?(div|br)[^>]*> *)+", "\n\n", all_stripped)
        fixed_apostrophes = re.sub(r"&apos;", "'", formatted_string)
        fixed_quotes = re.sub(r"&quot;", '"', fixed_apostrophes)
        fixed_spans = re.sub(r"</?span[^>]*>", '', fixed_quotes)

        return fixed_spans.strip()


    def addToDayOne(self, journal):
        """Adds to the the Day One journal specified."""

        # Using communicate per https://stackoverflow.com/questions/8475290/how-do-i-write-to-a-python-subprocess-stdin
        p = Popen(['/usr/local/bin/dayone2',
                   '-t', 'travel',
                   '-j', journal,
                   '-d', self.created,
                   'new'], stdout=PIPE, stdin=PIPE, stderr=PIPE, encoding='utf-8')

        stdout_data = p.communicate(input=f"{self.title}\n{self.content}")[0]


def parseEvernoteXML(xmlFile):
    """Parse the entire export into individual note objects."""
    notes = []
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    return [ Note(child) for child in root ]


def parseCommandLineArguments():
    """Gets
        - name of evernote file to parse
        - journal into which to load the notes
    """

    # create parser
    parser = argparse.ArgumentParser(
            prog = 'evernote2dayone',
            description = 'Loads entries from an evernote export file into Day One.')

    # add arguments to the parser
    parser.add_argument('evernote_file',
                        help='The name of the .enex file to parse.')
    parser.add_argument('-j',
                        '--journal',
                        help=f'Destination journal in Day One. Defaults to "{DEFAULT_JOURNAL}"',
                        default=DEFAULT_JOURNAL)

    # parse the arguments
    args = parser.parse_args()

    return args

def getEvernoteFile(args):
    """Gets the name of the evernote file."""
    # read in the data from evernote

    logging.info(f"args.evernote_file: {args.evernote_file}")
    return args.evernote_file


def getJournalName(args):
    """Returns the name of the Day One journal into which to write the evernote notes."""
    logging.info(f"journal name:{args.journal}")
    return args.journal


def main():
    function_name_max_length=str(max([len(f.__name__) for f in globals().values() if callable(f)]))
    FORMAT="%(asctime)s %(levelname)-7s %(funcName)-"+function_name_max_length+"s [%(lineno)-3d] %(message)s"
    logging.basicConfig( format=FORMAT,
                       #filename='evernote2dayone.log', filemode='w',
                        level=logging.DEBUG)

    args = parseCommandLineArguments()
    evernote_file = getEvernoteFile(args)
    journal = getJournalName(args)

    notes = parseEvernoteXML(evernote_file)

    for note in notes:
        logging.info(f"Adding {note.title}")
        note.addToDayOne('test')


        if re.search('en-media', note.content):
            logging.warning(f"See {note.title} about an image.")


if __name__ == '__main__':
    main()

