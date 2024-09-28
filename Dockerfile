# 使用 Debian 或 Ubuntu 基础镜像
FROM ubuntu:20.04
FROM python:3.8
# 设置环境变量以避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive
# 更新包列表并安装 libGL.so.1
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/
RUN pip install --upgrade pip
RUN pip install -r requirement.txt
RUN pip install paddlepaddle==2.6.1 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
WORKDIR /wows_ocr
COPY ./ /wows_ocr
CMD ["python", "main.py"]
