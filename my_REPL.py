import tkinter as tk

def my_repl(first_commands=[], LOCAL_VARIABLES=None):
    """
    Opens a REPL anywhere.
    Usage: my_repl(["# Opening a REPL!", "a=1", "print(a)"], locals())
    """
    
    def clear_console(evt=None):
        console.delete(1.0, 'end-1c')
        write_to_console(">>> ", end="")

    def close_window():
        root.destroy()

    root = tk.Tk()
    root.title("My REPL")
    root.geometry("1000x750")

    root.history = [""]
    root.history_index = -1

    console = tk.Text(root, width=250, height=35)
    root.bind("<Control-Key-l>", clear_console)
    root.bind("<Up>", lambda x: restore_last_command(-1))
    root.bind("<Down>", lambda x: restore_last_command(1))
    # Close window
    root.bind("<Escape>", lambda x: close_window())
    root.bind("<Control-Key-w>", lambda x: close_window())

    label = tk.Label(root, text="Enter commands:")

    inputBox = tk.Text(root, width=250, height=8)
    inputBox.bind("<Return>", lambda x: execute_command(inputBox.get(1.0,'end-1c')))

    button = tk.Button(root, text="Execute", command=lambda: execute_command(inputBox.get(1.0,'end-1c')))

    console.pack(); label.pack(); inputBox.pack(); button.pack()
    inputBox.focus()

    def restore_last_command(increment=-1):
        if (increment < 0 and root.history_index > 0) or \
           (increment > 0 and root.history_index < len(root.history)-1):
            root.history_index += increment
            inputBox.delete(1.0, 'end-1c')
            inputBox.insert('end-1c', root.history[root.history_index])

    def write_to_console(txt, begin="", end="\n"):
        # console["text"] += begin + str(txt) + end
        console.insert('end-1c', begin + str(txt) + end)

    def write_command_in_input(txt, clear=True):
        # Clear inputBox
        if clear:
            inputBox.delete(1.0, 'end-1c')
        inputBox.insert('end-1c', txt)

    def execute_command(command):
        root.history.insert(-1, command ) # insert before the last element ("")
        root.history_index = len(root.history)-1

        # Based on https://dev.to/amal/building-the-python-repl-3468
        write_to_console(command)
        try:
            try:
                printed_result = str(eval(command, globals(), LOCAL_VARIABLES)) # when this fails, jump to exec
                if printed_result[0] == "{":
                    print("Dictionary detected, inserting new lines at commas.")
                    printed_result = printed_result.replace(", '", ",\n'")
                write_to_console(printed_result, begin="µv> ")
            except:
                out = exec(command, globals(), LOCAL_VARIABLES) # add newly created variables to global scope
                if out != None:
                    write_to_console(out, begin="µX> ")
                # else:
                #     write_to_console("None") # happens in assignments
        except Exception as exc:
            write_to_console(f"µ Error: '{exc}'")

        # Scroll to bottom
        console.see('end-1c')

        # Clear inputBox
        inputBox.delete(1.0, 'end-1c')
        write_to_console(">>> ", end="")

        return 'break'

    # Menu bar

    menubar = tk.Menu(root)
    root.config(menu=menubar)

    menu_commands = tk.Menu(menubar, tearoff=False)

    # -----
    menu_commands.add_command(label="Display attributes and methods of an object",
        command=lambda: write_command_in_input("dir(obj)"))
    # -----
    menu_commands.add_command(label="Result -> show list of computed fields",
        command=lambda: write_command_in_input(
"""[key for key,val in result.LIST_CHAMPS().items() if len(val)>0]
"""))
    # -----
    menu_commands.add_separator()
    # -----
    menu_commands.add_command(label="Continue script even if solver failed to converge (to be tested)",
        command=lambda: write_command_in_input(
"""try:
    STAT_NON_LINE(...)
except:
    print("An error occured in STAT_NON_LINE, but successfull steps are saved.")
"""))
    # -----
    menu_commands.add_command(label="Get mesh nodes IDs from field",
        command=lambda: write_command_in_input("champ.getMesh().getNodes()")) # ?
    # -----
    menu_commands.add_command(label="Ramp function from 0 to 1",
        command=lambda: write_command_in_input(
"""# Format is (x1,y1, x2,y2, x3,y3, ...)
ramp = DEFI_FONCTION(NOM_PARA='INST',
            VALE=(0.0,0.0, 1.0,1.0,),);"""))
    # -----
    menu_commands.add_command(label="Extract table",
        command=lambda: write_command_in_input("tab = tab_CONT.EXTR_TABLE().values()"))
    # -----
    menu_commands.add_separator()
    # -----
    menu_commands.add_command(label="MAIL_PY() (DEPRECATED)",
        command=lambda: write_command_in_input(
"""from code_aster.MacroCommands.Utils.partition import MAIL_PY # v15
mp = MAIL_PY()
mp.FromAster(mesh)
# mp.cn # coordinates table
# mp.co # connectivity table
# mp.gno # dict of node groups
# mp.gma # dict of element groups
# print(dir(mp))"""))
    # -----
    menu_commands.add_command(label="Get displacements at nodes (before v16)",
        command=lambda: write_command_in_input(
"""displacement_field = CREA_CHAMP(RESULTAT=result,
        OPERATION='EXTR',
        NOM_CHAM='DEPL', TYPE_CHAM='NOEU_DEPL_R',
        INST=t, # specify time here
)
DX = displacement_field.EXTR_COMP('DX').valeurs
DY = displacement_field.EXTR_COMP('DY').valeurs
DZ = displacement_field.EXTR_COMP('DZ').valeurs"""))
    # -----
    menu_commands.add_command(label="Get displacements at nodes (from v16)",
        command=lambda: write_command_in_input(
"""field = CREA_CHAMP(RESULTAT=result,
        OPERATION='EXTR',
        NOM_CHAM='DEPL', TYPE_CHAM='NOEU_DEPL_R',
        INST=t, # specify time here
)
DX = np.asarray(field.getValuesWithDescription('DX')[0])
DY = np.asarray(field.getValuesWithDescription('DY')[0])
DZ = np.asarray(field.getValuesWithDescription('DZ')[0])"""))
    # -----
    menu_commands.add_command(label="Get closest node to given 3D coordinates",
        command=lambda: write_command_in_input(
"""# import numpy as np
# mesh = LIRE_MAILLAGE(...)
cn = np.asarray( mesh.getCoordinates().getValues() ).reshape((-1,3))
tx,ty,tz = 0,0,0 # target position
index_closest_node = np.argmin((cn[:,0]-tx)**2+(cn[:,1]-ty)**2+(cn[:,2]-tz)**2)
position = cn[index_closest_node, :]
"""))
    # -----
    menu_commands.add_command(label="Node groupe -> all nodes coordinates",
        command=lambda: write_command_in_input(
"""# Coordinates of all nodes in a group of nodes
# mp is a MAIL_PY object
coords = mp.cn[ mp.gno['NODEGROUP'], : ]
"""))
# coords = np.asarray([ mp.cn[i,:] for i in mp.gno['NODEGROUP'] ])
    # -----
    menu_commands.add_command(label="Node number -> group of connected elements",
        command=lambda: write_command_in_input(
"""# List of all the elements connected to a given node
# mp is a MAIL_PY object
selected_node = 0
gma = [  index_maille  for index_maille, elt_array in enumerate(mp.co) if selected_node in elt_array]
"""))
    # -----
    menu_commands.add_command(label="Element group -> nodes coordinates",
        command=lambda: write_command_in_input(
"""# Coordinates of all nodes in a group of elements
# mp is a MAIL_PY object
coords = mp.cn[ np.unique([ mp.co[i] for i in mp.gma['ELEMENTGROUP'] ]), : ]
"""))
    # -----
    menu_commands.add_command(label="Element group -> list of element types",
        command=lambda: write_command_in_input(
"""# Types of element in a group of elements (mp.gma['groupname'] is a list of element indices)
# mp is a MAIL_PY object
[ mp.nom[mp.tm[elt]] for elt in gma]
"""))
    # -----
    menu_commands.add_separator()
    # -----
    menu_commands.add_command(label="Get indices of all nodes in a GROUP_MA",
        command=lambda: write_command_in_input(
"""# mp is a MAIL_PY object
indices_of_nodes_on_face = np.unique([ mp.co[i] for i in mp.gma['GROUP_MA'] ])
# after DEFI_GROUP/CREA_GROUP_NO/TOUT_GROUP_MA:
indices_of_nodes_on_face = mp.gno['GROUP_NO']
# without MAIL_PY
indices_of_nodes_on_face = np.asarray(mesh.getNodes('GROUP_NO'))-1
"""))
    # -----
    menu_commands.add_command(label="Get array of coordinates for all nodes (without MAIL_PY)",
        command=lambda: write_command_in_input("coord_array = np.asarray( mesh.getCoordinates().getValues() ).reshape((-1,3))"))
    # -----
    menu_commands.add_command(label="Get array of coordinates for nodes in node group (without MAIL_PY)",
        command=lambda: write_command_in_input(
"""coord_array = np.asarray( mesh.getCoordinates().getValues() ).reshape((-1,3))
coord_group = coord_array[ mesh.getNodes('NODE_GROUP_NAME'), : ]"""))
    # -----
    menu_commands.add_separator()
    # -----
    menu_commands.add_command(label="Install matplotlib",
        command=lambda: write_command_in_input(
"""try:
    import matplotlib
    print("Matplotlib is already installed!")
except ModuleNotFoundError:
    import subprocess
    import sys
    # # Check NumPy version
    # subprocess.check_call([sys.executable, "-m", "pip", "list"])
    # # Upgrade pip (may work without this step, I haven't tried)
    # subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    # Install matplotlib 3.4 for compatibility with NumPy 1.16
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib==3.4"])
except Exception as exc:
    print("Unexpected error", exc)

# /!\\ Always change the backend after importing matplotlib:
# matplotlib.use('TkAgg')
"""))
    # -----
    menubar.add_cascade(label="Code snippets", menu=menu_commands)


    menubar.add_command(label="Edit previous command (Up)", command=restore_last_command, accelerator="UP")
    menubar.add_command(label="\"try: except:\"", command=lambda:write_command_in_input("try:\n\t\nexcept Exception as e:\n\tprint(e)")) # avoid raise
    menubar.add_command(label="Clear outputs (Ctrl+L)", command=clear_console, accelerator="CTRL+L")
    menubar.add_command(label="Info", command=lambda: write_to_console("\n\nSimple REPL for Code_Aster\nUse this REPL to experiment and try out new things.\nOriginal code: github.com/lacorrep\n"))

    # Start REPL

    # Execute all commands in first_commands
    write_to_console(">>> ", end="")
    if type(first_commands) is str:
        execute_command(first_commands)
    elif type(first_commands) is list:
        for c in first_commands:
            execute_command(c)
    else:
        raise TypeError

    root.mainloop()



# if __name__ == '__main__':
#     my_repl(["# Start", "1+1"])