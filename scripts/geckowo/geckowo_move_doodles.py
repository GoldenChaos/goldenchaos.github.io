import os, shutil, glob

import shutil
from pathlib import Path

IDS = [
    "1964314103863705905","1934320424961073523","1906457320898326660","1905430005103948109",
    "1904931179666567262","1904682651404947719","1909075939134185849","1899340715127194094",
    "1902469409009992048","1902573765239669222","1903939797917266021","1904325170447393018",
    "1945726526621679961","1945726519847915927","1986888060072575412",
    "1991617767242625433","1906885517863461162","1911485363702419697",
    "1929225464897327236","1932060194756055376",
    "1920938098956870081","1906461229985538398","1898610649556492581","1898604513449197853",
    "1889859988644036730","1889708973697237476","1894266609742590249","1889149385885233377",
    "1884775370655736032","1884781660379521495","1859671154677702680","1859033478358302873",
    "1859113446287003915","1848416343588020679","1846737870272303134","1843741258113749412",
    "1843685106550223306","1843635401082262010","1842663848446493167","1842234285836599687",
    "1842028984776769971","1841987072099549609","1841948247012868581","1841867700156469497",
    "1841592538240553109","1841586191524561108","1841343308930707604","1841275257820242373",
    "1840962769052479650","1840120083487830348","1840107774522601498","1839886011519627449",
    "1838424904825217472","1836975477115822149","1836927607943680213","1835830663708049851",
    "1835828891593605530","1835727275880300968","1835148653536657472","1835103106591514778",
    "1835073115506069504","1835019485176050163","1833722928313077851","1831530070927646909",
    "1829607289722192035","1828187791693349050","1828118161969033379","1909972205053542681",
    "1912354039683043709","1914089569701572647","1914352806049263765",
    "1914806450121060652","1917824099100852709"
]

DEST = Path("geckowo_archive/doodles")
SOURCES = [Path("geckowo_archive/comics"), Path("geckowo_comics"), Path("geckowo_comics/doodles")]

DEST.mkdir(parents=True, exist_ok=True)

moved = 0
deleted = 0

for sid in IDS:
    dest_file = DEST / f"{sid}.jpg"
    for src in SOURCES:
        if not src.exists():
            continue
        for file in src.rglob("*.jpg"):
            if sid not in file.name:
                continue
            if dest_file.exists():
                file.unlink()
                deleted += 1
                continue
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), dest_file)
            moved += 1
            break

print(f"Moved: {moved}, Deleted duplicates: {deleted}")
DEST = 'geckowo_archive/doodles'
SOURCES = ['geckowo_archive/comics', 'geckowo_comics', 'geckowo_comics/doodles']

os.makedirs(DEST, exist_ok=True)

# Move files for each ID
for _id in IDS:
    for src in SOURCES:
        if not os.path.isdir(src):
            continue
        for path in glob.glob(os.path.join(src, f'*{_id}*.jpg')):
            dest_path = os.path.join(DEST, os.path.basename(path))
            if not os.path.exists(dest_path):
                shutil.move(path, dest_path)
            else:
                # drop duplicates once we already have a copy
                os.remove(path)

# Normalize: prefer status_id.jpg
for _id in IDS:
    status = os.path.join(DEST, f'{_id}.jpg')
    matches = glob.glob(os.path.join(DEST, f'*{_id}*.jpg'))
    if os.path.exists(status):
        for m in matches:
            if os.path.abspath(m) != os.path.abspath(status):
                os.remove(m)
    else:
        if matches:
            keep = matches[0]
            os.rename(keep, status)
            for m in matches[1:]:
                os.remove(m)

print('Done')
