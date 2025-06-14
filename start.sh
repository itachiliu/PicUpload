#!/bin/bash

set -e

IMAGE_NAME=picupload
CONTAINER_NAME=picupload

# 构建镜像
docker build -t $IMAGE_NAME .

# 如果容器已存在则先删除
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    docker rm -f $CONTAINER_NAME
fi

# 启动容器，并挂载 uploads 目录
docker run -d -p 5000:5000 \
    -v $(pwd)/uploads:/app/uploads \
    --name $CONTAINER_NAME $IMAGE_NAME

echo "服务已启动，访问：http://localhost:5000"