# 分流確認實驗結果

依 [預註冊](../../docs/ECPF_ROUTED_預註冊.md) 判定。差值 = 前者 − 後者；accuracy 單位為百分點；CI 為分層配對 bootstrap 10,000 次（seed 20261012）的 95% 區間。

## 假設判定

| 假設 | 內容 | 比較 | 結果 |
|---|---|---|---|
| H1 | 設計 2 不比只用 HDDM-A 差 | `fw_vs_hddma` | 成立 |
| H2 | 設計 1 的 accuracy 優於設計 2 | `tr_vs_fw` | 不成立 |
| H3 | 設計 2 的偵測優於聯集 | `fw_vs_union` | 不成立 |

## 配對比較（45 條串流合併）

| 比較 | 串流 | Δaccuracy pp [CI] | accuracy | Δdrift 後 acc. pp [CI] | ΔFP [CI] | ΔX [CI] | 偵測 |
|---|---|---|---|---|---|---|---|
| `fw_vs_hddma` | 45 | +0.041 [-0.473, +0.586] | 持平 | +0.187 [-0.502, +0.928] | +58.0 [+29.0, +88.0] | +8.57 [-1.70, +20.88] | 持平 |
| `tr_vs_fw` | 45 | +0.539 [-0.037, +1.111] | 持平 | -0.965 [-1.753, -0.177] | -57.0 [-79.0, -35.0] | -6.56 [-13.50, -0.50] | 持平 |
| `fw_vs_union` | 45 | +0.017 [-0.215, +0.276] | 持平 | -0.013 [-0.260, +0.257] | +6.0 [-10.0, +24.0] | +1.56 [-1.37, +5.15] | 持平 |
| `tr_vs_hddma` | 45 | +0.580 [+0.094, +1.100] | 優於 | -0.778 [-1.582, +0.052] | +1.0 [-26.0, +27.0] | +2.01 [-9.10, +14.72] | 持平 |
| `union_vs_hddma` | 45 | +0.024 [-0.412, +0.476] | 持平 | +0.200 [-0.414, +0.822] | +52.0 [+23.0, +82.0] | +7.00 [-2.88, +19.12] | 持平 |
| `fw_vs_adwin` | 45 | -0.540 [-1.080, -0.049] | 不如 | +1.183 [+0.378, +1.993] | +46.0 [+21.0, +71.0] | +20.51 [+9.98, +31.61] | 持平 |
| `tr_vs_adwin` | 45 | -0.001 [-0.411, +0.416] | 持平 | +0.219 [-0.399, +0.833] | -11.0 [-31.0, +9.0] | +13.95 [+6.04, +22.52] | 持平 |
| `union_vs_adwin` | 45 | -0.557 [-1.083, -0.087] | 不如 | +1.197 [+0.374, +2.023] | +40.0 [+12.0, +67.0] | +18.94 [+8.66, +29.91] | 持平 |
| `fw_vs_e10bft_lw0` | 45 | -0.124 [-0.644, +0.421] | 持平 | +1.776 [+1.063, +2.555] | +48.0 [+24.0, +71.0] | +10.40 [-0.24, +22.22] | 持平 |
| `tr_vs_e10bft_lw0` | 45 | +0.415 [+0.074, +0.771] | 優於 | +0.811 [+0.292, +1.342] | -9.0 [-33.0, +14.0] | +3.85 [-3.92, +12.43] | 持平 |
| `union_vs_e10bft_lw0` | 45 | -0.141 [-0.600, +0.308] | 持平 | +1.789 [+1.074, +2.547] | +42.0 [+12.0, +71.0] | +8.84 [-1.49, +19.84] | 持平 |
| `tr_vs_hddma_adwin` | 45 | +1.693 [+1.123, +2.253] | 優於 | +3.175 [+1.720, +4.742] | +88.0 [+65.0, +113.0] | +181.54 [+157.61, +205.87] | 持平 |
| `fw_vs_hddma_adwin` | 45 | +1.154 [+0.551, +1.760] | 優於 | +4.140 [+2.152, +6.205] | +145.0 [+116.0, +172.0] | +188.09 [+164.53, +212.82] | 持平 |
| `union_vs_hddma_adwin` | 45 | +1.137 [+0.535, +1.727] | 優於 | +4.153 [+2.148, +6.254] | +139.0 [+108.0, +169.0] | +186.53 [+163.16, +211.25] | 持平 |
| `tr_vs_adwin_hddma` | 45 | +0.327 [-0.213, +0.845] | 持平 | +0.803 [+0.070, +1.513] | +26.0 [+4.0, +48.0] | +41.70 [+23.80, +61.28] | 持平 |
| `hddma_adwin_vs_hddma` | 45 | -1.113 [-1.751, -0.448] | 不如 | -3.953 [-6.115, -1.839] | -87.0 [-119.0, -58.0] | -179.53 [-205.69, -154.48] | 持平 |
| `adwin_hddma_vs_adwin` | 45 | -0.328 [-0.799, +0.135] | 持平 | -0.584 [-1.213, +0.085] | -37.0 [-62.0, -10.0] | -27.75 [-46.14, -11.22] | 持平 |

e10bft lw0 的 learn_during_warning 與其他組不同，只作描述性參考。

## 各組合併數值

| 組別 | accuracy | drift 後 accuracy | 警報 | FP | X | 平均延遲 |
|---|---|---|---|---|---|---|
| 設計 1：分類器分流 | 0.6313 | 0.5118 | 446 | 127 | 289.22 | 507.9 |
| 設計 2：誰先發誰確認 | 0.6259 | 0.5215 | 525 | 184 | 295.77 | 384.6 |
| 聯集 | 0.6257 | 0.5216 | 513 | 178 | 294.21 | 377.3 |
| 只用 HDDM-A（DET4 S1） | 0.6255 | 0.5196 | 460 | 126.0 | 287.21 | 376.3 |
| 只用 ADWIN（DET4 S1） | 0.6313 | 0.5096 | 433 | 138.0 | 275.27 | 532.6 |
| HDDM-A warning + ADWIN 確認（DET4 S1） | 0.6143 | 0.4801 | 157 | 39.0 | 107.68 | 498.8 |
| ADWIN warning + HDDM-A 確認（DET4 S1） | 0.6280 | 0.5038 | 365 | 101.0 | 247.52 | 525.8 |
| e10bft lw0（DET3 F-D0-lw0） | 0.6271 | 0.5037 | 442 | 136.0 | 285.37 | — |

## 11 個資料組（點估計）

### accuracy

| 資料組 | 設計 1：分類器分流 | 設計 2：誰先發誰確認 | 聯集 | 只用 HDDM-A（DET4 S1） | 只用 ADWIN（DET4 S1） | HDDM-A warning + ADWIN 確認（DET4 S1） | ADWIN warning + HDDM-A 確認（DET4 S1） | e10bft lw0（DET3 F-D0-lw0） |
|---|---|---|---|---|---|---|---|---|
| insects_abrupt_balanced | 0.6518 | 0.6476 | 0.6476 | 0.6457 | 0.6469 | 0.6037 | 0.6349 | 0.6469 |
| insects_incremental_abrupt_reoccurring_balanced | 0.6546 | 0.6584 | 0.6584 | 0.6482 | 0.6527 | 0.6322 | 0.6344 | 0.6622 |
| insects_incremental_balanced | 0.5617 | 0.5596 | 0.5596 | 0.5644 | 0.5671 | 0.5519 | 0.5389 | 0.5659 |
| insects_incremental_gradual_balanced | 0.6585 | 0.6624 | 0.6624 | 0.6615 | 0.6721 | 0.6384 | 0.6545 | 0.6643 |
| insects_incremental_reoccurring_balanced | 0.6778 | 0.6796 | 0.6796 | 0.6777 | 0.6800 | 0.5858 | 0.6488 | 0.6734 |
| synthetic_multiclass:gradual | 0.6086 | 0.6030 | 0.6049 | 0.6096 | 0.6094 | 0.5983 | 0.6086 | 0.6069 |
| synthetic_multiclass:incremental | 0.6257 | 0.6196 | 0.6207 | 0.6153 | 0.6248 | 0.6097 | 0.6255 | 0.6189 |
| synthetic_multiclass:recurring_gradual | 0.6550 | 0.6679 | 0.6578 | 0.6439 | 0.6642 | 0.6523 | 0.6590 | 0.6529 |
| synthetic_multiclass:recurring_incremental | 0.6562 | 0.5987 | 0.5970 | 0.6112 | 0.6485 | 0.6264 | 0.6265 | 0.6308 |
| synthetic_multiclass:recurring_sudden | 0.6762 | 0.6650 | 0.6649 | 0.6754 | 0.6667 | 0.6445 | 0.6834 | 0.6749 |
| synthetic_multiclass:sudden | 0.6258 | 0.6226 | 0.6243 | 0.6257 | 0.6253 | 0.6089 | 0.6201 | 0.6226 |

### X

| 資料組 | 設計 1：分類器分流 | 設計 2：誰先發誰確認 | 聯集 | 只用 HDDM-A（DET4 S1） | 只用 ADWIN（DET4 S1） | HDDM-A warning + ADWIN 確認（DET4 S1） | ADWIN warning + HDDM-A 確認（DET4 S1） | e10bft lw0（DET3 F-D0-lw0） |
|---|---|---|---|---|---|---|---|---|
| insects_abrupt_balanced | 2.23 | 1.97 | 1.97 | 3.41 | 3.14 | 3.90 | 3.14 | 3.14 |
| insects_incremental_abrupt_reoccurring_balanced | 1.55 | 1.45 | 1.45 | 1.67 | 1.45 | 1.76 | 1.63 | 1.38 |
| insects_incremental_balanced | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| insects_incremental_gradual_balanced | 0.74 | 0.77 | 0.77 | 0.74 | -0.46 | 0.92 | 0.68 | 0.59 |
| insects_incremental_reoccurring_balanced | 1.51 | 1.53 | 1.53 | 1.49 | 1.43 | 0.83 | 1.63 | 1.51 |
| synthetic_multiclass:gradual | 71.56 | 74.21 | 73.18 | 71.75 | 65.13 | 23.37 | 61.13 | 70.84 |
| synthetic_multiclass:incremental | 69.11 | 72.15 | 72.34 | 71.27 | 64.59 | 22.44 | 56.69 | 66.96 |
| synthetic_multiclass:recurring_gradual | 28.48 | 29.72 | 30.20 | 23.30 | 27.56 | 9.67 | 27.83 | 28.19 |
| synthetic_multiclass:recurring_incremental | 15.18 | 16.27 | 14.99 | 14.63 | 13.46 | 4.00 | 6.16 | 13.53 |
| synthetic_multiclass:recurring_sudden | 23.64 | 23.80 | 23.80 | 23.90 | 24.00 | 8.90 | 18.90 | 23.90 |
| synthetic_multiclass:sudden | 75.24 | 73.89 | 73.98 | 75.05 | 74.95 | 31.90 | 69.74 | 75.32 |

### FP

| 資料組 | 設計 1：分類器分流 | 設計 2：誰先發誰確認 | 聯集 | 只用 HDDM-A（DET4 S1） | 只用 ADWIN（DET4 S1） | HDDM-A warning + ADWIN 確認（DET4 S1） | ADWIN warning + HDDM-A 確認（DET4 S1） | e10bft lw0（DET3 F-D0-lw0） |
|---|---|---|---|---|---|---|---|---|
| insects_abrupt_balanced | 8 | 11 | 11 | 6 | 9 | 1 | 9 | 9 |
| insects_incremental_abrupt_reoccurring_balanced | 20 | 25 | 25 | 14 | 25 | 10 | 16 | 29 |
| insects_incremental_balanced | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| insects_incremental_gradual_balanced | 7 | 6 | 6 | 7 | 14 | 2 | 9 | 12 |
| insects_incremental_reoccurring_balanced | 22 | 21 | 21 | 23 | 26 | 7 | 16 | 22 |
| synthetic_multiclass:gradual | 16 | 31 | 31 | 24 | 21 | 6 | 21 | 14 |
| synthetic_multiclass:incremental | 24 | 37 | 35 | 25 | 19 | 6 | 15 | 25 |
| synthetic_multiclass:recurring_gradual | 7 | 17 | 11 | 10 | 6 | 5 | 2 | 11 |
| synthetic_multiclass:recurring_incremental | 9 | 8 | 11 | 4 | 6 | 0 | 9 | 5 |
| synthetic_multiclass:recurring_sudden | 4 | 2 | 2 | 1 | 0 | 1 | 1 | 1 |
| synthetic_multiclass:sudden | 10 | 26 | 25 | 12 | 12 | 1 | 3 | 8 |

## 分流診斷

### 設計 2：誰先發誰確認

- warning 事件 3168 次；結束原因 {'zone_exit': 1867, 'timeout': 74, 'confirmed': 424, 'cooldown': 762, 'reset': 41}
- 先發 warning：{'hddma': 3040, 'adwin': 128}；確認者：{'hddma': 365, 'adwin': 59}
- 被分流忽略的 drift 23 次；冷卻期擋掉 774 次
- 落在真實 drift 的事件 1623 次；先發者與類型相符 0.311
- 分類器（是否 sudden）：{"100": {"n": 46, "accuracy": 0.6956521739130435, "sudden_recall": 0.2222222222222222, "non_sudden_recall": 0.8108108108108109}, "200": {"n": 20, "accuracy": 0.7, "sudden_recall": 0.0, "non_sudden_recall": 0.9333333333333333}, "300": {"n": 15, "accuracy": 0.8666666666666667, "sudden_recall": 0.0, "non_sudden_recall": 1.0}, "confirm": {"n": 274, "accuracy": 0.635036496350365, "sudden_recall": 0.1566265060240964, "non_sudden_recall": 0.8429319371727748}}

### 設計 1：分類器分流

- warning 事件 1228 次；結束原因 {'timeout': 394, 'confirmed': 218, 'reset': 184, 'cooldown': 431, 'stream_end': 1}
- 先發 warning：{'hddma': 1108, 'adwin': 120}；確認者：{'adwin': 169, 'hddma': 49}
- 被分流忽略的 drift 80 次；冷卻期擋掉 434 次
- 落在真實 drift 的事件 635 次；先發者與類型相符 0.189
- 分類器（是否 sudden）：{"100": {"n": 290, "accuracy": 0.6827586206896552, "sudden_recall": 0.1686746987951807, "non_sudden_recall": 0.8888888888888888}, "200": {"n": 179, "accuracy": 0.7094972067039106, "sudden_recall": 0.0975609756097561, "non_sudden_recall": 0.8913043478260869}, "300": {"n": 130, "accuracy": 0.7538461538461538, "sudden_recall": 0.07692307692307693, "non_sudden_recall": 0.9230769230769231}, "confirm": {"n": 137, "accuracy": 0.583941605839416, "sudden_recall": 0.42857142857142855, "non_sudden_recall": 0.6704545454545454}}

### 聯集

- warning 事件 2830 次；結束原因 {'zone_exit': 1724, 'timeout': 73, 'confirmed': 422, 'cooldown': 578, 'reset': 31, 'stream_end': 2}
- 先發 warning：{'hddma': 2709, 'adwin': 121}；確認者：{'hddma': 361, 'adwin': 61}
- 被分流忽略的 drift 0 次；冷卻期擋掉 592 次
- 落在真實 drift 的事件 1377 次；先發者與類型相符 0.220
- 分類器（是否 sudden）：{"100": {"n": 36, "accuracy": 0.8055555555555556, "sudden_recall": 0.2, "non_sudden_recall": 0.9032258064516129}, "200": {"n": 13, "accuracy": 0.7692307692307693, "sudden_recall": 0.0, "non_sudden_recall": 0.9090909090909091}, "300": {"n": 10, "accuracy": 0.8, "sudden_recall": 0.0, "non_sudden_recall": 0.8888888888888888}, "confirm": {"n": 273, "accuracy": 0.5970695970695971, "sudden_recall": 0.10344827586206896, "non_sudden_recall": 0.8279569892473119}}

