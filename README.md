```python
import sys
_p  = 'I:/script/bin/td/lts/python/ex_maya_ass'
if _p not in sys.path:
    sys.path.append(_p)
import jobSubmit_Callback_build
reload(jobSubmit_Callback_build)
PROJ_NAME="axc"
_seq = "s02"
_shot = "c080"
jobSubmit_Callback_build.main(PROJ_NAME,_seq,_shot)

import jobSubmit_Callback_deadline
reload(jobSubmit_Callback_deadline)
MAYA_VERSION=2022
OCIO="J:/%s/proj/%s/tool/settings/ocio/v5/config.ocio" % (PROJ_NAME, PROJ_NAME)

jobSubmit_Callback_deadline.main(_p,MAYA_VERSION,OCIO,PROJ_NAME,_seq,_shot)
```

```python
import sys
_p  = 'I:/script/bin/td/lts/python/ex_maya_ass'
if _p not in sys.path:
    sys.path.append(_p)
import separate_asset_and_build_ass
reload(separate_asset_and_build_ass)
_proj = "axc"
_seq = "s02"
_shot = "c080"
separate_asset_and_build_ass.build_shot_f_ass(_proj,_seq,_shot)
```

## flow
jobSubmit_Callback_build.main(_seq,_shot,current)
jobSubmit_Callback_deadline.main(_seq,_shot)
bake_ass_deadline.bat
separate_asset_and_build_ass.run_json()

```bat
"I:/script/bin/td/lts/python/ex_maya_ass/bake_ass_deadline.bat" "I:/script/bin/td/lts/python/ex_maya_ass" 2022 J:/axc/proj/axc/tool/settings/ocio/v5/config.ocio s02 c080 CHadas_00
```


####### build ass shot ########
import sys
_p  = 'J:/vd2/work/project_tools/python/submit_qube/ex_maya_ass'
if _p not in sys.path:
    sys.path.append(_p)
import separate_asset_and_build_asss
reload(separate_asset_and_build_asss)
_seq = "s028"
_shot = "110"
separate_asset_and_build_asss.build_shot_f_ass(_seq,_shot)