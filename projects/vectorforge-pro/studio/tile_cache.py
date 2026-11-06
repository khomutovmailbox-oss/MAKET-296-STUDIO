"""Memory-bounded, page-local RGBA tile cache for the VectorForge SVG subset.

A renderer owns one document revision and one raster scale. Instantiate a new
renderer when page, SVG, resolution or document revision changes; preserve it on
viewport pans. No full-page pixel buffer is required for viewport rendering.
"""
from __future__ import annotations

from collections import OrderedDict
import xml.etree.ElementTree as ET

from PIL import Image

from fx_compositor import RenderUnsupported, render_svg_region, _MAX_SVG_BYTES


class TiledPreviewRenderer:
    def __init__(self, svg: bytes, width: int, height: int, *, tile_size=256,
                 max_cache_bytes=32*1024*1024):
        if not isinstance(svg, bytes) or len(svg)>_MAX_SVG_BYTES:
            raise RenderUnsupported('Invalid or oversized SVG')
        if b'<!DOCTYPE' in svg.upper() or b'<!ENTITY' in svg.upper():
            raise RenderUnsupported('XML entity declarations are not supported')
        if not isinstance(width,int) or not isinstance(height,int) or width<=0 or height<=0:
            raise RenderUnsupported('Invalid page dimensions')
        if not isinstance(tile_size,int) or not (32<=tile_size<=1024):
            raise ValueError('Tile dimensions must be 32–1024')
        if not isinstance(max_cache_bytes,int) or max_cache_bytes<0:
            raise ValueError('Invalid cache budget')
        try:
            self._root=ET.fromstring(svg)
        except ET.ParseError as exc:
            raise RenderUnsupported('Malformed SVG') from exc
        self.width=width
        self.height=height
        self.tile_size=tile_size
        self.max_cache_bytes=max_cache_bytes
        self._tiles=OrderedDict()
        self.cache_bytes=0
        self.hits=0
        self.misses=0
        self.evictions=0

    def _tile(self,x,y):
        key=(x,y)
        tile=self._tiles.get(key)
        if tile is not None:
            self.hits+=1
            self._tiles.move_to_end(key)
            return tile
        self.misses+=1
        n=self.tile_size
        box=(x,y,min(self.width,x+n),min(self.height,y+n))
        # Cairo antialiasing/filter kernels can sample over tile edges.
        # A small halo followed by cropping eliminates visible seams.
        halo=4
        extended=(max(0,box[0]-halo),max(0,box[1]-halo),
                  min(self.width,box[2]+halo),min(self.height,box[3]+halo))
        expanded=render_svg_region(self._root,self.width,self.height,extended)
        tile=expanded.crop((box[0]-extended[0],box[1]-extended[1],
                            box[2]-extended[0],box[3]-extended[1]))
        cost=tile.width*tile.height*4
        if cost<=self.max_cache_bytes:
            self._tiles[key]=tile
            self.cache_bytes+=cost
            while self.cache_bytes>self.max_cache_bytes:
                _,removed=self._tiles.popitem(last=False)
                self.cache_bytes-=removed.width*removed.height*4
                self.evictions+=1
        return tile

    def render_viewport(self,rect: tuple[int,int,int,int]):
        """Return RGBA for a viewport in full-page pixel coordinates.

        Use only on one render worker thread. The returned image starts at the
        viewport's top-left page pixel and excludes all offscreen pixels.
        """
        if (not isinstance(rect,(tuple,list)) or len(rect)!=4 or
            not all(isinstance(v,int) for v in rect)):
            raise RenderUnsupported('Invalid viewport')
        x0,y0,x1,y1=rect
        if (not (0<=x0<x1<=self.width and 0<=y0<y1<=self.height) or
            (x1-x0)*(y1-y0)>8_000_000):
            raise RenderUnsupported('Invalid viewport bounds')
        result=Image.new('RGBA',(x1-x0,y1-y0))
        step=self.tile_size
        for tile_y in range((y0//step)*step,y1,step):
            for tile_x in range((x0//step)*step,x1,step):
                tile=self._tile(tile_x,tile_y)
                cx0=max(x0,tile_x);cy0=max(y0,tile_y)
                cx1=min(x1,tile_x+tile.width);cy1=min(y1,tile_y+tile.height)
                if cx1<=cx0 or cy1<=cy0:continue
                result.paste(tile.crop((cx0-tile_x,cy0-tile_y,
                                         cx1-tile_x,cy1-tile_y)),
                             (cx0-x0,cy0-y0))
        return result

    def clear(self):
        self._tiles.clear()
        self.cache_bytes=0
