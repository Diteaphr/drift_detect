# covertype

UCI / sklearn Covertype（7 類森林覆蓋）。

| 項目 | 值 |
|---|---|
| 任務 | multi-class（7） |
| 筆數 | 100,000（來源約 581k，保留前 10 萬，以符合 GitHub <100MB） |
| 特徵 | 54（`x0`…） |
| 目標 `y` | Cover_Type → 0…6 |
| 來源 | https://archive.ics.uci.edu/dataset/31/covertype |

重跑：

```bash
cd data/dataset_0921/real_dataset/script
python3 prepare_all.py --datasets covertype
```
