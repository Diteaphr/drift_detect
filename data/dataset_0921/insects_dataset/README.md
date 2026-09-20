# insects_dataset

獨立於 `data/real_dataset/` 的 **Insects** 真實串流（Souza et al. 2020）。  
此集合有論文公布的 **concept drift change points**（Table 2），因此與一般無 GT drift 的真實集分開存放。

目前只收錄 **balanced (bal.)** 變體；imbalanced / out-of-control 未納入。

## 檔案結構

```text
data/insects_dataset/
├── multi_classification/
│   ├── incremental_balanced/                      # Incremental (bal.)
│   ├── abrupt_balanced/                           # Abrupt (bal.)
│   ├── incremental_gradual_balanced/              # Incremental-gradual (bal.)
│   ├── incremental_abrupt_reoccurring_balanced/   # Incremental-abrupt-reoccurring (bal.)
│   ├── incremental_reoccurring_balanced/          # Incremental-reoccurring (bal.)
│   └── drift_plots/
├── script/
├── _raw/
└── README.md
```

每個 variant 含：`{name}.csv`、`{name}_drift_times.txt`、`{name}_meta.json`。

## 與論文 Table 2 對照（balanced）

| 論文名稱 | 本目錄 variant | 總樣本數 | Change points | 飄移模式與溫度說明 |
|---|---|---|---|---|
| Incremental (bal.) | `incremental_balanced` | 57,018 | 貫穿整條（`[]`） | 溫度由 20°C 平滑遞增至 40°C，特徵呈現連續且緩慢的遞增型飄移。 |
| Abrupt (bal.) | `abrupt_balanced` | 52,848 | 14,352；19,500；33,240；38,682；39,510 | 包含 5 個突發切換點，將數據分為 6 個穩定的溫度概念區間（A–F）。 |
| Incremental-gradual (bal.) | `incremental_gradual_balanced` | 24,150 | 14,028 | 由 37°C 遞減至 35°C 後進入漸進過渡期，35°C 與 23°C 兩種概念交替出現，過渡點在第 14,028 筆，最後完全轉為 23°C 並平滑升至 27°C。 |
| Incremental-abrupt-reoccurring (bal.) | `incremental_abrupt_reoccurring_balanced` | 79,986 | 26,568；53,364 | 包含 3 個 20°C→40°C 的遞增升溫週期，週期之間在第 26,568 與 53,364 筆發生斷崖式突發跳躍跌回 20°C。 |
| Incremental-reoccurring (bal.) | `incremental_reoccurring_balanced` | 79,986 | 26,568；53,364 | 包含 3 個連續升降溫週期（20°C→40°C→20°C→40°C），在第 26,568 與 53,364 筆為平滑轉折點，無突發斷層。 |

- 任務：multi-class（6 類；原始碼 remap 為 0..5）
- 特徵：33 維 → `x0..x32` + `y`
- `*_drift_times.txt`：`[[t, t], ...]`；連續飄移者為 `[]`
- 注意：y 的 rolling 比例圖常有「成群出現」造成的局部尖峰，**不等於**論文 GT change points；評估請以 `*_drift_times.txt` 為準。

## 來源

- Paper: https://arxiv.org/abs/2005.00113  
- Repo: https://sites.google.com/view/uspdsrepository  

## 重跑

```bash
cd data/insects_dataset/script
python3 prepare_all.py
python3 prepare_all.py --variants abrupt_balanced,incremental_gradual_balanced
```
