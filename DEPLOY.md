# 部署到 Streamlit Community Cloud

這個 live monitor（`monitor_app.py`）只跑 repo 內既有的資料，不接受使用者上傳。
部署步驟如下。

## 1. 把這個分支推上 GitHub
本分支已含部署所需的一切：
- `requirements.txt` 已加入 `streamlit` 與 `altair`
- `.streamlit/config.toml` 主題與伺服器設定
- 選單只列出每種 drift type 各 2 份的精選資料（見 `monitor_app.py` 的 `DEMO_DRIFT_DIRS` / `DEMO_PER_TYPE`）

## 2. 在 Streamlit Cloud 建立 app
1. 到 https://share.streamlit.io → **New app**
2. 選這個 GitHub repo 與本分支
3. **Main file path** 填 `monitor_app.py`
4. 按 **Deploy**

Streamlit Cloud 會自動讀 `requirements.txt` 安裝依賴。約 2–3 分鐘後就有公開網址。

## 記憶體注意事項
免費方案約 1GB RAM，而資料檔是 100k 列。UI 的 `max_steps` 預設 20000，
展示綽綽有餘；若要跑完整 100k，把 `max_steps` 設 0，但接近上限時可能較慢。

## 想調整展示的資料
改 `monitor_app.py` 開頭的 `DEMO_DRIFT_DIRS`（有哪些 drift type）
和 `DEMO_PER_TYPE`（每種列幾份），重推即可。repo 內四種型態各有 10 份可選。
