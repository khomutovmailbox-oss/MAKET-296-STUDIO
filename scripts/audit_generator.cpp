#include "model.h"
#include "renderer.h"
#include <QApplication>
#include <QDir>
#include <QFile>
#include <QImage>
#include <QPainter>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLinearGradient>
#include <QDebug>
int main(int argc,char**argv){
 QApplication app(argc,argv);
 QDir cwd=QDir::current();
 if(!cwd.mkpath("audit_render/source")||!cwd.mkpath("audit_render/posters")||!cwd.mkpath("audit_render/letters"))return 10;
 QStringList images;
 for(int i=0;i<22;i++){
   QImage im(1000,1300,QImage::Format_RGB32);QPainter p(&im);
   QLinearGradient gradient(0,0,1000,1300);
   gradient.setColorAt(0,QColor::fromHsv((i*43)%360,150,240));
   gradient.setColorAt(1,QColor::fromHsv((i*43+90)%360,125,110));
   p.fillRect(im.rect(),gradient);p.setPen(QPen(Qt::white,12));
   p.drawRect(QRect(30,30,940,1240));p.setPen(QPen(QColor("#1e293b"),13));
   p.drawLine(0,0,1000,1300);p.drawLine(0,1300,1000,0);
   p.setBrush(Qt::white);p.setPen(Qt::NoPen);p.drawEllipse(QRect(240,190,520,520));
   p.setFont(QFont("Arial",170,QFont::Bold));p.setPen(QColor("#14233f"));
   p.drawText(QRect(0,250,1000,380),Qt::AlignCenter,QString::number(i+1));p.end();
   QString path=cwd.absoluteFilePath(QString("audit_render/source/photo_%1.jpg").arg(i+1,2,10,QLatin1Char('0')));
   if(!im.save(path,"JPEG",91))return 11;images<<path;
 }
 auto save=[&](QString path,const Maket::Design&d,int dpi)->bool{
   QString err; if(!Maket::Renderer::exportFile(path,d,dpi,&err)){
      qCritical().noquote()<<"Export error"<<path<<err;return false;
   }return true;
 };
 QJsonArray meta;
 for(const Maket::Preset &preset:Maket::presets()){
   Maket::Design d=Maket::defaultDesign(preset.id);
   QJsonObject item{{"id",preset.id},{"name",preset.name},{"height_mm",d.heightMm},{"slots",int(d.photos.size())}};
   QJsonArray rectangles;
   for(const auto&s:Maket::photoSlots(d)){
     QJsonArray r;r<<s.r.x()/1000.0<<s.r.y()/(1000*d.heightMm/Maket::WidthMm)<<s.r.width()/1000.0<<s.r.height()/(1000*d.heightMm/Maket::WidthMm);rectangles.append(r);
   }
   item["rectangles"]=rectangles;meta.append(item);
   if(!save(QString("audit_render/posters/empty_%1.png").arg(preset.id),d,96))return 20;
   for(int i=0;i<d.photos.size();i++)d.photos[i].path=images[(i+preset.id)%images.size()];
   if(!save(QString("audit_render/posters/filled_%1.png").arg(preset.id),d,96))return 21;
   if(preset.id==2){
     if(!save("audit_render/dtf_296x465_300dpi.png",d,300))return 22;
     if(!save("audit_render/dtf_296x465.pdf",d,300))return 23;
     if(!save("audit_render/dtf_296x465.svg",d,300))return 24;
   }
 }
 for(int style=0;style<5;style++)for(int fill=0;fill<4;fill++){
   Maket::Design d=Maket::defaultDesign(2);d.letters=true;d.heightMm=340;d.word="MOM";
   d.letterStyle=style;d.letterFill=fill;d.photos.resize(Maket::photoSlots(d).size());
   for(int i=0;i<d.photos.size();i++)d.photos[i].path=images[(i+style*5)%images.size()];
   if(!save(QString("audit_render/letters/word_s%1_f%2.png").arg(style).arg(fill),d,100))return 30;
 }
 QFile metaFile("audit_render/layout.json");if(!metaFile.open(QIODevice::WriteOnly))return 40;
 metaFile.write(QJsonDocument(meta).toJson(QJsonDocument::Indented));
 qInfo()<<"Audit outputs generated"<<meta.size()<< "layouts, 20 word variants";
 return 0;
}