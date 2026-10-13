#!/usr/bin/env python3
"""Compute preregistered DET1 lw0 metrics from immutable run artifacts."""
from __future__ import annotations
import collections, csv, hashlib, json, math, os, pathlib, statistics, sys, tempfile
import numpy as np

os.environ.setdefault('MPLCONFIGDIR',str(pathlib.Path(tempfile.gettempdir())/'det1-mpl-cache'))
REPO=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO))
from src.metrics.evaluate_run import detection_metrics
from scripts.run_benchmark import dataset_sources,load_stream,load_preset

ROOT=REPO/'outputs/benchmark/det1'
COMMIT='0b98e29a708ee55f3bcc7f47165696981aa2e282'
PRESETS={
 'A1':'det1_dual_adwin_lw0',
 'A2':'det1_zone_ddm_lw0',
 'A3':'det1_zone_hddm_a_lw0',
 'A4':'det1_zone_rddm_lw0',
 'A5':'det1_zone_magseed_lw0',
}
REGISTRY=json.loads((REPO/'configs/datasets_0921.json').read_text())['datasets']
INSECTS=[k for k in REGISTRY if k.startswith('insects_') and k.endswith('_balanced')]
DATASETS=['synthetic_multiclass',*INSECTS,'injected_paper_electricity']
EXPECTED={'synthetic_multiclass':40,'injected_paper_electricity':160,**{k:1 for k in INSECTS}}


def sha256(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()


def windows(gt,n,start,delta=1000):
 """Inclusive, clipped [d_s,d_s+delta] windows after scored start."""
 return [(max(s,start),min(s+delta,n-1)) for s,e in gt if s>=start and s<n]


def union_length(ivs):
 total=0;end=-1
 for s,e in sorted(ivs):
  if e>=s:
   total+=max(0,e-max(s,end+1)+1);end=max(end,e)
 return total


def type_flags(dataset,stream):
 text=(dataset+'_'+stream).lower()
 flags=[]
 if 'abrupt' in text or 'sudden' in text:flags.append('突變')
 if 'gradual' in text:flags.append('漸變')
 if 'incremental' in text:flags.append('incremental')
 if 'recurring' in text or 'reoccurring' in text:flags.append('recurring')
 return flags


def group_of(dataset):
 if dataset.startswith('insects_'):return 'INSECTS'
 if dataset=='injected_paper_electricity':return 'injected'
 if dataset=='synthetic_multiclass':return 'synthetic'
 raise ValueError(dataset)


def score_one(path,arm,source_hashes):
 m=json.loads((path/'manifest.json').read_text());v=json.loads((path/'metrics.json').read_text());events=json.loads((path/'warning_events.json').read_text())
 ds=m['dataset'];stream=m['stream'];n=m['n_input'];gt=[tuple(z) for z in m['gt_intervals']]
 assert m['preset']==load_preset(PRESETS[arm]) and m['git']=={'commit':COMMIT,'dirty':False}
 assert m['registry_entry']==REGISTRY[ds]
 assert m['max_steps'] is None and m['record_warning_events'] and m['versions']['river']=='0.21.2'
 assert m['effective_config']['model_type']=='ht' and m['effective_config']['ecpf_learn_during_warning'] is False
 assert ds in DATASETS
 source=REPO/m['data'].get('file',m['data'].get('generator',{}).get('source',''))
 if source not in source_hashes:source_hashes[source]=sha256(source)
 assert source_hashes[source]==m['data'].get('sha256',m['data'].get('source_sha256'))
 with np.load(path/'preds.npz') as rec:
  yt=rec['y_true'].copy();yp=rec['y_pred'].copy();al=rec['alarm_idx_input'].copy() if m['coordinates']=='input' else rec['alarm_idx'].copy()
 assert len(yt)==len(yp)==v['n_samples']
 assert int((al>=m['detect_from']).sum())==v['n_alarms']
 assert n>=len(yt) and len(gt)==v['n_gt']
 scored_start=max(m['detect_from'],m['warm_start'])
 alarms=np.sort(al[al>=scored_start])
 wins=windows(gt,n,scored_start)
 scored_gt=[(s,e) for s,e in gt if s>=scored_start and s<n]
 out={'arm':arm,'dataset':ds,'stream':stream,'group':group_of(ds),'cell':m['cell'],'n_input':n,'n_output':len(yt),'n_scored':v['n_scored'],'acc':v['acc_prequential'],'kappa':v['kappa'],'runtime':m['runtime_s'],'rss':m['peak_rss_mb'],'alarms':len(alarms),'gt':len(scored_gt),'types':type_flags(ds,stream),'path':str(path.relative_to(REPO)), 'y_true_sha256':hashlib.sha256(yt.tobytes()).hexdigest(), 'frozen':v.get('warning_frozen_steps',0)}
 cnt=collections.Counter((e['event'],e['reason']) for e in events)
 assert sum(x['event']=='open' for x in events)==sum(x['event'] in ('close','censored') for x in events)
 out['warning']={f'{a}:{b}':z for (a,b),z in cnt.items()}
 out['confirmed_buffer']=[e['buffer_len'] for e in events if e['event']=='close' and e['reason']=='confirmed']
 out['discarded_buffer']=[e['buffer_len'] for e in events if e['event']=='close' and e['reason']!='confirmed']
 if not scored_gt:
  assert ds=='insects_incremental_balanced' and v['tp'] is None and v['fp'] is None
  out.update(fp=None,tp=None,fn=None,hits=None,C=None,X=None,O=None,mdt=None)
 else:
  det=detection_metrics(alarms,scored_gt,n_instances=n,delta_max=1000,anchor='start')
  bench=detection_metrics(al[al>=m['detect_from']],gt,n_instances=n,delta_max=REGISTRY[ds]['delta_max'],anchor='start')
  assert (bench['tp'],bench['fp'],bench['fn'])==(v['tp'],v['fp'],v['fn']), (path,bench,v)
  if scored_gt==gt and REGISTRY[ds]['delta_max']==1000:
   assert (det['tp'],det['fp'],det['fn'])==(v['tp'],v['fp'],v['fn']), (path,det,v)
  O=n-scored_start-union_length(wins)
  assert O>0,(path,O)
  lam=det['fp']/O
  C=sum(-math.expm1(-lam*(e-s+1)) for s,e in wins)
  hit=det['n_episodes']-det['fn']
  out.update(fp=det['fp'],tp=det['tp'],fn=det['fn'],hits=hit,C=C,X=hit-C,O=O,mdt=det['mdt'],cerqueira_2500={'tp':v['tp'],'fp':v['fp'],'fn':v['fn']} if ds=='injected_paper_electricity' else None)
 return out


def load_all():
 rows=[];sources={}
 for ds in DATASETS:
  for arm,pre in PRESETS.items():
   base=ROOT/ds/pre
   paths=sorted(base.glob('*/manifest.json'))
   if len(paths)!=EXPECTED[ds]:raise ValueError(f'{ds}/{pre}: {len(paths)} manifests, expected {EXPECTED[ds]}')
   for p in paths:
    row=score_one(p.parent,arm,sources)
    rows.append(row)
 assert len(list(ROOT.rglob('manifest.json')))==1025
 for ds in DATASETS:
  assert {p.name for p in (ROOT/ds).iterdir() if p.is_dir()}==set(PRESETS.values())
  streams={r['stream'] for r in rows if r['dataset']==ds and r['arm']=='A1'}
  registered={z['stem'] for z in dataset_sources(REGISTRY[ds],20 if ds=='injected_paper_electricity' else None)}
  assert streams==registered,(ds,streams^registered)
  for arm in PRESETS:
   assert {r['stream'] for r in rows if r['dataset']==ds and r['arm']==arm}==streams
  for st in streams:
   assert len({r['y_true_sha256'] for r in rows if r['dataset']==ds and r['stream']==st})==1,(ds,st)
 return rows


def add_post_accuracy(rows):
 inj_entry=REGISTRY['injected_paper_electricity'];srcs={s['stem']:s for s in dataset_sources(inj_entry,20)}
 mask_cache={}
 for row in rows:
  if row['gt']==0:row['post_correct']=row['post_count']=0;continue
  ds=row['dataset'];st=row['stream'];key=(ds,st)
  if key not in mask_cache:
   base=json.loads((ROOT/ds/PRESETS['A1']/st/'manifest.json').read_text())
   with np.load(ROOT/ds/PRESETS['A1']/st/'preds.npz') as rec: base_y=rec['y_true'].copy()
   n=len(base_y);positions=np.arange(n)
   if ds=='injected_paper_electricity':
    stream=load_stream(srcs[st],inj_entry)
    positions=stream['kept']
    assert np.array_equal(stream['df']['y'].to_numpy(dtype=float),base_y)
   mask=np.zeros(n,dtype=bool)
   for s,e in base['gt_intervals']:
    if s<max(base['warm_start'],base['detect_from']):continue
    mask |= (positions>=s)&(positions<=s+999)
   mask_cache[key]=mask
  with np.load(ROOT/ds/PRESETS[row['arm']]/st/'preds.npz') as rec: yt=rec['y_true'].copy();yp=rec['y_pred'].copy()
  mask=mask_cache[key]&np.isfinite(yp)
  row['post_correct']=int(np.count_nonzero(yt[mask]==yp[mask]));row['post_count']=int(mask.sum())


def aggregate(items):
 valid=[r for r in items if r['gt']]
 nsc=sum(r['n_scored'] for r in items)
 a=dict(runs=len(items),gt=sum(r['gt'] for r in valid),alarms=sum(r['alarms'] for r in items),acc=sum(r['acc']*r['n_scored'] for r in items)/nsc if nsc else None,kappa=sum(r['kappa']*r['n_scored'] for r in items)/nsc if nsc else None,runtime=sum(r['runtime'] for r in items),rss=max((r['rss'] for r in items),default=None),post_accuracy=sum(r.get('post_correct',0) for r in items)/sum(r.get('post_count',0) for r in items) if sum(r.get('post_count',0) for r in items) else None)
 if len(valid)==len(items):
  a.update(fp=sum(r['fp'] for r in valid),tp=sum(r['tp'] for r in valid),fn=sum(r['fn'] for r in valid),hits=sum(r['hits'] for r in valid),C=sum(r['C'] for r in valid),X=sum(r['X'] for r in valid),mdt=sum(r['mdt']*r['hits'] for r in valid if r['mdt'] is not None)/sum(r['hits'] for r in valid) if sum(r['hits'] for r in valid) else None,far_mean=sum(r['fp']/r['n_input']*1000 for r in valid)/len(valid) if valid else None)
 else:a.update(fp=None,tp=None,fn=None,hits=None,C=None,X=None,mdt=None,far_mean=None)
 return a


def compare(rows):
 lookup={(r['dataset'],r['stream'],r['arm']):r for r in rows}
 judged=[r for r in rows if r['gt']]
 streams={g:sorted({(r['dataset'],r['stream']) for r in judged if r['group']==g}) for g in ('injected','synthetic','INSECTS')}
 out={}
 for arm in ('A2','A3','A4','A5'):
  rng=np.random.default_rng(20261012);samples=np.zeros((10000,2));point=np.zeros(2);by_group={}
  for g,keys in streams.items():
   dif=np.array([[lookup[(ds,st,arm)]['fp']-lookup[(ds,st,'A1')]['fp'],lookup[(ds,st,arm)]['X']-lookup[(ds,st,'A1')]['X']] for ds,st in keys],dtype=float)
   assert np.isfinite(dif).all()
   got=dif.sum(axis=0);point+=got;by_group[g]={'n_streams':len(keys),'delta_fp':int(got[0]),'delta_x':float(got[1])}
   idx=rng.integers(0,len(keys),size=(10000,len(keys)))
   samples+=dif[idx].sum(axis=1)
  lo=np.percentile(samples,2.5,axis=0);hi=np.percentile(samples,97.5,axis=0)
  p1='成立' if hi[0]<0 else '不成立' if lo[0]>0 else '持平'
  p2='成立' if lo[1]>0 else '不成立' if hi[1]<0 else '持平'
  verdict='優於' if (p1,p2)==('成立','成立') else '不如' if (p1,p2)==('不成立','不成立') else '持平' if '持平' in (p1,p2) else '如實報告'
  directions={}
  for metric,i,beneficial in [('P1',0,-1),('P2',1,1)]:
   total=np.sign(point[i])*beneficial
   ds={g:('有利' if np.sign(v['delta_fp' if i==0 else 'delta_x'])*beneficial>0 else '不利' if np.sign(v['delta_fp' if i==0 else 'delta_x'])*beneficial<0 else '相同') for g,v in by_group.items()}
   n_consistent=sum((np.sign(v['delta_fp' if i==0 else 'delta_x'])*beneficial)==total for v in by_group.values()) if total!=0 else None
   directions[metric]={'group_directions':ds,'same_as_total':n_consistent,'total_direction':'有利' if total>0 else '不利' if total<0 else '相同'}
  out[arm]={'point':{'delta_fp':int(point[0]),'delta_x':float(point[1])},'ci':{'fp':[float(lo[0]),float(hi[0])],'x':[float(lo[1]),float(hi[1])]},'p1':p1,'p2':p2,'verdict':verdict,'by_group':by_group,'directions':directions}
 return out


def summarize(rows):
 main={g:{a:aggregate([r for r in rows if r['group']==g and r['arm']==a and r['gt']]) for a in PRESETS} for g in ('injected','synthetic','INSECTS')}
 main['total']={a:aggregate([r for r in rows if r['arm']==a and r['gt']]) for a in PRESETS}
 by_dataset={ds:{a:aggregate([r for r in rows if r['dataset']==ds and r['arm']==a]) for a in PRESETS} for ds in DATASETS}
 no_gt={ds:{a:aggregate([r for r in rows if r['dataset']==ds and r['arm']==a]) for a in PRESETS} for ds in INSECTS if all(not r['gt'] for r in rows if r['dataset']==ds)}
 types={t:{a:aggregate([r for r in rows if r['gt'] and t in r['types'] and r['arm']==a]) for a in PRESETS} for t in ('突變','漸變','incremental','recurring')}
 warning={}
 for a in PRESETS:
  rr=[r for r in rows if r['arm']==a];counts=collections.Counter();frozen=0;confirmed=[];discarded=[]
  for r in rr:
   counts.update(r['warning']);frozen+=r['frozen'];confirmed+=r['confirmed_buffer'];discarded+=r['discarded_buffer']
  warning[a]={'counts':dict(counts),'frozen':frozen,'confirmed_buffer_median':statistics.median(confirmed) if confirmed else None,'discarded_buffer_median':statistics.median(discarded) if discarded else None,'confirmed_n':len(confirmed),'discarded_n':len(discarded)}
 cells={}
 for cell in sorted({r['cell'] for r in rows if r['group']=='injected'}):
  cells[cell]={}
  for a in PRESETS:
   rr=[r for r in rows if r['cell']==cell and r['arm']==a]
   tp=sum(r['cerqueira_2500']['tp'] for r in rr);fp=sum(r['cerqueira_2500']['fp'] for r in rr);fn=sum(r['cerqueira_2500']['fn'] for r in rr)
   prec=tp/(tp+fp) if tp+fp else 0;rec=tp/(tp+fn) if tp+fn else 0
   cells[cell][a]={'runs':len(rr),'tp':tp,'fp':fp,'fn':fn,'f1':2*prec*rec/(prec+rec) if prec+rec else 0}
 return {'main':main,'by_dataset':by_dataset,'no_gt':no_gt,'types':types,'warning':warning,'comparisons':compare(rows),'cells':cells}


def main():
 rows=load_all();add_post_accuracy(rows);s=summarize(rows)
 assert len(rows)==1025
 out=REPO/'outputs/det1/det1_verdict_data.json';out.write_text(json.dumps(s,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist() if isinstance(x,np.ndarray) else str(x))+'\n')
 score_csv=REPO/'outputs/det1/det1_run_scores.csv'
 fields=['dataset','stream','cell','arm','group','n_input','n_output','n_scored','gt','alarms','tp','fp','fn','hits','C','X','O','acc','kappa','post_correct','post_count','runtime','rss','frozen','y_true_sha256','path']
 with score_csv.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r.get(k) for k in fields} for r in rows)
 print('rows',len(rows),'summary',out,'scores',score_csv)
 for arm, cmp in s['comparisons'].items(): print(arm,cmp['p1'],cmp['p2'],cmp['verdict'])

if __name__=='__main__':main()
