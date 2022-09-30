FROM alpine:3.16.2

# Metadata params
ARG BUILD_DATE
ARG ANSIBLE_VERSION
ARG ANSIBLE_LINT_VERSION
ARG MITOGEN_VERSION
ARG VCS_REF

# Metadata
LABEL maintainer="Pascal A. <emanoelopes@gmail.com>" \
      org.label-schema.url="https://github.com/emanoelopes/ansible-labs/README.md" \
      org.label-schema.build-date=${BUILD_DATE} \
      org.label-schema.version=${ANSIBLE_VERSION} \
      org.label-schema.vcs-url="https://github.com/emanoelopes/ansible-labs.git" \
      org.label-schema.vcs-ref=${VCS_REF} \
      org.label-schema.docker.dockerfile="/Dockerfile" \
      org.label-schema.description="Ansible on alpine docker image" \
      org.label-schema.schema-version="0.1"

RUN apk --update --no-cache add \
        ca-certificates \
        openssl \
        python3 \
        py3-pip \
        py3-cryptography \
        sshpass \
        pywinrm[credssp] \
        openssh-client \
        rsync 

RUN apk --update add --virtual \
        .build-deps \
        python3-dev \
        libffi-dev \
        openssl-dev \
        build-base \
 && pip3 install --upgrade \
        pip \
        cffi \
        pywinrm[credssp] \
 && pip3 install \
        ansible \
 && apk del \
        .build-deps \
 && rm -rf /var/cache/apk/*

RUN mkdir -p /etc/ansible \
 && echo 'localhost' > /etc/ansible/hosts \
 && echo -e """\
\n\
Host *\n\
    StrictHostKeyChecking no\n\
    UserKnownHostsFile=/dev/null\n\
""" >> /etc/ssh/ssh_config

#COPY entrypoint /usr/local/bin/

WORKDIR /ansible-labs

#ENTRYPOINT ["entrypoint"]

# default command: display Ansible version
CMD [ "ansible-playbook", "--version" ]

