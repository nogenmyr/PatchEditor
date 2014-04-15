PatchEditor
===========

A Blender addon to edit OpenFOAM mesh patches.

Short usage on a test case:

1. Take a tutorial
```
   cp -r $FOAM_TUTORIALS/mesh/snappyHexMesh/flange/ $FOAM_RUN
   run
   cd flane
   ./Allrun
   foamToSurface test.obj
```
2. Put PatchEditor so that Blender sees it:
```
   cd your_blenderpath
   cd 2.70/scripts/addons
   git clone https://github.com/nogenmyr/PatchEditor
```
   
3. Enable PatchEditor in Blender (User prefs. OpenFOAM category).

4. Locate the Addons User Interface in Object Properties Panel.

5. Click Import Patches and locate the test.obj and open it.

6. Click Setup initial patches to assign all faces to the correct patch. 

7. Find out which face in your OpenFOAM mesh that is the first boundary face. This is the "startFace" of the first patch in polyMesh/boundary. Put this number in the "1st BC face" in the User Interface.

8. Edit the faces patch belonging as you like. You may also introduce new patches. This is similar as in the Swift-tools.

9. When done, click "Write". The File select dialog should open in your case' system folder. Put the createPatchDict there. A file named "batchFile" will be created in the case directory.

10. Create faceSets which describes the new patch layout by running
```
    setSet -batch batchFile
```
    in the case directory
    
11. Create the new patches using the faceSets by running:
```
    createPatch
    or
    createPatch -overwrite
```
    
12. The mesh will now conform to the changes you did in Blender


Note: Tested in Blender 2.70 and OpenFOAM 2.2
