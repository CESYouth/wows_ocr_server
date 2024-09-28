FROM python:3.8
RUN pip install --upgrade pip
WORKDIR /wows_ocr
COPY ./ /wows_ocr
RUN pip install -r requirement.txt
RUN pip install paddlepaddle==2.6.1 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
CMD ["python", "main.py"]
