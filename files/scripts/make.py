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
import json
import argparse
from collections.abc import Callable

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


#--------------------------------- HELPERS ---------------------------------#

def is_zconfig_file(file_path: str) -> bool:
    """
    Determines if a given file is a ZCONFIG configuration file.

    Args:
        file_path: The path to the file to be checked.
    Returns:
        `True` if the file is a ZCONFIG file, `False` otherwise.
    """
    try:
        with open(file_path, 'r') as f:
            first_chars = f.read(20)
            return first_chars.startswith("#!ZCONFIG")
    except Exception as e:
        return False


#------------------------- CONFIGURATION VARIABLES -------------------------#

class ConfigVars(dict):
    """
    A dictionary-like class that stores configuration variables and styles.

    This class inherits from Python's built-in dict, extending its functionality
    to include a list of styles under the property `self.styles`.
    It also handles missing keys by returning the key itself, allowing safe use
    in `string.format_map()`.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args,**kwargs)
        self.styles             = []
        self.node_modifications = []

    def __missing__(self,key):
        return '{' + key + '}'


def process_action(config_vars: ConfigVars,
                   action     : str,
                   content    : str
                   ) -> None:
    """
    Processes an action and updates the configuration dictionary accordingly.

    Args:
        config_vars: The destination configuration dictionary that will be updated.
        action     : The action line that defines how to handle the content.
        content    : The actual content associated with the action line.

    This function modifies 'config_vars' in-place based on the specified 'action':
     - Actions with "{#VARNAME}" format, add a variable to the dictionary.
     - Actions with ">>>STYLE NAME" format, add a style to the dictionary.
     - Actions with ">>:COMMAND" format are commands to be executed
       (such as enabling or disabling nodes).

    Returns:
        None, the function modifies 'config_vars' in-place.
    """
    # actions with format "{#VARNAME}" add a variable to the dictionary
    if action.startswith("{#"):
        varname = action[1:].strip().rstrip('}')
        config_vars[varname] = content.strip()

    # actions with format ">>>STYLE NAME" add a style to the dictionary
    elif action.startswith(">>>"):
        style_name = action[2:].strip()
        style      = (style_name, content.strip())
        config_vars.styles.append( style )

    # actions with format ">>:COMMAND" are commands to modify nodes
    elif action.startswith(">>:"):

        if action == ">>:ENABLE":
            for line in content.splitlines():
                node_title = line.strip()
                if node_title:
                    config_vars.node_modifications.append( (node_title, {"mode":0}) )

        elif action == ">>:DISABLE":
            for line in content.splitlines():
                node_title = line.strip()
                if node_title:
                    config_vars.node_modifications.append( (node_title, {"mode":2}) )

        else:
            warning(f"Unknown command '{action}'")


def read_vars_from_file(config_vars: ConfigVars,
                        filepath   : str
                        ) -> None:
    """
    Reads a configuration file and populates the vars dictionary with its contents.

    This function processes a file line by line, identifying actions and their
    associated content. It uses the 'process_action' helper function to add
    either variables or styles to the provided dictionary.

    Args:
        config_vars: The configuration dictionary to populate with variables
                     and styles from the file.
        filepath   : The path to the configuration file to read.
    Returns:
        None, this function modifies the 'config_dict' in-place.
    Note:
        - Lines defined as "{#VARNAME}" or ">>STYLE_NAME" are treated as a action.
        - Multi-line content is supported.
    """
    action  = None
    content = ""

    with open(filepath) as f:

        is_first_line = True
        for line in f.readlines():
            is_shebang_line = is_first_line and line.startswith("#!")
            is_first_line   = False

            line = line.rstrip() #< trailing whitespaces are lost at the end of each line
            if ( is_shebang_line        or
                 line.startswith("{#")  or #< variable definition action
                 line.startswith(">>:") or #< action to modify node property
                 line.startswith(">>>")    #< style definition action
               ):
                # a new action is detected, so the previous pending one is processed
                if action:
                    process_action(config_vars, action, content.format_map(config_vars))
                # the new action is stored as pending
                action, content = line, ""
            else:
                content += line + "\n"

    # before ending, process any pending action
    if action:
        process_action(config_vars, action, content.format_map(config_vars))


#----------------------------- JSON TEMPLATES ------------------------------#

def resolve_vars_in_json(json_collection,
                         config_vars: ConfigVars
                         ) -> None:
    """
    Recursively resolves variables within a JSONstructure using `config_vars`.

    This function traverses the provided collection and replaces any string
    values that contain placeholders with their corresponding variable values
    from `config_vars`.

    Args:
        json_collection : The JSON object (dict or list) to process recursively.
        config_vars     : Dictionary of variables used for substitution in strings.
    Note:
        - This function modifies the original `json_collection` in place.
        - It handles both dictionaries and lists within the collection, applying
          variable resolution recursively.
    """
    if isinstance(json_collection, dict):
        for key in json_collection.keys():
            jobject = json_collection[key]
            if isinstance(jobject, str):
                json_collection[key] = jobject.format_map(config_vars)
            elif isinstance(jobject, (list, dict)):
                resolve_vars_in_json(jobject, config_vars)

    elif isinstance(json_collection, list):
        for index in range(len(json_collection)):
            jobject = json_collection[index]
            if isinstance(jobject, str):
                json_collection[index] = jobject.format_map(config_vars)
            elif isinstance(jobject, (list, dict)):
                resolve_vars_in_json(jobject, config_vars)


def get_group_rectangle(json: dict, group_name:str) -> list[int]:
    """
    Retrieves the bounding rectangle of a specific workflow group.
    Args:
        json      : The dictionary containing the full comfyui workflow.
        group_name: The name of the group whose bounding rectangle is desired.
    Returns:
        A list [left, top, width, height] representing the group's bounding box,
        or None if the group does not exist.
    """
    if not isinstance(json, dict)  or  "groups" not in json:
        return None

    groups = json["groups"]
    for group in groups:

        if not isinstance(group, dict) and "title" not in group:
            continue

        if group["title"] == group_name:
            return group.get('bounding')

    return None


def find_node(workflow: dict, title: str) -> dict:
    """
    Searches for a node in a workflow JSON structure based on its title.
    Args:
        json  : The dictionary containing the full comfyui workflow.
        title : The title of the node to find in the workflow JSON structure.
    Returns:
        The node dictionary corresponding to the given title, or None if not found.
    """
    if not isinstance(workflow, dict):
        return None

    for node in workflow.get("nodes", []):
        if not isinstance(node, dict):
            continue
        if node.get("title") == title:
            return node
    return None


def find_nodes_in_rectangle(json: dict, rectangle: list[int]) -> list:
    """
    Identifies all nodes that fall within a given rectangular region from a workflow.
    Args:
        json      : The dictionary containing the full comfyui workflow.
        rectangle : A list [left, top, width, height] defining the bounds to check against.
    Returns:
        A sorted list of nodes (dictionaries) that fall within the specified
        rectangular area, ordered by their y-coordinate position. If no valid
        nodes are found an empty list will be returned.
    """
    if not isinstance(json, dict):
        return []

    in_bounds_nodes = [ ]
    for node in json.get("nodes", []):
        if not isinstance(node, dict):
            continue

        pos = node.get("pos")
        if not isinstance(pos, list) or len(pos) < 2:
            continue

        # discard nodes that are not inside the rectangle
        x, y = pos[:2]
        if x < rectangle[0] or y < rectangle[1]:
            continue
        if x > (rectangle[0] + rectangle[2]):
            continue
        if y > (rectangle[1] + rectangle[3]):
            continue

        # add the node to the list (including the 'y' coord)
        in_bounds_nodes.append( (y,node) )

    # sort the list by coord y (the first element of each tuple)
    # and return only nodes
    in_bounds_nodes.sort(key=lambda y_node: y_node[0])
    return [node for _, node in in_bounds_nodes]


def apply_operation_to_node(workflow : dict,
                            title    : str,
                            operation: Callable[[dict], None]
                            ) -> int:
    """
    Applies a given operation to all nodes in the workflow with a matching title.
    Args:
        workflow : The dictionary representing the comfyui workflow.
        title    : The title of the node(s) to which the operation should be applied
                   Use "*" as a wildcard to apply the operation to all nodes.
        operation: A callable function that takes a single argument (the node dictionary)
                   and applies some modification or action to it.
    Returns:
        An integer representing the number of nodes on which the operation was performed.
    """
    if not isinstance(workflow, dict):
        return 0

    count = 0
    for node in workflow.get("nodes", []):
        if not isinstance(node, dict):
            continue

        if title=="*" or node.get("title") == title:
            operation(node)
            count += 1

    return count


def update_node_mode(workflow: dict, title: str, mode: int) -> int:
    """
    Modifies the mode of a node with a matching title in the workflow.
    Args:
        workflow: The dictionary representing the comfyui workflow.
        title   : The title of the node(s) to which the operation should be applied
                  Use "*" as a wildcard to apply the operation to all nodes.
        mode    : The new mode value to set for the specified node.
    """
    def update_mode(node: dict) -> None:
        node["mode"] = mode
    apply_operation_to_node(workflow, title, update_mode)


def apply_style_to_nodes(nodes: list[dict], styles: list[tuple[str,str]]) -> None:
    """
    Set the title and content of each node using the provided style list.

    Args:
        nodes  : The list of nodes (dict) to be updated.
        styles : A list of tuples where each tuple contains two strings; 
                 the first is the style name, and the second is the style template.
    """
    # iterate over the nodes, updating the title and content of each one
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue

        if index < len(styles) and isinstance(styles[index], tuple) and len(styles[index]) >= 2:
            title          = styles[index][0]
            template_value = styles[index][1]
        else:
            title           = ""
            template_value = ""

        node["title"]          = f"STYLE: {title}"
        node["widgets_values"] = [template_value]


#------------------------------- STYLES.TXT --------------------------------#

def save_styles_txt(filepath: str,
                    styles  : list[tuple[str,str]],
                    prompts : list[str]
                    ) -> None:
    """
    Saves the style list (and example prompts) to a text file.
    Args:
        filepath : The path where the output text file will be saved.
        styles   : A list of tuples containing style names and their template values.
        prompts  : A list of strings representing different example prompts.
    """
    with open(filepath, 'w') as file:

        for index, prompt in enumerate(prompts):
            file.write(f"IMAGE{index+1} PROMPT:\n")
            file.write(f"{prompt}\n")
            file.write("\n")

        file.write("STYLES\n")
        for style in styles:
            file.write(f" * {style[0]}\n")
        file.write("\n")


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def make_workflow(template_filepath     : str,
                  config_filepath       : str,
                  global_config_filepath: str  = None,
                  create_styles_txt     : bool = False,
                  overwrite             : bool = False
                 ) -> bool:
    """
    Creates a workflow based on the provided template and configuration.

    This function reads variables from the specified configuration files, and
    creates a workflow using the given template.

    Args:
        template_filepath     : The path to the template file used for creating the workflow.
        config_filepath       : The path to the specific configuration file.
        global_config_filepath: Optional; the path to a global configuration file containing shared settings.
    Returns:
        True if the workflow was successfully created.
    """
    config_vars = ConfigVars()

    template_name = os.path.basename(template_filepath).split(".")[0]
    if template_name.startswith("template"):
        template_name = template_name[9:].rstrip('_')

    config_vars["#TEMPLATE_NAME"] = template_name
    if global_config_filepath:
        read_vars_from_file( config_vars, global_config_filepath )
    read_vars_from_file( config_vars, config_filepath )

    # always "{#FILEPREFIX}" must be defined in the configuration file
    if not "#FILEPREFIX" in config_vars:
        error('The "{#FILEPREFIX}" variable is missing from the configuration file.')
        return False

    # generate the name of the output files
    workflow_filename = config_vars["#FILEPREFIX"] + template_name + ".json"
    styles_filename   = config_vars["#FILEPREFIX"] + "styles.txt"
    if not create_styles_txt:
        styles_filename = None

    # if overwrite is disabled, check if output files already exist
    if not overwrite:
        if workflow_filename and os.path.exists( workflow_filename ):
            error(f'The output path "{workflow_filename}" already exists.',
                   "Use the '--overwrite' flag to overwrite any existing file.")
            return False
        if styles_filename and os.path.exists( styles_filename ):
            error(f'The output path "{styles_filename}" already exists.',
                   "Use the '--overwrite' flag to overwrite any existing file.")
            return False

    # try to read the workflow template by parsing a json
    template_json = None
    with open(template_filepath) as file:
        try:
            template_json = json.load(file)
        except json.JSONDecodeError:
            template_json = None
    if not template_json:
        error(f"Error decoding JSON in template.")
        return False


    #=== WORKFLOW VARIABLES ===#

    # resolve all variables in any strings within the json
    resolve_vars_in_json(template_json,
                         config_vars = config_vars)


    #=== WORKFLOW STYLES ===#

    # finds the coordinates of the "STYLES" group
    style_rectangle = get_group_rectangle(template_json, group_name="STYLES")
    if style_rectangle == None:
        error("The 'STYLES' group is missing from the template.")
        return False

    # find all nodes within style_rectangle
    nodes = find_nodes_in_rectangle(template_json, style_rectangle)
    if not nodes:
        error("No nodes found within the 'STYLES' group.")

    # apply the styles to each node within style_rectangle
    apply_style_to_nodes(nodes, config_vars.styles)


    #=== WORKFLOW PROMPT ===#

    if "#PROMPT" in config_vars:
        prompt_node = find_node(template_json, title="PROMPT")
        if prompt_node:
            prompt_node["widgets_values"] = [ config_vars["#PROMPT"] ]

    #=== WORKFLOW NODE MODIFICATIONS ===#

    for node_title, modification in config_vars.node_modifications:
        if not isinstance(node_title, str) or not isinstance(modification, dict):
            continue

       # try to find the node that is being modified by the configuration
        node = find_node(template_json, title=node_title)
        if not node:
            warning(f"The node with title '{node_title}' was not found.")
            continue

        # the only modification that is implemented so far is
        # changing the node's "mode" (enable=0, disable=2, bypass=4)
        if "mode" in modification:
            update_node_mode(template_json, title=node_title, mode=modification["mode"])
 
    #=== STYLES.TXT ===#

    if styles_filename:
        prompts = []
        if "#PROMPT" in config_vars:
            prompts.append( config_vars["#PROMPT"] )
        if "#PROMPT2" in config_vars:
            prompts.append( config_vars["#PROMPT2"] )
        save_styles_txt( styles_filename, styles=config_vars.styles, prompts=prompts )

    # saves modified workflow in output_filepath
    with open(workflow_filename, "w", encoding="utf-8") as file:
        json.dump(template_json, file, ensure_ascii=False, indent=4)

    return True



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
    parser.add_argument('-w','--overwrite' , action='store_true', help="Overwrite existing output file if exists.")


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
    #   2. List of .txt files with "#!ZCONFIG" flag (zconfig files)
    #   3. Specific global configuration file matching GLOBAL_CONFIG_FILES
    #
    json_templates = []  #< list to store paths of .json template files
    text_configs   = []  #< list to store paths of valid text config files
    global_config  = ""  #< path to the global configuration file (if found)
    for filename in os.listdir(source_dir):
        if filename.endswith(".json") and not filename.endswith("~.json"):
            json_templates.append( os.path.join(source_dir, filename) )
        elif filename.endswith(".txt") and is_zconfig_file(os.path.join(source_dir, filename)):
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
            make_workflow(template_filepath      = template_path,
                          config_filepath        = config_path,
                          global_config_filepath = global_config,
                          overwrite              = args.overwrite,
                          create_styles_txt      = True,
                          )




if __name__ == "__main__":
    main()
