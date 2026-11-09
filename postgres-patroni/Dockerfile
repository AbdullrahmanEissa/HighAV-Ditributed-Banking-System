FROM postgres:16-alpine

RUN apk add --no-cache python3 py3-pip curl gcc python3-dev musl-dev linux-headers su-exec && \
    pip3 install --no-cache-dir --break-system-packages patroni[etcd3] psycopg2-binary && \
    apk del gcc python3-dev musl-dev linux-headers && \
    mkdir -p /var/lib/postgresql/data/pgdata /run/postgresql && \
    chown -R postgres:postgres /var/lib/postgresql /run/postgresql

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
