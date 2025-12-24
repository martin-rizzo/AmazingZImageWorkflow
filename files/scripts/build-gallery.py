"""
  File    : build-gallery.py
  Purpose : Creates a image with a grid of images with labels.
  Author  : Martin Rizzo | <martinrizzo@gmail.com>
  Date    : Dec 1, 2025
  Repo    : https://github.com/martin-rizzo/AmazingZImageWorkflow
  License : Unlicense2
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                            Amazing Z-Image Workflow
   Z-Image workflow with customizable image styles and GPU-friendly versions
 _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import os
import sys
import json
import argparse
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

# Default label metrics
DEFAULT_FONT_SIZE    = 64
DEFAULT_LABEL_WIDTH  = 512
DEFAULT_LABEL_HEIGHT = 64

## Color used for prompt text
#PROMPT_TEXT_COLOR = "#333344"

# Flag to display a warning if a font fails to load
SHOW_FONT_WARNING = True

# Hex color codes for different style names
# (if the style name contains one of these words, use that color)
COLORS_BY_WORD = {
    "PHOTO"     : "#006e18",
    "NEON"      : "#c900c9",
    "VINTAGE"   : "#834C0D",
    "RETRO"     : "#6E3F09",
    "B&W"       : "#5F5F5F",
}
def get_text_color(style_name: str, default_color: str=None) -> str:
    for word, color in COLORS_BY_WORD.items():
        if word in style_name.upper():
            return color
    return default_color


# ANSI escape codes for colored terminal output
RED    = '\033[91m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
DKGRAY = '\033[90m'
RESET  = '\033[0m'

#----------------------------- ERROR MESSAGES ------------------------------#

def disable_colors():
    global RED, GREEN, YELLOW, CYAN, DKGRAY, RESET
    RED, GREEN, YELLOW, CYAN, DKGRAY, RESET = "", "", "", "", "", ""

def warning(message: str, *info_messages: str) -> None:
    """Displays and logs a warning message to the standard error stream.
    """
    print()
    print(f"{CYAN}[{YELLOW}WARNING{CYAN}]{RESET} {message}", file=sys.stderr)
    for info_message in info_messages:
        print(f"          {YELLOW}{info_message}{RESET}", file=sys.stderr)

def error(message: str, *info_messages: str) -> None:
    """Displays and logs an error message to the standard error stream.
    """
    print()
    print(f"{CYAN}[{RED}ERROR{CYAN}]{RESET} {message}", file=sys.stderr)
    for info_message in info_messages:
        print(f"          {RED}{info_message}{RESET}", file=sys.stderr)

def fatal_error(message: str, *info_messages: str) -> None:
    """Displays and logs an fatal error to the standard error stream and exits.
    Args:
        message       : The fatal error message to display.
        *info_messages: Optional informational messages to display after the error.
    """
    error(message)
    for info_message in info_messages:
        print(f" {CYAN}\u24d8  {info_message}{RESET}", file=sys.stderr)
    print()
    exit(1)

#--------------------------------- HELPERS ---------------------------------#

def is_valid_png_image(path: str, valid_prefix: str = "") -> bool:
    """Check if a given path is a PNG image file with a valid prefix.
    """
    if not os.path.isfile(path):
        return False
    lower_filename = os.path.basename(path).lower()
    if not lower_filename.endswith(".png"):
        return False
    if not lower_filename.startswith(valid_prefix.lower()):
        return False
    return True



def find_valid_png_images_in_dir(directory: str, valid_prefix: str = "") -> list[str]:
    """Find all PNG image files with a valid prefix in a directory.
    """
    images = []
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if is_valid_png_image(file_path, valid_prefix):
            images.append(file_path)
    return images


def get_node(workflow: dict, /,*,
             type          : str = None,
             title         : str = None,
             title_contains: str = None,
             ) -> dict[str, any] | None:
    """Retrieve a node from the workflow that matches the given criteria.

    if more than one criteria are provided, the returned node
    will fulfill all of them.
    Args:
        workflow                : The workflow dictionary to search.
        type  (optional)        : The type of the desired node.
        title (optional)        : The title of the desired node.
        title_contains(optional): The desired node's title must contain this string.
    Returns:
        A dictionary with the desired node's details if found, otherwise None.
    """
    type           = type.lower()           if type           else None
    title          = title.lower()          if title          else None
    title_contains = title_contains.lower() if title_contains else None
    nodes = workflow.get('nodes', [])
    for node in nodes:
        node_type = node.get('type', '')
        node_id   = node.get('id', 0)
        if type and node_type.lower() != type:
            continue

        if title and node.get('title','').lower() != title:
            continue
        if title_contains and title_contains not in node.get('title','').lower():
            continue
        return node
    return None

def is_node_enabled(workflow: dict, /,*, title: str = None, type : str = None
                    ) -> bool | None:
    """Check if a specified node in the workflow is enabled.
    Args:
        workflow        : The workflow dictionary to search.
        title (optional): The title of the desired node.
        type_ (optional): The type of the desired node.
    Returns:
        True if the node is enabled, False if it's disabled, or None if not found.
    """
    node = get_node(workflow, title=title, type=type)
    if not isinstance(node, dict):
        return None
    if not "mode" in node:
        return None
    return node["mode"] == 0


def get_workflow_from_image(image_path: str) -> dict[str, any] | None:
    """Extract the workflow data from a given PNG image.
    Args:
        image_path: The path to the PNG image containing workflow data.
    Returns:
        The extracted workflow dictionary if successful, otherwise None.
    """
    with Image.open(image_path) as image:
        text_chunks = image.text if hasattr(image,'text') else []
        workflow    = text_chunks.get('workflow') # text_chunks.get('workflow')
        if not workflow:
            return None

    # try to parse the workflow as JSON
    try:
        workflow = json.loads(workflow)
    except:
        return None

    # workflow must be a dictionary
    return workflow if isinstance(workflow, dict) else None


def extract_style_list(image_paths     : list[str],
                       include_no_style: bool = False
                       ) -> list[str] | None:
    """Extracts the style list from the first image with amazing workflow
    """
    discard_no_style = not include_no_style
    for image_path in image_paths:
        if not os.path.isfile(image_path):
            continue

        # check if image has a workflow
        workflow = get_workflow_from_image(image_path)
        if not workflow: continue

        # search the "node collector (rgthree)" with "style" in the title
        node_collector = get_node(workflow, type="Node Collector (rgthree)", title_contains="style")
        if not isinstance(node_collector, dict):
            # fallback to any "node collector (rgthree)" (old workflow versions)
            node_collector = get_node(workflow, type="Node Collector (rgthree)")
            if not isinstance(node_collector, dict):
                continue

        style_list = []

        # collects the names of each node input
        input_list = node_collector.get('inputs', [])
        if not isinstance(input_list, list): continue
        for input in input_list:
            name = input.get('name')
            if not name: continue
            if name == "none" and discard_no_style: continue
            style_list.append( name )

        # return if any styles were found
        if len(style_list)>0:
            return style_list

    # no styles were found at this point
    return None

def group_images_by_prompt_and_style(image_paths: list[str],
                                     style_list: list[str]
                                     ) -> dict[str, list[str]]:
    """
    Groups images by their prompt and style.
    Args:
        image_paths: A list of file paths to the images.
        style_list : A list with the names of the available styles.
    Returns:
        A dictionary where keys are prompts and values are lists containing image paths.
    """
    image_styles_by_prompt = { }
    if not isinstance(style_list, list) or len(style_list)==0:
        style_list = [ ]

    for image_path in image_paths:
        if not os.path.isfile(image_path):
            continue

        # check if the image has a workflow associated with it
        workflow = get_workflow_from_image(image_path)
        if not workflow: continue

        # default values when the prompt or style are not found in the image
        image_prompt = "??"
        style_index  = -1

        # try to extract the prompt from the current image
        prompt_node = get_node(workflow, title="PROMPT")
        if isinstance(prompt_node, dict):
            values = prompt_node.get('widgets_values')
            if isinstance(values, list) and len(values)>0:
                image_prompt = values[0]

        # try to find out which style is enabled on the current image
        for i, style_name in enumerate(style_list):
            if is_node_enabled(workflow, title=style_name):
                style_index = i
                break

        # if no style was found for this image, continue with next one
        if style_index<0:
            continue

        # add the path of the current image to 'image_styles_by_prompt'
        # but first, check if there's an entry for the current prompt.
        # If not, create a new entry with empty strings equal to the number of styles
        if not image_prompt in image_styles_by_prompt:
            image_styles_by_prompt[image_prompt] = [""] * len(style_list)

        # assign the image path to its corresponding prompt and style index
        image_styles_by_prompt[image_prompt][style_index] = image_path

    return image_styles_by_prompt



#---------------------------------- FONTS ----------------------------------#

def load_font(filepath: str, font_size: int) -> ImageFont:
    """Attempts to load a font from the specified file.

    Args:
        filepath  (str): The path to the font file;
                         Si `None` o string vacio, retornara el font default.
        font_size (int): The desired font size.
    Returns:
        The loaded font or the default font if loading failed.
    """
    global SHOW_FONT_WARNING

    try:
        font = filepath and ImageFont.truetype(filepath, font_size)
    except Exception:
        font = None

    if not font:
        if SHOW_FONT_WARNING:
            SHOW_FONT_WARNING = False
            warning(f"Could not load font from {filepath}. Using default font.")
        font = ImageFont.load_default()

    return font


def select_font_variation(font: ImageFont,
                          variation: str,
                          variation_alt1: str = None,
                          variation_alt2: str = None) -> None:
    """Selects a specific font variation based on the given names.

    Args:
        font     (ImageFont): This should be a font that supports font variations.
        variation      (str): The primary variation name to apply to the font.
        variation_alt1 (str): An alternative variation name to use if the main variation is not found.
        variation_alt2 (str): Another alternative variation name to use.

    Example:
        >>> font = ImageFont.truetype('arial.ttf', 14)
        >>> select_font_variation(font, 'ital', 'wght')
    """
    try:
        available_variations = font.get_variation_names()
        if variation in available_variations:
            font.set_variation_by_name(variation)
        elif variation_alt1 in available_variations:
            font.set_variation_by_name(variation_alt1)
        elif variation_alt2 in available_variations:
            font.set_variation_by_axes(variation_alt2)
    except:
        return


def save_image(filepath        : str,
               image           : Image,
               metadata        : dict[str, str] = [],
               should_make_dirs: bool           = False,
               ) -> None:
    """Save an image to a specified filepath with optional metadata.

    The function supports both JPEG and PNG formats, saving in the appropriate
    format based on the file extension.

    Args:
        filepath          (str): The full path where the image will be saved.
        image           (Image): The PIL Image object to be saved.
        text_chunks      (dict): A dictionary containing key-value metadata
                                 that will be embedded into the PNG file.
        should_make_dirs (bool): If true, creates necessary directories before saving the image.
    """
    extension = os.path.splitext(filepath)[1].lower()

    # create new directories if necessary
    if should_make_dirs:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # save the image using the appropriate format according to the extension
    if extension == '.jpg' or extension == '.jpeg':
        image.save(filepath, 'JPEG', quality=80)
    else:
        # prepare text chunks to be saved together with the PNG image
        pnginfo = PngInfo()
        for key, value in metadata:
            pnginfo.add_text(key, value)
        image.save(filepath, format='PNG', pnginfo=pnginfo, compress_level=9)


#-------------------------------- BOX CLASS --------------------------------#
class Box(tuple):
    """
    A class representing a bounding box defined by its left, top, right, and bottom coordinates.

    The Box class is built on top of Python's tuple type to provide additional methods for manipulating 
    and accessing the bounding box properties. It allows for easy creation, modification, and querying of
    2D rectangular regions in an image or graphics context.

    Instance Creation:
        Box(left, top, right, bottom): Creates a new Box instance with specified coordinates.

    Attributes:
        left   (int|float): The x-coordinate of the left edge.
        top    (int|float): The y-coordinate of the top edge.
        right  (int|float): The x-coordinate of the right edge.
        bottom (int|float): The y-coordinate of the bottom edge.

    Properties:
        left   (int|float)       : Returns the x-coordinate of the left edge.
        top    (int|float)       : Returns the y-coordinate of the top edge.
        right  (int|float)       : Returns the x-coordinate of the right edge.
        bottom (int|float)       : Returns the y-coordinate of the bottom edge.
        width  (int|float)       : Returns the width of the box, calculated as right - left.
        height (int|float)       : Returns the height of the box, calculated as bottom - top.
        center (tuple[int|float]): Returns the x and y coordinates of the center point.

    Factory Methods:

        Box.bounding_for_text(cls, text: str, font: ImageFont) -> Box:
            Creates a Box instance from the bounding box of a given text rendered with a specified font.

        Box.multiline_textbbox(cls, draw: ImageDraw, xy: tuple[float, float], text: str, font: ImageFont, anchor: str | None = None, spacing: float = 4, align: str = "left") -> Box:
            Creates a Box instance from the bounding box of multi-line text.

        Box.container_for_text(cls, text: str, font) -> Box:
            Creates a Box that can contain single line of given text rendered with specified font.

    Methods:

        get_size() -> tuple[int|float]:
            Returns a tuple representing the width and height of the Box instance.

        get_pos(anchor: str | None = None) -> tuple[int|float]:
            Returns the position based on anchor. Default is top-left corner ('lt').

        with_size(width, height) -> Box:
            Creates a new Box instance with the specified size while maintaining the current position.

        with_pos(left, top) -> Box: 
            Creates a new Box instance at the specified (left, top) coordinates while maintaining the current size.

        moved_to(x, y=None, anchor=None) -> Box:
            Moves the box to the specified x and y coordinates based on the provided anchor point. If an anchor
            is not given, it defaults to moving based on the top-left corner ('lt').

        moved_by(dx, dy) -> Box:
            Returns a new Box instance that has been shifted by dx in the horizontal direction and dy in the vertical direction.

        centered_in(container_box) -> Box:
            Centers this Box within the provided container box while maintaining its size.

        shrunken(dx: float, dy: float) -> Box:
            Creates a new Box instance with reduced width and height by moving its edges inward.

    Usage example:
        >>> my_box = Box(10, 20, 30, 40)
        >>> print(my_box.left)
        10
        >>> print(my_box.width)
        20
    """
    def __new__(cls, left, top=None, right=None, bottom=None):
        if isinstance(left,tuple) and len(left)==4:
            left, top, right, bottom = left[0], left[1], left[2], left[3]
        return super(Box, cls).__new__(cls, (left, top, right, bottom))

    @classmethod
    def bounding_for_text(cls, text: str, font: ImageFont):
        return cls( font.getbbox(text) )

    @classmethod
    def multiline_textbbox(cls,
                           draw   : ImageDraw,
                           xy     : tuple[float, float],
                           text   : str,
                           font   : ImageFont,
                           anchor : str | None = None,
                           spacing: float      = 4,
                           align  : str        = "left"
                           ):
        return cls( draw.multiline_textbbox( xy, text, font=font, anchor=anchor, spacing=spacing, align=align ) )

    @classmethod
    def container_for_text(cls, text: str, font):
        ascent, descent = font.getmetrics()
        return cls( 0,0, font.getlength(text), ascent+descent )


    @property
    def left(self):
        return self[0]

    @property
    def top(self):
        return self[1]

    @property
    def right(self):
        return self[2]

    @property
    def bottom(self):
        return self[3]

    @property
    def width(self):
        return self[2] - self[0]

    @property
    def height(self):
        return self[3] - self[1]

    @property
    def center(self):
        return (self[0] + self[2])/2

    def get_size(self):
        """Returns the width and height of the box."""
        width = self.right - self.left
        height = self.bottom - self.top
        return width, height

    def get_pos(self, anchor=None):
        """Returns the position of the box based on the specified anchor.
        Args:
            anchor (str, optional): The anchor point to use. Valid values are:
                - 'lt':  Top-left corner (default).
                - 'rb':  Bottom-right corner.
                - 'rt':  Top-right corner.
                - 'lb':  Bottom-left corner.
        Returns:
            A Box containing the x and y coordinates of the specified anchor point.
        """
        if anchor is None or anchor == 'lt':
            return self.left, self.top
        elif anchor == 'rb':
            return self.right, self.bottom
        elif anchor == 'rt':
            return self.right, self.top
        elif anchor == 'lb':
            return self.left, self.bottom
        else:
            raise ValueError(f"Invalid anchor: {anchor}. Valid anchors are: 'lt', 'rb', 'rt', 'lb'.")

    def with_size(self, width, height):
        """Returns a new Box with the specified size."""
        return Box(self.left, self.top, self.left + width, self.top + height)

    def with_pos(self, left, top):
        """Returns a new Box with the specified top-left position."""
        width, height = self.get_size()
        return Box(left, top, left + width, top + height)

    def moved_to(self, x, y=None, anchor=None ):
        if isinstance(x,tuple) and len(x)>=2:
            x, y = x[0], x[1]
        currx, curry = self.get_pos(anchor)
        return self.moved_by( x-currx, y-curry)

    def moved_by(self, dx, dy):
        """Returns a new Box moved by (dx, dy)."""
        return Box(self.left + dx, self.top + dy, self.right + dx, self.bottom + dy)

    def centered_in(self, container_box):
        """Returns a new Box with the same size but centered within the provided container box."""
        offset_x = (container_box.left + container_box.right  - self.left - self.right )/2
        offset_y = (container_box.top  + container_box.bottom - self.top  - self.bottom)/2
        return self.moved_by(offset_x, offset_y)

    def shrunken(self, dx: float, dy: float) -> 'Box':
        """Returns a new Box with reduced size by moving its edges inward.
        Args:
            dx (float): The number of pixels to move the left and right edges.
            dy (float): The number of pixels to move the top and bottom edges.
        Returns:
            A new Box with the specified size after shrinking.
        """
        return Box(self.left + dx, self.top + dy, self.right - dx, self.bottom - dy)

    def __repr__(self):
        return f"Box(left={self.left}, top={self.top}, right={self.right}, bottom={self.bottom})"


#------------------------ COMPLEX DRAWING FUNCTIONS ------------------------#

def wrap_text(text: str, font: ImageFont, width: int) -> tuple[list[str], float]:
    """Splits text into lines that fit within the given width.

    Args:
        text      (str) : The input text to be split.
        font (ImageFont): Font used for rendering the text.
        width     (int) : Maximum width in pixels that each line of text can occupy.

    Returns:
        A list of lines (strings)
        and the percentage length of the last line.
    """
    words = text.split()
    lines = []
    current_line = ""
    for i, word in enumerate(words):
        test_line = f"{current_line} {word}" if i>0 else word
        if font.getlength(test_line) <= width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    last_line_percent = 100.0 * len(lines[-1]) / len(lines[0])
    return lines, last_line_percent


def add_borders(image : Image,
                left  : int,
                top   : int,
                right : int,
                bottom: int,
                border_color: tuple[int, int, int] | str
                ) -> Image:
    """Expand the image by adding borders on all sides.

    This function takes an image and expands it by adding specified borders on
    each side with a given color. The size of the new image will be expanded
    based on the provided left, top, right, and bottom values.

    Args:
        image (Image): The original image to which borders are added.
        left   (int) : Number of pixels to add to the left side of the image.
        top    (int) : Number of pixels to add to the top side of the image.
        right  (int) : Number of pixels to add to the right side of the image.
        bottom (int) : Number of pixels to add to the bottom side of the image.
        border_color (tuple or str): The color for the borders, specified as a tuple
            (R, G, B) where R, G, and B are integers in the range [0, 255],
            or as a string representing the color name ("red", "blue", etc.).

    Returns:
        The image with expanded borders.
    """
    width, height = image.size

    # create a new blank image with the expanded size including borders
    new_width  = width  + left + right
    new_height = height + top  + bottom
    new_image  = Image.new(image.mode, (new_width, new_height), color=border_color)

    # paste the original image onto the new image at the correct offset
    new_image.paste(image, (left, top))
    return new_image


def write_text_in_box(image  : Image,
                      box    : Box,
                      text   : str,
                      font   : ImageFont,
                      spacing: float = 4,
                      align  : str  = 'left',
                      color  : str  = 'black',
                      force  : bool = False
                      ) -> bool:
    """Attempts to write a given text within the rectangle defined by the Box object.

    This function only writes the text if it fits completely within the box.

    Args:
        image    (Image): The image object where the text will be written.
        box       (Box) : The bounding box specifying the region in the image where the text should be placed.
        text      (str) : The text string to be written.
        font (ImageFont): The font object used for rendering the text.
        align     (str) : Alignment of the text within the box ('left', 'center' or 'right').
        color     (str) : Color to use for the text.
        force     (bool): If True, writes the text even if it doesn't fit completely inside
                          the box; default is False.
    Returns:
        True if the text was written successfully, False otherwise.
    """
    draw = ImageDraw.Draw(image)

    # split the text into lines within the box width and adjust the box size
    # dynamically to prevent excessively short final line (ensuring last_line>35%)
    for i in range(1, 10):
        lines, last_line_percent = wrap_text( text, font, box.width )
        if last_line_percent > 35  or  box.width < 300:
            break
        box = box.shrunken(20,0)

    # join all lines with newline characters
    text = '\n'.join(lines)

    # set the appropriate position based on alignment
    if align == 'center':
        x, y   = box.center, box.top
        anchor = 'ma'
    elif align == 'right':
        x, y   = box.right, box.top
        anchor = 'ra'
    else:
        align  = 'left'
        x, y   = box.left, box.top
        anchor = 'la'

    textbbox = Box.multiline_textbbox( draw, (0,0), text, font=font, anchor=anchor, spacing=spacing, align=align )
    top_offset = textbbox.top
    _, descent = font.getmetrics()

    textbbox = textbbox.centered_in( box )
    y = textbbox.top - top_offset + (descent/4)

    ## debug rectangles
    #draw.rectangle( box, fill='red' )
    #draw.rectangle( textbbox, fill='yellow')

    if force or textbbox.top >= box.top:
        draw.multiline_text( (x,y), text, font=font, anchor=anchor, spacing=spacing, align=align, fill=color)
        return True
    else:
        return False


def draw_text_label(image  : Image,
                    width  : int,
                    height : int,
                    text   : str,
                    color  : str,
                    font   : ImageFont,
                    ) -> Image:
    """Draws a rectangle containing the given text in the specified image.

    Args:
        image    (Image) : The original image to be labeled.
        width     (int)  : The width of the label rectangle.
        height    (int)  : The height of the label rectangle.
        text      (str)  : The text to be displayed in the label.
        color     (str)  : The color of the text.
        font  (ImageFont): The font used for rendering the text.
    Returns:
        PIL.Image: The image with the label added.
    """
    image_width, image_height = image.size
    unit   = Box.container_for_text('m', font).width
    margin = 1 * unit # minimum margin between the border and the text

    draw = ImageDraw.Draw(image)

    # calculate the space occupied by the text
    text_box   = Box.container_for_text(text, font)
    min_width  = text_box.width  + margin
    min_height = text_box.height + margin/2

    if width < min_width:
        width = min_width
    if height < min_height:
        height = min_height

    ## adjust the size of the rectangle to contain the two words
    #minimum_width = margin + total_box.width + margin
    #if width < minimum_width:
    #    width = minimum_width

    # draw the white rectangle
    radius    = height/3 # radius of the rectangle's corner
    whitebox1 = Box(0,0,width,height).moved_to( (image_width, image_height), anchor='rb' )
    whitebox2 = whitebox1.moved_by(-radius,radius).with_size( radius, whitebox1.height-radius )
    circlebox = whitebox1.moved_by(-radius,0).with_size( radius*2, radius*2 )
    draw.rectangle(whitebox1, fill="white")
    draw.rectangle(whitebox2, fill="white")
    draw.ellipse(  circlebox, fill="white")

    # center both words within the whitebox
    text_box = text_box.centered_in( whitebox1.moved_by(-radius/2,0) )

    # write the words and return the image
    draw.text(text_box, text, fill=color, font=font, anchor='la')
    return image


#------------------------ LABEL RENDERING FUNCTIONS ------------------------#

def get_required_fonts(font_size: int,
                       scale    : float = 1.0
                       ) -> tuple:
    """Loads all the fonts required for rendering text.

    Args:
        font_size (int): The desired base size of the fonts in points.
        scale   (float): A multiplier to adjust the size of the loaded
                         fonts, default is 1.0 which means no scaling.
    Returns:
        A tuple containing two elements:
            - label_font  : The font used to write the label.
            - prompt_fonts: A list of additional fonts in different sizes used to write the prompt.
    """
    script_dir, script_name = os.path.split( os.path.abspath(__file__) )
    font_folder = os.path.splitext(script_name)[0] + "-font"
    font_folder = "fonts"
    font_full_dir = os.path.join(script_dir, font_folder)

    # if the font directory does not exist, return immediately
    if not os.path.exists(font_full_dir):
        return None

    # search through the font directory for TTF files
    opensans_ttf_file   = None
    robotoslab_ttf_file = None
    default_ttf_file    = None
    for filename in os.listdir(font_full_dir):
        filename_lower = filename.lower()
        if not filename_lower.endswith(".ttf"):
            continue
        elif 'opensans' in filename_lower:
              opensans_ttf_file = os.path.join(font_full_dir, filename)
        elif 'robotoslab' in filename_lower:
              robotoslab_ttf_file = os.path.join(font_full_dir, filename)
        elif default_ttf_file is None:
             default_ttf_file = os.path.join(font_full_dir, filename)

    # load the fonts based on what was found
    label_ttf_file   = robotoslab_ttf_file or default_ttf_file
    prompt_ttf_file  = opensans_ttf_file   or default_ttf_file

    label_font   = load_font(label_ttf_file, int(font_size * scale * 1.0) )
    prompt_fonts = [load_font(prompt_ttf_file, size) for size in range(int(font_size * scale * 1.3), 10, -2)]

    select_font_variation(label_font, b'ExtraBold', b'Black', b'Bold')
    for font in prompt_fonts:
        select_font_variation(font, b'Regular', b'Medium')

    return (label_font, prompt_fonts)


def draw_label(image: Image, /,*,
               text : str,
               color: str,
               font : ImageFont,
               scale: float = 1.0
               ) -> Image:
    """Adds a label with text to an existing image.

    Args:
        image    (Image) : The base image to which labels will be added.
        text       (str) : The input text to be written as a label.
        font  (ImageFont): The font object to use for writing the label.
        scale    (float) : A scaling factor that adjusts the size of the label.
    Returns:
        The modified image with the labels added.
    """
    # calculate the label size based on the scale provided
    label_width   = int( DEFAULT_LABEL_WIDTH  * scale )
    label_height  = int( DEFAULT_LABEL_HEIGHT * scale )
    return draw_text_label(image,
                           label_width, label_height,
                           text, color, font
                           )


# def add_prompt_to_image(image : Image,
#                         prompt: str,
#                         fonts : [ImageFont],
#                         scale : float = 1.0
#                         ) -> Image:
#     """Adds a text prompt to the image at the top.
#
#     Args:
#         image      (Image) : The base image to which prompts will be added.
#         prompt      (str)  : The text string containing the prompt to be displayed.
#         fonts ([ImageFont]): A list of fonts in decreasing order of size for
#                              rendering the text. The function will attempt to
#                              use the appropriate font size (not implemented)
#         scale      (float) : A scaling factor that adjusts the size of the prompt.
#     Returns:
#         The modified image with the prompt added.
#     """
#     width, _ = image.size
#     box = Box(0,0, int(width), int(200*scale))
#
#     # add a border on top of the image
#     # and write the prompt inside the defined box area
#     image = add_borders(image, 0, box.height, 0, 0, 'white')
#
#     # va recorriendo todos los fonts hasta que encuentra un font
#     # que hace que el texto entre completo dentro del box
#     for i, font in enumerate(fonts):
#         is_last = ( i == len(fonts)-1 )
#         fit = write_text_in_box(image,
#                                 box.shrunken(16,8),
#                                 prompt,
#                                 font,
#                                 spacing = 0,
#                                 align   = 'center',
#                                 color   = PROMPT_TEXT_COLOR,
#                                 force   = is_last
#                                 )
#         if fit:
#             break
#     return image


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def build_gallery(image_paths : list[str],
                  style_list  : list[str],
                  grid_size   : tuple[int, int],
                  image_scale : float =  1,
                  font_scale  : float =  1,
                  border      : float = 30, # margins around the gallery
                  gap         : float = 24, # separation between images
                  prompt      : str   = "",
                  ) -> tuple[Image.Image, dict]:
    """
    Creates a large image containing multiple PNG images arranged in a grid.

    Args:
        image_paths  (list): List of file paths to PNG images
        grid_size   (tuple): Grid dimensions as (columns, rows)
        scale       (float): Scale factor for the images
    Returns:
        A tuple containing the generated image and its PNG metadata.
    """
    number_of_images = len(image_paths)
    border = int(border * image_scale) # apply scale to border width
    gap    = int(gap    * image_scale) # apply scale to gap between images

    # get the appropriate fonts based on the calculated scale
    label_font, prompt_fonts = get_required_fonts(DEFAULT_FONT_SIZE, scale=font_scale)

    # validate grid size
    if len(grid_size) != 2:
        raise ValueError("grid_size must be a tuple with 2 elements (columns, rows)")
    columns, rows = grid_size
    if columns <= 0 or rows <= 0:
        raise ValueError("Grid dimensions must be positive")

    # determine the size of each cell in the grid
    cell_width  = 0
    cell_height = 0
    for path in image_paths:
        img = Image.open(path) if path and os.path.isfile(path) else None
        if img and img.width > 0 and img.height > 0:
            cell_width  = int(image_scale*img.width )
            cell_height = int(image_scale*img.height)
            break
    if cell_width <= 0 or cell_height <= 0:
        raise ValueError("No valid image found")

    # determine how many full complete rows there are
    number_of_complete_rows = (number_of_images-1) // columns

    # calculate the empty space for missing images at last row
    empty_space_in_last_row = 0
    if number_of_complete_rows < rows:
        _columns_in_last_row = number_of_images - (number_of_complete_rows * columns)
        empty_space_in_last_row = (columns - _columns_in_last_row) * (cell_width+gap)

    # create a big empty black image for the gallery
    gallery_width   = (border*2) + (gap * (columns-1)) + (cell_width  * columns)
    gallery_height  = (border*2) + (gap * (rows   -1)) + (cell_height * rows   )
    gallery_image = Image.new('RGB', (gallery_width, gallery_height), color='black')

    # draw each image in a grid
    metadata = None
    for i, path in enumerate(image_paths):

        # if the image for this style was not found then skip to the next one
        if not path or not os.path.isfile(path):
            continue

        # load image
        # (if it's the first image then also load the PNG metadata)
        img = Image.open(path)
        if not metadata:
            metadata = img.info.items()

        # if the image style is valid, add a label with the name of the style
        if i < len(style_list):
            style_name = style_list[i]
            if style_name.startswith("STYLE:"):
                style_name = style_name[6:]
            style_name = style_name.strip()
            print(f" - {style_name}")
            text_color = get_text_color(style_name, "black")
            img = draw_label(img, text=style_name, color=text_color, font=label_font, scale=1)

        cell_img = img.resize((cell_width, cell_height), Image.LANCZOS)

        # calculate the position of the cell within the grid
        row = i // columns
        col = i %  columns
        xoffset = border + (cell_width +gap)*col
        yoffset = border + (cell_height+gap)*row
        if row >= number_of_complete_rows:
            xoffset += empty_space_in_last_row // 2
        if row >= rows:
            break

        # paste image into the gallery
        gallery_image.paste(cell_img, (xoffset,yoffset) )

    return gallery_image, metadata



def main(args=None, parent_script=None):
    prog = None
    if parent_script:
        prog = parent_script + " " + os.path.basename(__file__).split('.')[0]

    parser = argparse.ArgumentParser(
        prog=prog,
        description="Generate a gallery of style images.",
        formatter_class=argparse.RawTextHelpFormatter
        )
    parser.add_argument('images'              , nargs="+",           help="Image files (or directories containing .png) to include in the gallery")
    parser.add_argument('-s', '--scale'       , type=float,          help="Scaling factor (max 1.0) to scale down the gallery images")
    parser.add_argument('-j', '--jpeg'        , action='store_true', help="Save gallery as JPEG instead of PNG")
    # parser.add_argument('-p', '--write-prompt', action='store_true', help="Display the prompt of the first image in the gallery")
    # parser.add_argument('-t', '--text'        ,                      help="Text to write on the header of the gallery")
    # parser.add_argument('-n', '--no-label'    , action='store_true', help="Prevents labels from being added to any image.")
    # parser.add_argument('-o', '--output-dir'  ,                      help="Directory where builded galleries will be saved")
    # parser.add_argument(      '--prefix'      ,                      help="Prefix for generated gallery files")
    # parser.add_argument(      '--font'        ,                      help="Path to font file")
    # parser.add_argument(      '--font-size'   , type=int,            help="Font size for the label")

    args  = parser.parse_args()

    # default values
    scale              = 0.5
    extension          = '.png'
    valid_input_prefix = 'ZI'

    # change scale if requested by user
    if args.scale:
        scale = 0.01 if args.scale<=0.01 else 1.0 if args.scale>=1.0 else args.scale

    # change extension if requested by user
    if args.jpeg:
        extension = '.jpg'

    # find all images from the provided arguments (files or directories)
    images = []
    for image in args.images:
        if is_valid_png_image(image, valid_input_prefix):
            images.append(image)
        #elif os.path.isdir(image):
        #    images.extend(find_images_in_dir(image, valid_input_prefix))

    if not images:
        fatal_error("No images found.")

    # get the list of styles directly from the workflow
    # and use that to group all images
    style_list     = extract_style_list(images)
    grouped_images = group_images_by_prompt_and_style(images, style_list)

    # generate the gallery image and save it
    gallery_index = 0
    for prompt, image_paths in grouped_images.items():
        print(f"\nPrompt: \"{prompt[:40]}...\"")
        gallery_image, metadata = build_gallery(image_paths,
                                                style_list,
                                                grid_size   = (4,4),
                                                image_scale = scale,
                                                prompt      = prompt
                                                )
        filename=f"gallery{gallery_index}{extension}"
        save_image( filename, gallery_image, metadata, should_make_dirs=False)
        gallery_index += 1


if __name__ == "__main__":
    main()
