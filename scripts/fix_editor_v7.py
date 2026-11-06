from pathlib import Path

def replace_once(path, old, new):
    p=Path(path)
    text=p.read_text(encoding="utf-8")
    count=text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one patch anchor, got {count}: {old[:90]!r}")
    p.write_text(text.replace(old,new),encoding="utf-8")

replace_once("src/renderer.cpp",
    "    if(d.letters) decorations(p,d);\n    else if(!renderOriginalArtwork(p,d)) decorations(p,d);",
    "    if(d.letters) decorations(p,d);\n    else if(!d.decorations.isEmpty()) renderEditableArtwork(p,d);\n    else decorations(p,d);")
r=Path("src/renderer.cpp").read_text(encoding="utf-8")
if "#include <QHash>" not in r:
    r=r.replace("#include <QSharedPointer>","#include <QSharedPointer>\n#include <QHash>")
Path("src/renderer.cpp").write_text(r,encoding="utf-8")

replace_once("src/window.cpp",
"""void resetPhotoFrames(Design &d){
    for(auto &photo:d.photos)photo.hasRect=false;
    const auto frames=photoSlots(d);const int old=d.photos.size();d.photos.resize(frames.size());
    for(int i=0;i<d.photos.size();++i){d.photos[i].rect=frames[i].r;d.photos[i].hasRect=true;if(i>=old)d.photos[i].z=i;}
}""",
"""void resetPhotoFrames(Design &d){
    const QVector<Photo> previous=d.photos;
    for(auto &photo:d.photos)photo.hasRect=false;
    const auto frames=photoSlots(d);const int baseCount=frames.size();
    d.photos.resize(baseCount);
    for(int i=0;i<baseCount;++i){d.photos[i].rect=frames[i].r;d.photos[i].hasRect=true;d.photos[i].z=i;}
    for(int i=baseCount;i<previous.size();++i)if(previous[i].hasRect)d.photos.push_back(previous[i]);
}""")
replace_once("src/window.cpp",
    'connect(tabs_,&QTabWidget::currentChanged,this,[this](int ix){if(!loading_)switchMode(ix==1);});',
    'connect(tabs_,&QTabWidget::currentChanged,this,[this](int ix){if(loading_)return;if(ix==0)switchMode(false);else if(ix==1)switchMode(true);});')
replace_once("src/window.cpp",
    "void Canvas::setCropMode(bool enabled){cropMode_=enabled;setCursor(enabled?Qt::SizeAllCursor:Qt::CrossCursor);update();}",
    "void Canvas::setCropMode(bool enabled){cropMode_=enabled;setCursor(enabled?Qt::SizeAllCursor:Qt::CrossCursor);update();emit objectSelectionChanged();}")
replace_once("src/window.cpp",
    'if(any){xSpin_->setValue(bounds.x()/UnitsPerMm);ySpin_->setValue(bounds.y()/UnitsPerMm);wSpin_->setValue(bounds.width()/UnitsPerMm);hSpin_->setValue(bounds.height()/UnitsPerMm);groupWidthSpin_->setValue(bounds.width()/UnitsPerMm);groupHeightSpin_->setValue(bounds.height()/UnitsPerMm);}',
    'if(any){xSpin_->setValue(bounds.x()/UnitsPerMm);ySpin_->setValue(bounds.y()/UnitsPerMm);wSpin_->setValue(bounds.width()/UnitsPerMm);hSpin_->setValue(bounds.height()/UnitsPerMm);}\n    if(photos.size()>1){const auto frames=photoSlots(design_);int active=canvas_->selected();if(active>=0&&active<frames.size()){groupWidthSpin_->setValue(frames[active].r.width()/UnitsPerMm);groupHeightSpin_->setValue(frames[active].r.height()/UnitsPerMm);}}\n    else if(any){groupWidthSpin_->setValue(bounds.width()/UnitsPerMm);groupHeightSpin_->setValue(bounds.height()/UnitsPerMm);}')
replace_once("src/window.cpp",
    "for(int i:selectedPhotos_)if(i>=0&&i<frames.size())dragPhotoRects_.insert(i,frames[i].r);",
    "for(int i:selectedPhotos_)if(i>=0&&i<frames.size()&&!design_->photos[i].locked)dragPhotoRects_.insert(i,frames[i].r);")
replace_once("src/window.cpp",
    "for(int i:selectedDecorations_)if(i>=0&&i<design_->decorations.size())dragDecorationRects_.insert(i,design_->decorations[i].rect);",
    "for(int i:selectedDecorations_)if(i>=0&&i<design_->decorations.size()&&!design_->decorations[i].locked)dragDecorationRects_.insert(i,design_->decorations[i].rect);")
replace_once("src/window.cpp",
    "if(!photos.isEmpty()){auto frames=photoSlots(design_);for(int i:photos)if(i>=0&&i<frames.size()){ids<<i;old<<frames[i].r;}}\n    else for(int i:decos)if(i>=0&&i<design_.decorations.size()){ids<<i;old<<design_.decorations[i].rect;}",
    "if(!photos.isEmpty()){auto frames=photoSlots(design_);for(int i:photos)if(i>=0&&i<frames.size()&&!design_.photos[i].locked){ids<<i;old<<frames[i].r;}}\n    else for(int i:decos)if(i>=0&&i<design_.decorations.size()&&!design_.decorations[i].locked){ids<<i;old<<design_.decorations[i].rect;}")
replace_once("src/window.cpp",
    "if(!photos.isEmpty()){auto frames=photoSlots(design_);for(int i:photos)if(i>=0&&i<frames.size()){design_.photos[i].rect=apply(frames[i].r);design_.photos[i].hasRect=true;}}\n    else for(int i:decos)if(i>=0&&i<design_.decorations.size())design_.decorations[i].rect=apply(design_.decorations[i].rect);",
    "if(!photos.isEmpty()){auto frames=photoSlots(design_);for(int i:photos)if(i>=0&&i<frames.size()&&!design_.photos[i].locked){design_.photos[i].rect=apply(frames[i].r);design_.photos[i].hasRect=true;}}\n    else for(int i:decos)if(i>=0&&i<design_.decorations.size()&&!design_.decorations[i].locked)design_.decorations[i].rect=apply(design_.decorations[i].rect);")
replace_once("src/window.cpp",
    "for(int i:photos)if(i>=0&&i<design_.photos.size())design_.photos[i].z=z++;",
    "for(int i:photos)if(i>=0&&i<design_.photos.size()&&!design_.photos[i].locked)design_.photos[i].z=z++;")
replace_once("src/window.cpp",
    "for(int i:decos)if(i>=0&&i<design_.decorations.size())design_.decorations[i].z=z++;",
    "for(int i:decos)if(i>=0&&i<design_.decorations.size()&&!design_.decorations[i].locked)design_.decorations[i].z=z++;")
replace_once("src/window.cpp",
    "for(int i:ds)if(i>=0&&i<design_.decorations.size())design_.decorations.removeAt(i);QList<int> ps=canvas_->selectedPhotos();for(int i:ps)if(i>=0&&i<design_.photos.size())design_.photos[i].path.clear();",
    "for(int i:ds)if(i>=0&&i<design_.decorations.size()&&!design_.decorations[i].locked)design_.decorations.removeAt(i);QList<int> ps=canvas_->selectedPhotos();for(int i:ps)if(i>=0&&i<design_.photos.size()&&!design_.photos[i].locked)design_.photos[i].path.clear();")

replace_once("src/window.cpp",
    "design_.decorations.push_back(o);canvas_->setDecorationSelection({design_.decorations.size()-1},design_.decorations.size()-1);modified();syncLayerList();syncObjectControls();",
    "design_.decorations.push_back(o);const int index=int(design_.decorations.size())-1;canvas_->setDecorationSelection({index},index);modified();syncLayerList();syncObjectControls();")
replace_once("src/window.cpp",
    "if(!design_.photos.isEmpty())canvas_->setPhotoSelection({design_.photos.size()-1},design_.photos.size()-1);",
    "if(!design_.photos.isEmpty()){const int index=int(design_.photos.size())-1;canvas_->setPhotoSelection({index},index);}")

main=Path("src/main.cpp").read_text(encoding="utf-8")
if "#include <QFile>" not in main:
    main=main.replace("#include <QFileInfo>","#include <QFileInfo>\n#include <QFile>")
main=main.replace("        Maket::Design d=Maket::defaultDesign(2);",
"""        for(int t=0;t<10;++t){const auto probe=Maket::defaultDesign(t);if(probe.decorations.isEmpty())return 9;}
        Maket::Design d=Maket::defaultDesign(2);if(d.decorations.isEmpty())return 10;""")
main=main.replace(
    "for(int i=0;i<3;++i){d.photos[i].path=fixtures[i];d.photos[i].rect=QRectF(70+i*185,350+i*45,490,390);d.photos[i].hasRect=true;d.photos[i].z=i;d.photos[i].zoom=1.35+i*.2;d.photos[i].shiftX=(i-1)*.18;}",
    """for(int i=0;i<3;++i){d.photos[i].path=fixtures[i];d.photos[i].rect=QRectF(70+i*185,350+i*45,490,330+i*30);d.photos[i].hasRect=true;d.photos[i].z=i;d.photos[i].zoom=1.35+i*.2;d.photos[i].shiftX=(i-1)*.18;}
        const qreal commonHeight=240.0;
        for(int i=0;i<3;++i){QRectF &r=d.photos[i].rect;const qreal factor=commonHeight/r.height();r.setWidth(r.width()*factor);r.setHeight(commonHeight);}""")
main=main.replace("if(qAbs(roundTrip.photos[1].rect.height()-390)>0.01||roundTrip.photos[1].z!=5||roundTrip.photos[1].zoom<1.5)return 6;",
    "if(qAbs(roundTrip.photos[1].rect.height()-240)>0.01||qAbs(roundTrip.photos[0].rect.height()-roundTrip.photos[2].rect.height())>0.01||roundTrip.photos[1].z!=5||roundTrip.photos[1].zoom<1.5)return 6;")
Path("src/main.cpp").write_text(main,encoding="utf-8")
print("Applied editor v7 follow-up fixes.")
