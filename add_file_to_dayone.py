#!/usr/bin/env python3
import logging
import argparse # to read command line args
from subprocess import Popen, PIPE, STDOUT
import os
from datetime import datetime
from striprtf.striprtf import rtf_to_text


# name of the day one journal to which imported notes are written by default
DEFAULT_JOURNAL='import'


class Note:
    """A note to be added to Day One."""

    def __init__(self, args):
        self.set_journal(args)
        self.set_title(args)
        self.set_created(args)
        self.set_tags(args)
        self.set_content(args)


    def __str__(self):
        mystr = f"TITLE:   {self.title}\nCREATED: {self.created}\nCONTENT: {self.content[:25]}\n"
        if self.attachments:
            mystr += f"ATTACHMENTS: {self.attachments}\n"

        if self.tags:
            mystr += f"TAGS: {self.tags}\n"

        return mystr


    def set_tags(self, args):
        """Set tags to those specified on the command line."""
        if args.tags:
            self.tags = args.tags
        else:
            self.tags = None


    def set_journal(self, args):
        """Set name of the Day One journal into which to write note."""
        self.journal = args.journal


    def set_content(self, args):
        """Set content to content of file minus leading/trailing space."""

        file_names = args.file_name
        file_name = file_names[0]

        if file_name[-3:] in ['rtf', 'txt']:
            with open(file_name, 'r') as f:
                content = f.read()

            if file_name[-3:] in ['rtf']:
                content = rtf_to_text(content, errors="ignore")

            file_names.pop(0)
        else:
            content = "See attached files"


        if len(file_names) > 0:
            self.attachments = file_names
        else:
            self.attachments = None

        self.content = content.strip()


    def set_title(self, args):
        """Set note title to the file name minus path and extension."""

        if not args.title:
            file_name = args.file_name[0]

            file_name_only = os.path.basename(file_name)
            without_extension = file_name_only.rsplit( '.', 1 )[0]
            self.title = without_extension.title()
        else:
            self.title = args.title.title()


    def set_created(self, args):
        """Set created date to file creation date or to current date if no file specified."""
        if not args.date:
            file_name = args.file_name[0]
            create_date = datetime.fromtimestamp(os.path.getmtime(file_name))
        else:
            if len(args.date) == 6:
                create_date = datetime.strptime(f"{args.date}", '%y%m%d')
            elif len(args.date) == 8:
                create_date = datetime.strptime(f"{args.date}", '%Y%m%d')
            else:
                create_date = datetime.strptime(f"{args.date}EST", '%Y%m%d%H%M%S%Z')

        self.created = create_date.strftime("%Y-%m-%d %H:%M:%S")


    def write(self):
        """Adds to the the Day One journal specified."""

        # Using communicate per
        # https://stackoverflow.com/questions/8475290/how-do-i-write-to-a-python-subprocess-stdin
        arguments = ['/usr/local/bin/dayone2',
                     '-j', self.journal,
                     '-d', self.created]

        if self.attachments is not None:
            arguments.append('-a')
            arguments.extend(self.attachments)
            if self.tags is None:
                arguments.append('--')

        if self.tags is not None:
            arguments.append('-t')
            arguments.extend(self.tags)
            arguments.append('--')


        arguments.append('new')

        logging.debug('arguments: %s' , str(arguments))
        p = Popen(arguments, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        # ignore stdout_data
        stdout_data = p.communicate(input=f"{self.title}\n{self.content}".encode())[0]

        logging.info("Added %s", str(self))



def parse_command_line_arguments():
    """Gets
        - name of file to parse
        - journal into which to load the notes
    """

    # create parser
    parser = argparse.ArgumentParser( description = 'Loads a file into Day One.')

    # add arguments to the parser
    parser.add_argument('file_name',
                        help='The name of the file to add to Day One.',
                        nargs='+')

    parser.add_argument('-j',
                        '--journal',
                        help=f'Destination journal in Day One. Default: "{DEFAULT_JOURNAL}"',
                        default=DEFAULT_JOURNAL)

    parser.add_argument('--date',
                        help="Creation date for new journal entry. " + \
                              "Use format yymmdd or yyyymmddhh24misstz. " + \
                              "Default: file creation date."
                        )

    parser.add_argument('--title',
                        help="Title of the note. Default: file name without extension.")

    parser.add_argument('--tags',
                        help="Comma delimited list of tag(s) added to journal entry",
                        nargs='+')

    parser.add_argument('--dry-run',
                        help='Reports what would be done without actually affecting Day One',
                        action='store_true')

    # parse the arguments
    args = parser.parse_args()

    return args


def main():
    """Main function to add a file to Day One."""
    function_name_max_length=str(max([len(f.__name__) for f in globals().values() if callable(f)]))
    log_format=("%(asctime)s %(levelname)-7s %(funcName)-"
            +function_name_max_length+"s [%(lineno)-3d] %(message)s")
    logging.basicConfig( format=log_format, level=logging.DEBUG)

    args = parse_command_line_arguments()

    note = Note(args)

    if args.dry_run:
        logging.info(note)
    else:
        note.write()



if __name__ == '__main__':
    main()
