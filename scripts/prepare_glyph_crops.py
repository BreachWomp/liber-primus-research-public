"""Unresampled evidence crops for manual inspection; originals stay unchanged."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import time
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPECS = [
    ('LP2-49', 6, 6, (1370, 2120, 1480, 2230), 'disputed 1L / 1l'),
    ('LP2-49', 7, 3, (945, 2300, 1055, 2410), 'disputed 0L / 0l'),
    ('LP2-50', 11, 6, (1330, 2400, 1440, 2510), 'disputed 0l / 0I'),
    ('LP2-50', 12, 5, (1225, 2575, 1360, 2690), 'disputed 2s / 2S'),
    ('LP2-51', 8, 7, (1490, 1860, 1600, 1970), 'disputed 3i / 3I'),
    ('LP2-49', 4, 7, (1450, 1765, 1560, 1880), 'agreed 2L; foot'),
    ('LP2-49', 4, 2, (825, 1765, 930, 1880), 'agreed 3I; stem'),
    ('LP2-49', 1, 3, (965, 1230, 1065, 1340), 'agreed 2l; stem'),
    ('LP2-49', 10, 1, (685, 2840, 790, 2950), 'agreed 2i; dot'),
    ('LP2-50', 9, 6, (1360, 2045, 1475, 2155), 'agreed 2s; lower'),
    ('LP2-50', 1, 6, (1345, 610, 1465, 720), 'agreed 0S; upper'),
    ('LP2-50', 12, 8, (1605, 2575, 1710, 2690), 'agreed 0I; stem'),
    ('LP2-50', 13, 7, (1465, 2755, 1565, 2870), 'agreed 2l; stem'),
    ('LP2-51', 2, 8, (1585, 790, 1690, 900), 'agreed 0l; stem'),
    ('LP2-51', 3, 8, (1615, 965, 1725, 1080), 'agreed 0L; foot'),
    ('LP2-50', 2, 3, (945, 790, 1045, 900), 'agreed 3I; stem'),
]

def main():
    tick = time.perf_counter()
    folder = ROOT / 'sources/glyph_crops'
    folder.mkdir(exist_ok=True)
    layout = json.loads((ROOT/'sources/layout_audit.json').read_text(encoding='utf-8'))
    pages = {p['page_id']: p for p in layout['pages']}
    manifest = {'created_at': datetime.now(timezone.utc).isoformat(),
                'coordinate_convention': 'Native pixels; left,top inclusive; right,bottom exclusive.',
                'resampling': 'none', 'crops': []}
    sheet = Image.new('RGB', (1000, 4*160), 'white')
    draw = ImageDraw.Draw(sheet)
    for k, (page, row, col, box, label) in enumerate(SPECS):
        source = pages[page]
        raw = ROOT/source['image_path']
        assert hashlib.sha256(raw.read_bytes()).hexdigest() == source['image_sha256']
        with Image.open(raw) as im:
            assert im.size == (2400, 3600)
            crop = im.crop(box)
        path = f'sources/glyph_crops/{page}-r{row:02}-c{col:02}.png'
        crop.save(ROOT/path)
        x, y = (k % 4)*250, (k//4)*160
        draw.text((x+5, y+3), f'{page} r{row} c{col}', fill='black')
        draw.text((x+5, y+18), label, fill='black')
        sheet.paste(crop, (x+5, y+36))
        measurements = []
        gray = crop.convert('L')
        for threshold in (32, 128, 224):
            points = {(i,j) for j in range(gray.height) for i in range(gray.width)
                      if gray.getpixel((i,j)) < threshold}
            components = []
            while points:
                seed = min(points); points.remove(seed); pending = [seed]; seen = [seed]
                while pending:
                    i,j = pending.pop()
                    for neighbor in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
                        if neighbor in points:
                            points.remove(neighbor);pending.append(neighbor);seen.append(neighbor)
                if len(seen) >= 8:
                    xs,ys = zip(*seen)
                    components.append({'box': [min(xs), min(ys), max(xs)+1, max(ys)+1], 'pixels': len(seen)})
            measurements.append({'threshold': threshold, 'components': sorted(components, key=lambda c: c['box'])})
        manifest['crops'].append({'page_id': page, 'row_1based': row, 'column_1based': col,
            'label': label, 'box': list(box), 'image_path': source['image_path'],
            'image_sha256': source['image_sha256'], 'source_url': source['source_url'],
            'source_commit': source['source_commit'], 'retrieved_at_utc': source['retrieved_at_utc'],
            'crop_path': path, 'crop_sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
            'ink_measurements': measurements})
    sheet_path = 'sources/glyph_crops/contact_sheet.png'
    sheet.save(ROOT/sheet_path)
    manifest['contact_sheet'] = {'path': sheet_path, 'sha256': hashlib.sha256((ROOT/sheet_path).read_bytes()).hexdigest()}
    (ROOT/'sources/glyph_crop_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    assert time.perf_counter()-tick < 30

if __name__ == '__main__':
    main()
