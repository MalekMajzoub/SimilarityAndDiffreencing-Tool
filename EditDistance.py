import numpy as np
import xml.etree.ElementTree as ET

#Creating the global variables to be used in our application
global EditScript
global labelA
global labelB
global dict_ES
global realES
global editScript
labelA = {}
labelB = {}
dict_ES = {}
realES = []
editScript = {}

# Main method which will call all the the necessary methods to parse files and create their editScript
# Returns Distance and Similarity between the two files
def parsedocs(file1, file2):
    global EditScript
    tree1 = ET.parse(file1)
    tree2 = ET.parse(file2)
    root1 = tree1.getroot()
    root2 = tree2.getroot()
    labelA["A"] = root1
    labelB["B"] = root2
    createDictionaries(root1, root2)
    distance = nier_jaga(root1, root2)
    distance = distance/100
    sim = 1/(1+distance)
    print(dict_ES)
    new_ES = get_ES(dict_ES, "")
    extract_ES(new_ES)
    ES_list_to_dict(realES)
    createXML(editScript)
    return distance, sim
    # patchf2f1("editscript.xml", file1, file2)

# Creating dictionary for each file where the key is the label of the subtree
# and the value is the node
def createDictionaries(root1, root2):
    count1 = 0
    count2 = 0
    lastLabelA = next(reversed(labelA.keys()))
    lastLabelB = next(reversed(labelB.keys()))
    for child1 in root1:
        count1 = count1 + 1
        labelA[lastLabelA + "." + count1.__str__()] = child1
        createDictionaries(child1, "")
    for child2 in root2:
        count2 = count2 + 1
        labelB[lastLabelB + "." + count2.__str__()] = child2
        createDictionaries("", child2)

# Implementing nierman and jagadish algorithm
def nier_jaga(node1, node2):
    global EditScript
    n, m, temp0, temp1 = degree(node1, node2)
    # Base case for the recursive method
    if n == 0 and m == 0:
        # we are comparing individual nodes
        z = calc_update(node1, node2)
        keyA = get_key(labelA, node1)
        keyB = get_key(labelB, node2)
        # adding to the dictionary the update value for the concatenation of keys
        dict_ES[keyA + keyB] = z
        return z

    else:
        # Fill the matrix with zeros
        EDistance = np.zeros(shape=(n + 1, m + 1), dtype=float)
        # We compare the roots of these subtrees
        EDistance[0, 0] = calc_update(node1, node2)
        for i in range(1, n + 1):
            EDistance[i, 0] = EDistance[i - 1, 0] + degree2(node1, i)  # cost of deletion
        for j in range(1, m + 1):
            EDistance[0, j] = EDistance[0, j - 1] + degree2(node2, j)  # cost of insertion
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                deleting = EDistance[i - 1, j] + degree2(node1, i)  # cost of deleting
                inserting = EDistance[i, j - 1] + degree2(node2, j)   # cost of insertion

                updating = EDistance[i - 1, j - 1] + nier_jaga(temp0[i], temp1[j]) # cost of updating

                updating, inserting, deleting = minimum(updating, inserting, deleting)

                # get the minimum between update, insert, and delete costs
                min_operation = np.min([deleting, inserting, updating])
                # set the value of the cell to be the minimum of the operations
                EDistance[i, j] = min_operation

    keyA = get_key(labelA, node1)
    keyB = get_key(labelB, node2)
    dict_ES[keyA + keyB] = EDistance
    Distance = EDistance[n][m] # adding to the dictionary the update value for the concatenation of keys
    return Distance

# Get the first level sub-elements of the nodes provided
def degree(node1, node2):
    count1 = 0
    count2 = 0
    children1 = [node1]
    children2 = [node2]
    for child1 in node1:
        count1 = count1 + 1
        children1.append(child1)
    for child2 in node2:
        count2 = count2 + 1
        children2.append(child2)
    return count1, count2, children1, children2

# Gets number of the children and their respective children of a sub-tree
def degree2(node, index):
    children = []
    count = 1
    if index == "":
        for child in node:
            count = count + degree2(child, "")
    else:
        for child in node:
            children.append(child)
        for child in children[index-1]:
            count = count + degree2(child, "")
    return count

# Calculate the difference between given nodes based on our assumptions
def calc_update(node, node1):
    weight_att = 0.1
    weight_text = 0.4
    weight_tag = 0.5
    weight_structure = 0

    if node.tag == node1.tag:
        weight_tag = weight_tag * 0

    if node.attrib == node1.attrib:
        weight_att = weight_att * 0

    if node.text == node1.text:
        weight_text = weight_text * 0
    # Retrieve number of children under each node to be compared
    countChild1 = degree2(node, "")
    countChild2 = degree2(node1, "")
    if countChild1 == countChild2:
        weight_structure = weight_structure * 0
    # If there is a difference, we compute the difference in the number of children
    # The weight structure will be the computed difference
    else:
        if countChild1 > countChild2:
            temp = countChild1 - countChild2
        else:
            temp = countChild2 - countChild1
        weight_structure = temp
    # Sum the differences and return it
    sum_weights = weight_structure + weight_att + weight_tag + weight_text

    return sum_weights

# If we have equal cost of operations, we set the priority for the update -> insert -> delete
def minimum(number1, number2, number3):
    if (number1 > number2) or (number1 > number3):
        if number2 == number3:
            number3 = 90000
    if (number2 > number1) or (number2 > number3):
        if number1 == number3:
            number3 = 90000
    if (number3 > number1) or (number3 > number2):
        if number1 == number2:
            number2 = 90000
    return number1, number2, number3

# Get the key that has a value of a specific node inside either labelA or labelB
def get_key(dict1, val):
    for key, value in dict1.items():
        if val == value:
            return key

# We are getting the edit script
def get_ES(dict1, key):
    ES = []
    # starting with an empty string gives us the main matrix for AB
    if key == "":
        key = next(reversed(dict1.keys()))
        matrix = dict1.get(key)
    # else if we have the key through a recursive call, we just get the value based on the key
    else:
        matrix = dict1.get(key)
    # get the value of rows and columns to index the labels
    rows = len(matrix) - 1
    columns = len(matrix[0]) - 1
    # while loop that checks we are not at the end of the matrix
    while (columns, rows) != (0, 0):
        # we split the key that we have of the update operation of the two sub-trees we are comparing
        split = key.split('B')
        split[1] = "B" + split[1] + "." + str(columns)  # for insertions
        split[0] = split[0] + "." + str(rows)  # for deleting
        if rows == 0:
            # if i still have columns, I need to insert
            while columns != 0:
                ES.append("insert " + split[1] + " " + split[0])
                columns = columns - 1
        elif columns == 0:
            # if i still have rows, I need to delete
            while rows != 0:
                ES.append("delete " + split[0] + " " + split[1])
                rows = rows - 1
        # else it is still traversing inside the matrix
        else:
            # value to compare with the operations
            value = matrix[rows, columns]

            cost_ins = (matrix[0, columns] - matrix[0, columns - 1]) + matrix[rows, columns - 1]
            cost_del = (matrix[rows, 0] - matrix[rows - 1, 0]) + matrix[rows - 1, columns]

            split = key.split('B')
            split[1] = "B" + split[1] + "." + str(columns)
            split[0] = split[0] + "." + str(rows)

            upd_key = split[0] + "" + split[1]
            # value1 is cost of updating without the previous cell, it is either a matrix or a single value
            value1 = dict1.get(upd_key)

            if isinstance(value1, np.ndarray):
                # if it is a matrix i get the last value and use it to calculate the cost of update
                value1 = get_last_value(value1)
                cost_upd = matrix[rows - 1, columns - 1] + value1
                if cost_upd == value:
                    rows, columns = rows - 1, columns - 1
                    new_ES = get_ES(dict1, upd_key)
                    ES.append(new_ES)
                elif cost_del == value:
                    rows, columns = rows - 1, columns
                    ES.append("delete " + split[0] + " " + split[1])
                elif cost_ins == value:
                    rows, columns = rows, columns - 1
                    ES.append("insert " + split[1] + " " + split[0])
            else:
                cost_upd = matrix[rows - 1, columns - 1] + value1
                if cost_upd == value:
                    if value1 == 0:
                        rows, columns = rows - 1, columns - 1
                    else:
                        rows, columns = rows - 1, columns - 1
                        ES.append("update " + upd_key)
                elif cost_del == value:
                    rows, columns = rows - 1, columns
                    ES.append("delete " + split[0] + " " + split[1])
                elif cost_ins == value:
                    rows, columns = rows, columns - 1
                    ES.append("insert " + split[1] + " " + split[0])

    return ES

# Extracting the ES embedded lists into one list
def extract_ES(list_ES):
    for element in list_ES:
        if isinstance(element, list):
            extract_ES(element)
        else:
            realES.append(element)

# Converting the list that contains the edit script into a dictionary
def ES_list_to_dict(list1):
    for pair in list1:
        split = pair.split()
        if split[0] == "insert":
            editScript[str(split[1] + " " + split[2])] = split[0]
        elif split[0] == "delete":
            editScript[str(split[1] + " " + split[2])] = split[0]
        else:
            editScript[split[1]] = split[0]

# Get the last value of matrix
def get_last_value(matrix):
    value = matrix[-1, -1]
    return value

# Traversing the edit script dictionary and creating the XML file
def createXML(dict1):
    root = ET.Element("EditScript")
    for label, edit in dict1.items():
        temp = ET.SubElement(root, edit)
        temp.text = label
    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write("editscript.xml", encoding="utf-8")

# Patching file1 to file2
def patchf1f2(editscriptXML, file1, file2):
    # Parsing Edit Script XML file
    tree = ET.parse(editscriptXML)
    root = tree.getroot()
    # Parsing files to be patched
    tree1 = ET.parse(file1)
    root1 = tree1.getroot()
    tree2 = ET.parse(file2)
    root2 = tree2.getroot()
    # Traversing the XML file and getting the operations needed
    for node in root:
        # Updating
        if node.tag == "update":
            # Keys that will indicate location of update operation
            edit = node.text
            # split to get the two keys
            split = edit.split('B')
            split[1] = "B" + split[1]
            list1 = split[0].split('.')
            list2 = split[1].split('.')
            # we get the indices of the operation
            list1.pop(0)
            list2.pop(0)
            child1 = None
            child2 = None
            # Traversing the indices and getting the child to update and the child we are updating from
            for i in list1:
                if child1 is None:
                    child1 = get_children(root1, int(i))
                else:
                    child1 = get_children(child1, int(i))
            for j in list2:
                if child2 is None:
                    child2 = get_children(root2, int(j))
                else:
                    child2 = get_children(child2, int(j))
            if child1.text != child2.text:
                child1.text = child2.text
            if child1.tag != child2.tag:
                child1.tag = child2.tag
            if child1.attrib != child2.attrib:
                child1.attrib = child2.attrib
        # Delete
        elif node.tag == "delete":
            edit = node.text
            split = edit.split('.')
            split1 = edit.split()
            split2 = split1[0].split('.')
            split3 = split1[1].split('.')
            split2.pop(0)
            split3.pop(0)
            child1 = None
            child2 = None
            # child1 is the child we want to delete
            for i in split2:
                if child1 is None:
                    child1 = get_children(root1, int(i))
                else:
                    child1 = get_children(child1, int(i))
            # child2 is the node to delete from
            for j in split2[:-1]:
                if child2 is None:
                    child2 = get_children(root1, int(j))
                else:
                    child2 = get_children(child2, int(j))

            child2.remove(child1)
        # insert
        elif node.tag == "insert":
            edit = node.text
            split1 = edit.split()
            split2 = split1[0].split('.')
            split3 = split1[1].split('.')
            split2.pop(0)
            split3.pop(0)

            child2 = None
            child1 = None
            # child2 is the node to be added
            for i in split2:
                if child2 is None:
                    child2 = get_children(root2, int(i))
                else:
                    child2 = get_children(child2, int(i))
            # child 1 is the node we need to add to
            for j in split3[:-1]:
                if child1 is None:
                    child1 = get_children(root1, int(j))
                else:
                    child1 = get_children(child1, int(j))
            # split3[-1] is the index at which we need to add to
            child1.insert(int(split3[-1]) , child2)
    # writing our changes into the original xml file
    tree1.write(file1)

def patchf2f1(editscriptXML, file1, file2):
    tree = ET.parse(editscriptXML)
    root = tree.getroot()
    tree1 = ET.parse(file1)
    root1 = tree1.getroot()
    tree2 = ET.parse(file2)
    root2 = tree2.getroot()
    for node in root:
        if node.tag == "update":
            edit = node.text
            split = edit.split('B')
            split[1] = "B" + split[1]
            list1 = split[0].split('.')
            list2 = split[1].split('.')
            list1.pop(0)
            list2.pop(0)
            child1 = None
            child2 = None
            for i in list1:
                if child1 is None:
                    child1 = get_children(root1, int(i))
                else:
                    child1 = get_children(child1, int(i))
            for j in list2:
                if child2 is None:
                    child2 = get_children(root2, int(j))
                else:
                    child2 = get_children(child2, int(j))
            if child1.text != child2:
                child2.text = child1.text
            if child1.tag != child2.tag:
                child2.tag = child1.tag
            if child1.attrib != child2.attrib:
                child2.attrib = child1.attrib
        elif node.tag == "insert":
            edit = node.text
            split1 = edit.split()
            split2 = split1[0].split('.')
            split3 = split1[1].split('.')
            split2.pop(0)
            split3.pop(0)
            child1 = None
            child2 = None
            for i in split2:
                if child1 is None:
                    child1 = get_children(root2, int(i))
                else:
                    child1 = get_children(child1, int(i))

            for j in split2[:-1]:
                if child2 is None:
                    child2 = get_children(root2, int(j))
                else:
                    child2 = get_children(child2, int(j))

            child2.remove(child1)
        elif node.tag == "delete":
            edit = node.text
            split1 = edit.split()
            split2 = split1[0].split('.')
            split3 = split1[1].split('.')
            split2.pop(0)
            split3.pop(0)

            child2 = None
            child1 = None
            for i in split2:
                if child2 is None:
                    child2 = get_children(root1, int(i))
                else:
                    child2 = get_children(child2, int(i))
            for j in split3[:-1]:
                if child1 is None:
                    child1 = get_children(root2, int(j))
                else:
                    child1 = get_children(child1, int(j))
            child1.insert(int(split3[-1]), child2)

    tree2.write(file2)

# get all children and sub-children under a certain node
def get_children(node, index):
    count1 = 0
    for child in node:
        # index =  means that there are no children under this node
        if index == 0:
            return node
        # else access each child and get their respective children
        elif count1 == (index-1):
            return child
        # return number of children + root
        count1 = count1 +1

