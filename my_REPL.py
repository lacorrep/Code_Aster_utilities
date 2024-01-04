import tkinter as tk

def my_repl(first_commands=[]):
    """
    Opens a REPL anywhere.
    """
    
    def clear_console(evt=None):
        console.delete(1.0, 'end-1c')
        write_to_console(">>> ", end="")

    root = tk.Tk()
    root.title("My REPL")
    root.geometry("1000x750")

    root.lastcommand = ""

    console = tk.Text(root, width=250, height=35)
    root.bind("<Control-Key-l>", clear_console)
    root.bind("<Up>", lambda x: restore_last_command())

    label = tk.Label(root, text="Enter a command:")

    inputBox = tk.Text(root, width=250, height=8)
    inputBox.bind("<Return>", lambda x: execute_command(inputBox.get(1.0,'end-1c')))

    button = tk.Button(root, text="Execute", command=lambda: execute_command(inputBox.get(1.0,'end-1c')))

    console.pack(); label.pack(); inputBox.pack(); button.pack()
    inputBox.focus()

    def restore_last_command():
        inputBox.delete(1.0,'end-1c')
        inputBox.insert('end-1c', root.lastcommand)

    def write_to_console(txt, begin="", end="\n"):
        # console["text"] += begin + str(txt) + end
        console.insert('end-1c', begin + str(txt) + end)

    def write_command_in_input(txt, clear=True):
        # Clear inputBox
        if clear:
            inputBox.delete(1.0, 'end-1c')
        inputBox.insert('end-1c', txt)

    def execute_command(command):
        root.lastcommand = command
        # Based on https://dev.to/amal/building-the-python-repl-3468
        write_to_console(command)
        try:
            try:
                printed_result = str(eval(command, globals())) # when this fails, jump to exec
                if printed_result[0] == "{":
                    print("Dictionary detected, inserting new lines at commas.")
                    printed_result = printed_result.replace(", '", ",\n'")
                write_to_console(printed_result, begin="µv> ")
            except:
                out = exec(command, globals()) # add newly created variables to global scope
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
    menu_commands.add_command(label="Display attributes of an object",
        command=lambda: write_command_in_input("dir(obj)"))
    # -----
    menu_commands.add_command(label="Get mesh nodes",
        command=lambda: write_command_in_input("champ.getMesh().getNodes()"))
    # -----
    menu_commands.add_command(label="MAIL_PY()",
        command=lambda: write_command_in_input(
"""from code_aster.MacroCommands.Utils.partition import MAIL_PY # v15
mapy = MAIL_PY()
mapy.FromAster(mesh)
# mapy.cn # coordinates table
# mapy.gno #dict of node groups
# mapy.gma #dict of element groups
# print(dir(mapy))"""))
    # -----
    menu_commands.add_command(label="Get displacements at nodes",
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
    menu_commands.add_command(label="Ramp function from 0 to 1",
        command=lambda: write_command_in_input(
"""# Format is (x1,y1, x2,y2, x3,y3, ...)
ramp = DEFI_FONCTION(NOM_PARA='INST',
            VALE=(0.0,0.0, 1.0,1.0,),);"""))
    # -----
    menu_commands.add_command(label="Extract table",
        command=lambda: write_command_in_input("tab = tab_CONT.EXTR_TABLE().values()"))
    # -----
    menu_commands.add_command(label="Extract field components",
        command=lambda: write_command_in_input(
"""champ = CREA_CHAMP(TYPE_CHAM = 'NOEU_DEPL_R', # see CREA_CHAMP [U4.72.04] §3.9.1
                OPERATION = 'EXTR',
                RESULTAT = result,
                INST = 1.0,
                NOM_CHAM = 'DEPL',)
champ.EXTR_COMP(comp='DX',lgma=[],topo=0).valeurs"""))
    # -----
    menu_commands.add_separator()
    # -----
    menu_commands.add_command(label="Get closest node to given 3D coordinates",
        command=lambda: write_command_in_input(
"""# https://code-aster.org/forum2/viewtopic.php?id=26935
# import numpy as np
# mesh = LIRE_MAILLAGE(...)
cn = np.array( mesh.getCoordinates().getValues() ).reshape((-1,3))
index_closest_node = np.argmin((mail.cn[:,0]-tx)**2+(mail.cn[:,1]-ty)**2+(mail.cn[:,2]-tz)**2)
"""))
    # -----
    menu_commands.add_command(label="Node groupe -> nodes coordinates",
        command=lambda: write_command_in_input(
"""# Coordinates of all nodes in a group of nodes
# mapy is a MAIL_PY object
coords = np.array([ mapy.cn[i,:] for i in mapy.gno['NODEGROUP'] ])
"""))
    # -----
    menu_commands.add_command(label="Node number -> group of connected elements",
        command=lambda: write_command_in_input(
"""# List of all the elements connected to a given node
# mapy is a MAIL_PY object
selected_node = 0
gma = [  index_maille  for index_maille, elt_array in enumerate(mapy.co) if selected_node in elt_array]
"""))
    # -----
    menu_commands.add_command(label="Element group -> nodes coordinates",
        command=lambda: write_command_in_input(
"""# Coordinates of all nodes in a group of elements
# mapy is a MAIL_PY object
coords = mapy.cn[ np.unique([mapy.co[i] for i in mapy.gma['ELEMENTGROUP'] ]), : ]
"""))
    # -----
    menu_commands.add_command(label="Element group -> list of element types",
        command=lambda: write_command_in_input(
"""# Types of element in a group of elements (mapy.gma['groupname'] is a list of element indices)
# mapy is a MAIL_PY object
[ mapy.nom[mapy.tm[elt]] for elt in gma]
"""))
    # -----
    menu_commands.add_separator()
    # -----
    menu_commands.add_command(label="Result -> list of computed fields",
        command=lambda: write_command_in_input(
"""[key for key,val in result.LIST_CHAMPS().items() if len(val)>0]
"""))
    # -----
    menubar.add_cascade(label="Code snippets", menu=menu_commands)


    menubar.add_command(label="Restore last command (↑)", command=restore_last_command, accelerator="UP")
    menubar.add_command(label="Clear outputs (Ctrl+L)", command=clear_console, accelerator="CTRL+L")

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