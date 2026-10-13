# DET1 RDDM 與 MOA 觸發全部同一步

執行時間：2026-10-12T14:34:38.601395+00:00；Python 3.14.5；CapyMOA 0.14.0；numpy 2.5.4。
輸入：同一 0/1 誤差序列，固定 RNG seed=20261012；各 detector 全程依自身語意運作，沒有外部重置。warning 只計進入 warning 區的時點；drift 計每次確認。
±32 步內重合：每個方向各用自己的觸發總數作分母；exact 為同一步觸發。

| 序列 | 步數 | 事件 | Python 次數 | MOA 次數 | Python→MOA | MOA→Python | 同步 |
|---|---:|---|---:|---:|---:|---:|---:|
| up_0.1_to_0.5 | 4,000 | warning | 17 | 17 | 1.000 | 1.000 | 1.000 |
| up_0.1_to_0.5 | 4,000 | drift | 2 | 2 | 1.000 | 1.000 | 1.000 |
| down_0.5_to_0.1 | 4,000 | warning | 0 | 0 | n/a | n/a | n/a |
| down_0.5_to_0.1 | 4,000 | drift | 0 | 0 | n/a | n/a | n/a |
| alternating_8_cycles | 32,000 | warning | 111 | 111 | 1.000 | 1.000 | 1.000 |
| alternating_8_cycles | 32,000 | drift | 12 | 12 | 1.000 | 1.000 | 1.000 |
| gradual_rise | 11,000 | warning | 144 | 144 | 1.000 | 1.000 | 1.000 |
| gradual_rise | 11,000 | drift | 7 | 7 | 1.000 | 1.000 | 1.000 |
| stable_45k_then_up | 47,500 | warning | 102 | 102 | 1.000 | 1.000 | 1.000 |
| stable_45k_then_up | 47,500 | drift | 7 | 7 | 1.000 | 1.000 | 1.000 |

## 28 次 drift 全部通過 MOA 雙向重合率閘門

- warning: Python 374、MOA 374；Python→MOA 1.000；MOA→Python 1.000；同一步 1.000。
- drift: Python 28、MOA 28；Python→MOA 1.000；MOA→Python 1.000；同一步 1.000。

**RDDM drift 雙向重合率 ≥0.90：通過。**

來源：[Waikato MOA RDDM.java](https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/classifiers/core/driftdetection/RDDM.java)、[CapyMOA RDDM API](https://capymoa.org/api/modules/capymoa.drift.detectors.RDDM.html)。
