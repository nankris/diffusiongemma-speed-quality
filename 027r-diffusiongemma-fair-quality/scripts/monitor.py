import pathlib,json,time,datetime,os
R=pathlib.Path('/content/r027r');rd=int(os.environ.get('ROUND','1'))
while True:
 parts=[]
 for arm in ['dg','ar']:
  rows=[json.load(open(p)) for p in R.glob(f'r{rd}_{arm}_*.meta.json')]
  avg=sum(r['wall_s'] for r in rows)/len(rows) if rows else 0
  parts.append(f'{arm}={len(rows)}/150, mean turn {avg:.1f}s')
 print(datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S'),'; '.join(parts),flush=True)
 if (R/f'ROUND{rd}_DONE').exists():print('ROUND_DONE',rd,flush=True);break
 if time.time()>float((R/'recovery_deadline').read_text()):print('CU_DEADLINE',flush=True);break
 log=pathlib.Path('/content/benchmark.log').read_text() if pathlib.Path('/content/benchmark.log').exists() else ''
 if 'Traceback' in log:print(log[-1800:],flush=True);break
 time.sleep(40)
