import json, os, sys
b = sys.argv[1]; dst = sys.argv[2]
lander = json.load(open(os.path.join(b,'countries.json')))
codes = {g['properties']['a'] for g in lander['objects']['countries50']['geometries']}
reg = {}
for fn in sorted(os.listdir(os.path.join(b,'out15'))):
    a = fn[:-5]
    if a not in codes: continue
    t = json.load(open(os.path.join(b,'out15',fn)))
    obj = t['objects'].pop(a); t['objects']['r'] = obj
    reg[a] = t
s = json.dumps({'lander':lander,'regioner':reg}, ensure_ascii=False, separators=(',',':'))
open(dst,'w').write('/* Kartdata: Natural Earth (public domain), naturalearthdata.com. admin-0 1:50m och admin-1 1:10m, version 5.2.0-pre, förenklade med mapshaper. */\nwindow.MQ_DATA=' + s + ';\n')
print(len(reg), os.path.getsize(dst))
