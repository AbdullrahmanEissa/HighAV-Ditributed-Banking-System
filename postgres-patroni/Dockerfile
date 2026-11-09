FROM postgres:16-alpine

RUN apk add --no-cache python3 py3-pip py3-psycopg2 curl su-exec && \
    pip3 install --no-cache-dir --break-system-packages patroni[etcd] urllib3 && \
    mkdir -p /var/lib/postgresql/data/pgdata /run/postgresql && \
    chown -R postgres:postgres /var/lib/postgresql /run/postgresql

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
