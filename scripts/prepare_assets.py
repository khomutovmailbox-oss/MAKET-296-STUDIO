from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]/"assets"/"templates"
ET.register_namespace("","http://www.w3.org/2000/svg")
ET.register_namespace("xlink","http://www.w3.org/1999/xlink")
DRAWABLE={"path","g","rect","circle","ellipse","line","polyline","polygon","text","use"}

for template_id in range(10):
    path=ROOT/f"overlay_{template_id:02d}.svg"
    tree=ET.parse(path);root=tree.getroot();index=0
    replacements={}
    for element in list(root):
        if element.tag.rsplit("}",1)[-1] not in DRAWABLE:
            continue
        old=element.get("id")
        new=f"editable_{template_id:02d}_{index:03d}"
        if old and old!=new:
            replacements[old]=new
        element.set("id",new)
        index+=1
    if replacements:
        for element in root.iter():
            for key,value in list(element.attrib.items()):
                for old,new in replacements.items():
                    value=value.replace(f"#{old}",f"#{new}")
                element.set(key,value)
            if element.text:
                text=element.text
                for old,new in replacements.items():
                    text=text.replace(f"#{old}",f"#{new}")
                element.text=text
    tree.write(path,encoding="utf-8",xml_declaration=True)
    print(f"{path.name}: {index} independently editable vector objects")
