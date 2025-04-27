#!/bin/bash
set -e

echo "=== 停止所有運行中之容器 ==="

docker-compose -f "docker/docker-compose.issuer.yml" -p issuer down --remove-orphans

echo "=== 所有容器已停止 ==="