# Covertype（本機產生，不入 Git）

`covertype.csv` 約 **132 MB**，超過 GitHub 單檔 100 MB 上限，故 **不納入版本庫**。

本機若尚無此檔，請執行：

```bash
cd data/dataset_0921/real_dataset/script
python3 prepare_all.py --datasets covertype
```

`covertype_meta.json` 仍會入庫；CSV 產生後會留在此目錄（已被 `.gitignore` 忽略）。
