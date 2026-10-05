"""Execute each migrated report in a fresh Python process without acquisition."""
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
results=[]
for report in sorted((ROOT/'notebooks').glob('*.qmd')):
    blocks=re.findall(r'```\{python\}\n(.*?)\n```',report.read_text(),re.S)
    code='import os\nos.environ["MPLCONFIGDIR"]=".cache/matplotlib"\n'+'\n'.join(blocks)
    for index,block in enumerate(blocks): compile(block,str(report)+':'+str(index+1),'exec')
    result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
    results.append({'report':str(report.relative_to(ROOT)),'python_cells':len(blocks),'passed':result.returncode==0,'error':result.stderr[-3000:] if result.returncode else None})
    print(report.name,result.returncode,len(blocks),flush=True)
path=ROOT/'docs/verification/notebook_execution.json';path.write_text(json.dumps(results,indent=2)+'\n')
if not all(r['passed'] for r in results): raise SystemExit(1)
