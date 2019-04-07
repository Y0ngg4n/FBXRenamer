############################################################################################################
# This Program renames FBX Nodes recursive to ensure correct import from e.g. Mixamo                       #
# It changes for example all '.' and ':' characters to '_'                                                 #
# It uses the FBX Python SDK from Autodesk                                                                 #
# Based on this post: https://www.riggingdojo.com/2017/04/04/guest-post-fbx-file-solutions-python-fbx-sdk/ #
# and based on this gist: https://gist.github.com/Meatplowz/8f408912cf554f2d11085fb68b62d3a3               #
# Python 3.3 needed!                                                                                       #
# Customized FBX Common 'def SaveScene' by changing Parameter 'pEmbedMedia' to True                        #
# Author: Yonggan                                                                                          #
############################################################################################################

import FBX_Scene
import fbx
import os
import shutil


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles


def crawlFiles(dirName):
    # Get the list of all files in directory tree at given path
    listOfFiles = getListOfFiles(dirName)

    # Print the files
    for elem in listOfFiles:
        patharry = os.path.splitext(elem)
        if ".git" not in patharry:
            if patharry[-1] == ".fbx.meta":
                print("Removing: "+ ".".join(patharry))
                os.remove(patharry)
            elif patharry[-1] == ".fbx":
                clean_character_scene(elem)

    print("****************")

    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    # Print the files
    for elem in listOfFiles:
        patharry = os.path.splitext(elem)
        if ".git" not in patharry:
            if patharry[-1] == ".fbx.meta":
                print("Removing: " + ".".join(patharry))
                os.remove(patharry)
            elif patharry[-1] == ".fbx":
                clean_character_scene(elem)


def clean_character_scene(fbx_file):
    """
    Clean up character fbx file
    """

    # open the fbx scenes and get the scene nodes
    fbx_scene = FBX_Scene.FBX_Class(fbx_file)
    if not fbx_scene:
        return False

    remove_names = []
    keep_names = []

    # remove invalid nodes noted by properties assigned in the DCC application
    all_nodes = fbx_scene.get_scene_nodes()
    for node in all_nodes:
        export_property = fbx_scene.get_property(node, 'no_export')
        if export_property:
            property_value = fbx_scene.get_property_value(node, 'no_export')
            if property_value == True:
                node_name = node.GetName()
                fbx_scene.scene.DisconnectSrcObject(node)
                remove_names.append(node_name)
            else:
                node_name = node.GetName()
                keep_names.append(node_name)

    # remove the nodes from the scene by name
    fbx_scene.remove_nodes_by_names(remove_names)

    # remove display layers
    # For some reason these change FbxCollection ID and NodeName
    layer_objs = fbx_scene.get_class_nodes(fbx.FbxCollectionExclusive.ClassId)
    if layer_objs:
        remove_layers(fbx_scene, layer_objs)

    # remove FbxContainers
    nodes = fbx_scene.get_class_nodes(fbx.FbxObject.ClassId)
    if nodes in nodes:
        if node.GetClassId().GetName() == 'FbxContainer':
            # disconnect the layer from the scene
            node.DisconnectAllDstObject()
            node.DisconnectAllSrcObject()
            fbx_scene.scene.RootProperty.DisconnectSrcObject(node)

    # remove display layers
    display_layers = fbx_scene.get_type_nodes(u'DisplayLayer')
    if display_layers:
        remove_layers(fbx_scene, display_layers)

    # save the modified fbx scene
    fbx_scene.save()

    folderpath = os.path.splitext(fbx_file)
    folderpath = folderpath[:-1]
    folderpath = ''.join(repr(i) for i in folderpath)
    folderpath = folderpath[1:-1]
    folderpath = folderpath + ".fbm"
    if os.path.isdir(folderpath):
        shutil.rmtree(folderpath)
    print("Succesfully saved: " + fbx_file)
    return True

print("Starting FBXRenamer...")
crawlFiles(input("Please enter a Directory: "))
print("Finished Renaming :)")
