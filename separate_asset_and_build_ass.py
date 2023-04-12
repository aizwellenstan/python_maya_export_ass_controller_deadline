import maya.cmds as cmds
import os
import mtoa.core
import maya.mel as mel
import json
from mtoa.core import createOptions

def set_motion_blur(switch):
    createOptions()
    if switch == "on":
        cmds.setAttr("defaultArnoldRenderOptions.motion_blur_enable", 1)
        cmds.setAttr("defaultArnoldRenderOptions.ignoreMotionBlur" ,1)
        cmds.setAttr("defaultArnoldRenderOptions.range_type", 0)
        cmds.setAttr("defaultArnoldRenderOptions.motion_frames" ,1)
    elif switch == "off":        
        cmds.setAttr("defaultArnoldRenderOptions.motion_blur_enable", 0)
        cmds.setAttr("defaultArnoldRenderOptions.ignoreMotionBlur" ,0)
        cmds.setAttr("defaultArnoldRenderOptions.range_type", 1)
        cmds.setAttr("defaultArnoldRenderOptions.motion_frames" ,0.5)

def create_ass(rn,_path,startTime,endTime,ass_path):
    objList = []
    #### mesh #####
    for _mesh in cmds.ls(type="mesh",l=True):
        if rn  in _mesh:
            objList.append(_mesh)

    referenceList = cmds.ls(rf = True)
    for ref in referenceList:
        p = cmds.referenceQuery(ref, filename = True)
        if "environment" in p:
            patterns = ["Geometry"]
            for p in patterns:
                objects = cmds.ls("*:%s" % p)
                for o in objects:
                    objList.append(o)
            break

    ### pfx
    for _pfx in cmds.ls(type="pfxHair",l=True):
        if rn in _pfx:
            objList.append(_pfx)

    ### follicle
    for _follicle in cmds.ls(type="follicle",l=True):
        if rn in _follicle:
            objList.append(_follicle)

    cmds.select(objList)
    assfileName = os.path.join(ass_path,"%s.ass" % rn).replace("\\","/")
    _str  = '''file -force -options "-shadowLinks 0;-endFrame %s;-mask 4121;-lightLinks 0;-frameStep 1.0;-boundingBox;-startFrame %s" -typ "ASS Export" -pr -es "%s";''' % (endTime,startTime,assfileName)
    mel.eval(_str)

def get_reference():
    rn = ""
    for i in cmds.ls(type="reference"):
        if "RN" in i:
            rn = i.split("RN")[0]
        else:
            rn = i
    return rn

def GetCurves():
    curve_transforms = [cmds.listRelatives(i, p=1, type='transform')[0] for i
    in cmds.ls(type='nurbsCurve', o=1, r=1, ni=1)]
    selectList = []
    for c in curve_transforms:
        if "FKNeck_M" in c:
            selectList.append(c)
            selectList.append(c[0:-8]+"FKRoot_M")
    return selectList

def CreateLocators(rn):
    locList = []
    curves = GetCurves()
    if len(curves) > 1:
        for curve in curves:
            name=rn+"_"+curve
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
    cmds.loadPlugin( 'AbcExport.mll' )
    cmds.AbcExport ( j = command )

def run_json():
    _proj= os.environ["_proj"]
    _sq = os.environ["_sq"]
    _shot = os.environ["_shot"]
    rn = os.environ["_RN"]
    folderPath = os.path.join("J:",_proj,"work/prod/lig")
    json_file = os.path.join(folderPath,_sq,_shot,"scenes","separate_file","%s__%s__info.json" % (_sq,_shot)).replace("\\","/")
    jsData = load_json_file(json_file)
    fileName = os.path.join(folderPath,_sq,_shot,"scenes","separate_file","%s.ma" % rn).replace("\\","/")
    _path = (os.path.dirname(fileName))

    cmds.file(new=True, force=True) 
    cmds.file(fileName, open=True)

    mtoa.core.createOptions()
    cmds.setAttr('defaultArnoldRenderOptions.autotx',0)
    set_motion_blur("on")

    startTime = jsData[rn]["STARTTIME"]
    endTime = jsData[rn]["ENDTIME"]

    abc_path = os.path.join(folderPath,_sq,_shot,"cache","alembic").replace("\\","/")
    if os.path.isdir(abc_path) == False:
        os.makedirs(abc_path)

    file_name = rn+"_controller" 
    output = os.path.join(abc_path,"%s.abc" % file_name)
    locs = CreateLocators(rn)
    if len(locs) > 0 and "Sword" not in rn:
        ExportAbc(locs, startTime, endTime, output)

    ass_path = os.path.join(folderPath,_sq,_shot,"cache","ass",rn).replace("\\","/")
    if os.path.isdir(ass_path) == False:
        os.makedirs(ass_path)

    create_ass(rn,_path,startTime,endTime,ass_path)

def load_json_file(file):
    jsonData  = json.loads(open(file).read())
    return jsonData

def run():
    fileName = os.environ["_fileName"]
    _path = (os.path.dirname(fileName))
    startTime = os.environ["STARTTIME"]
    endTime = os.environ["ENDTIME"]

    cmds.file(new=True, force=True) 
    cmds.file(fileName, open=True)

    mtoa.core.createOptions()
    cmds.setAttr('defaultArnoldRenderOptions.autotx',0)    

    rn = get_reference()
    ass_path = os.path.join(_path,"cache","ass",rn).replace("\\","/")
    if os.path.isdir(ass_path) == False:
        os.makedirs(ass_path)

    create_ass(rn,_path,startTime,endTime,ass_path)
    pass

def deleteRenderableCamera():
    cmds.setAttr("frontShape.renderable", False)
    cmds.setAttr("perspShape.renderable", False)
    cmds.setAttr("sideShape.renderable", False)
    cmds.setAttr("topShape.renderable", False)

def build_shot_f_ass(PROJ_NAME,_seq,_shot):
    shotFolder = "J:/%s/work/prod/lig/%s/%s" % (PROJ_NAME,_seq,_shot)
    seperateFolder = "%s/scenes/separate_file" % (shotFolder)
    camFile = seperateFolder + "/cam.ma"
    cmds.file(camFile, open=True, force=True)
    
    abcFolder = "%s/cache/alembic" % (shotFolder)
    for filename in os.listdir(abcFolder):
        f = os.path.join(abcFolder, filename)
        if os.path.isfile(f):
            objName, ext = os.path.splitext(os.path.basename(f))
            cmds.file(f, i=True, namespace=objName)

    json_file = os.path.join(shotFolder,"scenes","separate_file","%s__%s__info.json" % (_seq,_shot)).replace("\\","/")
    jsData = load_json_file(json_file)
    fileName = os.path.join(shotFolder,"scenes","%s__%s__lig_ASS_v000.ma" % (_seq,_shot)).replace("\\","/")

    rnList = []
    for i in jsData:
        rnList.append(i)
    rnList = sorted(rnList)

    st = 0
    et = 0
    for rn in rnList:
        st = int(jsData[rn]["STARTTIME"])
        et = int(jsData[rn]["ENDTIME"])
        submit = int(jsData[rn]["SUBMIT"])

        standin = mtoa.core.createStandIn()
        path = "%s/cache/ass/%s/%s.####.ass" % (shotFolder,rn,rn)
        cmds.setAttr('{}.dso'.format(standin), path, type="string")
        ass_temp = cmds.listRelatives(standin,p=True)[0]
        if st != et:
            cmds.setAttr("%s.useFrameExtension" % standin,1)
        else:
            cmds.setAttr("%s.frameNumber" % standin,int(st))
            cmds.setAttr("%s.frameNumber" % standin,l=True)
        cmds.rename(ass_temp,"%s_ass" % rn)

    cmds.playbackOptions(minTime=st, maxTime=et)

    deleteRenderableCamera()
