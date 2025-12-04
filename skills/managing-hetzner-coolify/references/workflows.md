# Detailed Workflows - Hetzner + Coolify

Step-by-step procedures for common infrastructure tasks.

---

## Deploy New Application to Coolify

### Prerequisites
- Coolify-managed server (rnpr-internal or rnpr-clients)
- Application repository or Docker image
- Domain name (optional)

### Steps

**1. Via Coolify Web UI (Recommended)**

```bash
# Navigate to Coolify Dashboard
open https://app.coolify.io/team/depressed-dolphin-soc400ow08o004wkk0ggckcg

# Steps in UI:
# 1. Select server (e.g., rnpr-clients)
# 2. Click "New Resource" → Application
# 3. Choose source:
#    - Public Git Repository
#    - Private Git Repository (requires credentials)
#    - Docker Image
#    - Docker Compose
# 4. Configure application:
#    - Name: my-app
#    - Build Pack: (auto-detected or manual)
#    - Port: (application port, e.g., 3000)
#    - Domain: (optional, e.g., app.realnewspr.com)
# 5. Set environment variables
# 6. Click "Deploy"
```

**2. Verify Deployment**

```bash
# Check via Coolify CLI
coolify servers get mkk0koo0g04sog8o8cwow0ks  # rnpr-clients

# Check running containers
ssh root@157.180.85.128 "docker ps"

# Monitor logs
ssh root@157.180.85.128 "docker logs -f <container-name>"
```

**3. Configure Domain (if using)**

```bash
# Add DNS A record:
# app.realnewspr.com → 157.180.85.128

# SSL will be automatically provisioned by Coolify via Let's Encrypt

# Test endpoint
curl -I https://app.realnewspr.com
```

---

## Add Firewall Rule

### Use Case: Allow external access to database

**Quick Method (Script):**
```bash
bash ~/.claude/skills/managing-hetzner-coolify/scripts/add_firewall_rule.sh \
  postgres-access \
  5432 \
  1.2.3.4/32 \
  rnpr-clients
```

**Manual Method:**

**1. Create Firewall**
```bash
# Create new firewall
hcloud firewall create --name postgres-access

# Verify creation
hcloud firewall list
```

**2. Add Rules**
```bash
# Add rule for specific IP
hcloud firewall add-rule postgres-access \
  --direction in \
  --protocol tcp \
  --port 5432 \
  --source-ips 1.2.3.4/32

# Add rule for subnet
hcloud firewall add-rule postgres-access \
  --direction in \
  --protocol tcp \
  --port 5432 \
  --source-ips 10.0.0.0/24

# Add multiple ports
hcloud firewall add-rule postgres-access \
  --direction in \
  --protocol tcp \
  --port 80 \
  --source-ips 0.0.0.0/0,::/0

hcloud firewall add-rule postgres-access \
  --direction in \
  --protocol tcp \
  --port 443 \
  --source-ips 0.0.0.0/0,::/0
```

**3. Apply to Server**
```bash
# Apply firewall to server
hcloud firewall apply-to-resource postgres-access \
  --type server \
  --server rnpr-clients

# Verify
hcloud firewall describe postgres-access
```

**4. Test Connectivity**
```bash
# Test port from your machine
telnet 157.180.85.128 5432

# Or use nc
nc -zv 157.180.85.128 5432

# Test database connection
psql "postgresql://user:pass@157.180.85.128:5432/dbname" -c 'SELECT 1;'
```

---

## Migrate Server to New Type

### Use Case: Migrate capture-radio from deprecated CX22 to CX23

**Prerequisites:**
- Server to migrate
- New server type chosen
- Maintenance window scheduled

### Steps

**1. Create Snapshot (Backup)**

```bash
# Shutdown server for consistency
hcloud server shutdown capture-radio-20251005

# Create snapshot
hcloud server create-image capture-radio-20251005 \
  --description "pre-cx23-migration-$(date +%Y%m%d)"

# Get snapshot ID
SNAPSHOT_ID=$(hcloud image list --type snapshot | grep pre-cx23 | awk '{print $1}')

# Verify snapshot
hcloud image describe $SNAPSHOT_ID

# Power on old server (temporarily)
hcloud server poweron capture-radio-20251005
```

**2. Create New Server from Snapshot**

```bash
# Create new server with CX23 type
hcloud server create \
  --name capture-radio \
  --type cx23 \
  --location fsn1 \
  --image $SNAPSHOT_ID \
  --ssh-key your-key-name

# Get new server IP
NEW_IP=$(hcloud server describe capture-radio | grep "IPv4:" | awk '{print $2}')
echo "New server IP: $NEW_IP"
```

**3. Test New Server**

```bash
# SSH to new server
ssh root@$NEW_IP

# Check services
systemctl status radio-capture

# Check disk usage
df -h

# Check running containers
docker ps

# Test application
curl -I http://$NEW_IP:8080
```

**4. Update DNS (if applicable)**

```bash
# Update DNS A records to point to new IP
# app.example.com → $NEW_IP

# Wait for DNS propagation (check with)
dig app.example.com
```

**5. Swap IPs (Optional - if using floating IP)**

```bash
# If using floating IP, reassign it
hcloud floating-ip assign <floating-ip-id> --server capture-radio

# Verify
hcloud floating-ip describe <floating-ip-id>
```

**6. Delete Old Server**

```bash
# CAUTION: Only after verifying new server works!

# Final verification
ssh root@$NEW_IP "uptime && docker ps"

# Delete old server
hcloud server delete capture-radio-20251005

# Verify deletion
hcloud server list
```

**7. Clean Up Old Snapshots (After 30 days)**

```bash
# List old snapshots
hcloud image list --type snapshot

# Delete old snapshot
hcloud image delete $SNAPSHOT_ID
```

---

## Setup New PostgreSQL Test Database

### Use Case: Create isolated database for Codex CI testing

**Recommended Server:** rnpr-clients (4GB RAM, empty, geographically isolated)

**Method 1: Via Script (Automated)**

```bash
bash ~/.claude/skills/managing-hetzner-coolify/scripts/deploy_database.sh \
  postgres \
  rnpr-clients \
  intermedia_test_db \
  CODEX_EGRESS_IP
```

**Method 2: Manual (Full Control)**

**1. Deploy PostgreSQL via Coolify UI**

```bash
# Navigate to Coolify
open https://app.coolify.io

# Steps:
# 1. Select rnpr-clients server
# 2. New Resource → Database → PostgreSQL 16
# 3. Configure:
#    - Name: intermedia-test-db
#    - Database: intermedia_test_db
#    - Username: codex_ci
#    - Password: [secure password]
# 4. Click Deploy
```

**2. Get Container Name**

```bash
ssh root@157.180.85.128 "docker ps | grep postgres"

# Output example:
# postgres-abc123def456-171234567890   postgres:16   Up 2 minutes   5432/tcp

CONTAINER=$(ssh root@157.180.85.128 "docker ps | grep postgres | awk '{print \$NF}'")
echo "Container: $CONTAINER"
```

**3. Configure Firewall**

```bash
# Create and apply firewall
hcloud firewall create --name postgres-test-db

# Add rule for Codex CI (example IP)
hcloud firewall add-rule postgres-test-db \
  --direction in \
  --protocol tcp \
  --port 5432 \
  --source-ips CODEX_EGRESS_IP/32

# Add rule for your local development
hcloud firewall add-rule postgres-test-db \
  --direction in \
  --protocol tcp \
  --port 5432 \
  --source-ips YOUR_IP/32

# Apply to server
hcloud firewall apply-to-resource postgres-test-db \
  --type server \
  --server rnpr-clients

# Verify
hcloud firewall describe postgres-test-db
```

**4. Create Database and User**

```bash
# Create role
ssh root@157.180.85.128 "docker exec -it $CONTAINER psql -U postgres -c \"CREATE ROLE codex_ci WITH LOGIN PASSWORD 'secure_password_here';\""

# Create database
ssh root@157.180.85.128 "docker exec -it $CONTAINER psql -U postgres -c \"CREATE DATABASE intermedia_test_db OWNER codex_ci;\""

# Grant privileges
ssh root@157.180.85.128 "docker exec -it $CONTAINER psql -U postgres -c \"GRANT ALL PRIVILEGES ON DATABASE intermedia_test_db TO codex_ci;\""

# Verify
ssh root@157.180.85.128 "docker exec -it $CONTAINER psql -U postgres -c '\l'" | grep intermedia_test_db
```

**5. Test Connectivity**

```bash
# From your local machine
psql "postgresql://codex_ci:secure_password_here@157.180.85.128:5432/intermedia_test_db?sslmode=require" -c 'SELECT 1;'

# Expected output:
#  ?column?
# ----------
#         1
# (1 row)
```

**6. Configure Codex Environment**

```bash
# Add to Codex CI configuration
TEST_POSTGRES_HOST=157.180.85.128
TEST_POSTGRES_PORT=5432
TEST_POSTGRES_USER=codex_ci
TEST_POSTGRES_PASSWORD=secure_password_here
TEST_POSTGRES_DB=intermedia_test_db
TEST_POSTGRES_SSLMODE=require
```

**7. Set Up Automated Backups (Optional)**

```bash
# Create backup script
cat > ~/backup-test-db.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/backups/intermedia-test"
mkdir -p $BACKUP_DIR

ssh root@157.180.85.128 "docker exec $CONTAINER pg_dump -U codex_ci intermedia_test_db -F c" > \
  $BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).dump

# Keep only last 7 days
find $BACKUP_DIR -name "backup-*.dump" -mtime +7 -delete
EOF

chmod +x ~/backup-test-db.sh

# Add to cron (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-test-db.sh") | crontab -
```

---

## Create Server Snapshot for Backup

### Use Case: Backup before major changes or upgrades

**Quick Snapshot (Server Running - May Be Inconsistent)**

```bash
# Create snapshot
hcloud server create-image rnpr-internal \
  --description "backup-$(date +%Y%m%d)-$(date +%H%M)"

# Verify
hcloud image list --type snapshot | head -5
```

**Consistent Snapshot (Recommended for Databases)**

```bash
# 1. Notify users of downtime
echo "Server will be down for 5 minutes for snapshot"

# 2. Shutdown server
hcloud server shutdown rnpr-internal

# 3. Wait for shutdown
while [ "$(hcloud server describe rnpr-internal | grep Status: | awk '{print $2}')" != "off" ]; do
  echo "Waiting for shutdown..."
  sleep 2
done

# 4. Create snapshot
hcloud server create-image rnpr-internal \
  --description "consistent-backup-$(date +%Y%m%d)"

# 5. Power on
hcloud server poweron rnpr-internal

# 6. Verify services
sleep 10
ssh root@5.161.214.194 "docker ps"
```

**Snapshot Management**

```bash
# List all snapshots
hcloud image list --type snapshot

# List snapshots for specific server
hcloud image list --type snapshot | grep rnpr-internal

# Delete old snapshots (keep only last 3)
hcloud image list --type snapshot -o json | \
  jq -r '.[] | select(.created | split("T")[0] < (now - 259200 | strftime("%Y-%m-%d"))) | .id' | \
  xargs -I {} hcloud image delete {}

# Restore from snapshot
hcloud server rebuild rnpr-internal --image <snapshot-id>
```

---

## Set Up Private Network Between Servers

### Use Case: Secure communication between rnpr-internal and rnpr-clients

**1. Create Private Network**

```bash
# Create network
hcloud network create \
  --name internal-network \
  --ip-range 10.0.0.0/16

# Verify
hcloud network list
```

**2. Add Subnet**

```bash
# Add subnet for servers
hcloud network add-subnet internal-network \
  --network-zone eu-central \
  --type cloud \
  --ip-range 10.0.1.0/24

# Verify
hcloud network describe internal-network
```

**3. Attach Servers**

```bash
# Attach rnpr-internal
hcloud server attach-to-network rnpr-internal \
  --network internal-network \
  --ip 10.0.1.2

# Attach rnpr-clients
hcloud server attach-to-network rnpr-clients \
  --network internal-network \
  --ip 10.0.1.3

# Verify
hcloud server describe rnpr-internal | grep -A 5 "Private Network"
hcloud server describe rnpr-clients | grep -A 5 "Private Network"
```

**4. Configure Server Networking**

```bash
# On rnpr-internal, test connectivity to rnpr-clients
ssh root@5.161.214.194 "ping -c 3 10.0.1.3"

# On rnpr-clients, test connectivity to rnpr-internal
ssh root@157.180.85.128 "ping -c 3 10.0.1.2"
```

**5. Update Application Configurations**

```bash
# Update database connection strings to use private IPs
# Example: DATABASE_HOST=10.0.1.2 instead of 5.161.214.194

# Update firewall rules to restrict to private network
hcloud firewall add-rule <firewall> \
  --direction in \
  --protocol tcp \
  --port 5432 \
  --source-ips 10.0.1.0/24
```

---

## Automated Infrastructure Backup Script

```bash
#!/bin/bash
# Complete infrastructure backup script

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/$DATE"
mkdir -p "$BACKUP_DIR"

echo "=== Infrastructure Backup - $DATE ==="

# 1. Backup PostgreSQL databases
echo "Backing up PostgreSQL..."
ssh root@5.161.214.194 "docker exec postgres-xwk488ccc4sg0ssw844wccog-083810202435 pg_dump -U universal_sync universal_sync -F c" > \
  "$BACKUP_DIR/postgres-universal-sync.dump"

# 2. Backup server configs
echo "Backing up server configurations..."
for ip in 5.161.214.194 157.180.85.128; do
  ssh root@$ip "tar czf - /etc /opt" > "$BACKUP_DIR/config-$ip.tar.gz"
done

# 3. Create Hetzner snapshots
echo "Creating Hetzner snapshots..."
hcloud server create-image rnpr-internal --description "auto-backup-$DATE"
hcloud server create-image rnpr-clients --description "auto-backup-$DATE"

# 4. Backup Coolify configuration
echo "Backing up Coolify state..."
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  "$COOLIFY_API/servers" > "$BACKUP_DIR/coolify-servers.json"

curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  "$COOLIFY_API/applications" > "$BACKUP_DIR/coolify-applications.json"

# 5. Cleanup old backups (keep 7 days)
echo "Cleaning up old backups..."
find /backups -type d -mtime +7 -exec rm -rf {} \;

# 6. Cleanup old snapshots (keep 3)
echo "Cleaning up old snapshots..."
hcloud image list --type snapshot -o json | \
  jq -r '.[] | select(.created | split("T")[0] < (now - 259200 | strftime("%Y-%m-%d"))) | .id' | \
  xargs -I {} hcloud image delete {} 2>/dev/null || true

echo "✅ Backup complete: $BACKUP_DIR"
```

Save as `~/backup-infrastructure.sh` and add to cron:
```bash
# Daily at 3 AM
0 3 * * * ~/backup-infrastructure.sh
```
