FROM alpine
# 指定基础的镜像包，‘：’后面是包的标签
MAINTAINER chen_zhuohan <chen_zhuohan@163.com>
# MAINTAINER 是用于指定镜像创建者和联系方式
WORKDIR /home
# 更新镜像源
RUN echo "http://mirrors.aliyun.com/alpine/latest-stable/main/" > /etc/apk/repositories &&\
    echo "http://mirrors.aliyun.com/alpine/latest-stable/community/" >> /etc/apk/r &&\
    apk update  &&\
    # 设置编码
    echo "export LC_ALL=en_US.UTF-8" >> ~/.bashrc &&\
    echo "export LANG=en_US.UTF-8" >> ~/.bashrc &&\
    # 设置时区
    apk add tzdata &&\
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime &&\
    echo "Asia/Shanghai" > /etc/timezone &&\
    # 安装python3
    apk add python3-dev python3 &&\
	python3 -m ensurepip &&\
    mkdir -p ~/.pip3/ && touch ~/.pip3/pip3.conf &&\
    echo "[global]" >> ~/.pip3/pip3.conf &&\
    echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> ~/.pip3/pip3.conf &&\
    pip3 install --upgrade pip setuptools &&\
    # 删除一些文件，减小文件大小
    rm -rf /var/lib/apt/lists/* &&\
    rm -rf .cache/pip &&\
    rm -rf /root/.cache /tmp/* &&\
    find / -name "*.py[co]" -exec rm '{}' ';'  &&\
	rm -rf /tmp/* /var/lib/apt/* /var/cache/* /var/log/*
ENV TZ Asia/Shanghai