# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ===== 基础镜像参数配置 =====
# 基础Ubuntu镜像地址和标签
ARG BASE_IMAGE_URL=nvcr.io/nvidia/base/ubuntu
ARG BASE_IMAGE_TAG=22.04_20240212

# Python和AIQ版本配置
ARG PYTHON_VERSION=3.12
ARG AIQ_VERSION=1.0.0
ARG UV_VERSION=0.5.31

# ===== 构建阶段：获取UV工具 =====
# 从官方UV镜像获取uv二进制文件
FROM --platform=$TARGETPLATFORM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv_base

# ===== 主镜像构建阶段 =====
# 基于Ubuntu的基础镜像
FROM ${BASE_IMAGE_URL}:${BASE_IMAGE_TAG} AS base

# 重新声明参数以便在主镜像中使用
ARG AIQ_VERSION
ARG PYTHON_VERSION
ARG UV_VERSION

# 从UV基础镜像复制uv工具
COPY --from=uv_base /uv /uvx /bin/

# 禁用Python字节码生成以减小镜像大小
ENV PYTHONDONTWRITEBYTECODE=1

# ===== 系统依赖安装 =====
# 更新系统并安装必要的证书包和git工具
RUN export DEBIAN_FRONTEND=noninteractive && \
    export TZ=Etc/UTC && \
    apt-get update && \
    apt upgrade -y && \
    apt-get install --no-install-recommends -y ca-certificates git && \
    apt clean && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ===== SSL证书配置 =====
# 设置SSL证书环境变量，确保HTTPS连接正常
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# ===== 工作目录设置 =====
# 创建并设置工作目录
WORKDIR /workspace

# ===== 项目文件拷贝 =====
# 拷贝所有项目文件到容器工作目录
COPY . /workspace/

# ===== 完整环境安装 =====
# 在一个RUN命令中完成所有安装步骤，减少镜像层数
RUN --mount=type=cache,id=uv_cache,target=/root/.cache/uv,sharing=locked \
    uv venv --python ${PYTHON_VERSION} /workspace/.venv && \
    . /workspace/.venv/bin/activate && \
    uv pip install -e . && \
    uv pip install -e .[langchain] && \
    uv pip install tavily-python && \
    uv pip install langchain && \
    uv pip install langchain_chroma && \
    uv pip install langchain_dashscope && \
    uv pip install -e external/my_multi_agent

# ===== 环境变量配置 =====
# 将虚拟环境的bin目录添加到PATH，确保可以直接使用安装的命令
ENV PATH="/workspace/.venv/bin:$PATH"

# ===== 端口暴露 =====
# 仅暴露后端API端口8001
EXPOSE 8001

# ===== 容器入口点 =====
# 设置容器启动命令为AIQ服务
ENTRYPOINT ["aiq", "serve", "--config_file", "external/my_multi_agent/src/my_multi_agent/configs/multi_agent_config.yml", "--host", "0.0.0.0", "--port", "8001"]