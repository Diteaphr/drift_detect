# synthetic_dataset

整理後的合成概念漂移資料集，可供現行 ECPF / pipeline（`load_recurring_stream_pair`）直接讀取。

## 檔案結構

```text
data/synthetic_dataset/
├── binary/
│   ├── drift_plots/          # g00 驗證圖
│   ├── sudden/               # SEA sudden
│   ├── gradual/              # SEA gradual（width ≤ 1000）
│   ├── incremental/          # 過渡 width≤1000，新概念持續至下一次漂移
│   └── recurring/            # 隨機 sudden/gradual/incremental + manifest.json
├── multi_classification/
│   ├── drift_plots/
│   ├── sudden/               # RandomRBF4
│   ├── gradual/
│   ├── incremental/
│   └── recurring/
├── regression/
│   ├── drift_plots/
│   ├── sudden/               # Friedman
│   ├── gradual/
│   ├── incremental/
│   └── recurring/
├── script/                   # 產生與畫圖腳本
│   ├── generate_all.py       # 主入口
│   ├── generators.py         # 各 task 產生邏輯
│   ├── common.py             # I/O、驗證、計畫、畫圖
│   └── config.py             # 參數
└── README.md
```

## 檔案說明

| 路徑 / 檔名 | 功能 |
|---|---|
| `*/sudden|gradual|incremental|recurring/*.csv` | 串流樣本（特徵欄 + `y`） |
| `*_drift_times.txt` | drift 區間 `[[start, end], ...]` |
| `recurring/*.json` | 單一 recurring 檔的 seed / mode / 參數 |
| `recurring/manifest.json` | 該 task 全部 recurring 抽樣結果 |
| `*/drift_plots/*.png` | g00 驗證圖（**with drift / no drift** 雙線 + 區間） |
| `script/generate_all.py` | 一鍵產生（含 smoke test） |

## 重跑

```bash
cd data/synthetic_dataset/script

# 小樣本檢查
python3 generate_all.py --smoke

# 完整 100k、g00–g09
python3 generate_all.py
```
