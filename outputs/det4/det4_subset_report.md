# DET4 子資料集層級彙整：事後探索，不改變預註冊判定

## 子資料集分析僅供事後探索，不產生新判定

**定位聲明：** 子資料集分析是**事後探索分析**，不在 DET4 預註冊範圍內；本報告不產生新的判定，也不改變 H1–H3 的結論。

**多重比較提醒：** 88 個子資料集 × 17 個比較，單純因為機率就會出現不少「信賴區間不含 0」的格子。以下只描述跨多個子資料集一致的型態，不以單一格子下結論；CI 是以串流為配對單位、10,000 次 percentile bootstrap、seed `20261012`。

## 30,456 列逐 run 表完整重現既有 DET4 資料集層級結果

- 逐 run 列數：**30,456**；18 個組合各 **1,692** 列。
- 子資料集：**88** 個；去重串流：**1,692** 條。
- 來源：DET4 新 run **29,431**；DET1 沿用 **615**；DET3 沿用 **410**。
- 重現檢查：**通過**；q4 數值點估計 1,008 格（另核對空值範圍，共 1,584 格）、T1/T3 aggregate 540 欄，絕對誤差皆 `< 1e-09`。
- skill pooled detection：**1,440** 列；先加總 TP/FP/FN，再由 repo 既有 `pool_detection_runs` 計算 precision、recall、F1。

## 四個主要組合顯示每個子資料集的加權準確率與 drift 後準確率

每格為 `準確率 / drift 後 1000 步準確率`；`—` 表示該子資料集沒有可用 GT／drift 後窗口。

| 子資料集 | n | 論文 ECPF Dual ADWIN | 論文 ECPF HDDM-A | 完整系統 Dual ADWIN | 完整系統 HDDM-A |
|---|---:|---:|---:|---:|---:|
| ai4i2020 | 1 | 0.9666 / — | 0.9648 / — | 0.9660 / — | 0.9658 / — |
| airlines | 1 | 0.6556 / — | 0.6532 / — | 0.6517 / — | 0.6585 / — |
| airlines_full | 1 | 0.6338 / — | 0.6305 / — | 0.6326 / — | 0.6279 / — |
| covertype | 1 | 0.8108 / — | 0.8494 / — | 0.8226 / — | 0.8376 / — |
| covertype_full | 1 | 0.7841 / — | 0.8618 / — | 0.8239 / — | 0.8408 / — |
| electricity | 1 | 0.8114 / — | 0.8475 / — | 0.8403 / — | 0.8464 / — |
| gas_sensor_drift | 1 | 0.8377 / — | 0.8876 / — | 0.8961 / — | 0.9002 / — |
| injected_ai4i2020/abrupt/class_prior | 10 | 0.9693 / 0.9517 | 0.9695 / 0.9527 | 0.9694 / 0.9524 | 0.9694 / 0.9523 |
| injected_ai4i2020/abrupt/feature_filtering | 10 | 0.9684 / 0.9771 | 0.9684 / 0.9771 | 0.9684 / 0.9771 | 0.9684 / 0.9771 |
| injected_ai4i2020/abrupt/feature_permutation | 10 | 0.9665 / 0.9640 | 0.9665 / 0.9638 | 0.9665 / 0.9640 | 0.9665 / 0.9640 |
| injected_ai4i2020/abrupt/label_swap | 10 | 0.9748 / 0.9615 | 0.9766 / 0.9811 | 0.9751 / 0.9649 | 0.9767 / 0.9824 |
| injected_ai4i2020/gradual/class_prior | 10 | 0.9673 / 0.9464 | 0.9674 / 0.9479 | 0.9674 / 0.9478 | 0.9673 / 0.9472 |
| injected_ai4i2020/gradual/feature_filtering | 10 | 0.9679 / 0.9764 | 0.9679 / 0.9764 | 0.9679 / 0.9764 | 0.9679 / 0.9764 |
| injected_ai4i2020/gradual/feature_permutation | 10 | 0.9662 / 0.9641 | 0.9662 / 0.9641 | 0.9662 / 0.9641 | 0.9662 / 0.9641 |
| injected_ai4i2020/gradual/label_swap | 10 | 0.9730 / 0.9348 | 0.9727 / 0.9330 | 0.9731 / 0.9353 | 0.9728 / 0.9331 |
| injected_airlines/abrupt/class_prior | 10 | 0.6916 / 0.6608 | 0.6950 / 0.7508 | 0.6976 / 0.6803 | 0.6963 / 0.7351 |
| injected_airlines/abrupt/feature_filtering | 10 | 0.6610 / 0.6770 | 0.6653 / 0.6769 | 0.6637 / 0.6755 | 0.6652 / 0.6761 |
| injected_airlines/abrupt/feature_permutation | 10 | 0.6626 / 0.6460 | 0.6623 / 0.6451 | 0.6613 / 0.6441 | 0.6610 / 0.6441 |
| injected_airlines/abrupt/label_swap | 10 | 0.7722 / 0.7919 | 0.7744 / 0.9144 | 0.7756 / 0.7837 | 0.7734 / 0.8646 |
| injected_airlines/gradual/class_prior | 10 | 0.6920 / 0.6451 | 0.6917 / 0.6732 | 0.6939 / 0.6511 | 0.6918 / 0.6748 |
| injected_airlines/gradual/feature_filtering | 10 | 0.6567 / 0.6604 | 0.6624 / 0.6689 | 0.6669 / 0.6762 | 0.6634 / 0.6722 |
| injected_airlines/gradual/feature_permutation | 10 | 0.6576 / 0.6581 | 0.6578 / 0.6547 | 0.6590 / 0.6552 | 0.6596 / 0.6566 |
| injected_airlines/gradual/label_swap | 10 | 0.7772 / 0.6029 | 0.7809 / 0.7310 | 0.7838 / 0.6478 | 0.7800 / 0.7235 |
| injected_covertype/abrupt/class_prior | 10 | 0.7288 / 0.7226 | 0.7369 / 0.7348 | 0.7349 / 0.7328 | 0.7345 / 0.7310 |
| injected_covertype/abrupt/feature_filtering | 10 | 0.7337 / 0.7462 | 0.7434 / 0.7639 | 0.7449 / 0.7654 | 0.7455 / 0.7687 |
| injected_covertype/abrupt/feature_permutation | 10 | 0.7002 / 0.6154 | 0.7203 / 0.6590 | 0.7194 / 0.5996 | 0.7182 / 0.6244 |
| injected_covertype/abrupt/label_swap | 10 | 0.7140 / 0.6901 | 0.7367 / 0.7468 | 0.7352 / 0.7399 | 0.7350 / 0.7442 |
| injected_covertype/gradual/class_prior | 10 | 0.7261 / 0.7270 | 0.7295 / 0.7315 | 0.7351 / 0.7456 | 0.7359 / 0.7455 |
| injected_covertype/gradual/feature_filtering | 10 | 0.7194 / 0.7257 | 0.7422 / 0.7547 | 0.7445 / 0.7651 | 0.7441 / 0.7567 |
| injected_covertype/gradual/feature_permutation | 10 | 0.7040 / 0.5850 | 0.7205 / 0.6829 | 0.7207 / 0.6468 | 0.7196 / 0.6381 |
| injected_covertype/gradual/label_swap | 10 | 0.7269 / 0.7169 | 0.7400 / 0.7507 | 0.7413 / 0.7516 | 0.7388 / 0.7453 |
| injected_electricity/abrupt/class_prior | 10 | 0.7782 / 0.8004 | 0.7803 / 0.8060 | 0.7808 / 0.8097 | 0.7805 / 0.8092 |
| injected_electricity/abrupt/feature_filtering | 10 | 0.7567 / 0.7754 | 0.7575 / 0.7756 | 0.7583 / 0.7772 | 0.7584 / 0.7774 |
| injected_electricity/abrupt/feature_permutation | 10 | 0.7481 / 0.6585 | 0.7503 / 0.7117 | 0.7487 / 0.6767 | 0.7496 / 0.7028 |
| injected_electricity/abrupt/label_swap | 10 | 0.8368 / 0.7342 | 0.8383 / 0.8746 | 0.8375 / 0.8034 | 0.8382 / 0.8442 |
| injected_electricity/gradual/class_prior | 10 | 0.7710 / 0.7575 | 0.7692 / 0.7547 | 0.7701 / 0.7570 | 0.7695 / 0.7553 |
| injected_electricity/gradual/feature_filtering | 10 | 0.7561 / 0.7625 | 0.7578 / 0.7636 | 0.7581 / 0.7646 | 0.7579 / 0.7656 |
| injected_electricity/gradual/feature_permutation | 10 | 0.7482 / 0.6736 | 0.7483 / 0.6841 | 0.7482 / 0.6778 | 0.7474 / 0.6762 |
| injected_electricity/gradual/label_swap | 10 | 0.8206 / 0.6738 | 0.8334 / 0.7417 | 0.8248 / 0.6946 | 0.8261 / 0.7239 |
| injected_gas_sensor_drift/abrupt/class_prior | 10 | 0.5641 / 0.5708 | 0.5635 / 0.5684 | 0.5633 / 0.5685 | 0.5634 / 0.5685 |
| injected_gas_sensor_drift/abrupt/feature_filtering | 10 | 0.5691 / 0.5587 | 0.5725 / 0.6006 | 0.5697 / 0.5589 | 0.5715 / 0.5783 |
| injected_gas_sensor_drift/abrupt/feature_permutation | 10 | 0.5621 / 0.4800 | 0.5658 / 0.5483 | 0.5631 / 0.5010 | 0.5654 / 0.5417 |
| injected_gas_sensor_drift/abrupt/label_swap | 10 | 0.5558 / 0.4910 | 0.5583 / 0.5078 | 0.5562 / 0.4945 | 0.5609 / 0.5184 |
| injected_gas_sensor_drift/gradual/class_prior | 10 | 0.5674 / 0.5587 | 0.5673 / 0.5582 | 0.5674 / 0.5583 | 0.5674 / 0.5583 |
| injected_gas_sensor_drift/gradual/feature_filtering | 10 | 0.5680 / 0.5360 | 0.5701 / 0.5476 | 0.5677 / 0.5347 | 0.5711 / 0.5491 |
| injected_gas_sensor_drift/gradual/feature_permutation | 10 | 0.5562 / 0.4753 | 0.5576 / 0.4978 | 0.5563 / 0.4813 | 0.5581 / 0.4980 |
| injected_gas_sensor_drift/gradual/label_swap | 10 | 0.5580 / 0.5266 | 0.5611 / 0.5277 | 0.5599 / 0.5258 | 0.5637 / 0.5263 |
| injected_paper_covertype/abrupt/class_prior | 50 | 0.5565 / 0.5522 | 0.5568 / 0.5537 | 0.5602 / 0.5559 | 0.5583 / 0.5666 |
| injected_paper_covertype/abrupt/feature_filtering | 50 | 0.5507 / 0.5519 | 0.5530 / 0.5584 | 0.5512 / 0.5542 | 0.5482 / 0.5525 |
| injected_paper_covertype/abrupt/feature_permutation | 50 | 0.5392 / 0.3626 | 0.5432 / 0.4665 | 0.5425 / 0.3984 | 0.5384 / 0.3849 |
| injected_paper_covertype/abrupt/label_swap | 50 | 0.5591 / 0.5332 | 0.5590 / 0.5643 | 0.5588 / 0.5497 | 0.5587 / 0.5531 |
| injected_paper_covertype/gradual/class_prior | 50 | 0.5557 / 0.5472 | 0.5578 / 0.5522 | 0.5607 / 0.5525 | 0.5586 / 0.5497 |
| injected_paper_covertype/gradual/feature_filtering | 50 | 0.5532 / 0.5542 | 0.5498 / 0.5491 | 0.5495 / 0.5524 | 0.5479 / 0.5512 |
| injected_paper_covertype/gradual/feature_permutation | 50 | 0.5424 / 0.4689 | 0.5422 / 0.4807 | 0.5409 / 0.4636 | 0.5379 / 0.4635 |
| injected_paper_covertype/gradual/label_swap | 50 | 0.5523 / 0.5460 | 0.5507 / 0.5458 | 0.5523 / 0.5513 | 0.5509 / 0.5459 |
| injected_paper_electricity/abrupt/class_prior | 50 | 0.7667 / 0.7666 | 0.7680 / 0.7736 | 0.7677 / 0.7729 | 0.7681 / 0.7722 |
| injected_paper_electricity/abrupt/feature_filtering | 50 | 0.7571 / 0.7750 | 0.7579 / 0.7762 | 0.7578 / 0.7743 | 0.7578 / 0.7740 |
| injected_paper_electricity/abrupt/feature_permutation | 50 | 0.7491 / 0.6370 | 0.7517 / 0.7041 | 0.7507 / 0.6449 | 0.7509 / 0.6803 |
| injected_paper_electricity/abrupt/label_swap | 50 | 0.8356 / 0.7166 | 0.8403 / 0.8702 | 0.8373 / 0.7577 | 0.8401 / 0.8471 |
| injected_paper_electricity/gradual/class_prior | 50 | 0.7678 / 0.7605 | 0.7682 / 0.7636 | 0.7692 / 0.7626 | 0.7686 / 0.7632 |
| injected_paper_electricity/gradual/feature_filtering | 50 | 0.7574 / 0.7587 | 0.7575 / 0.7621 | 0.7580 / 0.7613 | 0.7578 / 0.7603 |
| injected_paper_electricity/gradual/feature_permutation | 50 | 0.7446 / 0.7177 | 0.7458 / 0.7233 | 0.7460 / 0.7240 | 0.7468 / 0.7235 |
| injected_paper_electricity/gradual/label_swap | 50 | 0.8073 / 0.7114 | 0.8129 / 0.7141 | 0.8149 / 0.7131 | 0.8143 / 0.7130 |
| injected_paper_gas_sensor_drift/abrupt/class_prior | 50 | 0.5686 / 0.5734 | 0.5686 / 0.5736 | 0.5685 / 0.5728 | 0.5687 / 0.5738 |
| injected_paper_gas_sensor_drift/abrupt/feature_filtering | 50 | 0.5708 / 0.5482 | 0.5747 / 0.5699 | 0.5730 / 0.5485 | 0.5752 / 0.5744 |
| injected_paper_gas_sensor_drift/abrupt/feature_permutation | 50 | 0.5604 / 0.4597 | 0.5641 / 0.5286 | 0.5621 / 0.4889 | 0.5645 / 0.5343 |
| injected_paper_gas_sensor_drift/abrupt/label_swap | 50 | 0.5570 / 0.5045 | 0.5622 / 0.5230 | 0.5594 / 0.5049 | 0.5626 / 0.5240 |
| injected_paper_gas_sensor_drift/gradual/class_prior | 50 | 0.5685 / 0.5701 | 0.5686 / 0.5693 | 0.5686 / 0.5700 | 0.5685 / 0.5697 |
| injected_paper_gas_sensor_drift/gradual/feature_filtering | 50 | 0.5669 / 0.5665 | 0.5708 / 0.5663 | 0.5683 / 0.5661 | 0.5705 / 0.5663 |
| injected_paper_gas_sensor_drift/gradual/feature_permutation | 50 | 0.5549 / 0.4708 | 0.5574 / 0.4998 | 0.5552 / 0.4744 | 0.5564 / 0.4873 |
| injected_paper_gas_sensor_drift/gradual/label_swap | 50 | 0.5540 / 0.5430 | 0.5531 / 0.5438 | 0.5553 / 0.5435 | 0.5559 / 0.5433 |
| insects_abrupt_balanced | 1 | 0.6361 / 0.5089 | 0.6326 / 0.5290 | 0.6469 / 0.5574 | 0.6457 / 0.5213 |
| insects_incremental_abrupt_reoccurring_balanced | 1 | 0.6611 / 0.5760 | 0.6321 / 0.6315 | 0.6527 / 0.5755 | 0.6482 / 0.5590 |
| insects_incremental_balanced | 1 | 0.5553 / — | 0.5646 / — | 0.5671 / — | 0.5644 / — |
| insects_incremental_gradual_balanced | 1 | 0.6381 / 0.5690 | 0.6706 / 0.5610 | 0.6721 / 0.5660 | 0.6615 / 0.5700 |
| insects_incremental_reoccurring_balanced | 1 | 0.6671 / 0.6205 | 0.6411 / 0.6265 | 0.6800 / 0.6365 | 0.6777 / 0.6665 |
| synthetic_binary/gradual | 10 | 0.9564 / 0.9281 | 0.9637 / 0.9313 | 0.9638 / 0.9319 | 0.9575 / 0.9279 |
| synthetic_binary/incremental | 10 | 0.9273 / 0.8938 | 0.9310 / 0.8987 | 0.9311 / 0.8962 | 0.9311 / 0.8967 |
| synthetic_binary/recurring_gradual | 4 | 0.9664 / 0.9310 | 0.9692 / 0.9273 | 0.9698 / 0.9290 | 0.9577 / 0.9238 |
| synthetic_binary/recurring_incremental | 2 | 0.9321 / 0.8677 | 0.9353 / 0.8733 | 0.9318 / 0.8646 | 0.9351 / 0.8751 |
| synthetic_binary/recurring_sudden | 4 | 0.9661 / 0.9439 | 0.9708 / 0.9546 | 0.9679 / 0.9436 | 0.9679 / 0.9531 |
| synthetic_binary/sudden | 10 | 0.9597 / 0.9256 | 0.9638 / 0.9257 | 0.9635 / 0.9264 | 0.9640 / 0.9273 |
| synthetic_multiclass/gradual | 10 | 0.5872 / 0.4659 | 0.6118 / 0.4853 | 0.6094 / 0.4913 | 0.6096 / 0.4944 |
| synthetic_multiclass/incremental | 10 | 0.5948 / 0.4797 | 0.6192 / 0.5060 | 0.6248 / 0.5086 | 0.6153 / 0.5004 |
| synthetic_multiclass/recurring_gradual | 5 | 0.6351 / 0.4871 | 0.6520 / 0.5210 | 0.6642 / 0.5275 | 0.6439 / 0.5005 |
| synthetic_multiclass/recurring_incremental | 2 | 0.6093 / 0.4839 | 0.6081 / 0.5006 | 0.6485 / 0.5234 | 0.6112 / 0.5175 |
| synthetic_multiclass/recurring_sudden | 3 | 0.6482 / 0.5365 | 0.6452 / 0.6058 | 0.6667 / 0.5587 | 0.6754 / 0.6071 |
| synthetic_multiclass/sudden | 10 | 0.6087 / 0.4743 | 0.6236 / 0.5470 | 0.6253 / 0.4950 | 0.6257 / 0.5399 |

## 完整系統 Dual ADWIN 相對完整系統 HDDM-A 的差異以配對 CI 呈現

差值方向固定為 `完整系統 Dual ADWIN − 完整系統 HDDM-A`。子資料集少於 5 條串流時只列點估計。

| 子資料集 | n | Δ準確率 [95% CI] | Δdrift 後準確率 [95% CI] | ΔFP [95% CI] | ΔX [95% CI] |
|---|---:|---:|---:|---:|---:|
| ai4i2020 | 1 | 0.0002 | — | — | — |
| airlines | 1 | -0.0068 | — | — | — |
| airlines_full | 1 | 0.0046 | — | — | — |
| covertype | 1 | -0.0149 | — | — | — |
| covertype_full | 1 | -0.0170 | — | — | — |
| electricity | 1 | -0.0061 | — | — | — |
| gas_sensor_drift | 1 | -0.0041 | — | — | — |
| injected_ai4i2020/abrupt/class_prior | 10 | 0.0000 [-0.0001, 0.0001] | 0.0001 [0.0000, 0.0003] | 5.00 [2.00, 8.00] | 0.46 [-0.87, 2.67] |
| injected_ai4i2020/abrupt/feature_filtering | 10 | -0.0000 [-0.0001, 0.0000] | 0.0000 [0.0000, 0.0000] | 1.00 [0.00, 3.00] | 0.86 [-0.42, 3.00] |
| injected_ai4i2020/abrupt/feature_permutation | 10 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 1.00 [0.00, 3.00] | -0.11 [-0.32, 0.00] |
| injected_ai4i2020/abrupt/label_swap | 10 | -0.0016 [-0.0031, -0.0002] | -0.0175 [-0.0318, -0.0049] | 2.00 [0.00, 5.00] | 1.78 [-0.32, 4.78] |
| injected_ai4i2020/gradual/class_prior | 10 | 0.0001 [0.0000, 0.0003] | 0.0006 [0.0000, 0.0018] | 4.00 [1.00, 7.00] | 0.57 [-0.76, 2.78] |
| injected_ai4i2020/gradual/feature_filtering | 10 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| injected_ai4i2020/gradual/feature_permutation | 10 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| injected_ai4i2020/gradual/label_swap | 10 | 0.0003 [-0.0001, 0.0008] | 0.0022 [-0.0024, 0.0067] | 5.00 [2.00, 8.00] | -0.54 [-0.86, -0.22] |
| injected_airlines/abrupt/class_prior | 10 | 0.0012 [-0.0005, 0.0029] | -0.0548 [-0.0925, -0.0201] | -2.00 [-11.00, 6.00] | 1.03 [-0.06, 3.08] |
| injected_airlines/abrupt/feature_filtering | 10 | -0.0015 [-0.0050, 0.0005] | -0.0006 [-0.0018, 0.0000] | -2.00 [-7.00, 2.00] | 0.02 [-0.03, 0.08] |
| injected_airlines/abrupt/feature_permutation | 10 | 0.0003 [-0.0013, 0.0021] | 0.0000 [0.0000, 0.0000] | 5.00 [-6.00, 18.00] | -3.05 [-6.11, -0.06] |
| injected_airlines/abrupt/label_swap | 10 | 0.0022 [-0.0013, 0.0055] | -0.0809 [-0.1962, 0.0203] | -2.00 [-13.00, 9.00] | 5.02 [2.02, 8.03] |
| injected_airlines/gradual/class_prior | 10 | 0.0021 [0.0002, 0.0040] | -0.0237 [-0.0413, -0.0069] | 8.00 [2.00, 13.00] | -3.09 [-6.11, -0.12] |
| injected_airlines/gradual/feature_filtering | 10 | 0.0035 [-0.0000, 0.0088] | 0.0040 [-0.0002, 0.0111] | 4.00 [-5.00, 12.00] | -0.05 [-0.14, 0.06] |
| injected_airlines/gradual/feature_permutation | 10 | -0.0005 [-0.0035, 0.0021] | -0.0014 [-0.0042, 0.0000] | -15.00 [-29.00, -2.00] | 0.15 [0.02, 0.29] |
| injected_airlines/gradual/label_swap | 10 | 0.0037 [0.0004, 0.0072] | -0.0757 [-0.1415, -0.0168] | 0.00 [-8.00, 6.00] | 1.00 [-0.06, 3.08] |
| injected_covertype/abrupt/class_prior | 10 | 0.0003 [-0.0004, 0.0011] | 0.0018 [0.0000, 0.0050] | -8.00 [-20.00, 3.00] | 1.09 [-0.01, 3.13] |
| injected_covertype/abrupt/feature_filtering | 10 | -0.0006 [-0.0017, 0.0000] | -0.0033 [-0.0099, 0.0000] | -6.00 [-12.00, 0.00] | 0.06 [-0.00, 0.12] |
| injected_covertype/abrupt/feature_permutation | 10 | 0.0012 [-0.0002, 0.0028] | -0.0248 [-0.0488, -0.0045] | -9.00 [-17.00, -2.00] | -0.91 [-3.99, 2.16] |
| injected_covertype/abrupt/label_swap | 10 | 0.0002 [-0.0020, 0.0028] | -0.0043 [-0.0212, 0.0071] | -5.00 [-11.00, 1.00] | 0.05 [-0.01, 0.11] |
| injected_covertype/gradual/class_prior | 10 | -0.0008 [-0.0023, 0.0008] | 0.0001 [-0.0012, 0.0016] | -3.00 [-12.00, 6.00] | -2.98 [-6.04, -0.01] |
| injected_covertype/gradual/feature_filtering | 10 | 0.0004 [-0.0005, 0.0016] | 0.0084 [0.0000, 0.0240] | -11.00 [-19.00, -4.00] | 0.11 [0.04, 0.19] |
| injected_covertype/gradual/feature_permutation | 10 | 0.0010 [-0.0008, 0.0033] | 0.0087 [-0.0161, 0.0430] | -3.00 [-9.00, 3.00] | -0.97 [-3.96, 2.02] |
| injected_covertype/gradual/label_swap | 10 | 0.0024 [-0.0003, 0.0060] | 0.0063 [-0.0031, 0.0186] | -11.00 [-22.00, -3.00] | 0.11 [0.03, 0.22] |
| injected_electricity/abrupt/class_prior | 10 | 0.0002 [-0.0011, 0.0012] | 0.0005 [0.0000, 0.0015] | 3.00 [-3.00, 8.00] | 0.92 [-0.15, 2.93] |
| injected_electricity/abrupt/feature_filtering | 10 | -0.0000 [-0.0001, 0.0000] | -0.0002 [-0.0006, 0.0000] | 4.00 [-1.00, 9.00] | -0.11 [-0.25, 0.03] |
| injected_electricity/abrupt/feature_permutation | 10 | -0.0010 [-0.0016, -0.0004] | -0.0261 [-0.0524, -0.0017] | 3.00 [0.00, 6.00] | -1.07 [-3.07, -0.02] |
| injected_electricity/abrupt/label_swap | 10 | -0.0006 [-0.0058, 0.0059] | -0.0408 [-0.0997, 0.0203] | -2.00 [-6.00, 3.00] | 1.04 [-0.02, 3.07] |
| injected_electricity/gradual/class_prior | 10 | 0.0007 [-0.0000, 0.0016] | 0.0017 [0.0000, 0.0043] | 3.00 [-6.00, 10.00] | -1.07 [-3.21, 0.14] |
| injected_electricity/gradual/feature_filtering | 10 | 0.0002 [-0.0001, 0.0006] | -0.0010 [-0.0036, 0.0008] | 1.00 [-4.00, 7.00] | -1.02 [-3.02, 0.06] |
| injected_electricity/gradual/feature_permutation | 10 | 0.0009 [-0.0007, 0.0027] | 0.0016 [-0.0060, 0.0083] | 0.00 [-10.00, 8.00] | -4.00 [-7.16, -0.89] |
| injected_electricity/gradual/label_swap | 10 | -0.0013 [-0.0118, 0.0077] | -0.0293 [-0.0602, 0.0000] | -3.00 [-7.00, 1.00] | 0.07 [-0.02, 0.16] |
| injected_gas_sensor_drift/abrupt/class_prior | 10 | -0.0001 [-0.0004, 0.0001] | 0.0000 [0.0000, 0.0000] | 1.00 [-4.00, 8.00] | -1.06 [-3.22, 0.26] |
| injected_gas_sensor_drift/abrupt/feature_filtering | 10 | -0.0017 [-0.0036, -0.0000] | -0.0194 [-0.0365, -0.0045] | 1.00 [-2.00, 4.00] | 1.91 [-0.25, 4.90] |
| injected_gas_sensor_drift/abrupt/feature_permutation | 10 | -0.0023 [-0.0035, -0.0011] | -0.0407 [-0.0551, -0.0245] | 0.00 [-3.00, 3.00] | 0.00 [-0.23, 0.23] |
| injected_gas_sensor_drift/abrupt/label_swap | 10 | -0.0047 [-0.0098, -0.0004] | -0.0239 [-0.0497, -0.0031] | 3.00 [-2.00, 8.00] | -5.22 [-9.37, -0.77] |
| injected_gas_sensor_drift/gradual/class_prior | 10 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | -1.00 [-3.00, 0.00] | 0.08 [0.00, 0.24] |
| injected_gas_sensor_drift/gradual/feature_filtering | 10 | -0.0034 [-0.0060, -0.0008] | -0.0144 [-0.0251, -0.0050] | 4.00 [-1.00, 8.02] | -1.37 [-5.68, 3.06] |
| injected_gas_sensor_drift/gradual/feature_permutation | 10 | -0.0018 [-0.0045, 0.0007] | -0.0167 [-0.0306, -0.0016] | -3.00 [-8.00, 2.00] | -0.78 [-3.15, 0.52] |
| injected_gas_sensor_drift/gradual/label_swap | 10 | -0.0037 [-0.0085, -0.0006] | -0.0005 [-0.0026, 0.0013] | -3.00 [-14.00, 7.00] | 0.19 [-3.15, 3.38] |
| injected_paper_covertype/abrupt/class_prior | 50 | 0.0018 [-0.0010, 0.0046] | -0.0106 [-0.0269, 0.0046] | 42.00 [20.00, 63.00] | 0.45 [-2.73, 4.32] |
| injected_paper_covertype/abrupt/feature_filtering | 50 | 0.0030 [0.0008, 0.0053] | 0.0017 [-0.0077, 0.0107] | 66.00 [35.00, 98.00] | -1.86 [-5.18, 1.27] |
| injected_paper_covertype/abrupt/feature_permutation | 50 | 0.0041 [0.0003, 0.0077] | 0.0135 [-0.0224, 0.0492] | 41.00 [12.00, 72.00] | 5.47 [-1.70, 12.59] |
| injected_paper_covertype/abrupt/label_swap | 50 | 0.0001 [-0.0041, 0.0041] | -0.0034 [-0.0167, 0.0097] | 57.00 [26.00, 90.00] | 0.26 [-4.82, 5.43] |
| injected_paper_covertype/gradual/class_prior | 50 | 0.0021 [-0.0009, 0.0052] | 0.0028 [-0.0101, 0.0164] | 51.00 [14.00, 87.00] | 0.34 [-0.99, 2.55] |
| injected_paper_covertype/gradual/feature_filtering | 50 | 0.0016 [-0.0011, 0.0048] | 0.0012 [-0.0112, 0.0125] | 52.00 [25.00, 81.00] | -0.68 [-1.06, -0.33] |
| injected_paper_covertype/gradual/feature_permutation | 50 | 0.0030 [-0.0001, 0.0061] | 0.0000 [-0.0118, 0.0121] | 56.00 [30.00, 83.00] | 1.27 [-7.01, 9.33] |
| injected_paper_covertype/gradual/label_swap | 50 | 0.0014 [-0.0026, 0.0054] | 0.0054 [-0.0047, 0.0161] | 77.00 [53.00, 101.00] | 1.99 [-0.96, 5.84] |
| injected_paper_electricity/abrupt/class_prior | 50 | -0.0004 [-0.0010, 0.0001] | 0.0007 [-0.0015, 0.0029] | 12.00 [0.00, 24.00] | -8.36 [-15.39, -1.27] |
| injected_paper_electricity/abrupt/feature_filtering | 50 | 0.0001 [-0.0001, 0.0003] | 0.0004 [-0.0007, 0.0016] | -2.00 [-10.00, 6.00] | -0.94 [-3.06, 0.27] |
| injected_paper_electricity/abrupt/feature_permutation | 50 | -0.0002 [-0.0008, 0.0005] | -0.0353 [-0.0505, -0.0217] | -8.00 [-21.00, 5.00] | -1.77 [-6.79, 3.15] |
| injected_paper_electricity/abrupt/label_swap | 50 | -0.0028 [-0.0064, 0.0005] | -0.0894 [-0.1159, -0.0631] | 3.00 [-6.00, 11.00] | -4.09 [-10.27, 1.94] |
| injected_paper_electricity/gradual/class_prior | 50 | 0.0006 [-0.0000, 0.0013] | -0.0006 [-0.0018, 0.0005] | 20.00 [8.00, 32.00] | -0.60 [-0.95, -0.24] |
| injected_paper_electricity/gradual/feature_filtering | 50 | 0.0002 [-0.0000, 0.0005] | 0.0010 [-0.0003, 0.0025] | -5.00 [-16.00, 6.00] | -0.85 [-3.12, 0.42] |
| injected_paper_electricity/gradual/feature_permutation | 50 | -0.0007 [-0.0015, -0.0001] | 0.0005 [-0.0018, 0.0032] | -8.00 [-22.00, 5.00] | -6.77 [-12.72, -1.52] |
| injected_paper_electricity/gradual/label_swap | 50 | 0.0006 [-0.0040, 0.0056] | 0.0001 [-0.0013, 0.0015] | 19.00 [3.00, 35.00] | -14.56 [-22.50, -7.24] |
| injected_paper_gas_sensor_drift/abrupt/class_prior | 50 | -0.0002 [-0.0006, 0.0001] | -0.0010 [-0.0025, 0.0001] | -10.00 [-17.00, -4.00] | -0.00 [-2.41, 1.50] |
| injected_paper_gas_sensor_drift/abrupt/feature_filtering | 50 | -0.0022 [-0.0034, -0.0010] | -0.0259 [-0.0400, -0.0134] | 11.00 [0.00, 22.00] | -6.14 [-14.50, 2.07] |
| injected_paper_gas_sensor_drift/abrupt/feature_permutation | 50 | -0.0023 [-0.0032, -0.0014] | -0.0455 [-0.0539, -0.0370] | -5.00 [-13.00, 3.00] | 0.48 [-0.30, 1.28] |
| injected_paper_gas_sensor_drift/abrupt/label_swap | 50 | -0.0032 [-0.0050, -0.0015] | -0.0190 [-0.0265, -0.0119] | 6.00 [-6.00, 17.00] | -17.63 [-25.53, -9.59] |
| injected_paper_gas_sensor_drift/gradual/class_prior | 50 | 0.0001 [-0.0001, 0.0003] | 0.0003 [0.0000, 0.0008] | -2.00 [-8.00, 4.00] | 0.20 [-2.80, 3.20] |
| injected_paper_gas_sensor_drift/gradual/feature_filtering | 50 | -0.0022 [-0.0042, -0.0002] | -0.0002 [-0.0005, 0.0000] | 3.00 [-7.00, 12.00] | 0.67 [-2.85, 4.63] |
| injected_paper_gas_sensor_drift/gradual/feature_permutation | 50 | -0.0011 [-0.0020, -0.0003] | -0.0129 [-0.0195, -0.0063] | 12.00 [2.00, 22.00] | -14.20 [-21.06, -7.98] |
| injected_paper_gas_sensor_drift/gradual/label_swap | 50 | -0.0006 [-0.0027, 0.0017] | 0.0003 [-0.0010, 0.0019] | -13.00 [-23.00, -3.00] | 1.17 [0.22, 2.13] |
| insects_abrupt_balanced | 1 | 0.0012 | 0.0360 | 3.00 | -0.27 |
| insects_incremental_abrupt_reoccurring_balanced | 1 | 0.0046 | 0.0165 | 11.00 | -0.22 |
| insects_incremental_balanced | 1 | 0.0027 | — | — | — |
| insects_incremental_gradual_balanced | 1 | 0.0106 | -0.0040 | 7.00 | -1.19 |
| insects_incremental_reoccurring_balanced | 1 | 0.0023 | -0.0300 | 3.00 | -0.06 |
| synthetic_binary/gradual | 10 | 0.0063 [0.0009, 0.0138] | 0.0040 [-0.0004, 0.0106] | 12.00 [3.00, 20.00] | 14.05 [6.56, 22.27] |
| synthetic_binary/incremental | 10 | -0.0000 [-0.0010, 0.0009] | -0.0005 [-0.0024, 0.0017] | 11.00 [2.00, 21.00] | 2.15 [-3.38, 7.04] |
| synthetic_binary/recurring_gradual | 4 | 0.0120 | 0.0052 | 1.00 | 8.89 |
| synthetic_binary/recurring_incremental | 2 | -0.0033 | -0.0105 | 2.00 | -2.22 |
| synthetic_binary/recurring_sudden | 4 | 0.0000 | -0.0094 | 20.00 | -0.48 |
| synthetic_binary/sudden | 10 | -0.0005 [-0.0035, 0.0026] | -0.0009 [-0.0072, 0.0054] | 15.00 [5.00, 25.00] | 15.63 [6.45, 24.40] |
| synthetic_multiclass/gradual | 10 | -0.0002 [-0.0088, 0.0082] | -0.0031 [-0.0090, 0.0045] | -3.00 [-13.00, 9.00] | -6.62 [-13.22, 1.48] |
| synthetic_multiclass/incremental | 10 | 0.0095 [-0.0025, 0.0237] | 0.0081 [-0.0038, 0.0213] | -6.00 [-23.00, 9.00] | -6.68 [-11.69, -2.20] |
| synthetic_multiclass/recurring_gradual | 5 | 0.0203 [0.0075, 0.0332] | 0.0270 [0.0062, 0.0474] | -4.00 [-5.00, -2.00] | 4.26 [-2.78, 12.26] |
| synthetic_multiclass/recurring_incremental | 2 | 0.0372 | 0.0059 | 2.00 | -1.17 |
| synthetic_multiclass/recurring_sudden | 3 | -0.0086 | -0.0484 | -1.00 | 0.10 |
| synthetic_multiclass/sudden | 10 | -0.0004 [-0.0096, 0.0078] | -0.0449 [-0.0538, -0.0365] | 0.00 [-10.00, 12.00] | -0.09 [-1.08, 0.76] |

## 跨子資料集方向計數顯示型態是否一致

嚴格以『同組所有可判讀子資料集同號』判定時，沒有任何 drift 型態或注入方式在任一指標上達到一致為正或一致為負；因此以下保留完整方向計數，不把多數方向寫成一致效果。

方向解讀：準確率、drift 後準確率與 X 的正值有利 Dual ADWIN；FP 的負值才有利 Dual ADWIN。描述性分布上，突變組的準確率與 drift 後準確率負向較多，漸變組則正向較多；incremental／recurring 的準確率正向較多但 X 負向較多。四種注入方式仍各自同時出現正負值：class_prior 正向較多，feature_permutation 的 X 負向較多，label_swap 的 drift 後準確率負向較多；這些都不是一致效果。

### Drift 型態均包含正負方向，不能推論普遍優勢

- **突變：** 準確率正/負/零=15/21/2；drift 後準確率正/負/零=9/25/4；FP正/負/零=23/13/2；X正/負/零=18/19/1。
- **漸變：** 準確率正/負/零=23/11/3；drift 後準確率正/負/零=21/13/3；FP正/負/零=18/15/4；X正/負/零=17/18/2。
- **incremental：** 準確率正/負/零=6/2/0；drift 後準確率正/負/零=3/4/0；FP正/負/零=6/1/0；X正/負/零=1/6/0。
- **recurring：** 準確率正/負/零=6/2/0；drift 後準確率正/負/零=4/4/0；FP正/負/零=6/2/0；X正/負/零=3/5/0。

### 注入方式以跨資料集／abruptness 的方向計數呈現

- **class_prior：** 準確率正/負/零=10/4/2；drift 後準確率正/負/零=9/5/2；FP正/負/零=10/6/0；X正/負/零=9/7/0。
- **feature_filtering：** 準確率正/負/零=7/8/1；drift 後準確率正/負/零=6/8/2；FP正/負/零=10/5/1；X正/負/零=6/9/1。
- **feature_permutation：** 準確率正/負/零=6/8/2；drift 後準確率正/負/零=5/8/3；FP正/負/零=6/7/3；X正/負/零=4/10/2。
- **label_swap：** 準確率正/負/零=8/8/0；drift 後準確率正/負/零=5/11/0；FP正/負/零=8/7/1；X正/負/零=11/5/0。

## 限制要求將成本缺口、CI 邊界與開發資料分開解讀

- 沿用 DET1／DET3 的 run 若未記錄成本欄位，成本中位數排除空值；不得把不同機器或不同 `concurrent_runs` 的時間當成正式效能比較。
- 單一串流，以及其他少於 5 條串流的子資料集，只報點估計、不報 bootstrap CI。
- `synthetic_binary`、`synthetic_multiclass` 與部分資料曾用於開發；其子資料集結果不能視為獨立外部驗證。
- 注入資料的 pooled detection 遵循 registry 的 skill window；DET 系列 `FP@1000`、`X` 則沿用 DET1–DET4 正式分析函式，兩者定義不可互換。

## 缺漏保持可稽核，不以推估值補齊

未發現缺失或損毀 run；30,456 列皆由本機原始 artifact 讀取並通過既有 DET4 audit。
