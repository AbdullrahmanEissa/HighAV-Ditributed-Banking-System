#!/bin/sh
set -e

mkdir -p /var/lib/postgresql/data/pgdata /run/postgresql
chown -R postgres:postgres /var/lib/postgresql /run/postgresql
chmod 700 /var/lib/postgresql/data/pgdata

cat << YAML > /tmp/patroni.yml
scope: ${PATRONI_SCOPE:-banking-cluster}
name: ${PATRONI_NAME}

restapi:
  listen: 0.0.0.0:8008
  connect_address: ${PATRONI_IP}:8008

etcd3:
  hosts: ${ETCD_HOSTS:-172.31.38.111:2379}

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        max_wal_senders: 10
        max_replication_slots: 10
        wal_keep_size: 512MB
  initdb:
    - encoding: UTF8
    - data-checksums
  pg_hba:
    - local all all trust
    - host replication replicator 0.0.0.0/0 md5
    - host all all 0.0.0.0/0 md5
  post_bootstrap: /tmp/post_init.sh

postgresql:
  listen: 0.0.0.0:5432
  connect_address: ${PATRONI_IP}:5432
  data_dir: /var/lib/postgresql/data/pgdata
  pgpass: /tmp/pgpass
  authentication:
    superuser:
      username: postgres
      password: ${DB_PASS:-dbprimarybanking}
    replication:
      username: replicator
      password: ${DB_PASS:-dbprimarybanking}
YAML

cat << 'INIT' > /tmp/post_init.sh
#!/bin/sh
psql -U postgres -c "CREATE DATABASE banking;" || true
INIT

chmod +x /tmp/post_init.sh
chown postgres:postgres /tmp/patroni.yml /tmp/post_init.sh

exec su-exec postgres patroni /tmp/patroni.yml
