"""Execute each Python report in a fresh Python process without acquisition."""
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
results=[]
if not list((ROOT/'code/reports').glob('*.py')): raise SystemExit('No report scripts found')
for report in sorted((ROOT/'code/reports').glob('*.py')):
    blocks=[report.read_text()]
    code='import os\nos.environ["MPLCONFIGDIR"]=".cache/matplotlib"\n'+'\n'.join(blocks)
    for index,block in enumerate(blocks): compile(block,str(report)+':'+str(index+1),'exec')
    result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
    results.append({'report':str(report.relative_to(ROOT)),'python_scripts':len(blocks),'passed':result.returncode==0,'error':result.stderr[-3000:] if result.returncode else None})
    print(report.name,result.returncode,len(blocks),flush=True)
path=ROOT/'docs/evidence/report_execution.json';path.write_text(json.dumps(results,indent=2)+'\n')
if not all(r['passed'] for r in results): raise SystemExit(1)
