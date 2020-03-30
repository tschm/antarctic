FROM rocker/tidyverse:3.6.1

# see https://arrow.apache.org/install/
# rocker/rstudio is based on debian
RUN apt update && \
    apt install -y -V apt-transport-https curl gnupg lsb-release apt-utils

RUN echo "deb http://deb.debian.org/debian $(lsb_release --codename --short)-backports main contrib"
RUN echo "deb http://deb.debian.org/debian $(lsb_release --codename --short)-backports main contrib" >> /etc/apt/sources.list.d/backports.list && \
    curl --output /usr/share/keyrings/apache-arrow-keyring.gpg https://dl.bintray.com/apache/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/apache-arrow-keyring.gpg] https://dl.bintray.com/apache/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/ $(lsb_release --codename --short) main" >> /etc/apt/sources.list.d/apache-arrow.list && \
    echo "deb-src [signed-by=/usr/share/keyrings/apache-arrow-keyring.gpg] https://dl.bintray.com/apache/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/ $(lsb_release --codename --short) main" >> /etc/apt/sources.list.d/apache-arrow.list && \
    curl https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add - && \
    echo "deb http://apt.llvm.org/$(lsb_release --codename --short)/ llvm-toolchain-$(lsb_release --codename --short)-7 main" >> /etc/apt/sources.list.d/llvm.list && \
    echo "deb-src http://apt.llvm.org/$(lsb_release --codename --short)/ llvm-toolchain-$(lsb_release --codename --short)-7 main" >> /etc/apt/sources.list.d/llvm.list && \
    echo "deb http://deb.debian.org/debian $(lsb_release --codename --short) contrib" >> /etc/apt/sources.list.d/contrib.list && \
    echo "deb http://deb.debian.org/debian $(lsb_release --codename --short) non-free" >> /etc/apt/sources.list.d/non-free.list

RUN apt update && \
    apt install -y -V -f \
    libarrow-dev \
    libarrow-glib-dev \
    libarrow-flight-dev \
    libparquet-dev \
    libparquet-glib-dev \
    libgandiva-dev \
    libgandiva-glib-dev \
    libplasma-dev \
    libplasma-glib-dev

#RUN install2.r --error --deps TRUE devtools remotes arrow

RUN install2.r --error --deps TRUE arrow

#&& \
#    R -e 'remotes::install_github("apache/arrow/r@apache-arrow-0.15.0")'

# bring some python into the image
RUN apt install -y -V  python3-pip
RUN pip3 install pandas requests pyarrow==0.15.0

# don't try to install a jupyter server in here... not worth the hassle

