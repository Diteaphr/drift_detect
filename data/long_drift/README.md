# long_drift · 長版測試串流

`sudden_sea1m_g00.csv` —— `data/sudden_drift/sudden_sea100k_g00.csv` 的十倍長版本
（1,000,000 筆、72 次漂移），給需要「跑久一點」的展示用。

| 項目 | 內容 |
|---|---|
| 樣本數 | 1,000,000（原檔 100,000） |
| 欄位 | `x0, x1, x2, y`，特徵 ~ Uniform(0, 10)，`x2` 無關 |
| 標籤 | `y = 1 if x0 + x1 > θ else 0`（river SEA 規則），無 label noise |
| θ | 在基準 8 與 {7, 9, 9.5} 之間交替 |
| 漂移 | 72 次，間隔 5.3k–21.8k（原檔 5.4k–22.3k），每次 80 筆過渡帶 |
| Groundtruth | `sudden_sea1m_g00_drift_times.txt`，格式 `[[start, start+80], ...]` |
| 檔案大小 | 約 57 MB |

## 這不是原檔的複製或重取樣

生成規則是從 g00 本身反推出來的（作法同 `data/recurring_drift/README.md`）：
分段套四個 SEA 門檻去比對標籤，過渡帶外吻合度 1.00000，因此可以確定
「無雜訊 + θ 只在少數幾個值之間切換」這個結構，再用同樣的過程重新生成。
產生器：`scripts/generate_long_sudden_stream.py`（固定 seed，可重現）。

**漂移密度維持原檔的尺度**，沒有跟著拉長十倍：也就是說任何一段
20,000 筆看起來都跟原檔差不多，只是整條串流變長、漂移次數變多。
若要「漂移之間隔十倍遠」的版本，改產生器裡的 `GAP_LO / GAP_HI`。

## 驗證

```bash
python scripts/generate_long_sudden_stream.py   # 重新產生（會覆蓋）
```
