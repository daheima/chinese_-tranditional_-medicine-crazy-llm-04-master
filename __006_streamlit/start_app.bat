@echo off
echo ==============================
echo 启动 Streamlit 同步版页面
echo ==============================
echo.
echo 页面地址: http://localhost:8501
echo.

streamlit run app.py --server.port 8501

pause
