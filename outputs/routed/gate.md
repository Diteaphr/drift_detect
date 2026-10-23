# 分流確認：可重現性閘門 通過

**結論：** 30/30 個 run 的 n_scored, correct, alarms, tp, fp, fn, hits, post_correct, post_count, warning_opened, warning_self_closed, warning_timeout, confirmations 與 X 和 DET4 完全相同。

| preset | dataset | stream | result | differing fields |
|---|---|---|---|---|
| s1route_fixed_adwin | insects_abrupt_balanced | abrupt_balanced | 相同 |  |
| s1route_fixed_hddma | insects_abrupt_balanced | abrupt_balanced | 相同 |  |
| s1route_fixed_adwin | insects_incremental_balanced | incremental_balanced | 相同 |  |
| s1route_fixed_hddma | insects_incremental_balanced | incremental_balanced | 相同 |  |
| s1route_fixed_adwin | insects_incremental_gradual_balanced | incremental_gradual_balanced | 相同 |  |
| s1route_fixed_hddma | insects_incremental_gradual_balanced | incremental_gradual_balanced | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | gradual_rbf4_100k_g00 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | gradual_rbf4_100k_g01 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | incremental_rbf4_100k_g00 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | incremental_rbf4_100k_g01 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | recurring_gradual_rbf4_100k_g01 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | recurring_gradual_rbf4_100k_g03 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | recurring_incremental_rbf4_100k_g00 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | recurring_incremental_rbf4_100k_g02 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | recurring_sudden_rbf4_100k_g07 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | recurring_sudden_rbf4_100k_g08 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | sudden_rbf4_100k_g00 | 相同 |  |
| s1route_fixed_adwin | synthetic_multiclass | sudden_rbf4_100k_g01 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | gradual_rbf4_100k_g00 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | gradual_rbf4_100k_g01 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | incremental_rbf4_100k_g00 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | incremental_rbf4_100k_g01 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | recurring_gradual_rbf4_100k_g01 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | recurring_gradual_rbf4_100k_g03 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | recurring_incremental_rbf4_100k_g00 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | recurring_incremental_rbf4_100k_g02 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | recurring_sudden_rbf4_100k_g07 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | recurring_sudden_rbf4_100k_g08 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | sudden_rbf4_100k_g00 | 相同 |  |
| s1route_fixed_hddma | synthetic_multiclass | sudden_rbf4_100k_g01 | 相同 |  |
