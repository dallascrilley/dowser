#!/bin/bash
# Deploy database via Coolify with firewall configuration
# Usage: bash deploy_database.sh <db_type> <server_name> <db_name> <allowed_ip>
# Example: bash deploy_database.sh postgres rnpr-clients test_db 1.2.3.4

set -euo pipefail

# Arguments
DB_TYPE=${1:-postgres}
SERVER_NAME=${2:-rnpr-clients}
DB_NAME=${3:-}
ALLOWED_IP=${4:-}

# Validate arguments
if [ -z "$DB_NAME" ]; then
    echo "❌ Error: Database name required"
    echo "Usage: bash deploy_database.sh <db_type> <server_name> <db_name> <allowed_ip>"
    echo "Example: bash deploy_database.sh postgres rnpr-clients test_db 1.2.3.4"
    exit 1
fi

if [ -z "$ALLOWED_IP" ]; then
    echo "⚠️  Warning: No IP provided. Database will not be accessible externally."
    echo "To add firewall rule later: bash add_firewall_rule.sh <firewall_name> 5432 <IP> $SERVER_NAME"
fi

# Server UUIDs
declare -A SERVER_UUIDS=(
    ["rnpr-internal"]="u4wck8s08k8osoowgs8kkwgs"
    ["rnpr-clients"]="mkk0koo0g04sog8o8cwow0ks"
)

# Server IPs
declare -A SERVER_IPS=(
    ["rnpr-internal"]="5.161.214.194"
    ["rnpr-clients"]="157.180.85.128"
)

# Validate server is Coolify-managed
if [ -z "${SERVER_UUIDS[$SERVER_NAME]:-}" ]; then
    echo "❌ Error: Server '$SERVER_NAME' is not Coolify-managed"
    echo "Available servers: rnpr-internal, rnpr-clients"
    exit 1
fi

UUID="${SERVER_UUIDS[$SERVER_NAME]}"
IP="${SERVER_IPS[$SERVER_NAME]}"

echo "=== Deploying $DB_TYPE Database to $SERVER_NAME ==="
echo ""
echo "📋 Configuration:"
echo "  - Database Type: $DB_TYPE"
echo "  - Server: $SERVER_NAME"
echo "  - UUID: $UUID"
echo "  - IP: $IP"
echo "  - Database Name: $DB_NAME"
if [ -n "$ALLOWED_IP" ]; then
    echo "  - Allowed IP: $ALLOWED_IP"
fi
echo ""

# Step 1: Deploy database via Coolify UI
echo "📝 Step 1: Deploy Database via Coolify UI"
echo ""
echo "1. Navigate to: https://app.coolify.io"
echo "2. Select server: $SERVER_NAME"
echo "3. Click 'New Resource' → Database → $(echo $DB_TYPE | sed 's/.*/\u&/') 16"
echo "4. Configure:"
echo "   - Database Name: $DB_NAME"
echo "   - Username: ${DB_NAME}_user"
echo "   - Password: [generate secure password]"
echo "5. Click 'Deploy'"
echo ""
read -p "Press Enter when deployment is complete..."

# Step 2: Get container name
echo ""
echo "📝 Step 2: Finding Container..."
echo ""

CONTAINER_NAME=$(ssh root@$IP "docker ps | grep $DB_TYPE | awk '{print \$NF}'" 2>/dev/null || echo "")

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ Could not find $DB_TYPE container on $SERVER_NAME"
    echo "Run manually: ssh root@$IP 'docker ps | grep $DB_TYPE'"
    exit 1
fi

echo "✅ Found container: $CONTAINER_NAME"

# Step 3: Configure firewall (if IP provided)
if [ -n "$ALLOWED_IP" ]; then
    echo ""
    echo "📝 Step 3: Configuring Firewall..."
    echo ""

    FIREWALL_NAME="${DB_NAME}-access"

    # Get database port
    case $DB_TYPE in
        postgres) PORT=5432 ;;
        mysql) PORT=3306 ;;
        mongo) PORT=27017 ;;
        redis) PORT=6379 ;;
        *) PORT=5432 ;;
    esac

    # Create/configure firewall
    if ! hcloud firewall describe "$FIREWALL_NAME" >/dev/null 2>&1; then
        echo "Creating firewall: $FIREWALL_NAME"
        hcloud firewall create --name "$FIREWALL_NAME"
    fi

    echo "Adding rule for $ALLOWED_IP:$PORT"
    hcloud firewall add-rule "$FIREWALL_NAME" \
        --direction in \
        --protocol tcp \
        --port "$PORT" \
        --source-ips "$ALLOWED_IP/32" 2>/dev/null || echo "Rule may already exist"

    echo "Applying firewall to $SERVER_NAME"
    hcloud firewall apply-to-resource "$FIREWALL_NAME" \
        --type server \
        --server "$SERVER_NAME" 2>/dev/null || echo "Firewall may already be applied"

    echo "✅ Firewall configured"
fi

# Step 4: Test connectivity
echo ""
echo "📝 Step 4: Testing Connectivity..."
echo ""

case $DB_TYPE in
    postgres)
        echo "Test connection with:"
        echo "  psql \"postgresql://${DB_NAME}_user:PASSWORD@${IP}:5432/${DB_NAME}\" -c 'SELECT 1;'"
        ;;
    mysql)
        echo "Test connection with:"
        echo "  mysql -h ${IP} -P 3306 -u ${DB_NAME}_user -p ${DB_NAME} -e 'SELECT 1;'"
        ;;
    *)
        echo "Connect to database at: ${IP}"
        ;;
esac

echo ""
echo "✅ Database deployment complete!"
echo ""
echo "📋 Connection Details:"
echo "  Host: $IP"
echo "  Database: $DB_NAME"
echo "  User: ${DB_NAME}_user"
echo "  Port: ${PORT:-5432}"
echo ""
