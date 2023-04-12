#!/usr/bin/python
import os, sys
import json
import optparse

def job_CallBack(TOOL_PATH,MAYA_VERSION,OCIO,PROJ_NAME,fileName,sq,shot,rn,startTime,endTime):
    name = fileName.split("/")[-1]
    name = name.split(".ma")[0]

    job_Base = {
        "cluster"    : "/comp/nuke/nuke_a",
        "groups"     : "rsmb",
        "hosts"      : "",
        "omitgroups" : "",
        "omithosts"  : "",
        "priority"   : 4000,
        "reservations" : "host.processors=1+",
    }
    # == Job Bake ==
    job_buildScene = {
        "name"      : "%s_bake_ASS_%s_%s_%s" % (PROJ_NAME,sq,shot,name),
        "label"     : "callbackBack%s" % name,
        "cpus"      : 1,
        "prototype" : "cmdline",
    }
    job_buildScene.update(job_Base)
    package_Bake = {}
    print rn
    package_Bake["cmdline"] = 'I:/script/bin/td/lts/python/ex_maya_ass/bake_ass_deadline.bat %s %s %s %s %s %s %s' % (
        TOOL_PATH,MAYA_VERSION,OCIO,PROJ_NAME,sq,shot,str(rn))
    job_buildScene["package"] = package_Bake
    
    return [job_buildScene]


def load_json_file(file):
    jsonData  = json.loads(open(file).read())
    return jsonData

def main(TOOL_PATH,MAYA_VERSION,OCIO,PROJ_NAME,_sq,_shot):
    sys.path.append('I:/script/bin/td/lts/deadline/python_api')
    import submit_python2
    reload(submit_python2)
    from submit_python2 import GetInfoTxtMayaAss, submit_to_deadline

    folderPath = "J:/%s/work/prod/lig" % (PROJ_NAME)
    json_file = os.path.join(folderPath,_sq,_shot,"scenes","separate_file","%s__%s__info.json" % (_sq,_shot)).replace("\\","/")

    nsList = []
    if os.path.isfile(json_file):
        jsData = load_json_file(json_file)
        for rn in jsData:
            nsList.append(rn)
        nsList = sorted(nsList)
        for i in nsList:
            if jsData[i]["SUBMIT"]:
                fileName = os.path.join(folderPath,_sq,_shot,"scenes","separate_file","%s.ma" % i).replace("\\","/")
                listOfJobsToSubmit = job_CallBack(
                    TOOL_PATH,MAYA_VERSION,OCIO,PROJ_NAME,fileName, _sq, _shot,i,jsData[i]["STARTTIME"],jsData[i]["ENDTIME"])
                job = listOfJobsToSubmit[0]
                arg = job['package']['cmdline']
                name = job['name']
                job_info_txt, plugin_info_txt = GetInfoTxtMayaAss(name, arg)
                submit_to_deadline(job_info_txt, plugin_info_txt)
