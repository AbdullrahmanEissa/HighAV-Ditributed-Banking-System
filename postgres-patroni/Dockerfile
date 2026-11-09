FROM postgres:16-alpine

RUN apk add --no-cache python3 py3-pip py3-psycopg2 curl su-exec gcc python3-dev musl-dev linux-headers && \
    pip3 install --no-cache-dir --break-system-packages patroni[etcd,etcd3] urllib3 && \
    apk del gcc python3-dev musl-dev linux-headers && \
    mkdir -p /var/lib/postgresql/data/pgdata /run/postgresql && \
    chown -R postgres:postgres /var/lib/postgresql /run/postgresql

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
