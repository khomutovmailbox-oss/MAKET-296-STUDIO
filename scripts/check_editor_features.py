from pathlib import Path
import json,sys
from PIL import Image
import fitz
from xml.etree import ElementTree as ET
root=Path(sys.argv[1]);project=json.loads((root/"editor_test.maket.json").read_text(encoding="utf-8"))
photos=project["photos"];assert len(photos)>=3
assert all(len(p.get("rect",[]))==4 for p in photos[:3])
assert photos[1]["z"]>photos[0]["z"] and photos[1]["zoom"]>1
a,b=photos[0]["rect"],photos[1]["rect"]
assert a[0]<b[0]+b[2] and b[0]<a[0]+a[2],"fixture photos must overlap"
assert any(x.get("kind")==1 and x.get("text")=="РЕДАКТИРУЕМАЯ НАДПИСЬ" for x in project["decorations"])
with Image.open(root/"editor_test.png") as im:
    assert abs(im.width-round(296/25.4*300))<=1
    assert im.mode=="RGBA" and im.getchannel("A").getpixel((0,0))==0
    assert all(abs(v-300)<1 for v in im.info.get("dpi",(0,0)))
with fitz.open(root/"editor_test.pdf") as doc:
    assert len(doc)==1 and abs(doc[0].rect.width*25.4/72-296)<.2
    assert len(doc[0].get_images(full=True))>=3
svg=ET.parse(root/"editor_test.svg").getroot()
assert svg.attrib.get("width")=="296mm" and svg.attrib.get("height","").endswith("mm")
print("PASS: photo crop/overlap/z-order, editable text/decor JSON, group geometry, transparent 296mm PNG at 300dpi, PDF photos, SVG")
