"""Bounded, page-local spatial index for fast object picking in VectorForge Studio.

This is a *view acceleration structure*, never a source of document truth.
It preserves C++ object stacking order and the existing rectangle/ellipse hit
semantics; the view invalidates it on a new object array or page change.
"""
from __future__ import annotations

import math
from collections import defaultdict


class SpatialHitIndex:
    def __init__(self, objects, bbox, page: str, *, cell_size=128.0, max_cells_per_object=64):
        if not (math.isfinite(cell_size) and cell_size > 0):
            raise ValueError('cell_size must be positive and finite')
        if max_cells_per_object < 1:
            raise ValueError('max_cells_per_object must be >=1')
        self.source_objects = objects  # strong ref: identity cache cannot be recycled
        self.cell_size = cell_size
        self.grid = defaultdict(list)
        self.large = []
        self.entries = []
        self.by_id = {}
        self.groups = defaultdict(list)
        self.ordered_ids = []
        self.order_index = {}
        for obj in objects:
            if obj.get('page_id') != page:
                continue
            object_id = obj.get('id')
            if not isinstance(object_id, str):
                continue
            self.by_id[object_id] = obj
            if not obj.get('paint_parent'):
                self.order_index[object_id] = len(self.ordered_ids)
                self.ordered_ids.append(object_id)
                if obj.get('group_id'):
                    self.groups[obj['group_id']].append(object_id)
            if not obj.get('visible', True):
                continue
            bounds = bbox(obj)
            if bounds is None or len(bounds) != 4 or not all(math.isfinite(float(v)) for v in bounds):
                continue
            x0, y0, x1, y1 = (float(v) for v in bounds)
            # Preserve pre-existing hit behavior for malformed negative-size objects.
            if x1 < x0 or y1 < y0:
                continue
            index = len(self.entries)
            self.entries.append((obj, (x0, y0, x1, y1)))
            xmin = math.floor((x0-4) / cell_size)
            xmax = math.floor((x1+4) / cell_size)
            ymin = math.floor((y0-4) / cell_size)
            ymax = math.floor((y1+4) / cell_size)
            if (xmax-xmin+1) * (ymax-ymin+1) > max_cells_per_object:
                self.large.append(index)
            else:
                for gx in range(xmin, xmax+1):
                    for gy in range(ymin, ymax+1):
                        self.grid[(gx, gy)].append(index)

    def pick(self, x: float, y: float):
        """Return highest visible object at document coordinates or None."""
        if not (math.isfinite(x) and math.isfinite(y)):
            return None
        key = (math.floor(x/self.cell_size), math.floor(y/self.cell_size))
        candidates = self.grid.get(key, ())
        # Both candidate lists are in stacking order. Merge backwards without
        # an O(k log k) sort on every click when many objects overlap.
        i=len(candidates)-1
        j=len(self.large)-1
        while i >= 0 or j >= 0:
            if j < 0 or (i >= 0 and candidates[i] > self.large[j]):
                index = candidates[i]
                i -= 1
            else:
                index = self.large[j]
                j -= 1
            obj, b = self.entries[index]
            if not (b[0]-4 <= x <= b[2]+4 and b[1]-4 <= y <= b[3]+4):
                continue
            if obj.get('kind') == 'ellipse':
                cx = (b[0]+b[2])/2
                cy = (b[1]+b[3])/2
                rx = max(1, (b[2]-b[0])/2)
                ry = max(1, (b[3]-b[1])/2)
                if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 > 1.3:
                    continue
            return obj['id']
        return None

    def expand_group(self, ids):
        chosen = set(ids)
        for object_id in ids:
            obj = self.by_id.get(object_id)
            if obj and obj.get('group_id'):
                chosen.update(self.groups[obj['group_id']])
        # A click on one object must not scan every object to restore z-order.
        return sorted((object_id for object_id in chosen if object_id in self.order_index),
                      key=self.order_index.__getitem__)
