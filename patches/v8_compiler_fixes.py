from pathlib import Path
p=Path("src/window.cpp")
s=p.read_text(encoding="utf-8")
old="const QRectF target(xSpin_->value()"
assert s.count(old)==1, "Geometry declaration changed"
s=s.replace(old,"QRectF target(xSpin_->value()")
start=s.index("void MainWindow::alignSelected(int axis){")
end=s.index("void MainWindow::updateHistoryButtons()",start)
chunk=s[start:end]
chunk=chunk.replace("const QVector<Slot> slots=photoSlots(design_);","const QVector<Slot> frames=photoSlots(design_);")
chunk=chunk.replace("slots.size()","frames.size()").replace("slots[i].r","frames[i].r")
assert "const QVector<Slot> frames=photoSlots" in chunk
s=s[:start]+chunk+s[end:]
p.write_text(s,encoding="utf-8")
print("Qt C++ compile fixes applied")
