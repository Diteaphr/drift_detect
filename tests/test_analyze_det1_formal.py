import math
import numpy as np
from scripts.analyze_det1_formal import windows, union_length, detection_metrics, type_flags


def test_inclusive_clipped_windows_and_overlap():
    assert windows([(100, 100), (150, 150), (990, 990)], 1000, 0, 100) == [(100, 200), (150, 250), (990, 999)]
    assert union_length([(100, 200), (150, 250), (990, 999)]) == 161
    assert windows([(0, 0), (200, 200)], 1000, 100, 100) == [(200, 300)]


def test_episode_hit_is_once_per_drift_even_with_repeat_alarms():
    gt = [(1000, 1000), (1500, 1500)]
    alarms = [1001, 1002, 1600, 2100, 3000]
    got = detection_metrics(alarms, gt, n_instances=4000, delta_max=1000, anchor='start')
    assert got['tp'] == 4
    assert got['fp'] == 1
    assert got['n_episodes'] - got['fn'] == 2
    assert union_length(windows(gt, 4000, 0)) == 1501


def test_random_alarm_excess_near_zero():
    rng = np.random.default_rng(20261012)
    gt = [(2000, 2000), (4500, 4500)]
    wins = windows(gt, 10000, 200)
    O = 10000 - 200 - union_length(wins)
    xs = []
    for _ in range(200):
        alarms = np.flatnonzero(rng.random(10000) < .002)
        alarms = alarms[alarms >= 200]
        got = detection_metrics(alarms, gt, n_instances=10000, delta_max=1000, anchor='start')
        C = sum(-math.expm1(-got['fp']/O * (e-s+1)) for s, e in wins)
        xs.append(2-got['fn']-C)
    assert abs(np.mean(xs)) < .3


def test_type_tags_are_descriptive_and_can_overlap():
    assert set(type_flags('insects_incremental_abrupt_reoccurring_balanced', 'x')) == {'incremental', '突變', 'recurring'}


def test_paired_bootstrap_sign_and_tie_rules():
    from scripts.analyze_det1_formal import compare
    streams=[('injected_paper_electricity','i','injected'),('synthetic_multiclass','s','synthetic'),('insects_abrupt_balanced','a','INSECTS')]
    rows=[]
    for ds,st,g in streams:
        for arm in ('A1','A2','A3','A4','A5'):
            fp,x=(10,1.0) if arm=='A1' else (5,2.0) if arm=='A2' else (10,1.0)
            rows.append({'dataset':ds,'stream':st,'group':g,'arm':arm,'gt':1,'fp':fp,'X':x})
    got=compare(rows)
    assert got['A2']['p1']=='成立' and got['A2']['p2']=='成立' and got['A2']['verdict']=='優於'
    assert got['A3']['p1']=='持平' and got['A3']['p2']=='持平' and got['A3']['verdict']=='持平'
    assert got['A2']['directions']['P1']['same_as_total']==3
