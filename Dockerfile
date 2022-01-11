FROM python:3.7.12-slim-bullseye
MAINTAINER Glenn Harper "zeigotaro@gmail.com"

RUN apt-get update -y; \
    apt-get upgrade -y; \
    apt-get install -y libpoppler-cpp-dev;
ENV BUILD_PACKAGES="\
        build-essential \
        linux-headers-5.10 \
        pkg-config \
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
        libx11-dev \
        fontconfig \
        libxrender-dev \
        libxext-dev \
        wkhtmltopdf" \
    PATH=/usr/local/bin:$PATH \
    PYTHON_PIP_VERSION=21.3.1 \
    LANG=C.UTF-8

RUN set -ex; 
RUN apt-get install -y --no-install-recommends ${APT_PACKAGES}; \
    apt-get install -y --no-install-recommends ${BUILD_PACKAGES};
RUN python3 --version;

RUN ln -s /usr/bin/idle3 /usr/bin/idle; \
    ln -s /usr/bin/pydoc3 /usr/bin/pydoc; \
    ln -s /usr/bin/python3 /usr/bin/python; \
    ln -s /usr/bin/python3-config /usr/bin/python-config;

ENV PIP_PACKAGES="\
        pyyaml \
        pymkl \
        Flask \
        requests \
        mysql-connector-python-rf \
        pdfkit \
        python-docx \
        pdftotext" 

RUN pip install -U -v setuptools wheel
RUN pip install pillow==9.0.0; 
RUN pip install numpy==1.18.5; \
    pip install pandas==1.0.5;
RUN pip install scipy==1.7.3; \
    pip install xlrd==1.2.0; \ 
    pip install grpcio==1.43.0; 
RUN pip install -U -v ${PIP_PACKAGES}; 
RUN pip install tensorflow==1.15

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