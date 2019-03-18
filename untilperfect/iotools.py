"""
iotools.py

Tools for reading and writing of files.
"""

import configparser
import csv


# TODO: Consider csv DictReader or something similar???
# TODO: Consider reorganising data in rows if it allows for easier parsing???
#       or ability to read in either format
# TODO: SQL Reader???
# TODO: Ability to parse info from SchedulePro database, perhaps based
#       on a config file
# TODO: Should any writing functions be included here?


def column_reader(filename):
    """Reads columnar data from csv file."""
    with open(filename) as file_obj:
        rows = csv.reader(
            file_obj,
            skipinitialspace=True,
            delimiter=",",
            quoting=csv.QUOTE_NONNUMERIC,
        )
        data_dict = {}
        is_header = True
        assert_missing_text = "Missing data - rows have unequal length"
        for row in rows:
            if is_header:
                is_header = False
                headers = row
                entries = len(row)
                for header in headers:
                    if header in data_dict:
                        error_text = "Duplicate column name: '{}'.".format(
                            header
                        )
                        raise ValueError(error_text)
                    data_dict[header] = []
            else:
                assert len(row) == entries, assert_missing_text
                for index, cell in enumerate(row):
                    data_dict[headers[index]].append(cell)
    return data_dict


def get_config_section(filename="config.ini", section="DEFAULT"):
    """Reads a section from a configuration file."""
    try:
        with open(filename) as _:
            parser = configparser.ConfigParser()
            parser.read(filename)
            return dict(parser.items(section))
    except IOError:
        raise IOError("could not open file '{}'".format(filename))
