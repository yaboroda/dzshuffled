"""
author:     yaBoroda
github:     https://github.com/yaboroda/dzshuffled
email:      yarboroda@gmail.com
"""

import os
import sys
import argparse
import subprocess
from typing import Union, Dict

from dztoolset.deezerconfig import DeezerConfig
from dztoolset.deezerapi import DeezerApiRequestError
from dztoolset.deezerscenario import DeezerScenario
from dztoolset.printer import Printer

SCRIPT_VERSION = '1.3.2.2'
DEBUG_MODE = False
printer = Printer()

"""If environment var defined, set CONFIG_PATH from it,
else set to ~/.config/dzshuffled/config.ini
"""
if 'DZSHUFFLED_CONFIG_PATH' in os.environ:
    CONFIG_PATH = os.environ['DZSHUFFLED_CONFIG_PATH']
else:
    CONFIG_PATH = (os.path.expanduser("~")
                   + "/.config/dzshuffled/config.ini")


def handle_exception_output(e, template: str ='{0}'):
    """If not DEBUG_MODE swallow tracing exception, output only message."""
    if not DEBUG_MODE:
        printer.print(template.format(e))
    else:
        raise e


def print_help_and_exit(parser: argparse.ArgumentParser):
    parser.print_help()
    sys.exit()


def build_cli_parser():
    parser = argparse.ArgumentParser(
        description='This script will create playlist in your Deezer'
                    ' library consisting of shuffled tracks from your'
                    ' other playlists. Pass scenario name or number to'
                    ' create playlist from it. Pass -l or -lv to see'
                    ' all scenarios. Scenarios sets up in config wich'
                    ' by default in ~/.config/dzshuffled/config.ini but'
                    ' you can reassign it with DZSHUFFLED_CONFIG_PATH'
                    ' environment variable.'
    )

    parser.add_argument(
        'scenario',
        metavar='SCENARIO',
        nargs='?',
        const='',
        default='',
        help='name or number of scenario. Pass -l argument to see full list'
    )

    parser.add_argument(
        '-l', '--list',
        action='store_const',
        const=True,
        help='show full list of scenarios to create playlist from,'
             ' pass -v param to show info about them'
    )

    parser.add_argument(
        '-v', '--verbous',
        action='store_const',
        const=True,
        help='if called with argument -l, show info about listed scenarios'
    )

    parser.add_argument(
        '-i', '--info',
        action='store_const',
        const=True,
        help='show info about selected scenario but not do anithing'
    )

    parser.add_argument(
        '-e', '--edit',
        action='store_const',
        const=True,
        help=('edit config file vith editor specified in config, by default'
              ' it is Vim')
    )

    parser.add_argument(
        '--editor',
        metavar='EDITOR',
        default=None,
        help=('edit config with passed program instead of editor from config')
    )

    parser.add_argument(
        '-d', '--debug',
        action='store_const',
        const=True,
        help=('debug mode for output full trace of exceptions')
    )

    parser.add_argument(
        '--version',
        action='store_const',
        const=True,
        help='show script version'
    )

    return parser


def print_info_about_scenario(number: Union[int, str], name: str,
                              data: Dict = None):
    if data:
        printer.print('[{0}] {1}'.format(number, name))
        printer.pprint(data)
    else:
        printer.print('[{0}] {1}'.format(number, name))


def print_list_scenarios(dz: DeezerScenario, verbosity: bool = False):
    scenarios = dz.get_list_of_scenarios()
    for i in range(len(scenarios)):
        if verbosity:
            print_info_about_scenario(
                i, scenarios[i], dz.get_scenario_config(scenarios[i])
            )
        else:
            print_info_about_scenario(i, scenarios[i])


def process_cli_scenario_call(scenario_input: str, dz: DeezerScenario,
                              info_flag: bool = False):
    if scenario_input.isnumeric():
        scenario_index = int(scenario_input)
        scenario_name = dz.get_scenario_name_by_index(scenario_index)
    else:
        scenario_name = scenario_input
        scenario_index = dz.get_scenario_index_by_name(scenario_name)

    if info_flag:
        print_info_about_scenario(
            scenario_index, scenario_name,
            dz.get_scenario_config(scenario_name)
        )
    else:
        dz.check_and_update_token()
        dz.exec_scenario(scenario_name)


def edit_config(config: DeezerConfig, editor=None):
    if not editor:
        editor = config.get('system', 'editor')
    p = subprocess.Popen([editor, config.path])
    return p.wait()


def main(custom_args=None, config_path=CONFIG_PATH):
    global DEBUG_MODE

    try:
        parser = build_cli_parser()
        args = parser.parse_args(custom_args)

        if args.debug:
            DEBUG_MODE = True

        config = DeezerConfig(config_path, printer=printer)

        if args.version:
            printer.print('version: {0}'.format(SCRIPT_VERSION))
            sys.exit()

        if args.edit:
            edit_config(config, args.editor)
            sys.exit()

        if not args.scenario and not args.list:
            print_help_and_exit(parser)

        dz = DeezerScenario(config)

        if args.list:
            print_list_scenarios(dz, args.verbous)
            sys.exit()

        if args.scenario:
            process_cli_scenario_call(args.scenario, dz, args.info)
            sys.exit()

    except DeezerApiRequestError as e:
        handle_exception_output(e)
    except Exception as e:
        raise(e)
        # handle_exception_output(e, 'Error: {0}')
