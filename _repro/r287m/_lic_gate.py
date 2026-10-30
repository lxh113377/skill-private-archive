import sys, os, json
sys.path.insert(0, os.path.abspath('05-exec'))
import r114_replacement_scan as R
D='_repro/r287m'
import base64
raw=base64.b64decode(open(os.path.join(D,'_lic.b64'),encoding='utf-8').read())
open(os.path.join(D,'_upstream_LICENSE.txt'),'wb').write(raw)
up=' '.join(raw.decode('utf-8','replace').upper().split())
spdx, cls, hits = R.classify_body(up)
print('classify_body ->', json.dumps({'spdx':spdx,'class':cls,'hits':hits}, ensure_ascii=False))
print('license_class(spdx) ->', R.license_class(spdx))
print('license_class(spdx, body_class=cls) ->', R.license_class(spdx, body_class=cls))
print('license_class(API-null) ->', R.license_class('', body_class=cls))
print('license_class(API UNLICENSED, no body) ->', R.license_class('UNLICENSED'))
print('LICENSE_CAPS ->', json.dumps(R.LICENSE_CAPS))
print('bytes', len(raw), 'sha256_12', __import__('hashlib').sha256(raw).hexdigest()[:12])
