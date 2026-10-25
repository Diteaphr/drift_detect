# 分流確認：可重現性閘門 通過

**結論：** 32/32 個 run 的 n_scored, correct, alarms, tp, fp, fn, hits, post_correct, post_count, warning_opened, warning_self_closed, warning_timeout, confirmations 與 X 和 DET4 完全相同。

| preset | dataset | stream | result | differing fields |
|---|---|---|---|---|
| s1route_fixed_adwin | injected_paper_electricity | electricity_class_prior_abrupt_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_electricity | electricity_class_prior_gradual_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_electricity | electricity_feature_filtering_abrupt_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_electricity | electricity_feature_filtering_gradual_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_electricity | electricity_feature_permutation_abrupt_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_electricity | electricity_feature_permutation_gradual_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_electricity | electricity_label_swap_abrupt_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_electricity | electricity_label_swap_gradual_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_electricity | electricity_class_prior_abrupt_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_electricity | electricity_class_prior_gradual_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_electricity | electricity_feature_filtering_abrupt_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_electricity | electricity_feature_filtering_gradual_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_electricity | electricity_feature_permutation_abrupt_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_electricity | electricity_feature_permutation_gradual_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_electricity | electricity_label_swap_abrupt_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_electricity | electricity_label_swap_gradual_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_gas_sensor_drift | gas_sensor_drift_class_prior_abrupt_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_gas_sensor_drift | gas_sensor_drift_class_prior_gradual_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_gas_sensor_drift | gas_sensor_drift_feature_filtering_abrupt_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_gas_sensor_drift | gas_sensor_drift_feature_filtering_gradual_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_gas_sensor_drift | gas_sensor_drift_feature_permutation_abrupt_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_gas_sensor_drift | gas_sensor_drift_feature_permutation_gradual_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_gas_sensor_drift | gas_sensor_drift_label_swap_abrupt_g00 | 相同 |  |
| s1route_fixed_adwin | injected_paper_gas_sensor_drift | gas_sensor_drift_label_swap_gradual_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_gas_sensor_drift | gas_sensor_drift_class_prior_abrupt_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_gas_sensor_drift | gas_sensor_drift_class_prior_gradual_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_gas_sensor_drift | gas_sensor_drift_feature_filtering_abrupt_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_gas_sensor_drift | gas_sensor_drift_feature_filtering_gradual_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_gas_sensor_drift | gas_sensor_drift_feature_permutation_abrupt_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_gas_sensor_drift | gas_sensor_drift_feature_permutation_gradual_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_gas_sensor_drift | gas_sensor_drift_label_swap_abrupt_g00 | 相同 |  |
| s1route_fixed_hddma | injected_paper_gas_sensor_drift | gas_sensor_drift_label_swap_gradual_g00 | 相同 |  |
