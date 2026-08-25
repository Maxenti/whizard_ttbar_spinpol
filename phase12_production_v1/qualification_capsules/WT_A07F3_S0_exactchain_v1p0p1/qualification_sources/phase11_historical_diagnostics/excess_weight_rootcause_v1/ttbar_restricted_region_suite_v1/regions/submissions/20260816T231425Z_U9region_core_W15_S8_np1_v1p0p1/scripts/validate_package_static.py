#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
for p in root.rglob('*.py'):
 if p.name=='validate_package_static.py': continue
 subprocess.run([sys.executable,'-m','py_compile',str(p)],check=True)
for p in root.rglob('*.sh'): subprocess.run(['bash','-n',str(p)],check=True)
subprocess.run([sys.executable,str(root/'tests/test_suite.py')],check=True)
print('PACKAGE_STATIC_VALIDATION=PASS')
