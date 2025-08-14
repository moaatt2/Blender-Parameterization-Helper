
import tkinter
from tkinter import ttk


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
ttk.Button(main_frame, text="Parameterize Code - Save to Clipboard").pack(side="bottom", fill="x", padx=5, pady=5)
ttk.Button(main_frame, text="Parameterize Code - Replace Text Box").pack(side="bottom", fill="x", padx=5, pady=5)
ttk.Separator(main_frame, orient="horizontal").pack(side="bottom", fill="x", pady=5)

# Add label
label = tkinter.Label(main_frame, text="Code Entry Box:")
label.config(font=("Arial", 12, "bold"))
label.pack(pady=5)

# Add textbox
code_entry = tkinter.Text(main_frame)
code_entry.pack(side="top", padx=5, fill="both", expand=True)


############################
### Start Tkinter Window ###
############################

window.mainloop()
