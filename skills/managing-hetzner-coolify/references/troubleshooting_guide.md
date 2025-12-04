# Troubleshooting Guide - Hetzner + Coolify

Common issues and solutions for Real News PR infrastructure.

---

## Container Issues

### Unhealthy Container

**Example: capture-radio container unhealthy**

```bash
# 1. Check container status
ssh root@91.98.145.239 "docker ps | grep radio"

# 2. View last 100 lines of logs
ssh root@91.98.145.239 "docker logs --tail 100 radio-capture-msowc48sk0k004o44o8w4k8g-171417583841"

# 3. Check health status
ssh root@91.98.145.239 "docker inspect radio-capture-msowc48sk0k004o44o8w4k8g-171417583841 | jq '.[0].State.Health'"

# 4. Restart container
ssh root@91.98.145.239 "docker restart radio-capture-msowc48sk0k004o44o8w4k8g-171417583841"

# 5. Follow logs in real-time
ssh root@91.98.145.239 "docker logs -f radio-capture-msowc48sk0k004o44o8w4k8g-171417583841"
```

**Common causes:**
- Out of memory: `ssh root@<ip> "docker stats --no-stream"`
- Missing environment variables: `docker inspect <container> | jq '.[0].Config.Env'`
- Network issues: `docker network inspect <network>`
- Permission issues: Check volume mounts
- Port conflicts: `netstat -tuln | grep LISTEN`

---

## Network Issues

### Test Connectivity Between Servers

```bash
# Ping test
ssh root@5.161.214.194 "ping -c 3 157.180.85.128"

# DNS resolution
ssh root@5.161.214.194 "dig sync.realnewspr.com"
ssh root@5.161.214.194 "nslookup sync.realnewspr.com"

# Test port connectivity
ssh root@5.161.214.194 "nc -zv 157.180.85.128 5432"
ssh root@5.161.214.194 "telnet 157.180.85.128 5432"
```

### Firewall Issues

```bash
# Check firewall rules (Hetzner)
hcloud firewall list
hcloud firewall describe <firewall-name>

# Check iptables rules (on server)
ssh root@<ip> "iptables -L -n -v"
ssh root@<ip> "ufw status"
```

### DNS Issues

```bash
# Check DNS resolution
ssh root@<ip> "cat /etc/resolv.conf"
ssh root@<ip> "dig google.com"
ssh root@<ip> "nslookup google.com"

# Test specific domain
dig sync.realnewspr.com
curl -I https://sync.realnewspr.com
```

---

## Proxy Issues (Traefik)

### Restart Traefik Proxy

```bash
# Restart on Coolify-managed servers
ssh root@5.161.214.194 "docker restart coolify-proxy"
ssh root@157.180.85.128 "docker restart coolify-proxy"

# Check Traefik status
ssh root@<ip> "docker ps --filter name=coolify-proxy"
```

### Check Traefik Configuration

```bash
# View Traefik config
ssh root@<ip> "docker exec coolify-proxy cat /etc/traefik/traefik.yml"

# View access logs
ssh root@<ip> "docker logs --tail 100 coolify-proxy"

# Filter for errors
ssh root@<ip> "docker logs coolify-proxy | grep -i error"
```

### SSL Certificate Issues

```bash
# Check SSL certificates
ssh root@<ip> "docker exec coolify-proxy ls -la /letsencrypt"

# View certificate details
ssh root@<ip> "docker exec coolify-proxy cat /letsencrypt/acme.json" | jq .
```

---

## Disk Space Issues

### Check Disk Usage

```bash
# Overall disk usage
ssh root@<ip> "df -h"

# Docker disk usage
ssh root@<ip> "docker system df"

# Find large directories
ssh root@<ip> "du -h --max-depth=1 /var/lib/docker | sort -hr"

# Find large files
ssh root@<ip> "find /var/lib/docker -type f -size +100M -exec ls -lh {} \;"
```

### Clean Up Docker

```bash
# Remove stopped containers
ssh root@<ip> "docker container prune -f"

# Remove unused images
ssh root@<ip> "docker image prune -a -f"

# Remove unused volumes
ssh root@<ip> "docker volume prune -f"

# Remove unused networks
ssh root@<ip> "docker network prune -f"

# Full system cleanup (CAUTION: removes everything unused)
ssh root@<ip> "docker system prune -a --volumes -f"
```

### Clean Up System Logs

```bash
# Remove old journal logs
ssh root@<ip> "journalctl --vacuum-time=7d"

# Check journal size
ssh root@<ip> "journalctl --disk-usage"
```

---

## Database Issues

### Connection Refused

**Check if database is running:**
```bash
ssh root@<ip> "docker ps | grep postgres"
```

**Check database logs:**
```bash
ssh root@<ip> "docker logs <postgres-container>"
```

**Check if port is exposed:**
```bash
ssh root@<ip> "docker port <postgres-container>"
ssh root@<ip> "netstat -tuln | grep 5432"
```

**Test connection from server:**
```bash
ssh root@<ip> "docker exec <postgres-container> psql -U <user> -d <db> -c 'SELECT 1;'"
```

### Slow Queries

```bash
# Check active connections
ssh root@<ip> "docker exec <postgres-container> psql -U <user> -d <db> -c \"SELECT count(*) FROM pg_stat_activity;\""

# Find slow queries
ssh root@<ip> "docker exec <postgres-container> psql -U <user> -d <db> -c \"SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;\""
```

### Database Corruption

```bash
# 1. Stop applications
ssh root@<ip> "docker stop <app-container>"

# 2. Create emergency backup
ssh root@<ip> "docker exec <postgres-container> pg_dump -U <user> <db> -F c" > emergency-backup.dump

# 3. Restore from known good backup
cat backup.dump | ssh root@<ip> "docker exec -i <postgres-container> pg_restore -U <user> -d <db> --clean --if-exists"

# 4. Restart applications
ssh root@<ip> "docker start <app-container>"
```

---

## Coolify Issues

### Coolify Agent Not Responding

```bash
# Check Sentinel status
ssh root@<ip> "docker ps --filter name=coolify-sentinel"

# View Sentinel logs
ssh root@<ip> "docker logs --tail 100 coolify-sentinel"

# Restart Sentinel
ssh root@<ip> "docker restart coolify-sentinel"
```

### Deployment Failures

**Check deployment logs via Coolify CLI:**
```bash
# Get deployment ID from application
coolify applications list --json | jq '.[] | select(.name == "<app-name>")'

# View deployment logs (via API)
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  "$COOLIFY_API/deployment/<id>/logs" | jq .
```

**Check build logs on server:**
```bash
# Find build containers
ssh root@<ip> "docker ps -a | grep build"

# View build logs
ssh root@<ip> "docker logs <build-container>"
```

---

## Server Unresponsive

### Emergency Recovery

```bash
# 1. Check server status via Hetzner
hcloud server describe <server-name>

# 2. Try hard reset
hcloud server reset <server-name>

# 3. Access via console (if SSH fails)
# Use Hetzner Cloud Console web interface:
# https://console.hetzner.cloud/ → Select server → Console

# 4. Check system logs after reboot
ssh root@<ip> "journalctl -xe"
ssh root@<ip> "dmesg | tail -100"
```

### High CPU/Memory Usage

```bash
# Check resource usage
ssh root@<ip> "top -bn1 | head -20"

# Find resource-heavy containers
ssh root@<ip> "docker stats --no-stream"

# Check system resources
ssh root@<ip> "free -h"
ssh root@<ip> "df -h"
```

---

## Quick Diagnostic Commands

```bash
# Health check all servers
for ip in 5.161.214.194 157.180.85.128 91.98.145.239 65.109.139.200; do
  echo "=== $ip ==="
  ssh root@$ip "uptime && free -h && df -h /"
done

# Check all Docker containers
for ip in 5.161.214.194 157.180.85.128 91.98.145.239; do
  echo "=== $ip ==="
  ssh root@$ip "docker ps"
done

# Test HTTP endpoints
curl -I https://sync.realnewspr.com
curl -I http://5.161.214.194

# Check open ports
nmap 5.161.214.194
nmap 157.180.85.128
```

---

## Emergency Contacts

- **Hetzner Support:** https://docs.hetzner.com/support/
- **Coolify Support:** https://coolify.io/docs
- **Status Pages:**
  - Hetzner: https://status.hetzner.com/
  - Coolify Cloud: https://status.coolify.io/
