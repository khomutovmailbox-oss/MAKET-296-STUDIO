"""Validate real native Windows Qt output after all photo slots have been filled."""
from pathlib import Path
import math,sys
from PIL import Image
import fitz
folder=Path(sys.argv[1])
png=folder/"dtf_296x465_300dpi.png"
pdf=folder/"dtf_296x465.pdf"
svg=folder/"dtf_296x465.svg"
for f in (png,pdf,svg):
    assert f.is_file() and f.stat().st_size>1000, f"Missing/empty {f}"
with Image.open(png) as im:
    assert im.mode=="RGBA",f"Expected RGBA alpha, got {im.mode}"
    w,h=im.size
    assert abs(w-round(296/25.4*300))<=1, ("wrong width",w)
    assert abs(h-round(464.72/25.4*300))<=1, ("wrong height",h)
    dpi=im.info.get("dpi",(0,0))
    assert all(abs(d-300)<1 for d in dpi),("wrong dpi",dpi)
    alpha=im.getchannel("A")
    assert alpha.getpixel((0,0))==0,"background is not transparent"
    # Adjacent rectangular photo cells must have fully opaque interiors.
    # The samples are opaque JPEGs, so partial alpha here is an actual gap.
    for normalized_y in [0.35,0.495,0.496,0.65]:
        y=round(h*normalized_y)
        for x in [round(w*v) for v in (0.05,0.25,0.5,0.75,0.95)]:
            a=alpha.getpixel((x,y))
            if a!=255: raise AssertionError(f"Photo tile seam / hole: ({x},{y}) alpha={a}")
    print("DTF PNG: dimensions",im.size,"DPI",dpi,"tagged_colorspace",bool(im.info.get("icc_profile") or im.info.get("srgb")))
with fitz.open(pdf) as doc:
    assert len(doc)==1
    page=doc[0]
    assert abs(page.rect.width*25.4/72-296)<0.2
    assert abs(page.rect.height*25.4/72-464.72)<0.2
    assert len(page.get_images(full=True))>=6, "PDF missing actual photo images"
    corners=page.get_pixmap(alpha=True)
    assert corners.pixel(0,0)[3]==0, "PDF page background not transparent"
    print("DTF PDF:",len(page.get_images(full=True)),"photo images, no background")
from xml.etree import ElementTree as ET
root=ET.parse(svg).getroot()
assert root.attrib["width"]=="296mm"
print("Qt actual populated export passed preflight; inspect line widths and effective PHOTO DPI separately.")
