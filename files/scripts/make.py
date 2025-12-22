"""
  File    : make.py
  Purpose : Build Z-Image Workflows from source templates and configuration files.
  Author  : Martin Rizzo | <martinrizzo@gmail.com>
  Date    : Dec 21, 2025
  Repo    : https://github.com/martin-rizzo/AmazingZImageWorkflow
  License : Unlicense
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                            Amazing Z-Image Workflow
   Z-Image workflow with customizable image styles and GPU-friendly versions
 _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import os
import sys
import argparse

# list of files that should be taken as global configuration
GLOBAL_CONFIG_FILES = ["global.txt", "globals.txt"]

# default directory where to look for source files
DEFAULT_SOURCE_DIR = "src"

# ANSI escape codes for colored terminal output
RED      = '\033[91m'
DKRED    = '\033[31m'
YELLOW   = '\033[93m'
DKYELLOW = '\033[33m'
GREEN    = '\033[92m'
CYAN     = '\033[96m'
DKGRAY   = '\033[90m'
RESET    = '\033[0m'

#----------------------------- ERROR MESSAGES ------------------------------#

def disable_colors():
    global RED, DKRED, YELLOW, DKYELLOW, GREEN, CYAN, DKGRAY, RESET
    RED, DKRED, YELLOW, DKYELLOW, GREEN, CYAN, DKGRAY, RESET = "", "", "", "", "", "", "", ""


def info(message: str, padding: int = 0, file=sys.stderr) -> None:
    """Displays an informational message to the error stream.
    """
    print(f"{" "*padding}{CYAN}\u24d8 {message}{RESET}", file=file)


def warning(message: str, *info_messages: str, padding: int = 0, file=sys.stderr) -> None:
    """Displays a warning message to the standard error stream.
    """
    print(f"{" "*padding}{CYAN}[{YELLOW}WARNING{CYAN}]{DKYELLOW} {message}{RESET}", file=file)
    for info_message in info_messages:
        info(info_message, padding=padding, file=file)


def error(message: str, *info_messages: str, padding: int = 0, file=sys.stderr) -> None:
    """Displays an error message to the standard error stream.
    """
    print(f"{" "*padding}{DKRED}[{RED}ERROR!{DKRED}]{DKYELLOW} {message}{RESET}", file=file)
    for info_message in info_messages:
        info(info_message, padding=padding, file=file)


def fatal_error(message: str, *info_messages: str, padding: int = 0, file=sys.stderr) -> None:
    """Displays a fatal error message to the standard error stream and exits with status code 1.
    """
    error(message, *info_messages, padding=padding, file=file)
    sys.exit(1)


#---------------------------- HELPER FUNCTIONS -----------------------------#

class ConfigDict(dict):
    """
    A dictionary-like class that allows for variable and style management.
    This class inherits from Python's built-in dict, extending its functionality
    to include a list of styles under the property `self.styles`.
    It also handles missing keys by returning the key itself, allowing safe use
    in string.format_map().
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args,**kwargs)
        self.styles = []

    def __missing__(self,key):
        return key


def add_var(config_dict: ConfigDict,
            action     : str,
            content    : str
            ) -> None:
    """
    Adds a variable or style to the dictionary based on the action line.
    Args:
        config_dict: The configuration dictionary to update with variables and styles.
        action     : The action line that defines how to handle the content.
        content    : The actual content associated with the action line.
    Returns:
        None, this function modifies the 'config_dict' in-place.
    """
    # actions with format "{#VARNAME}" add a variable to the dictionary
    if action.startswith("{#"):
        varname = action[1:].strip().rstrip('}')
        config_dict[varname] = content.strip()

    # actions with format ">>STYLE NAME" add a style to the dictionary
    elif action.startswith(">>"):
        style_name = action[2:].strip()
        style      = (style_name, content.strip())
        config_dict.styles.append( style )


def read_vars_from_file(config_dict: ConfigDict,
                        filepath   : str
                        ) -> None:
    """Reads a configuration file and populates the vars dictionary with its contents.

    This function processes a file line by line, identifying actions and their
    associated content. It uses the 'add_var' helper function to add either
    variables or styles to the provided dictionary.

    Args:
        config_dict: The configuration dictionary to populate with variables and styles from the file.
        filepath   : The path to the configuration file to read.
    Returns:
        None, this function modifies the 'config_dict' in-place.
    Note:
        - Lines defined as "{#VARNAME}" or ">>STYLE_NAME" are treated as a action.
        - Multi-line content is supported.
    """
    action  = None
    content = ""

    # necesito leer el archivo linea por linea
    with open(filepath) as f:
        for line in f.readlines():

            act_candidate = line.strip()
            if act_candidate.startswith("#!") or \
               act_candidate.startswith("{#") or \
               act_candidate.startswith(">>"):
                if action:
                    content = content.format_map(config_dict)
                    add_var(config_dict, action, content)
                action  = act_candidate
                content = ""
            else:
                content += line.rstrip() + "\n"


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def make_workflow(template_filepath     : str,
                  config_filepath       : str,
                  global_config_filepath: str = None
                 ) -> None:
    """
    Creates a workflow based on the provided template and configuration.

    This function reads variables from the specified configuration files, and
    creates a workflow using the given template.

    Args:
        template_filepath     : The path to the template file used for creating the workflow.
        config_filepath       : The path to the specific configuration file.
        global_config_filepath: Optional; the path to a global configuration file containing shared settings.
    Returns:
        None
    """
    config_dict = ConfigDict()

    template_name = os.path.basename(template_filepath).split(".")[0]
    if template_name.startswith("template"):
        template_name = template_name[9:].rstrip('_')

    config_dict["#TEMPLATE_NAME"] = template_name
    if global_config_filepath:
        read_vars_from_file( config_dict, global_config_filepath )
    read_vars_from_file( config_dict, config_filepath )

    print( config_dict.get("#OUTPUT","") )



def main(args=None, parent_script=None):
    """
    Main entry point for the script.
    Args:
        args          (optional): List of arguments to parse. Default is None, which will use the command line arguments.
        parent_script (optional): The name of the calling script if any. Used for customizing help output.
    """    
    prog = None
    if parent_script:
        prog = parent_script + " " + os.path.basename(__file__).split('.')[0]

    # set up argument parser for the script
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Build Z-Image Workflows from source templates and configuration files.",
        formatter_class=argparse.RawTextHelpFormatter
        )
    parser.add_argument('--no-color'       , action='store_true', help="Disable colored output.")
    parser.add_argument('-s','--source-dir', type=str,            help="The source dir containing templates and config files (default: /src)")

    args = parser.parse_args(args=args)

    # if the user requested to disable colors, call disable_colors()
    if args.no_color:
        disable_colors()

    # get source directory and convert it to absolute path
    source_dir = args.source_dir or DEFAULT_SOURCE_DIR
    source_dir = os.path.join(os.getcwd(), source_dir)
    source_dir = os.path.realpath(source_dir)

    # gather three types of files from the source directory:
    #   1. List of .json files (excluding temporary ~.json files)
    #   2. List of .txt files with "#!ZCONFIG" flag
    #   3. Specific global configuration file matching GLOBAL_CONFIG_FILES
    #
    json_templates = []  #< list to store paths of .json template files
    text_configs   = []  #< list to store paths of valid text config files
    global_config  = ""  #< path to the global configuration file (if found)
    for filename in os.listdir(source_dir):
        if filename.endswith(".json") and not filename.endswith("~.json"):
            json_templates.append( os.path.join(source_dir, filename) )
        elif filename.endswith(".txt") and "#!ZCONFIG" in open(os.path.join(source_dir, filename)).read():
            if filename in GLOBAL_CONFIG_FILES:
                global_config = os.path.join(source_dir, filename)
            else:
                text_configs.append( os.path.join(source_dir, filename) )

    # display errors if no required files were found
    if not json_templates:
        fatal_error("No JSON template files found in the source directory.")
    if not text_configs:
        fatal_error("No valid text configuration files found in the source directory.")

    # show a report of the found files
    print("")
    print(" Configuration Files:")
    if global_config:
        print(f"    - {os.path.basename(global_config)}")
    for fullpath in text_configs:
        print(f"    - {os.path.basename(fullpath)}")
    print(" Template Files:")
    for fullpath in json_templates:
        print(f"    - {os.path.basename(fullpath)}")
    print("")


    for config_path in text_configs:
        for template_path in json_templates:
            make_workflow(template_path, config_path, global_config)




if __name__ == "__main__":
    main()
