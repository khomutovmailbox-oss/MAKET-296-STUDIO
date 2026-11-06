# -*- coding: utf-8 -*-
from pathlib import Path
def read(p): return Path(p).read_text(encoding="utf-8")
def write(p,s): Path(p).write_text(s,encoding="utf-8")
def once(s, old,new,context):
    n=s.count(old)
    if n!=1: raise RuntimeError(f"{context}: expected one anchor, got {n}")
    return s.replace(old,new)
header=read("src/window.h")
header=once(header,"    void refresh();","    void refresh();\n    void setReferenceVisible(bool enabled){referenceVisible_=enabled;update();}\n    bool referenceVisible() const{return referenceVisible_;}","Canvas public API")
header=once(header,"    ImageCache cache_;","    ImageCache cache_;\n    bool referenceVisible_=false;","Canvas private state")
write("src/window.h",header)
source=read("src/window.cpp")
source="#include <QShortcut>\n#include <QSvgRenderer>\n#include <QHash>\n#include <QSharedPointer>\n"+source
start=source.index("void Canvas::paintEvent(")
end=source.index("void Canvas::mousePressEvent(",start)
block=source[start:end]
if "Renderer::paint(" not in block: raise RuntimeError("Canvas rendering anchor missing")
marker="    p.restore();\n"
ix=block.find(marker,block.index("Renderer::paint("))
if ix<0: raise RuntimeError("Canvas painter restoration missing")
overlay="""    if(referenceVisible_ && !design_->letters){
        // Reference artwork is drawn only on the editor canvas.
        const QString svgName=QString(":/templates/overlay_%1.svg").arg(design_->preset,2,10,QLatin1Char('0'));
        static QHash<QString,QSharedPointer<QSvgRenderer>> referenceCache;
        auto reference=referenceCache.value(svgName);
        if(!reference){
            reference=QSharedPointer<QSvgRenderer>::create(svgName);
            referenceCache.insert(svgName,reference);
        }
        if(reference->isValid()){
            p.save();
            p.setOpacity(0.50);
            reference->render(&p,QRectF(0,0,LogicalW,LogicalW*design_->heightMm/WidthMm));
            p.restore();
        }
    }
"""
block=block[:ix]+overlay+block[ix:]
source=source[:start]+block+source[end:]
ctor_anchor="    setStyleSheet(css());buildUi();"
source=once(source,ctor_anchor,ctor_anchor+"""
    auto *referenceShortcut=new QShortcut(QKeySequence(Qt::Key_F7),this);
    connect(referenceShortcut,&QShortcut::activated,this,[this]{
        if(!canvas_)return;
        canvas_->setReferenceVisible(!canvas_->referenceVisible());
        statusBar()->showMessage(canvas_->referenceVisible()
          ?QString::fromUtf8("F7: оригинальный векторный контур показан (не печатается)")
          :QString::fromUtf8("F7: оригинальный контур скрыт"),6000);
    });
""","MainWindow constructor")
write("src/window.cpp",source)
print("PASS: F7 original reference in Qt canvas only, not print exports")
