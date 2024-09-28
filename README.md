# wows_ocr_sever for docker

#### 介绍
wows-stats-bot水表插件，图片OCR_API服务器
采用fastapi框架+paddleocr进行识别


#### 安装教程

1.拉取docker镜像
```
docker pull mackerelfish/wows-ocr-web:cpu
```
2.启动docker容器
```
docker run -d \
-p 23338:23338 \
--name wows-ocr-web \
--restart=always \
mackerelfish/wows-ocr-web:cpu
```

#### 使用说明

1.  config.json配置文件
2.  ocr_log  paddleocr的dubug，api_log  fastapi的log，time_log  各种处理耗时的输出
3.  save_image  保存成功识别的图片，gpu  启用gpu识别，port  端口
4.  img_size_max  最大输入图片，img_size_min 最小输入图片，img_aim_long 缩放至识别分辨率

#### 本项目仅编译基于cpu运算的paddleocr，docker镜像已编译成默认值，使用时自行替换成http://<yourhost>:23338

#### 如需其他版本的paddleocr（如基于NVIDIA芯片运算），请前往原作者的项目 https://github.com/CESYouth/wows_ocr_server 自行安装
