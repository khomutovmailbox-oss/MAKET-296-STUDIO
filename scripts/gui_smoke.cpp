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
        qInfo()<<"Native Qt window captured"<<shot.size();
        app.quit();
    });
    return app.exec();
}
