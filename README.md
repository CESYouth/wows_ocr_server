# wows_ocr_sever

#### 介绍
wows-stats-bot水表插件，图片OCR_API服务器
采用fastapi框架+paddleocr进行识别


#### 安装教程

1.  测试环境 python==3.8
2.  git clone https://gitee.com/Youth_YU/wows_ocr_sever.git
3.  cd wows_ocr_sever
4.  pip install -r requirement.txt
5.  安装paddle框架 参考:https://www.paddlepaddle.org.cn/
6.  python main.py

#### 使用说明

1.  config.json配置文件
2.  ocr_log  paddleocr的dubug，api_log  fastapi的log，time_log  各种处理耗时的输出
3.  save_image  保存成功识别的图片，gpu  启用gpu识别，port  端口
4.  img_size_max  最大输入图片，img_size_min 最小输入图片，img_aim_long 缩放至识别分辨率
