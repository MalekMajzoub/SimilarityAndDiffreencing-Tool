from tkinter import *
from tkinter import filedialog
from EditDistance import parsedocs
from EditDistance import patchf1f2,patchf2f1

window = Tk()

window.title("Differencing tool and edit script generation")

window.geometry("800x600")

window.resizable(False, False)

window.config(background="white")

label_file_explorer = Label(window,
                            text="Edit Distance, Similarity,  and Edit Script Generator",
                            width=115,
                            height=4,
                            fg="black",
                            bg="#03f4fc",
                            justify=CENTER)

label_distance = Label(window,
                       text="Distance: Not Calculated",
                       width=115,
                       height=4,
                       justify=CENTER)

label_sim = Label(window,
                  text="Similarity: Not Calculated",
                  width=115,
                  height=4,
                  justify=CENTER)


inputPath = []
patchPath = []
def browseFiles():
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("XML files", "*.xml*")
                                                     , ("all files", "*.*")))
    label_file_explorer.configure(text="File Opened")
    inputPath.append(filename)
    if len(inputPath) == 1:
        button_file1.configure(state=DISABLED)
    if len(inputPath) == 2:
        button_file2.configure(state=DISABLED)
button_file1 = Button(window,
                      text="Get xml file 1",
                      command=browseFiles,
                      )
button_file2 = Button(window,
                      text="Get xml file 2",
                      command=browseFiles
                      )
def calculation():
    dist, sim = parsedocs(inputPath[0], inputPath[1])
    for path in inputPath:
        patchPath.append(path)
    for path in patchPath:
        inputPath.remove(path)
    button_file1.configure(state=NORMAL)
    button_file2.configure(state=NORMAL)
    print(inputPath)
    label_distance.configure(text="Distance: " + str(dist))
    label_sim.configure(text="Similarity: " + str(sim))

def patchingf1f2():
    patchf1f2("editscript.xml", patchPath[0], patchPath[1])
    patchPath.clear()
def patchingf2f1():
    patchf2f1("editscript.xml", patchPath[0], patchPath[1])
    patchPath.clear()

button_patch1=Button(window,
                      text="Patch XML file 1 to 2",
                      command=patchingf1f2)
button_patch2=Button(window,
                      text="Patch XML file 2 to 1",
                      command=patchingf2f1)

button_calculate = Button(window,
                      text="Calculate Dist and Sim",
                      command=calculation)

label_file_explorer.grid(column=1, pady=10, row=1)
button_file1.grid(column=1, pady=10, row=2)
button_file2.grid(column=1, pady=10, row=3)
button_calculate.grid(column=1, pady=10, row=4)
label_distance.grid(column=1, pady=10, row=5)
label_sim.grid(column=1, pady=10, row=6)
button_patch1.grid(column=1, pady=10, row=7)
button_patch2.grid(column=1, pady=10, row=8)

window.mainloop()
