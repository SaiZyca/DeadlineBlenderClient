#
#Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function
bl_info = {
    "name": "Submit Blender To Deadline",
    "description": "Submit a Blender job to Deadline",
    "author": "Thinkbox Software Inc",
    "version": (1,0),
    "blender" : (2, 80, 0),
    "category": "Render",
    "location": "Render > Submit To Deadline",
    }

import bpy
import os
import sys

import subprocess

def GetDeadlineCommand():
    deadlineBin = ""
    try:
        deadlineBin = os.environ['DEADLINE_PATH']
    except KeyError:
        #if the error is a key error it means that DEADLINE_PATH is not set. however Deadline command may be in the PATH or on OSX it could be in the file /Users/Shared/Thinkbox/DEADLINE_PATH
        pass
        
    # On OSX, we look for the DEADLINE_PATH file if the environment variable does not exist.
    if deadlineBin == "" and  os.path.exists( "/Users/Shared/Thinkbox/DEADLINE_PATH" ):
        with open( "/Users/Shared/Thinkbox/DEADLINE_PATH" ) as f:
            deadlineBin = f.read().strip()

    deadlineCommand = os.path.join(deadlineBin, "deadlinecommand")
    
    return deadlineCommand

def GetRepositoryPath(subdir = None):
    deadlineCommand = GetDeadlineCommand()
    
    startupinfo = None
    #if os.name == 'nt':
    #   startupinfo = subprocess.STARTUPINFO()
    #   startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    args = [deadlineCommand, "-GetRepositoryPath "]   
    if subdir != None and subdir != "":
        args.append(subdir)
    
    # Specifying PIPE for all handles to workaround a Python bug on Windows. The unused handles are then closed immediatley afterwards.
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)

    proc.stdin.close()
    proc.stderr.close()

    output = proc.stdout.read()

    path = output.decode("utf_8")
    path = path.replace("\r","").replace("\n","").replace("\\","/")

    return path

class SubmitToDeadline_Operator (bpy.types.Operator):
    bl_idname = "ops.submit_blender_to_deadline"
    bl_label = "Submit Blender To Deadline"
    
    def execute( self, context ):
        # Get the repository path
        path = GetRepositoryPath("submission/Blender/Main")
        if path != "":            
            # Add the path to the system path
            if path not in sys.path :
                print( "Appending \"%s\" to system path to import SubmitBlenderToDeadline module" % path )
                sys.path.append( path )
            else:
                print( "\"%s\" is already in the system path" % path )

            
            # Import the script and call the main() function
            import SubmitBlenderToDeadline
            SubmitBlenderToDeadline.main( )
        else:
            print( "The SubmitBlenderToDeadline.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine, that the Deadline Client bin folder is set in the DEADLINE_PATH environment variable, and that the Deadline Client has been configured to point to a valid Repository." )
        
        return {'FINISHED'}


    
def deadline_submit_button( self, context ):
    self.layout.separator()
    self.layout.operator( SubmitToDeadline_Operator.bl_idname, text="Submit To Deadline" )
    
classes = (
    SubmitToDeadline_Operator,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
    bpy.types.TOPBAR_MT_render.append( deadline_submit_button )

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
    bpy.types.TOPBAR_MT_render.remove( deadline_submit_button )

if __name__ == "__main__":
    register()
    
