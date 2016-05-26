###############
# Dockerfile for plumbery
###############

FROM python:2.7
ENV VERSION="0.9.2"
ENV MCP_USERNAME=""
ENV MCP_PASSWORD=""
ENV SHARED_SECRET=""
ENV REGION=""
ENV FITTINGS=""
ENV ACTION="deploy"
ENV OPTS="-d"
ENV WGET_OPTS=""
ENV PARAMETERS=""

MAINTAINER "Dimension Data"

# Install basic applications
RUN apt-get install -y git wget

# Download the code
RUN git clone -b $VERSION --single-branch https://github.com/DimensionDataCBUSydney/plumbery

# Copy the application folder inside the container
ADD plumbery plumbery

# Get pip to download and install requirements:
RUN pip install requests apache-libcloud==1.0.0-rc2 PyYAML paramiko netifaces pywinexe

# install winexe for remote windows commands.
RUN wget http://download.opensuse.org/repositories/home:/uibmz:/opsi:/opsi40-testing/xUbuntu_12.04/amd64/winexe_1.00.1-1_amd64.deb && dpkg --install winexe_1.00.1-1_amd64.deb

# Set the default directory where CMD will execute
WORKDIR plumbery

# Deploy fitting
CMD wget ${WGET_OPTS} ${FITTINGS} -O fittings.yaml && python -m plumbery ${OPTS} ${PARAMETERS} fittings.yaml ${ACTION}
