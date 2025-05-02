#!/bin/bash
set -e  # 任何錯誤立即終止腳本

# 定義常用變數
COMPOSE_FILE="docker-compose.yml"  # 你的 compose 檔案路徑
PROJECT_NAME="food_fridge"       # 專案名稱(需與 compose 的 container 前綴一致)
VOLUMES=("postgres_data" "static_volume")  # 需要檢查的 volume 列表

echo "=== 啟動剩食冰箱系統部署流程 ==="

# 1. 停止並移除現有容器(保留 volume)
echo "停止現有容器..."
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} down --remove-orphans

# 2. 建立必要 volume（如果不存在）
echo "檢查並建立 volume..."
for volume in "${VOLUMES[@]}"; do
    if ! docker volume inspect ${volume} > /dev/null 2>&1; then
        echo "建立 volume: ${volume}"
        docker volume create ${volume}
    else
        echo "Volume 已存在: ${volume}"
    fi
done

# 3. 複製環境變數檔案（根據你的專案結構調整）
if [ -f .env ]; then
    echo "複製環境變數檔案..."
    cp .env web/.env 2>/dev/null || echo "警告: 無法複製到 web 目錄"
    cp .env postgres/.env 2>/dev/null || echo "警告: 無法複製到 postgres 目錄"
else
    echo "警告: 未找到 .env 檔案，請確保已設定環境變數"
fi

# 4. 建置並啟動服務
echo "啟動容器..."
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} up --build -d

# 5. 等待 PostgreSQL 就緒（最多等待 60 秒）
echo "等待資料庫啟動..."
timeout=60
start_time=$(date +%s)
while :; do
    if docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} exec db pg_isready -U db_user -d fridge_db > /dev/null 2>&1; then
        break
    fi
    
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    
    if [ $elapsed -ge $timeout ]; then
        echo "錯誤: 資料庫啟動逾時"
        exit 1
    fi
    
    echo "等待資料庫... (已等待 ${elapsed} 秒)"
    sleep 5
done
echo "資料庫已就緒！"

# 6. 執行資料庫遷移
echo "執行 Django 資料庫遷移..."
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} exec web python manage.py makemigrations

echo "優先遷移自訂用戶模型 app..."
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} exec web python manage.py migrate food_fridge

echo "遷移所有 app..."
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} exec web python manage.py migrate

# 7. 收集靜態檔案（根據需要啟用）
echo "收集靜態檔案..."
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} exec web python manage.py collectstatic --noinput

echo "=== 系統部署完成！訪問 http://localhost:16701 ==="
