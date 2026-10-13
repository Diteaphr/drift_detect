# DET3 接線可行性：既有流程可同時啟用 HDDM-A 與完整系統元件

**檢查日期：** 2026-10-13；在 DET3 預註冊與新資料執行之前完成。本階段只核對既有程式，不改偵測器語意。

## Frozen reference 的分類損失已接到 zone detector

`src/pipeline.py` 建立 `ECPFZoneDetector("hddm_a")` 或 Dual ADWIN detector 後，兩者都進入 `ECPF_ADWIN_FAMILY_SIGNAL_MODES` 的共同分支。啟用 `ecpf_reference_signal` 時，先在第一個可預測步凍結 leader；每步用 frozen model 預測，`_ref_loss` 對分類回傳 0/1 損失，並作為 `det_err` 送進 `extract_signal("error")`。zone 的 `update_values()` 因而讀取 reference 損失，而非 leader 的 `err`。`src/ecpf_detector.py` 將同一值送給 River HDDM-A，並以其 warning/drift zone 回報狀態。

## 守衛、逾時與 reference 生命週期共用同一路徑

`ecpf_leader_guard=True` 時，pipeline 另建單側 Dual ADWIN 守衛。守衛每步獨立讀 leader 自己的 error；主 detector 與守衛的 warning、drift 分別以 OR 合併，任一方均可開 warning 或確認 drift。zone 離區規則檢查的是合併後狀態：zone 離區但守衛仍在 warning／drift 時保持 warning；兩者均解除才關閉。這是既有程式的確定語意，兩個完整系統組別均沿用。

`ecpf_detector_warning_timeout=1000` 在共同分支關閉過久的 warning，清空 buffer，並對主 detector 呼叫 `reset_warning()`；zone detector 的此方法為空操作，讓 zone 自行管理狀態。確認 drift 時，主 detector 與守衛一同 reset，reference 從新安裝的 leader 凍結，並排定 500 步後的二次凍結。二次凍結會 reset 主 detector、關閉當時的 warning 並丟棄 buffer；它**不 reset 守衛**，這也與 Dual ADWIN 既有路徑完全相同。分類不進入 `ecpf_guard_frozen_scale` 的迴歸條件分支。

**決定：** F-H1 可使用現有 config 組合，不需新增選項或修改 pipeline。後續 smoke 須核對 reference 事件、守衛欄位與 warning 事件守恆；本檢查不使用 DET3 report 結果。

**程式依據：** `src/pipeline.py` 的 detector 建立、`step()` 共同分支、`_ref_loss()`／`_freeze_reference()`／`_switch_reference()`；`src/ecpf_detector.py` 的 `ECPFZoneDetector.update_values()`；`src/config.py` 的預設關閉選項。
