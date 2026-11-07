# Banking Service High Availability Architecture

This document provides a technical overview of the production setup for the distributed banking core service. The design focuses on zero downtime, continuous failover, and data consistency across independent cloud compute instances.

---

## Production Arch Overview

The production infrastructure is built on an Active-Passive (Primary-Standby) deployment pattern running across two separate Amazon EC2 compute instances.

### 1. Global Traffic Management & Failover Layer

* **Cloudflare Global Load Balancer:** Sits at the edge in front of both servers. It receives all user traffic and routes it to the active node using Anycast routing.
* **Continuous Health Monitoring:** Cloudflare sends automated HTTP health requests to the `/health` endpoint every few seconds.
* **Automatic Failover:** If the Primary EC2 instance stops responding or becomes degraded, traffic instantly shifts to the Standby EC2 instance without dropping user sessions.

### 2. Primary Node (EC2-1 - Active / Read-Write)

* **Reverse Proxy:** An Nginx container receives public traffic on port 80/443, handles request forwarding, and enforces rate limits.
* **Application Services:**
* A stateless web user interface container served through Nginx.
* A FastAPI backend handling banking transfer logic and API routes.


* **Fast In-Memory Cache:** A Redis master instance storing active sessions, tokens, and temporary read caches to reduce direct database load.
* **Relational Database:** A PostgreSQL 16 Primary instance that processes all insert and update write operations.

### 3. Standby Node (EC2-2 - Passive / Read-Only Replica)

* **Identical Application Stack:** Houses identical Docker containers for Nginx, the frontend application, and the backend service.
* **Cache Node:** Redis running in replica mode, ready to take over cache state.
* **Database Replication:** PostgreSQL running in hot-standby mode. It continuously receives database changes from the primary node through PostgreSQL streaming replication via a secure private channel.

### 4. CI/CD Deployment Flow

* Changes pushed to the production branch trigger an automated GitHub Actions pipeline.
* Containers are built, verified, and uploaded to the centralized Docker Hub image registry (`abdueissa/banking-backend` and `abdueissa/banking-frontend`).
* Secure remote deployment updates both the primary and standby environments concurrently with zero service interruption.

---

## Verification & Operational Evidence

### System User Interface & Node Status

This Photo Shows the banking application running on the active node. The interface confirms the health status of the node, displays recent transactions, and provides the transfer execution form.



---

### Clean Deployment State

This Photo Shows the repository structure and the clean Git commit state after setting up all deployment orchestration files and service definitions.



---

### End-to-End API Routing & Database Operations

This Photo Shows the local reverse proxy routing traffic correctly. The health endpoint returns an active status, the transfer endpoint accepts write payloads into PostgreSQL, and read queries return committed records directly from the database.



---

### High-Speed Cache Hits (Redis Integration)

This Photo Shows repeat queries served directly from Redis memory cache (`"source": "redis_cache"`), preventing repeated read hits on the database engine during high-traffic windows.
