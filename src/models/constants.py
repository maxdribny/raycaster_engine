# /src/models/constants.py

import xml.etree.ElementTree as ET
import os

from src.exceptions.constant_exceptions import *

IS_BUILD_VERSION = True
VERSION = '0.0.1'

# Window size
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 512
WINDOW_TITLE = "Raycaster" + (" " + VERSION)

# World Settings
WORLD_SIZE_X = 8
WORLD_SIZE_Y = 8
WORLD_SCALE = WORLD_SIZE_X * WORLD_SIZE_Y

# Player Settings
PLAYER_INITIAL_X = 300.0
PLAYER_INITIAL_Y = 300.0
PLAYER_INITIAL_ANGLE = 0
PLAYER_ROTATION_SPEED = 35
PLAYER_MOVE_SPEED = 25
PLAYER_COLOR = (1, 1, 0)

# Render Settings
RENDER_FOV = 60

# Debug Settings
DEBUG_LOG_TO_CONSOLE = True


def set_new_constant(variable_name, value):
    # Check if the variable with the same type exists within this file.
    existing_value = globals().get(variable_name)

    if existing_value is None:
        raise SettingKeyValueError(f'Could not set {variable_name} to {value},'
                                   f'there is no existing variable with the same name.')

    if not isinstance(existing_value, type(value)):
        raise SettingKeyValueError(f'Could not set {variable_name} to {value},'
                                   f'{variable_name} is not the same type {type(variable_name)} as {existing_value} {type(existing_value)}')

    globals()[variable_name] = value
    print(f'Setting game parameter: {variable_name} = {value}')


def load_config_from_xml(file_path):
    tree = (ET.parse(file_path))
    root = tree.getroot()

    for variable in root.findall(".//variable"):
        variable_name = variable.get('name')
        value_str = variable.find('value').text
        value_type = variable.find('type').text

        if value_type == 'int':
            value = int(value_str)
        elif value_type == 'float':
            value = float(value_str)
        elif value_type == 'tuple':
            value_str = value_str.strip('()')  # Remove parenthesis for correct parsing
            value = tuple(map(int, value_str.split(',')))
        elif value_type == 'str':
            value = value_str
        else:
            print(f"Unsupported type {value_type} for variable {variable_name}. Skipping.")
            continue

        print(f'\nFound variable {variable_name} with value {value}')

        try:
            set_new_constant(variable_name, value)
        except SettingKeyValueError as e:
            print(e)
            continue

    print("\n---------------------")
    print(f"XML LOADING COMPLETE")
    print("---------------------\n")


def config_indent(elem, level=0):
    """Helper function to add indentation to an ElementTree element."""
    i = '\n' + level * '  '
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + '  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            config_indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def create_default_config(directory, file_name):
    # Check if the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, file_name)

    # Check if the file exists
    print(f'Checking if {file_path} exists')

    # TODO: this is very hacky, think of something better
    if IS_BUILD_VERSION:
        if os.path.exists(file_path):
            # Delete the path
            os.remove(file_path)

    if not os.path.exists(file_path):
        # Define default settings
        default_settings = [
            {"name": "WINDOW_WIDTH", "value": str(WINDOW_WIDTH), "type": "int"},
            {"name": "WINDOW_HEIGHT", "value": str(WINDOW_HEIGHT), "type": "int"},
            {"name": "WINDOW_TITLE", "value": WINDOW_TITLE, "type": "str"},
            {"name": "WORLD_SCALE", "value": str(WORLD_SCALE), "type": "int"},
            {"name": "WORLD_SIZE_X", "value": str(WORLD_SIZE_X), "type": "int"},
            {"name": "WORLD_SIZE_Y", "value": str(WORLD_SIZE_Y), "type": "int"},
            {"name": "PLAYER_INITIAL_X", "value": str(PLAYER_INITIAL_X), "type": "float"},
            {"name": "PLAYER_INITIAL_Y", "value": str(PLAYER_INITIAL_Y), "type": "float"},
            {"name": "PLAYER_INITIAL_ANGLE", "value": str(PLAYER_INITIAL_ANGLE), "type": "int"},
            {"name": "PLAYER_ROTATION_SPEED", "value": str(PLAYER_ROTATION_SPEED), "type": "int"},
            {"name": "PLAYER_MOVE_SPEED", "value": str(PLAYER_MOVE_SPEED), "type": "int"},
            {"name": "PLAYER_COLOR", "value": str(PLAYER_COLOR), "type": "tuple"},
            {"name": "RENDER_FOV", "value": str(RENDER_FOV), "type": "int"},
            {"name": "DEBUG_LOG_TO_CONSOLE", "value": str(DEBUG_LOG_TO_CONSOLE), "type": "bool"},
        ]

        # Create an XML tree with default settings
        config = ET.Element("config")
        for setting in default_settings:
            variable = ET.SubElement(config, "variable", name=setting["name"])
            ET.SubElement(variable, "value").text = setting["value"]
            ET.SubElement(variable, "type").text = setting["type"]

        # Add indentation to the XML tree
        config_indent(config)

        # Write the XML tree to the file
        tree = ET.ElementTree(config)
        tree.write(file_path)

    else:
        print(f'File {file_path} already exists, skipping creation.')


# Ensure config directory and file exist
create_default_config('./config', 'config.xml')

# TODO: Fix this as it is still broken
# Load config file at the start of the game
load_config_from_xml('./config/config.xml')
