import json, sys, os
src, outdir = sys.argv[1], sys.argv[2]
d = json.load(open(src))
by = {}
for f in d['features']:
    p = f['properties']
    a = p['adm0_a3']
    props = {
        'n': (p.get('name_sv') or p.get('name') or '').strip(),
        'o': (p.get('name') or '').strip(),
        't': p.get('type_en') or p.get('type') or '',
        'r': p.get('region') or '',
        'c': p.get('iso_3166_2') or '',
    }
    by.setdefault(a, []).append({'type':'Feature','properties':props,'geometry':f['geometry']})
for a, fs in by.items():
    json.dump({'type':'FeatureCollection','features':fs}, open(os.path.join(outdir, a+'.geojson'),'w'))
print(len(by))
c = json.load(open(sys.argv[3]))
codes = {f['properties']['ADM0_A3'] for f in c['features']}
print('admin1 not in countries:', sorted(set(by)-codes))
print('countries not in admin1:', sorted(codes-set(by)))
