"""Real pixel-by-pixel regression for letter-shaped photo masks, 5 styles x 4 fills."""
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageStat
import sys
root=Path(sys.argv[1])
results=[]
for style in range(5):
    mask_file=root/f"mask_s{style}.png"
    if not mask_file.is_file():raise AssertionError(f"Missing independent silhouette mask {mask_file}")
    with Image.open(mask_file) as img:
        expected=img.convert("RGBA").getchannel("A")
    dilated=expected.filter(ImageFilter.MaxFilter(7))
    for fill in range(4):
        photo_file=root/f"word_s{style}_f{fill}.png"
        if not photo_file.is_file():raise AssertionError(f"Missing actual photo-letter render: {photo_file}")
        with Image.open(photo_file) as img:
            actual=img.convert("RGBA").getchannel("A")
        assert actual.size==expected.size,(actual.size,expected.size,photo_file)
        # Alpha outside the geometric word must be zero (7x7 pixel antialias tolerance).
        outside=ImageChops.subtract(actual,dilated)
        leak_pixels=sum(outside.histogram()[40:])
        mask_sum=ImageStat.Stat(expected).sum[0]
        weighted_coverage=ImageStat.Stat(ImageChops.multiply(expected,actual)).sum[0]/max(mask_sum,1)
        if leak_pixels>45:
            raise AssertionError(f"LETTER MASK LEAK: style={style} fill={fill} {leak_pixels} pixels outside letter outlines")
        if weighted_coverage<0.78:
            raise AssertionError(f"LETTER FILL MISSING: style={style} fill={fill} alpha coverage={weighted_coverage:.2%}")
        results.append((style,fill,leak_pixels,round(weighted_coverage,3)))
print("PASS: 20 Qt photo-letter compositions have no visible pixels outside letter silhouettes")
print(results)
