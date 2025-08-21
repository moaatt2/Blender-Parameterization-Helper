
# GUI Libraries
import tkinter
from tkinter import ttk
from playsound3 import playsound

# User clipboard interaction
import pyperclip


#################
### Functions ###
#################

# parameterize given code
def parameterize_blender_code(code: str) -> str:
    """This function takes in rough blender modeling code and returns code that adds sliders.

    Args:
        code (str): Your starting rough model code.

    Returns:
        str: The updated model code in a framework to add a custom menu to blender where you can tweak the parameters.
    """

    ################################
    ### Split code into sections ###
    ################################

    # Set up section containers
    section_mapping = {
        "Imports":   "",
        "Parameters": "",
        "Model Code": "",
    }

    # Itterate over lines and split into sections
    current_section = None
    for line in code.split('\n'):

        # Check for section headers
        if ("### " in line) and (" ###" in line):
            current_section = line.replace("#","").strip()

        # Itterate over lines in a target section
        if current_section in section_mapping:

            # Skip useless lines
            if line.strip() == "": continue # empty lines
            if line.startswith("#"): continue # comments

            # Add line to the current section
            section_mapping[current_section] += line + "\n"


    ########################
    ### Parse Parameters ###
    ########################

    # Itterate over lines and parse paraemters
    parameters = dict()
    for line in section_mapping["Parameters"].split('\n'):

        # Determine if line is a parameter
        if "=" in line:

            # Get Values from lines
            split_vals = line.split("=")
            name, value = map(str.strip, split_vals)

            # Check type of value
            value_type = None
            if '"' in  value or "'" in value:
                value_type = "str"
            elif value.replace('.', '', 1).isdigit():
                value_type = "number"
            elif "radians" in value:
                value_type = "angle"
                value = value.replace("radians(", "").replace(")", "").replace("math.", "").strip()
                value = f"{value}/180 * math.pi"  # Convert to radians
            else:
                value_type = "Unknown"

            parameters[name] = [value, value_type]


    #############################
    ### Add imports to output ###
    #############################

    # Initialze output
    output = """
###############
### Imports ###
###############

"""

    # Check for bpy import
    imports_bpy = False
    for line in section_mapping["Imports"].split('\n'):
        if line.strip() == "import bpy":
            imports_bpy = True

    # Import bpy if not present
    if not imports_bpy:
        section_mapping["Imports"] = "import bpy\n" + section_mapping["Imports"]

    # Check for import of math library
    imports_math = False
    for line in section_mapping["Imports"].split('\n'):
        if line.strip() == "import math":
            imports_math = True

    # Import math if not present
    if not imports_math:
        section_mapping["Imports"] = "import math\n" + section_mapping["Imports"]

    # Add other user defined imports
    output += section_mapping["Imports"] + "\n\n"


    ##################################
    ### Set Weave Name If Provided ###
    ##################################

    weave_name = parameters.get("weave_name")
    if weave_name is not None:
        weave_name = weave_name[0]
        output += "################\n### Settings ###\n################\n\n# Weave Name\n"
        output += f"weave_name = {weave_name}\n\n\n"


    ####################################
    ### Create Model Update Function ###
    ####################################

    # Add section header
    output += "#############################\n### Model Update Function ###\n#############################\n\n"

    # Add function definition
    output += "def update_model(self, context):\n\n"

    # Add clean up section
    output += "\t################\n\t### Clean Up ###\n\t################\n\n"
    output += "\t# Clear Scene - Delete all Objects\n"
    output += "\tbpy.ops.object.select_all(action='DESELECT')\n"
    output += "\tbpy.ops.object.select_by_type(type='MESH')\n"
    output += "\tbpy.ops.object.delete()\n\n"

    # Add Code  header
    output += "\t####################\n\t### Create Rings ###\n\t####################\n\n"

    # Replace parameters in model code with self.<parameter_name>
    model_code = section_mapping["Model Code"]
    for key in parameters:
        model_code = model_code.replace(key, f"self.{key}")

    # Clean up cases where "self.self." could appear (if one parameter name is a substring of another e.g. "angle_1" and "angle_10")
    while "self.self." in model_code:
        model_code = model_code.replace("self.self.", "self.")

    # Prepend tabs and add to output
    for line in model_code.split('\n'):
        output += "\t" + line + "\n"


    ###################################
    ### Define Custom Menu Contents ###
    ###################################

    # Add Section Heading
    output += "\n\n############################\n### Define Menu Contents ###\n############################\n\n"

    # Add class definition
    output += "class ChainmailProperties(bpy.types.PropertyGroup):\n"

    # Add properties for each parameter
    for key, value in parameters.items():
        if key != "weave_name":

            # Create clean name for display
            clean_name = key.replace("_", " ").capitalize()

            # Create property
            output += f"\t{key}: bpy.props.FloatProperty(\n"
            output += f'\t\tname="{clean_name}",\n'
            output += f'\t\tdefault={value[0]},\n'

            # Add specific type handling
            if value[1] == "angle":
                output += '\t\tsubtype="ANGLE",\n'
                output += '\t\tunit="ROTATION",\n'

            # Close out property definition
            output += '\t\tupdate=update_model\n'
            output += "\t)\n"


    #########################################
    ### Create Custom Menu & Add Contents ###
    #########################################

    # Add Section Heading
    output += "\n\n###################\n### Create Menu ###\n###################\n\n"

    # Add class definition
    output += "class VIEW3D_PT_chainmail_panel(bpy.types.Panel):\n"

    # Add weave name
    if "weave_name" in parameters:
        weave_name = parameters["weave_name"][0].replace('"', '').replace("'", "")
        output += f'\tbl_label = "{weave_name} Modification Pannel"\n'
    else:
        output += '\tbl_label = "Chainmail Modification Pannel"\n'

    # Finish class variables
    output += "\tbl_idname = 'VIEW3D_PT_chainmail_ring'\n\tbl_space_type = 'VIEW_3D'\n\tbl_region_type = 'UI'\n\tbl_category = 'Chainmail'\n\n"

    # Add definition of draw function
    output += "\tdef draw(self, context):\n"

    # Add layout & props
    output += "\t\tlayout = self.layout\n"
    output += "\t\tprops = context.scene.chainmail_props\n\n"

    # Add item for each parameter
    for key in parameters:
        if key != "weave_name":
            output += f'\t\tlayout.prop(props, "{key}")\n'

    # Add button to start keyboard controls
    output += "\n\t\tlayout.separator()\n\t\tlayout.operator('wm.chainmail_tweak_modal', text='Keyboard Tweak Mode')\n"


    ################################
    ### Create Keyboard Controls ###
    ################################

    # Add Section Heading
    output += "\n\n################################\n### Create Keyboard Controls ###\n################################\n\n"

    # Add global variable to track selected index
    output += "tweaker_selected_index = 0\n"

    # Add Class Definition
    output += "class ChainmailTweaker(bpy.types.Operator):\n\n"

    output += '\tbl_idname = "wm.chainmail_tweak_modal"\n\tbl_label  = "Chainmail Tweaker (Arrow Keys + Tab)"\n\n'

    # Add variable names
    output += "\tvar_names = [\n"
    for key in parameters:
        if key != "weave_name":
            output += f'\t\t"{key}",\n'
    output += "\t]\n\n"


    ################################
    ### Add remaining fixed code ###
    ################################

    output += """
    def __init__(self):
        global tweaker_selected_index
        self.selected_index = tweaker_selected_index

    def invoke(self, context, event):
        self._area = context.area
        context.window_manager.modal_handler_add(self)
        self.update_display(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global tweaker_selected_index
        
        props = context.scene.chainmail_props

        if event.type == 'ESC':
            self._area.header_text_set(None)
            return {'CANCELLED'}

        if event.type in {'MIDDLEMOUSE', 'RIGHTMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        if event.value == 'PRESS':
            step = 0.10
            if event.shift: step = 1.00
            if event.ctrl:  step = 0.05
            if event.alt:   step = 0.01

            var_name = self.var_names[self.selected_index]

            if event.type == 'TAB':
                if event.shift:
                    self.selected_index = (self.selected_index - 1) % len(self.var_names)
                    tweaker_selected_index = self.selected_index
                    self.update_display(context)
                else:
                    self.selected_index = (self.selected_index + 1) % len(self.var_names)
                    tweaker_selected_index = self.selected_index
                    self.update_display(context)

            elif event.type == 'RIGHT_ARROW':
                self.change_value(props, var_name, step)
                self.update_display(context)

            elif event.type == 'LEFT_ARROW':
                self.change_value(props, var_name, -step)
                self.update_display(context)

        return {'RUNNING_MODAL'}

    def change_value(self, props, var_name, delta):
        current = getattr(props, var_name)
        setattr(props, var_name, current + delta)

    def update_display(self, context):
        props = context.scene.chainmail_props
        var_name = self.var_names[self.selected_index]
        value = getattr(props, var_name)
        self._area.header_text_set(f"Adjusting: {var_name} = {value:.3f}  (←/→ to adjust, Tab to switch, Esc to exit)")


#############################
### Add custom menu to UI ###
#############################

def register():
    bpy.utils.register_class(ChainmailProperties)
    bpy.utils.register_class(VIEW3D_PT_chainmail_panel)
    bpy.utils.register_class(ChainmailTweaker)
    bpy.types.Scene.chainmail_props = bpy.props.PointerProperty(type=ChainmailProperties)

def unregister():
    bpy.utils.unregister_class(ChainmailProperties)
    bpy.utils.unregister_class(VIEW3D_PT_chainmail_panel)
    bpy.utils.unregister_class(ChainmailTweaker)
    del bpy.types.Scene.chainmail_props

if __name__ == "__main__":
    register()
    """.replace("    ", "\t")  # Replace spaces with tabs for consistency

    return output


def parameterize_and_replace():
    # Get raw code from form
    raw_code = code_entry.get("1.0", "end").strip()

    # Create paramterized code & remove excess whitespace
    parameterized_code = parameterize_blender_code(raw_code).strip()

    # Clear Text Entry Area
    code_entry.delete("1.0", "end")

    # Put new code in text entry ares
    code_entry.insert("1.0", parameterized_code)


def parameterize_to_clipboard():
    # Get raw code from form
    raw_code = code_entry.get("1.0", "end").strip()

    # Create paramterized code & remove excess whitespace
    parameterized_code = parameterize_blender_code(raw_code)

    # Copy code to users clipboard
    pyperclip.copy(parameterized_code)

    # Let user know code has been copied
    clipboard_button.configure(text="Saved to Clipboard")
    clipboard_button.configure(state=tkinter.DISABLED)
    code_entry.edit_modified(False)
    playsound("assets/alert.wav")

def reset_button(event):
    if code_entry.edit_modified():
        clipboard_button.configure(text="Parameterize Code - Save to Clipboard")
        clipboard_button.configure(state=tkinter.NORMAL)


#################################
### Initialize Tkinter Window ###
#################################

window = tkinter.Tk()
window.title("Blender Parameterization Helper")
window.geometry("400x400")


##############
### Layout ###
##############

# Create primary fram to hold text entry and button
main_frame = tkinter.Frame(window)
main_frame.pack(expand=True, fill="both")

# Add Lower Half
clipboard_button = ttk.Button(main_frame, text="Parameterize Code - Save to Clipboard", command=parameterize_to_clipboard)
clipboard_button.pack(side="bottom", fill="x", padx=5, pady=5)
ttk.Button(main_frame, text="Parameterize Code - Replace Text Box", command=parameterize_and_replace).pack(side="bottom", fill="x", padx=5, pady=5)
ttk.Separator(main_frame, orient="horizontal").pack(side="bottom", fill="x", pady=5)

# Add label
label = tkinter.Label(main_frame, text="Code Entry Box:")
label.config(font=("Arial", 12, "bold"))
label.pack(pady=5)

# Add textbox
code_entry = tkinter.Text(main_frame)
code_entry.pack(side="top", padx=5, fill="both", expand=True)


######################
### Event Bindings ###
######################

code_entry.bind("<<Modified>>", reset_button)


############################
### Start Tkinter Window ###
############################

window.mainloop()
