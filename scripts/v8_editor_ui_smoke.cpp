#include "window.h"
#include <QApplication>
#include <QPushButton>
#include <QKeyEvent>
#include <QCheckBox>
#include <QDebug>
#include <cmath>
int main(int argc,char**argv) {
    QApplication app(argc,argv);
    Maket::MainWindow window; window.show();
    auto *canvas=window.findChild<Maket::Canvas*>();
    if(!canvas) return 21;
    Maket::Design model=Maket::defaultDesign(2);
    // Use a separate canvas for deterministic keyboard nudging.
    Maket::Canvas separate;
    separate.setDesign(&model);
    separate.setPhotoSelection({0},0);
    const QRectF original=Maket::photoSlots(model)[0].r;
    QKeyEvent key(QEvent::KeyPress,Qt::Key_Right,Qt::NoModifier);
    QApplication::sendEvent(&separate,&key);
    const QRectF nudged=Maket::photoSlots(model)[0].r;
    if(std::abs((nudged.x()-original.x())-1000.0/296.0)>.01)return 22;
    QKeyEvent fine(QEvent::KeyPress,Qt::Key_Down,Qt::AltModifier);
    QApplication::sendEvent(&separate,&fine);
    if(std::abs(Maket::photoSlots(model)[0].r.y()-original.y()-100.0/296.0)>.01)return 23;
    separate.setReferenceVisible(true);
    separate.setReferenceOpacity(60);
    if(separate.grab().isNull())return 24;
    // Check that real window exposes undo/redo and alignment surfaces.
    bool undo=false,redo=false,align=false;
    for(auto *button:window.findChildren<QPushButton*>()){
       undo |= button->toolTip().contains("Ctrl+Z");
       redo |= button->toolTip().contains("Ctrl+Y");
       align |= button->text().contains("Лево");
    }
    bool ref=false;
    for(auto *box:window.findChildren<QCheckBox*>())ref|=box->text().contains("эталон");
    if(!undo||!redo||!align||!ref)return 25;
    qInfo()<<"PASS: fine nudge, 1mm nudge, reference overlay, undo/redo and alignment UI";
    return 0;
}
