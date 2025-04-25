## 架構說明
- **Django**：後端主體與資料庫操作
- **Gunicorn**：WSGI 伺服器，負責執行 Django
- **Nginx**：反向代理，處理靜態檔案與流量分發
- **Docker**：容器化專案，方便部署與維護

## 簡單指令
1. 首次啟動時，收集靜態檔案：
python manage.py collectstatic

2. 建立新 app：
python manage.py startapp <app_name>

3. 執行資料庫遷移：
docker-compose run web python manage.py migrate

4. 啟動服務：
docker-compose up --build