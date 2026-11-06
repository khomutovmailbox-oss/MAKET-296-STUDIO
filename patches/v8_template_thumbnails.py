from pathlib import Path
file=Path("src/window.cpp")
text=file.read_text(encoding="utf-8")
old='''        const QString refPath=QCoreApplication::applicationDirPath()+QString("/reference/ref_%1.jpg").arg(pr.id,2,10,QLatin1Char('0'));
        QImage img=QImageReader(refPath).read();
        if(img.isNull())img=Renderer::preview(d,110);'''
new='''        // Thumbnails never display a template background, only vector artwork.
        // The real original is shown ONLY when the comparison switch is enabled.
        QImage img=Renderer::preview(d,110);'''
if text.count(old)!=1: raise RuntimeError("Unable to find original-preview thumbnail block")
file.write_text(text.replace(old,new),encoding="utf-8")
print("Template library: no sample backgrounds; comparison reference remains opt-in")
