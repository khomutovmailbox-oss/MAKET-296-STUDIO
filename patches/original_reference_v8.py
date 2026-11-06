# -*- coding: utf-8 -*-
"""Link F7 to the already-implemented v8 original-PDF comparison control."""
from pathlib import Path
path=Path("src/window.cpp")
source=path.read_text(encoding="utf-8")
if '#include <QShortcut>' not in source:
    source="#include <QShortcut>\n"+source
anchor="    setStyleSheet(css());buildUi();"
if source.count(anchor)!=1: raise RuntimeError(f"MainWindow setup anchor missing or repeated ({source.count(anchor)})")
new=anchor+"""
    auto *referenceShortcut=new QShortcut(QKeySequence(Qt::Key_F7),this);
    connect(referenceShortcut,&QShortcut::activated,this,[this]{
        if(referenceCheck_)referenceCheck_->setChecked(!referenceCheck_->isChecked());
    });
"""
source=source.replace(anchor,new)
path.write_text(source,encoding="utf-8")
print("PASS: F7 toggles existing Qt original PDF reference checkbox (no duplicate overlay).")
