FROM python:3.10.5-alpine

ENV USER_ID=65535
ENV USER_NAME=gitbackup

RUN adduser --shell /sbin/nologin --disabled-password \
    --no-create-home --uid $USER_ID $USER_NAME && \
    apk --no-cache add git

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./git_repo_backup ./git_repo_backup

USER $USER_NAME

ENTRYPOINT [ "python3", "git_repo_backup" ]