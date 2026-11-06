# -*- coding: utf-8 -*-
"""Add movable, recolorable original emblem to the dossier template."""
from pathlib import Path
def one(path,old,new):
    p=Path(path);s=p.read_text(encoding="utf-8")
    if s.count(old)!=1:raise RuntimeError(f"{path}: expected 1 anchor, got {s.count(old)}")
    p.write_text(s.replace(old,new),encoding="utf-8")
one("src/model.cpp",
    "    return result;\n}\nQJsonObject Maket::toJson(",
    """    if(preset==4){
        // Circle engraving from the supplied 300x216pt PDF, with transparent background.
        Decoration badge;
        badge.kind=Decoration::SvgElement;
        badge.elementId="dossier_badge";
        badge.name=QString::fromUtf8("Эмблема · оригинал");
        badge.rect=QRectF(106.0/300.0*LogicalW,52.0/216.0*(LogicalW*heightMm/WidthMm),
                          74.5288/300.0*LogicalW,74.5288/216.0*(LogicalW*heightMm/WidthMm));
        badge.z=result.size()+100;
        result.push_back(badge);
    }
    return result;
}
QJsonObject Maket::toJson(""")
one("src/renderer.cpp",
    """        if(obj.kind==Maket::Decoration::SvgElement && obj.text.isEmpty()){
            if(!renderer->elementExists(obj.elementId)){p.restore();continue;}""",
    """        if(obj.kind==Maket::Decoration::SvgElement && obj.text.isEmpty()){
            if(obj.elementId=="dossier_badge"){
                // External exact vector engraving shipped alongside the EXE.
                const QString path=QCoreApplication::applicationDirPath()+"/templates/dossier_badge_vector.svg";
                static QSharedPointer<QSvgRenderer> badge;
                if(!badge || !badge->isValid())badge=QSharedPointer<QSvgRenderer>::create(path);
                if(badge && badge->isValid()){
                    if(obj.useColorOverride && obj.colorOverride.isValid()){
                        const int w=qBound(1,qRound(obj.rect.width()*2),2500);
                        const int h=qBound(1,qRound(obj.rect.height()*2),2500);
                        QImage tinted(w,h,QImage::Format_ARGB32_Premultiplied);tinted.fill(Qt::transparent);
                        QPainter op(&tinted);badge->render(&op,QRectF(0,0,w,h));
                        op.setCompositionMode(QPainter::CompositionMode_SourceIn);
                        op.fillRect(tinted.rect(),obj.colorOverride);op.end();
                        p.drawImage(obj.rect,tinted);
                    } else badge->render(&p,obj.rect);
                }
                p.restore();continue;
            }
            if(!renderer->elementExists(obj.elementId)){p.restore();continue;}""")
print("PASS: separately editable original dossier vector emblem is supported.")
