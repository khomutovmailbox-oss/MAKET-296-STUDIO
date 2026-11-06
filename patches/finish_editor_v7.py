# -*- coding: utf-8 -*-
"""Apply Qt editor improvements after v7 patch and validate PDF visually."""
from pathlib import Path
def one(path,old,new):
    p=Path(path)
    s=p.read_text(encoding="utf-8")
    n=s.count(old)
    if n!=1:
        raise RuntimeError(f"{path}: expected one match, found {n}: {old[:100]}")
    p.write_text(s.replace(old,new),encoding="utf-8")

# Original lettering extracted from PDFs consists of vector contours, not text.
# Text replacement is opt-in: when a vector layer has nonempty text, render that
# editable text; clearing it restores the unchanged original vector artwork.
one("src/renderer.cpp",
    "if(obj.kind==Maket::Decoration::SvgElement){",
    "if(obj.kind==Maket::Decoration::SvgElement && obj.text.isEmpty()){")
one("src/renderer.cpp",
    "}else if(obj.kind==Maket::Decoration::Text){",
    "}else if(obj.kind==Maket::Decoration::Text || (obj.kind==Maket::Decoration::SvgElement && !obj.text.isEmpty())){")
one("src/window.cpp",
    'objectInfo_=label("Выбирай любой векторный элемент: перемещение, размер, цвет, прозрачность, порядок слоёв. Чтобы изменить надпись — скрой исходный контур и добавь новую.",true);',
    'objectInfo_=label("Каждый декоративный слой можно перемещать, масштабировать, перекрашивать и скрывать. Для замены надписи введи текст ниже; очисти поле, чтобы вернуть оригинальный контур.",true);')
one("src/window.cpp",
    'decorTextEdit_->setPlaceholderText("Текст выбранной надписи");',
    'decorTextEdit_->setPlaceholderText("Текст вместо оригинального векторного элемента");')
one("src/window.cpp",
    'if(i>=0&&i<design_.decorations.size()&&design_.decorations[i].kind==Decoration::Text){design_.decorations[i].text=v;modified();}',
    'if(i>=0&&i<design_.decorations.size()){design_.decorations[i].text=v;modified();}')
one("src/window.cpp",
    'decorTextEdit_->setEnabled(decor&&design_.decorations[active].kind==Decoration::Text);',
    'decorTextEdit_->setEnabled(decor);')
one("src/window.cpp",
    'if(decor&&design_.decorations[active].kind==Decoration::Text)decorTextEdit_->setText(design_.decorations[active].text);else decorTextEdit_->clear();',
    'if(decor)decorTextEdit_->setText(design_.decorations[active].text);else decorTextEdit_->clear();')
one("src/main.cpp",
    'QString file=dir.filePath(QString("fixture_%1.jpg").arg(i+1));',
    'QString file=dir.absoluteFilePath(QString("fixture_%1.jpg").arg(i+1));')
# A PDF is allowed to flatten several photographs into fewer image XObjects.
# Check actual rendered pixels in all three occupied photo areas instead.
one("scripts/check_editor_features.py",
    '    assert len(doc[0].get_images(full=True))>=3',
    '''    page=doc[0]
    image=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=True)
    board_h=1000*(page.rect.height/page.rect.width)
    colors=[]
    for ph in photos[:3]:
        x,y,w,h=ph["rect"]
        matches=[]
        for fx in (0.2,0.5,0.8):
            for fy in (0.2,0.5,0.8):
                sx=min(image.width-1,max(0,int((x+w*fx)/1000*image.width)))
                sy=min(image.height-1,max(0,int((y+h*fy)/board_h*image.height)))
                pixel=image.pixel(sx,sy)
                if len(pixel)>=4 and pixel[3]>200:
                    matches.append(pixel[:3])
        assert matches, ("No rendered pixels in photo rectangle",ph["rect"])
        colors.extend(matches)
    assert len(set(colors))>=3, ("Photo/overlay rendering unexpectedly flat",colors[:5])
    ''')
print("Editor finishing patch applied: individually editable original vector text overlays, crop controls, visual PDF photo test.")
