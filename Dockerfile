FROM debian:stretch-slim
MAINTAINER Glenn Harper "zeigotaro@gmail.com"

ENV BUILD_PACKAGES="\
        build-essential \
        linux-headers-4.9 \
        python3-dev \
        cmake \
        tcl-dev \
        xz-utils \
        zlib1g-dev \
        git \
        curl" \
    APT_PACKAGES="\
        ca-certificates \
        openssl \
        bash \
        libgomp1 \
        python3 \
        python3-pip" \
    PIP_PACKAGES="\
        pyyaml \
        pymkl \
        pillow \
        Flask \
        numpy \
        xlrd \
        tensorflow" \
    PYTHON_VERSION=3.6.5 \
    PATH=/usr/local/bin:$PATH \
    PYTHON_PIP_VERSION=18.0 \
    LANG=C.UTF-8

RUN set -ex; 
RUN apt-get update -y; \
    apt-get upgrade -y; \
    apt-get install -y --no-install-recommends ${APT_PACKAGES}; \
    apt-get install -y --no-install-recommends ${BUILD_PACKAGES};

RUN ln -s /usr/bin/idle3 /usr/bin/idle; \
    ln -s /usr/bin/pydoc3 /usr/bin/pydoc; \
    ln -s /usr/bin/python3 /usr/bin/python; \
    ln -s /usr/bin/python3-config /usr/bin/python-config; \
    ln -s /usr/bin/pip3 /usr/bin/pip; 

RUN pip install -U -v setuptools wheel; \
    pip install -U -v ${PIP_PACKAGES}; 

RUN apt-get remove --purge --auto-remove -y ${BUILD_PACKAGES}; \
    apt-get clean; \
    apt-get autoclean; \
    apt-get autoremove; \
    rm -rf /tmp/* /var/tmp/*; \
    rm -rf /var/lib/apt/lists/*; \
    rm -f /var/cache/apt/archives/*.deb \
        /var/cache/apt/archives/partial/*.deb \
        /var/cache/apt/*.bin; \
    find /usr/lib/python3 -name __pycache__ | xargs rm -r; \
    rm -rf /root/.[acpw]*;
 
ENV SERVER_HOST="0.0.0.0"
ENV SERVER_PORT=5555

RUN mkdir /code
WORKDIR /code
ADD . /code/

EXPOSE 5555

CMD ["python", "./runserver.py"]