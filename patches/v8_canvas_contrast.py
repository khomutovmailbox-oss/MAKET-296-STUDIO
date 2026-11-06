from pathlib import Path
def change(path,old,new):
    p=Path(path);s=p.read_text(encoding="utf-8")
    n=s.count(old)
    if n!=1:raise RuntimeError(f"{path} expected exactly one target, got {n}: {old[:65]}")
    p.write_text(s.replace(old,new),encoding="utf-8")

change("src/window.h",
    "    void setReferenceVisible(bool enabled){showReference_=enabled;update();}",
    "    void setReferenceVisible(bool enabled){showReference_=enabled;update();}\n    void setDarkPreview(bool dark){darkPreview_=dark;update();}")
change("src/window.h",
    "    bool showReference_=false;",
    "    bool showReference_=false;\n    bool darkPreview_=true;")
change("src/window.cpp",
    '    p.fillRect(paper,QColor("#edf0f3"));',
    '    p.fillRect(paper,darkPreview_?QColor("#29323d"):QColor("#edf0f3"));')
change("src/window.cpp",
    'p.fillRect(QRectF(paper.left()+c*tile,paper.top()+r*tile,tile,tile),QColor("#e1e5e9"));',
    'p.fillRect(QRectF(paper.left()+c*tile,paper.top()+r*tile,tile,tile),darkPreview_?QColor("#222b34"):QColor("#e1e5e9"));')
change("src/window.cpp",
    '    referenceCheck_=new QCheckBox("Показывать эталон поверх макета");refLay->addWidget(referenceCheck_);',
    '    auto *darkCheck=new QCheckBox("Тёмная подложка · только просмотр");darkCheck->setChecked(true);refLay->addWidget(darkCheck);\n    referenceCheck_=new QCheckBox("Показывать эталон поверх макета");refLay->addWidget(referenceCheck_);')
change("src/window.cpp",
    '    connect(referenceCheck_,&QCheckBox::toggled,canvas_,&Canvas::setReferenceVisible);',
    '    connect(darkCheck,&QCheckBox::toggled,canvas_,&Canvas::setDarkPreview);\n    connect(referenceCheck_,&QCheckBox::toggled,canvas_,&Canvas::setReferenceVisible);')
change("src/window.cpp",'preview.fill(QColor("#e3e9ee"));','preview.fill(QColor("#29323d"));')
print("V8 preview contrast fixed: dark / light selectable, never exported")
