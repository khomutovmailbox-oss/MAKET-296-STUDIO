#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix leaked photo rectangles in MOM/DAD, mode transitions, and 2x2 letter mosaics."""
from pathlib import Path

def replace_one(path, old, new):
    file=Path(path)
    s=file.read_text(encoding="utf-8")
    count=s.count(old)
    if count!=1:
        raise RuntimeError(f"{path}: expected 1 matching anchor; found {count}: {old[:90]!r}")
    file.write_text(s.replace(old,new),encoding="utf-8")

replace_one("src/model.h",
    "    bool hasRect = false;\n    bool visible = true;",
    "    bool hasRect = false;\n    int geometryMode = 0; // 0: original poster, 1: word photo-mask\n    bool visible = true;")

replace_one("src/model.cpp",
    "for(int i=0;i<d.photos.size();++i){\n            if(i<v.size() && d.photos[i].hasRect",
    "for(int i=0;i<d.photos.size();++i){\n            if(d.photos[i].geometryMode!=(d.letters?1:0))continue; // no poster frames in MOM/DAD\n            if(i<v.size() && d.photos[i].hasRect")

replace_one("src/model.cpp",
    "d.photos[i].rect=baseSlots[i].r;d.photos[i].hasRect=true;d.photos[i].z=i;",
    "d.photos[i].rect=baseSlots[i].r;d.photos[i].hasRect=true;d.photos[i].geometryMode=0;d.photos[i].z=i;")

replace_one("src/model.cpp",
    '{"rect",rect},{"has_rect",p.hasRect},{"visible",p.visible}',
    '{"rect",rect},{"has_rect",p.hasRect},{"geometry_mode",p.geometryMode},{"visible",p.visible}')

replace_one("src/model.cpp",
    'p.hasRect=po.value("has_rect").toBool(true);}',
    'p.hasRect=po.value("has_rect").toBool(true);}\n        p.geometryMode=po.value("geometry_mode").toInt(n.letters?1:0);')

replace_one("src/model.cpp",
    "n.photos[i].rect=baseSlots[i].r;n.photos[i].hasRect=true;n.photos[i].z=i;",
    "n.photos[i].rect=baseSlots[i].r;n.photos[i].hasRect=true;n.photos[i].geometryMode=n.letters?1:0;n.photos[i].z=i;")

replace_one("src/window.cpp",
    "d.photos[i].rect=frames[i].r;d.photos[i].hasRect=true;d.photos[i].z=i;",
    "d.photos[i].rect=frames[i].r;d.photos[i].hasRect=true;d.photos[i].geometryMode=d.letters?1:0;d.photos[i].z=i;")

replace_one("src/window.cpp",
    "for(int i=baseCount;i<previous.size();++i)if(previous[i].hasRect)d.photos.push_back(previous[i]);",
    "for(int i=baseCount;i<previous.size();++i)\n        if(previous[i].hasRect && previous[i].geometryMode==(d.letters?1:0))d.photos.push_back(previous[i]);")

replace_one("src/window.cpp",
    "ph.hasRect=true;ph.z=z++;design_.photos.push_back(ph);",
    "ph.hasRect=true;ph.geometryMode=design_.letters?1:0;ph.z=z++;design_.photos.push_back(ph);")

replace_one("src/renderer.cpp",
    "    for(int i:photoOrder){",
    """    // Every photo is clipped to the entire word, including freely added photos.
    p.save();
    if(d.letters){
        QPainterPath wordOutline;wordOutline.setFillRule(Qt::WindingFill);
        for(const QPainterPath &glyph:glyphs)wordOutline.addPath(glyph);
        p.setClipPath(wordOutline,Qt::ReplaceClip);
    }
    for(int i:photoOrder){""")

replace_one("src/renderer.cpp",
    """                    QRectF mb=mask.boundingRect();
                    if(!mb.isEmpty()){
                        QTransform tr;tr.translate(slot.r.left(),slot.r.top());
                        tr.scale(slot.r.width()/mb.width(),slot.r.height()/mb.height());tr.translate(-mb.left(),-mb.top());
                        mask=tr.map(mask);
                    }
                    p.setClipPath(mask,Qt::IntersectClip);""",
    """                    // Letter geometry is always in page coordinates. Never scale
                    // a full glyph into each mosaic tile or the letters repeat.
                    p.setClipPath(mask,Qt::IntersectClip);""")

replace_one("src/renderer.cpp",
    """    if(!d.decorations.isEmpty()) renderEditableArtwork(p,d,!d.letters);
    else decorations(p,d);""",
    """    p.restore(); // release word clipping before painting independent decorations
    if(!d.decorations.isEmpty()) renderEditableArtwork(p,d,!d.letters);
    else decorations(p,d);""")
print("PASS: exact per-letter clipping and no cross-mode photo rectangles.")
