# airlines

OpenML Airlines（航班延誤二分類串流）。

| 項目 | 值 |
|---|---|
| 任務 | binary |
| 筆數 | 100,000（來源約 539k，保留前 10 萬） |
| 目標 `y` | Delay 0/1 |
| 來源 | https://www.openml.org/d/1169 |

重跑：

```bash
cd data/dataset_0921/real_dataset/script
python3 prepare_all.py --datasets airlines
```
