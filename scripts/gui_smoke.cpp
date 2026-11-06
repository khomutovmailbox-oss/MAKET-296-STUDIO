#include "window.h"
#include <QApplication>
#include <QTimer>
#include <QPixmap>
#include <QDebug>
int main(int argc,char**argv){
    QApplication app(argc,argv);
    Maket::MainWindow window;
    window.show();
    QTimer::singleShot(600,&app,[&](){
        const QPixmap shot=window.grab();
        if(shot.isNull()||!shot.save("audit_render/native_window.png","PNG")){
            qCritical()<<"Could not capture native Qt window";
            app.exit(3);return;
        }
        auto *canvas=window.findChild<Maket::Canvas*>();
        if(!canvas){qCritical()<<"Canvas not found";app.exit(6);return;}
        const QImage baseline=canvas->grab().toImage();
        canvas->setReferenceVisible(true);
        QApplication::processEvents();
        const QImage reference=canvas->grab().toImage();
        if(reference.isNull() || !reference.save("audit_render/native_reference_overlay.png","PNG")){
            qCritical()<<"Could not render original reference overlay";app.exit(7);return;
        }
        if(baseline.size()!=reference.size()){app.exit(8);return;}
        int differences=0;
        for(int y=0;y<reference.height();y+=5)for(int x=0;x<reference.width();x+=5)
            if(baseline.pixel(x,y)!=reference.pixel(x,y))++differences;
        if(differences<20){qCritical()<<"F7 reference has no visible effect"<<differences;app.exit(9);return;}
        canvas->setReferenceVisible(false);
        qInfo()<<"Native Qt window captured, overlay pixels changed"<<differences;
        app.quit();
    });
    return app.exec();
}
