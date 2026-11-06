"""DTF print-safe fixes applied after ZIP extraction, before Qt compilation."""
from pathlib import Path
def replace(path, old, new):
    file=Path(path)
    source=file.read_text(encoding="utf-8")
    count=source.count(old)
    if count!=1: raise RuntimeError(f"{path}: expected exactly one match, found {count}: {old[:80]!r}")
    file.write_text(source.replace(old,new),encoding="utf-8")
replace("src/model.cpp", '{7, "ONLY YOU · двойной контур", 305,', '{7, "ONLY YOU · двойной контур", 291.1,')
replace("src/renderer.cpp", "#include <QImageReader>", "#include <QImageReader>\n#include <QColorSpace>")
replace("src/renderer.cpp", "if(outline)p.setPen(QPen(color,1.6));", "if(outline)p.setPen(QPen(color,2.1));")
replace("src/renderer.cpp", "p.setPen(QPen(color,1.55,Qt::SolidLine", "p.setPen(QPen(color,2.1,Qt::SolidLine")
replace("src/renderer.cpp", "double w=1.5+k%4*.48;", "double w=1.8+k%4*.48;")
replace("src/renderer.cpp", "x+=w+1.25+(k%3)*.6;", "x+=w+2.05+(k%3)*.6;")
replace("src/renderer.cpp", "p.save();p.setPen(QPen(color,width));", "p.save();p.setPen(QPen(color,std::max(width,2.1)));")
replace("src/renderer.cpp", "if(!photo.isNull()){\n                p.save();\n                QPainterPath clipping;clipping.addRect(slot.r);",
    "if(!photo.isNull()){\n                p.save();\n                // Hard-edge rectangular clips prevent transparent pixels between photo tiles.\n                if(!d.letters)p.setRenderHint(QPainter::Antialiasing,false);\n                QPainterPath clipping;clipping.addRect(d.letters?slot.r.adjusted(-.45,-.45,.45,.45):slot.r);")
replace("src/renderer.cpp", "QRectF dest=slot.r.adjusted(-.10,-.10,.10,.10);",
    "QRectF dest=d.letters?slot.r.adjusted(-.45,-.45,.45,.45):slot.r.adjusted(-.10,-.10,.10,.10);")
replace("src/renderer.cpp", "    p.restore();\n    p.restore();\n    Q_UNUSED(H)", "    p.restore();\n    Q_UNUSED(H)")
replace("src/renderer.cpp", "img.fill(Qt::transparent);img.setDotsPerMeterX",
    "img.fill(Qt::transparent);img.setColorSpace(QColorSpace(QColorSpace::SRgb));img.setDotsPerMeterX")
print("DTF patches applied: no tile seams, >=0.62 mm decorative lines, corrected second ONLY YOU size, sRGB, painter state.")
