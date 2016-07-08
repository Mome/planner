from configparser import ConfigParser
from os.path import expanduser, join, exists
import os

DEFAULT_PATH = expanduser('~/.planner')
DEFAULT_CONF_NAME = 'conf'

DEFAULT_CONF = ConfigParser()
DEFAULT_CONF.read_dict(
    {
        'CalendarInterface':{
            'ColumnNumber' : 5,
            'LineStyle1' : 'ascii',
            'LineStyle2' : 'ascii',
            'ActiveAnsiStyling' : 'yes',
            'HeadStyles' : 'f_magenta',
            'TerminStyles' : 'f_blue',
            'DoneStyles' : 'f_green',
            'UndoneStyles' : 'f_red',
        }
    })


def load_configuration(path=None, filename=None, default=DEFAULT_CONF):

    filepath = _construct_filepath(path, filename)

    if default in (None, 'empty') :
        config = ConfigParser()
    elif isinstance(default, ConfigParser):
        config = default
    elif isinstance(default, dict):
        config = default
    else:
        raise ValueError("´default´ must be None, 'empty', or instance of ConfigParser or dict.")

    if exists(filepath):
        config.read(filepath)
    elif default is None:
        raise IOError('No such file or directory:', filepath)        

    return config


def save_configuration(config, path=None, filename=None):
    filepath = _construct_filepath(path, filename, True)
    with open(filepath, 'w') as f:
        config.write(f)


def _construct_filepath(path, filename, create_dirs=False):
    if not path:
        path = DEFAULT_PATH
    else:
        path = expanduser(path)

    if create_dirs:
        os.makedirs(path, exist_ok=True)

    if not filename:
        filename = DEFAULT_CONF_NAME
    filepath = join(path, filename)
    

    return filepath
