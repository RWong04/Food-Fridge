#!/bin/bash
set -e

COMPOSE_FILE="docker-compose.yml"  # 你的 compose 檔案路徑
PROJECT_NAME="final_project"       # 專案名稱(需與 compose 的 container 前綴一致)

echo "=== 停止所有運行中之容器 ==="

docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} down --remove-orphans

echo "=== 所有容器已停止 ==="