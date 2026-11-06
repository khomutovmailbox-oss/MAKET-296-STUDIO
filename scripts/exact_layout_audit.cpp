#include "model.h"
#include "renderer.h"
#include <QApplication>
#include <QDir>
#include <QImage>
#include <QPainter>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QFile>
int main(int argc,char**argv){
 QApplication app(argc,argv);
 QDir().mkpath("exact_audit/photos");QDir().mkpath("exact_audit/posters");
 QStringList pictures;
 for(int i=0;i<20;++i){
  QImage im(1000,1400,QImage::Format_RGB32);QPainter p(&im);
  p.fillRect(im.rect(),QColor::fromHsv((35*i+7)%360,140,225));
  p.setPen(Qt::NoPen);p.setBrush(QColor(255,255,255,85));
  p.drawEllipse(230,100,540,540);p.drawRoundedRect(120,720,760,540,140,140);
  p.setPen(QColor("#182333"));QFont f("Arial",360,QFont::Black);p.setFont(f);
  p.drawText(im.rect(),Qt::AlignCenter,QString::number(i+1));p.end();
  QString name=QDir::current().absoluteFilePath(QString("exact_audit/photos/f%1.jpg").arg(i+1,2,10,QLatin1Char('0')));
  if(!im.save(name,"JPEG",90))return 10;pictures<<name;
 }
 QJsonArray all;
 for(const auto &t:Maket::presets()){
  Maket::Design d=Maket::defaultDesign(t.id);const auto cells=Maket::photoSlots(d);
  if(cells.isEmpty())return 11;
  QJsonObject meta{{"id",t.id},{"name",t.name},{"height_mm",d.heightMm},{"slots",cells.size()}};
  QJsonArray rects;
  for(const auto &cell:cells){QJsonArray a;a<<cell.r.x()<<cell.r.y()<<cell.r.width()<<cell.r.height();rects.append(a);}
  meta["rects"]=rects;all.append(meta);
  QString error;
  if(!Maket::Renderer::exportFile(QString("exact_audit/posters/blank_%1.png").arg(t.id),d,75,&error))return 20;
  for(int i=0;i<d.photos.size();++i)d.photos[i].path=pictures[(t.id+i)%pictures.size()];
  if(!Maket::Renderer::exportFile(QString("exact_audit/posters/filled_%1.png").arg(t.id),d,95,&error))return 21;
  if(t.id==2){
   if(!Maket::Renderer::exportFile("exact_audit/DTF_GIRLFRIEND_296mm_300dpi.png",d,300,&error))return 22;
   if(!Maket::Renderer::exportFile("exact_audit/DTF_GIRLFRIEND_296mm.pdf",d,300,&error))return 23;
  }
 }
 QFile data("exact_audit/layout.json");if(!data.open(QIODevice::WriteOnly))return 30;
 data.write(QJsonDocument(all).toJson());
 return 0;
}
