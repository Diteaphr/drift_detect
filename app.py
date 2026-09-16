"""ECPF 漂移監控 dashboard -- 角色切換入口。

    streamlit run app.py

Two views over one pipeline run (docs/DASHBOARD_TWO_VIEWS_PLAN.md):

* **一般使用者** (`views/operator.py`) -- 哪裡有 drift、什麼型態、影響多大、
  多久恢復。無參數。
* **工程師** (`views/engineer.py`) -- 原本的監控台：訊號、偵測器、模型池、
  離線報告，全部參數可調。

The run itself lives in `core/run.py` and its result is parked in
`st.session_state["run_result"]`, so switching roles re-renders the same run
instead of re-running the pipeline.
"""

from __future__ import annotations

import streamlit as st

from views import engineer, operator

# Operator first: the simple view is what a newcomer should land on (plan §5).
ROLES = {
    "🙂 一般使用者": operator.render,
    "🛠 工程師": engineer.render,
}


def main() -> None:
    st.set_page_config(page_title="ECPF 漂移監控", layout="wide")
    with st.sidebar:
        role = st.radio("介面", list(ROLES), index=0, key="role")
        st.divider()
    ROLES[role]()


if __name__ == "__main__":
    main()
