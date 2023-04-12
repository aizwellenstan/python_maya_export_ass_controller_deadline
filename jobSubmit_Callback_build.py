#!/usr/bin/python
import maya.cmds as cmds
import logging, os, re, json, functools
import os, sys
import json
import optparse
import maya.mel as mel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mocap_utils')

def job_CallBack(fileName, startTime, endTime):
    name = fileName.split("/")[-1]
    name = name.split(".ma")[0]

    job_Base = {
        "cluster"    : "/comp/nuke/nuke_a",
        "groups"     : "nuke",
        "hosts"      : "",
        "omitgroups" : "",
        "omithosts"  : "",
        "priority"   : 4000,
        "reservations" : "host.processors=1+",
    }
    # == Job Bake ==
    job_buildScene = {
        "name"      : "vd2_bake_ASS_%s" % name,
        "label"     : "callbackBack%s" % name,
        "cpus"      : 1,
        "prototype" : "cmdline",
    }
    job_buildScene.update(job_Base)
    package_Bake = {}
    package_Bake["cmdline"] = 'J:/vd2/work/project_tools/python/submit_qube/ex_maya_ass/vd2_bake_ass.bat %s %s %s' % (fileName, startTime,endTime)
    job_buildScene["package"] = package_Bake
    
    return [job_buildScene]

def hideAll():
    modelPanels = cmds.getPanel(type = 'modelPanel')
    for eachmodelPanel in modelPanels:
        cmds.modelEditor( eachmodelPanel, e=True, allObjects= False)

# def GetCam():
#     cameras = cmds.ls(type=('camera'), l=True)
#     startup_cameras = [camera for camera in cameras if cmds.camera(cmds.listRelatives(camera, parent=True)[0], startupCamera=True, q=True)]
#     non_startup_cameras = list(set(cameras) - set(startup_cameras))
#     non_startup_cameras_transforms = map(lambda x: cmds.listRelatives(x, parent=True)[0], non_startup_cameras)
#     return non_startup_cameras_transforms
def GetCam():
    cameras = cmds.ls(type='camera', long=True)
    non_startup_cameras = []

    for camera in cameras:
        transform = cmds.listRelatives(camera, parent=True, fullPath=True)[0]
        if cmds.camera(transform, startupCamera=True, query=True):
            continue  # skip startup cameras
        non_startup_cameras.extend([transform, camera])

    return non_startup_cameras

def GetCurves():
    curve_transforms = [cmds.listRelatives(i, p=1, type='transform')[0] for i
    in cmds.ls(type='nurbsCurve', o=1, r=1, ni=1)]
    selectList = []
    for c in curve_transforms:
        if "FKRoot_M" in c or "FKNeck_M" in c:
            selectList.append(c)
    return selectList

def CreateLocators():
    locList = []
    curves = GetCurves()
    for curve in curves:
        name=curve+"_loc"
        newLoc = cmds.spaceLocator(name=name)     
        newCon = cmds.parentConstraint(curve, newLoc, mo = 0)
        locList.append(name)
    return locList

def ExportAbc(selection, start, end, save_name):
    # AbcExport -j "-frameRange 1 120 -dataFormat ogawa -root |locator1 -root |locator2 -file D:/After.Effect.Plugins/test.abc"
    root = ""
    for i in selection:
        root += " -root %s" % (i)

    command = "-frameRange " + str(start) + " " + str(end) +" -uvWrite -worldSpace " + root + " -file " + save_name
    cmds.AbcExport ( j = command )

def main(PROJ_NAME,sq,st):
    hideAll()
    
    # st_time = cmds.getAttr("defaultRenderGlobals.startFrame")
    # ed_time = cmds.getAttr("defaultRenderGlobals.endFrame")
    st_time = cmds.playbackOptions(q=True, min=True)
    ed_time = cmds.playbackOptions(q=True, max=True)
    cmds.setAttr("defaultRenderGlobals.startFrame", st_time)
    cmds.setAttr("defaultRenderGlobals.endFrame", ed_time)

    separate = "J:/%s/work/prod/lig/%s/%s/scenes/separate_file" % (PROJ_NAME,sq,st)
    if os.path.isdir(separate) == False:
        os.makedirs(separate)

    file_name = "cam" 
    output = os.path.join(separate,"%s.ma" % file_name)
    cams = GetCam()
    cmds.select(cams)
    cmds.file(output, force=True, options = 'V=0', type= 'mayaAscii', pr=True, es=True)

    # file_name = "controller" 
    # # output = os.path.join(separate,"%s.ma" % file_name)
    # output = os.path.join(separate,"%s.abc" % file_name)
    # locs = CreateLocators()
    # # cmds.select(locs)
    # # cmds.file(output, force=True, options = 'V=0', type= 'mayaAscii', pr=True, es=True, exportSelected=True)
    # ExportAbc(locs, st_time, ed_time, output)

    # file_name = "curves" 
    # output = os.path.join(separate,"%s.ma" % file_name)
    # curves = GetCurves()
    # cmds.select(curves)
    # mel.eval("cleanUpScene 3")
    # cmds.file(output, force=True, options = 'V=0', type= 'mayaAscii', pr=True, es=True, exportSelected=True)

    dic = "{\n"
    check_ns = cmds.ls(type="reference")
    rn_list = []
    for i in check_ns:
        try:
            file_name = cmds.referenceQuery(i,filename=True)
            rn_list.append(i) 
        except Exception as e:
            pass
    for i in rn_list:
        file_name = cmds.referenceQuery(i,filename=True)
        ns = cmds.referenceQuery( i,namespace=True ).split(":")[1]
        output = os.path.join(separate,"%s.ma" % ns)

        if "camera" in file_name:
            pass
        else:
            dic += '''"%s":{"STARTTIME":%s,"ENDTIME":%s,"SEQ":"%s","SHOT":"%s","SUBMIT":1}\n''' % (ns,st_time,ed_time,sq,st)
            obj = get_topgrp(ns,sq,st)
            cmds.select(obj)
            cmds.file(output, force=True, options = 'V=0', type= 'mayaAscii', pr=True, es=True)
            if i != rn_list[-1]:
                dic += ",\n"

    dic +="}"

    jsonFile = os.path.join(separate,("%s__%s__info.json") % (sq,st)).replace("\\","/")
    with open(jsonFile, 'w') as f:
        f.write(dic)

def get_topgrp(ns,_seq,_shot):
    topList = cmds.ls(assemblies=True)
    cmds.select(cl=True)   
    for i in topList:
        if ns in i:
            cmds.select(i,add=True)
    return cmds.ls(sl=True,l=True)



# if __name__ == "__main__":
#     main()
#     sys.exit(0)
