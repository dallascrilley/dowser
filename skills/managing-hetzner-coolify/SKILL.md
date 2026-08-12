---
name: managing-hetzner-coolify
description: >-
  Manage Real News PR infrastructure on Hetzner Cloud and Coolify. Create
  servers, deploy applications/databases, configure firewalls, troubleshoot
  issues, and monitor health.
when_to_use: >-
  Use when working with hetzner, coolify, servers, deployment, infrastructure,
  VPS, containers, databases, firewall, or cloud hosting for Real News PR
  infrastructure.
version: 1.0.0
category: cloud-and-infra
---

# Managing Hetzner + Coolify Infrastructure

Manage Real News PR's cloud infrastructure across Hetzner Cloud and Coolify platform.

## Server Inventory (Real News PR)

| Name | IP | UUID | Type | RAM | Location | Coolify | Purpose |
|------|-----|------|------|-----|----------|---------|---------|
| **rnpr-internal** | `5.161.214.194` | `u4wck8s08k8osoowgs8kkwgs` | cpx11 | 2GB | Ashburn/US | ✅ | Universal Sync + PostgreSQL |
| **rnpr-clients** | `157.180.85.128` | `mkk0koo0g04sog8o8cwow0ks` | cx23 | 4GB | Helsinki/FI | ✅ | Client apps (empty) |
| **capture-radio** | `91.98.145.239` | - | cx22 | 4GB | Falkenstein/DE | ❌ | Radio capture |
| **cpanel** | `65.109.139.200` | - | cx33 | 8GB | Helsinki/FI | ❌ | Web hosting |

**Monthly Cost:** ~€21 (~$23 USD)

**Important Notes:**
- capture-radio uses deprecated CX22 (migrate to CX23 before Dec 31, 2025)
- rnpr-clients is empty and ready for deployments
- PostgreSQL on rnpr-internal not exposed externally (internal Docker network only)

---

## Tool Selection

**Use Coolify CLI/API for:**
- ✅ rnpr-internal (UUID: `u4wck8s08k8osoowgs8kkwgs`)
- ✅ rnpr-clients (UUID: `mkk0koo0g04sog8o8cwow0ks`)

**Use Hetzner CLI for:**
- All server lifecycle operations (create, resize, delete, snapshots)
- Firewall and network management
- Volume management
- All 4 servers (regardless of Coolify status)

**Use SSH + Docker for:**
- capture-radio (not Coolify-managed)
- Direct container inspection/troubleshooting

---

## Common Workflows

### 1. Check Infrastructure Health

**Quick health check:**
```bash
# Run the health check script
bash ~/.claude/skills/managing-hetzner-coolify/scripts/health_check.sh
```

**Manual checks:**
```bash
# Coolify-managed servers status
coolify servers list --json --pretty

# All Hetzner servers
hcloud server list

# Specific server details
coolify servers get u4wck8s08k8osoowgs8kkwgs  # rnpr-internal
hcloud server describe rnpr-clients
```

---

### 2. Deploy Database via Coolify

**Recommended: Use rnpr-clients (4GB RAM, empty, Finland)**

**Via Coolify UI (easiest):**
1. Navigate to https://app.coolify.io
2. Select rnpr-clients server
3. Click "New Resource" → Database → PostgreSQL 16
4. Configure database name, username, password
5. Deploy

**Via script (automated):**
```bash
# Deploy PostgreSQL with firewall configuration
bash ~/.claude/skills/managing-hetzner-coolify/scripts/deploy_database.sh \
  postgres \
  rnpr-clients \
  my_database_name \
  YOUR_IP_ADDRESS
```

**Manual setup steps:**
1. Deploy database via Coolify UI
2. Get container name: `ssh root@157.180.85.128 "docker ps | grep postgres"`
3. Configure firewall (see Firewall Configuration below)
4. Create database and user:
   ```bash
   ssh root@157.180.85.128 "docker exec -it <container> psql -U postgres -c \"CREATE ROLE myuser WITH LOGIN PASSWORD 'password';\""
   ssh root@157.180.85.128 "docker exec -it <container> psql -U postgres -c \"CREATE DATABASE mydb OWNER myuser;\""
   ```
5. Test connectivity:
   ```bash
   psql "postgresql://myuser:password@157.180.85.128:5432/mydb" -c 'SELECT 1;'
   ```

---

### 3. Configure Firewall

**Add firewall rule for database access:**
```bash
# Quick script (recommended)
bash ~/.claude/skills/managing-hetzner-coolify/scripts/add_firewall_rule.sh \
  postgres-access \
  5432 \
  YOUR_IP/32 \
  rnpr-clients
```

**Manual steps:**
```bash
# 1. Create firewall (if doesn't exist)
hcloud firewall create --name postgres-access

# 2. Add rule for your IP
hcloud firewall add-rule postgres-access \
  --direction in \
  --protocol tcp \
  --port 5432 \
  --source-ips YOUR_IP/32

# 3. Apply to server
hcloud firewall apply-to-resource postgres-access \
  --type server \
  --server rnpr-clients

# 4. Verify
hcloud firewall describe postgres-access
```

**Common ports:**
- PostgreSQL: 5432
- MySQL: 3306
- MongoDB: 27017
- Redis: 6379
- HTTP: 80
- HTTPS: 443
- SSH: 22

---

### 4. Create New Server

**Quick test server (auto-destruct):**
```bash
# Create CX11 server in Ashburn with 2-hour auto-destruct
hcloud server create \
  --name test-server \
  --type cpx11 \
  --image ubuntu-22.04 \
  --location ash \
  --ssh-key YOUR_KEY_NAME

# Add label for auto-cleanup
hcloud server add-label test-server environment=test
hcloud server add-label test-server autodestruct=2h
```

**Production server:**
```bash
# Create production server
hcloud server create \
  --name prod-app \
  --type cx23 \
  --image ubuntu-22.04 \
  --location hel1 \
  --ssh-key YOUR_KEY_NAME

# Add to Coolify (via UI)
# 1. Navigate to https://app.coolify.io/team/depressed-dolphin-soc400ow08o004wkk0ggckcg
# 2. Click "Add Server"
# 3. Enter IP, SSH details
# 4. Install Coolify agent
```

**Server types:**
- `cpx11`: 2GB shared - €4.99/month (test/small apps)
- `cx23`: 4GB dedicated - €3.49/month (recommended for apps)
- `cx33`: 8GB dedicated - €5.99/month (larger workloads)

**Locations:**
- `ash`: Ashburn, Virginia USA
- `hel1`: Helsinki, Finland
- `fsn1`: Falkenstein, Germany

---

### 5. Troubleshoot Unhealthy Container

**Example: capture-radio container unhealthy**

```bash
# 1. Check container status
ssh root@91.98.145.239 "docker ps | grep radio"

# 2. View logs
ssh root@91.98.145.239 "docker logs --tail 100 radio-capture-msowc48sk0k004o44o8w4k8g-171417583841"

# 3. Check health status
ssh root@91.98.145.239 "docker inspect radio-capture-msowc48sk0k004o44o8w4k8g-171417583841 | jq '.[0].State.Health'"

# 4. Restart container
ssh root@91.98.145.239 "docker restart radio-capture-msowc48sk0k004o44o8w4k8g-171417583841"

# 5. Follow logs
ssh root@91.98.145.239 "docker logs -f radio-capture-msowc48sk0k004o44o8w4k8g-171417583841"
```

**Common issues:**
- Out of memory: Check `docker stats`
- Network issues: Check `docker network inspect <network>`
- Permission issues: Check volume mounts and file permissions
- Port conflicts: Check `netstat -tuln | grep LISTEN`

---

### 6. Access PostgreSQL Database

**Production database (rnpr-internal):**

**Connection details:**
- Host: `5.161.214.194` (internal Docker network only)
- Database: `universal_sync`
- User: `universal_sync`
- Password: `UniversalSync2025!`
- Port: 5432 (not exposed externally)

**Access via SSH tunnel:**
```bash
# 1. Create SSH tunnel
ssh -L 5432:172.21.0.3:5432 root@5.161.214.194

# 2. Connect via local tunnel (in separate terminal)
psql -h localhost -U universal_sync -d universal_sync
```

**Access via SSH + Docker exec:**
```bash
ssh root@5.161.214.194 "docker exec -it postgres-xwk488ccc4sg0ssw844wccog-083810202435 psql -U universal_sync -d universal_sync"
```

**Run queries:**
```bash
# Check database size
ssh root@5.161.214.194 "docker exec postgres-xwk488ccc4sg0ssw844wccog-083810202435 psql -U universal_sync -d universal_sync -c \"SELECT pg_size_pretty(pg_database_size('universal_sync'));\""

# List tables
ssh root@5.161.214.194 "docker exec postgres-xwk488ccc4sg0ssw844wccog-083810202435 psql -U universal_sync -d universal_sync -c '\dt'"
```

**Backup database:**
```bash
ssh root@5.161.214.194 "docker exec postgres-xwk488ccc4sg0ssw844wccog-083810202435 pg_dump -U universal_sync universal_sync -F c" > backup-$(date +%Y%m%d).dump
```

---

### 7. Monitor Costs

**Current infrastructure cost:**
```bash
# Get current cost
hcloud server list -o json | \
  jq -r '.[] | "\(.name): \(.server_type.name) - €\(.server_type.prices[0].price_monthly.gross)"'

# Calculate total
hcloud server list -o json | \
  jq '[.[] | .server_type.prices[0].price_monthly.gross | tonumber] | add'
```

**Expected costs:**
- rnpr-internal (cpx11): €4.99/month
- rnpr-clients (cx23): €3.49/month
- capture-radio (cx22): €3.79/month (deprecated)
- cpanel (cx33): €5.99/month
- **Total: ~€18-21/month**

---

### 8. Create Server Snapshot

**For backup before major changes:**
```bash
# 1. Shutdown server (for consistency)
hcloud server shutdown rnpr-internal

# 2. Create snapshot
hcloud server create-image rnpr-internal --description "backup-$(date +%Y%m%d)"

# 3. Power on
hcloud server poweron rnpr-internal

# 4. Verify snapshot created
hcloud image list --type snapshot
```

**Live snapshot (may be inconsistent):**
```bash
hcloud server create-image rnpr-internal --description "live-backup-$(date +%Y%m%d)"
```

---

## Coolify API Access

**Authentication:**
```bash
export COOLIFY_TOKEN="your-api-token"
export COOLIFY_API="https://app.coolify.io/api/v1"
```

**Get API token:**
1. Navigate to https://app.coolify.io/security/api-tokens
2. Click "Create Token"
3. Copy token

**Common API calls:**
```bash
# List all servers
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API/servers" | jq .

# Get specific server
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API/server/u4wck8s08k8osoowgs8kkwgs" | jq .

# List applications
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API/applications" | jq .

# List databases
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" "$COOLIFY_API/databases" | jq .
```

---

## Quick SSH Access

```bash
# Coolify-managed servers
ssh root@5.161.214.194   # rnpr-internal
ssh root@157.180.85.128  # rnpr-clients

# Standalone servers
ssh root@91.98.145.239   # capture-radio
ssh root@65.109.139.200  # cpanel
```

---

## Emergency Procedures

### Server Unresponsive

```bash
# 1. Check server status
hcloud server describe <server-name>

# 2. Hard reset
hcloud server reset <server-name>

# 3. Check logs after reboot
ssh root@<ip> "journalctl -xe"
```

### Disk Full

```bash
# 1. Check disk usage
ssh root@<ip> "df -h && du -sh /var/lib/docker/*"

# 2. Clean up Docker
ssh root@<ip> "docker system prune -a --volumes -f"

# 3. Remove old logs
ssh root@<ip> "journalctl --vacuum-time=7d"
```

### Database Corruption

```bash
# 1. Stop application
ssh root@<ip> "docker stop <app-container>"

# 2. Backup current state
ssh root@<ip> "docker exec <postgres-container> pg_dump -U <user> <db> -F c" > emergency-backup.dump

# 3. Restore from backup
cat backup.dump | ssh root@<ip> "docker exec -i <postgres-container> pg_restore -U <user> -d <db> --clean --if-exists"
```

---

## Progressive Disclosure References

For detailed command references, see:

- **Full Command Reference:** `references/full_command_reference.md`
  - Complete hcloud CLI commands (servers, firewalls, networks, volumes)
  - Complete coolify CLI commands (instances, servers, applications)
  - Coolify REST API endpoints reference
  - Docker commands via SSH

- **Troubleshooting Guide:** `references/troubleshooting_guide.md`
  - Container issues (unhealthy, restart, logs)
  - Network issues (connectivity, DNS, firewall)
  - Proxy issues (Traefik configuration)
  - Disk space issues

- **Detailed Workflows:** `references/workflows.md`
  - Deploy new application to Coolify
  - Migrate server to new type
  - Set up private networking
  - Automated backup procedures

---

## Important URLs

- **Coolify Dashboard:** https://app.coolify.io
- **Coolify API Tokens:** https://app.coolify.io/security/api-tokens
- **Hetzner Console:** https://console.hetzner.cloud/
- **Infrastructure Docs:** `./docs/infrastructure-landscape.md`
- **Full Cheatsheet:** `./docs/hetzner-coolify-cheatsheet.md`

---

## Environment Variables

```bash
# Hetzner Cloud
export HCLOUD_TOKEN="your-hetzner-api-token"

# Coolify API
export COOLIFY_TOKEN="your-coolify-api-token"
export COOLIFY_API="https://app.coolify.io/api/v1"

# PostgreSQL Production (rnpr-internal)
export PROD_POSTGRES_HOST="5.161.214.194"
export PROD_POSTGRES_PORT="5432"
export PROD_POSTGRES_DB="universal_sync"
export PROD_POSTGRES_USER="universal_sync"
export PROD_POSTGRES_PASSWORD="UniversalSync2025!"
```
