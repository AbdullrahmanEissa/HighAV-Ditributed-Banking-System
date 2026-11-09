FROM postgres:16-alpine

RUN apk add --no-cache python3 py3-pip curl gcc python3-dev musl-dev linux-headers && \
    pip3 install --no-cache-dir --break-system-packages patroni[etcd3] psycopg2-binary && \
    apk del gcc python3-dev musl-dev linux-headers

USER postgres
