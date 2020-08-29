FROM debian:buster-slim
MAINTAINER Glenn Harper "zeigotaro@gmail.com"

RUN apt-get update -y; \
    apt-get upgrade -y; \
    apt-get install -y libpoppler-cpp-dev;
ENV BUILD_PACKAGES="\
        build-essential \
        linux-headers-4.19 \
        pkg-config \
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
        python3-pip \
        libx11-dev \
        fontconfig \
        libxrender-dev \
        libxext-dev \
        wget \
        wkhtmltopdf" \
    PIP_PACKAGES="\
        pyyaml \
        pymkl \
        pillow \
        Flask \
        xlrd \
        tensorflow \
        numpy \
        pandas \
        requests \
        mysql-connector-python-rf \
        pdfkit \
        python-docx \
        pdftotext" \
    PYTHON_VERSION=3.7.3 \
    PATH=/usr/local/bin:$PATH \
    PYTHON_PIP_VERSION=18.1 \
    LANG=C.UTF-8

RUN set -ex; 
RUN apt-get install -y --no-install-recommends ${APT_PACKAGES}; \
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

ENV DB_PASSWORD=<PASSWORD>
ENV DB_USER=<USER>
ENV DB_HOST=<HOST>
ENV DB_SCHEMA=<SCHEMA>
ENV CERT_FILE=<CERT>