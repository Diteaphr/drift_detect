"""Deprecated entry point -- kept because DEPLOY.md and the deployed Streamlit
Cloud app point at this filename. The console moved to `views/engineer.py` and
now sits behind a role switch; see `app.py`.

    streamlit run app.py
"""

from app import main

if __name__ == "__main__":
    main()
