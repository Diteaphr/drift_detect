# real_dataset

真實串流資料集（格式對齊實驗用：特徵 + `y`），無 sudden/gradual 等合成 drift 子目錄，亦無虛構 `drift_times`。

> 超過 **100,000** 筆的來源會**保留前 10 萬筆**（串流順序），避免單檔超過 GitHub 100MB 限制。

## 檔案結構

```text
data/real_dataset/
├── binary/
│   ├── ai4i2020/
│   ├── electricity/
│   ├── airlines/
│   └── drift_plots/
├── multi_classification/
│   ├── gas_sensor_drift/
│   ├── covertype/
│   └── drift_plots/
├── regression/
│   ├── metro_interstate_traffic/
│   ├── bike_sharing/
│   └── drift_plots/
├── script/          # prepare_all.py
├── _raw/            # 原始下載快取
└── README.md
```

每個資料集資料夾含：`{name}.csv`、`{name}_meta.json`。

## 資料集

| 路徑 | 任務 | 來源 | 目標 `y` | 筆數 |
|---|---|---|---|---|
| `binary/ai4i2020` | binary | [UCI 601](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset) | Machine failure (0/1) | 10,000 |
| `binary/electricity` | binary | [OpenML electricity](https://www.openml.org/d/151) | UP/DOWN → 1/0 | 45,312 |
| `binary/airlines` | binary | [OpenML airlines](https://www.openml.org/d/1169) | Delay 0/1 | 100,000（原 ~539k，截前 10 萬） |
| `multi_classification/gas_sensor_drift` | multi (6) | [UCI 224](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset) | gas class → 0..5 | 13,910 |
| `multi_classification/covertype` | multi (7) | [UCI Covertype](https://archive.ics.uci.edu/dataset/31/covertype) | Cover_Type → 0..6 | 100,000（原 ~581k，截前 10 萬） |
| `regression/metro_interstate_traffic` | regression | [UCI 492](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) | hourly traffic_volume | ~48,000 |
| `regression/bike_sharing` | regression | [UCI 275](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) | hourly `cnt` | 17,379 |

特徵欄統一為 `x0,x1,...` + `y`；列順序保留時間／原始串流順序（未 shuffle）。

`drift_plots/` 使用**因果** rolling mean：時刻 \(t\) 取**前至多 500 筆**（含 \(t\)）平均，無未來視窗。

## 重跑

```bash
cd data/dataset_0921/real_dataset/script
python3 prepare_all.py
python3 prepare_all.py --tasks binary
python3 prepare_all.py --datasets ai4i2020,electricity,airlines
```
