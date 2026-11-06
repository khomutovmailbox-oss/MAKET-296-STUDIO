# -*- coding: utf-8 -*-
"""Keep all photo paint inside the entire editable word, even for custom/moved frames.
Prevents a photo box turning rectangular when its per-letter mask is -1.
"""
from pathlib import Path
import re
p=Path("src/renderer.cpp")
s=p.read_text(encoding="utf-8")
start=s.find("void Maket::Renderer::paint(")
if start<0: raise RuntimeError("Renderer::paint missing")
end=s.find("bool Maket::Renderer::exportFile(",start)
if end<0: raise RuntimeError("exportFile anchor missing")
section=s[start:end]
# Qt original code: for(int i=0;i<items.size();i++){...}
matches=list(re.finditer(r"for\s*\(\s*int\s+i\s*=\s*0\s*;\s*i\s*<\s*items\.size\(\)\s*;\s*i\+\+\s*\)\s*\{",section))
if not matches:
    print("DEBUG: Renderer::paint source (first 8500 chars):")
    print(section[:8500])
    raise RuntimeError("photo render loop missing")
match=matches[0]
begin=match.start()
brace=section.find("{",match.start())
depth=0
close=-1
for k in range(brace,len(section)):
    if section[k]=='{': depth+=1
    elif section[k]=='}':
        depth-=1
        if depth==0:
            close=k+1
            break
if close<0: raise RuntimeError("unbalanced photo loop")
# Reject mistaken loops: must contain an actual photo drawing operation.
loop=section[begin:close]
if "drawImage(" not in loop:
    print("DEBUG: first loop was not drawing photos",loop[:1000])
    raise RuntimeError("first items loop not photo drawing")
if "const auto glyphs" not in section[:begin]:
    raise RuntimeError("glyph outlines not defined before photo drawing")
prefix="""p.save();
    if(d.letters){
        QPainterPath completeWord;
        completeWord.setFillRule(Qt::WindingFill);
        for(const auto &letterOutline:glyphs) completeWord.addPath(letterOutline);
        // Even custom photo frames and a temporary selection no longer bypass
        // the silhouette: all photo content is clipped to the word.
        p.setClipPath(completeWord,Qt::IntersectClip);
    }
    """
section=section[:begin]+prefix+section[begin:close]+"\n    p.restore(); // release word clipping before independent decorations\n    "+section[close:]
s=s[:start]+section+s[end:]
p.write_text(s,encoding="utf-8")
print("PASS: hard guarantee of complete-word clipping around photo rendering.")
