

import specStrings
from inspect import getmembers, isfunction
import os 

ultra = []
for dcts in [getattr(specStrings, o[0])() for o in getmembers(specStrings) if isfunction(o[1])]:
    for dct in dcts:
        ultra.append(dct)

for item in ultra[1:]:
    fKey,uId = (item['encoding']['path'].split("/")[-2:])
    uId = uId.split(".")[0]
    name = fKey+"#"+uId
    if os.path.isdir(".../validation/"+name): continue
    os.mkdir(".../validation/"+name)
    WebStore(".../validation/"+name).add_interactions(item)
