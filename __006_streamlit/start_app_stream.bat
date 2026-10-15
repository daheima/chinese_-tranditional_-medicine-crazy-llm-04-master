@echo off
echo ==============================
echo 启动 Streamlit 流式版页面
echo ==============================
echo.
echo 页面地址: http://localhost:8502
echo.

streamlit run app_stream.py --server.port 8502

pause
