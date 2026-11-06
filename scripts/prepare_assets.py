from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]/"assets"/"templates"
ET.register_namespace("","http://www.w3.org/2000/svg")
ET.register_namespace("xlink","http://www.w3.org/1999/xlink")
DRAWABLE={"path","g","rect","circle","ellipse","line","polyline","polygon","text","use"}
for template_id in range(10):
    path=ROOT/f"overlay_{template_id:02d}.svg"
    tree=ET.parse(path);root=tree.getroot();index=0
    for element in list(root):
        if element.tag.rsplit("}",1)[-1] in DRAWABLE:
            element.set("id",f"editable_{template_id:02d}_{index:03d}");index+=1
    tree.write(path,encoding="utf-8",xml_declaration=True)
    print(f"{path.name}: {index} editable vector objects")
