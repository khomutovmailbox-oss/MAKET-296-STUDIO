# -*- coding: utf-8 -*-
from pathlib import Path
p=Path("src/window.cpp")
s=p.read_text(encoding="utf-8")
if "#include <QSvgRenderer>" not in s:
    s="#include <QSvgRenderer>\n"+s
old="QImageReader reader(path);cachedReference_=reader.read();"
new="""QImageReader reader(path);cachedReference_=reader.read();
            if(cachedReference_.isNull()){
                // Portable fallback: the extracted original vector SVGs are compiled
                // into Qt resources, so the original reference works offline.
                const QString resource=QString(":/templates/overlay_%1.svg")
                    .arg(design_->preset,2,10,QLatin1Char('0'));
                QSvgRenderer original(resource);
                if(original.isValid()){
                    const int referenceWidth=1200;
                    const int referenceHeight=qMax(1,qRound(referenceWidth*design_->heightMm/WidthMm));
                    cachedReference_=QImage(referenceWidth,referenceHeight,QImage::Format_ARGB32_Premultiplied);
                    cachedReference_.fill(Qt::transparent);
                    QPainter refPainter(&cachedReference_);
                    original.render(&refPainter,QRectF(0,0,referenceWidth,referenceHeight));
                }
            }"""
if s.count(old)!=1: raise RuntimeError(f"Missing v8 JPG source anchor ({s.count(old)})")
s=s.replace(old,new)
s=s.replace('refLay->addWidget(label("Фон и чужие фотографии видны только для сравнения. В файлы для DTF эталон НЕ попадает.",true));',
            'refLay->addWidget(label("Сверка по оригинальным векторным контурам, без фона и чужих фото. В DTF-экспорт эталон не попадает.",true));')
p.write_text(s,encoding="utf-8")
print("PASS: embedded original SVG reference fallback, independent of external JPGs.")
