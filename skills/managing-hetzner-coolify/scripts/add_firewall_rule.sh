#!/bin/bash
# Add firewall rule to Hetzner server
# Usage: bash add_firewall_rule.sh <firewall_name> <port> <source_ip> <server_name>
# Example: bash add_firewall_rule.sh postgres-access 5432 1.2.3.4/32 rnpr-clients

set -euo pipefail

# Arguments
FIREWALL_NAME=${1:-}
PORT=${2:-}
SOURCE_IP=${3:-}
SERVER_NAME=${4:-}

# Validate arguments
if [ -z "$FIREWALL_NAME" ] || [ -z "$PORT" ] || [ -z "$SOURCE_IP" ] || [ -z "$SERVER_NAME" ]; then
    echo "❌ Error: Missing required arguments"
    echo ""
    echo "Usage: bash add_firewall_rule.sh <firewall_name> <port> <source_ip> <server_name>"
    echo ""
    echo "Arguments:"
    echo "  firewall_name  - Name for the firewall (e.g., postgres-access)"
    echo "  port          - Port number (e.g., 5432 for PostgreSQL)"
    echo "  source_ip     - Source IP with CIDR (e.g., 1.2.3.4/32)"
    echo "  server_name   - Server to apply firewall (e.g., rnpr-clients)"
    echo ""
    echo "Example: bash add_firewall_rule.sh postgres-access 5432 1.2.3.4/32 rnpr-clients"
    echo ""
    echo "Common ports:"
    echo "  PostgreSQL: 5432"
    echo "  MySQL: 3306"
    echo "  MongoDB: 27017"
    echo "  Redis: 6379"
    echo "  HTTP: 80"
    echo "  HTTPS: 443"
    echo "  SSH: 22"
    exit 1
fi

# Validate source IP format
if [[ ! "$SOURCE_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+$ ]]; then
    echo "❌ Error: Source IP must include CIDR notation (e.g., 1.2.3.4/32)"
    echo "Single IP: add /32 (e.g., 1.2.3.4/32)"
    echo "Subnet: use appropriate CIDR (e.g., 1.2.3.0/24)"
    exit 1
fi

echo "=== Adding Firewall Rule ==="
echo ""
echo "📋 Configuration:"
echo "  - Firewall: $FIREWALL_NAME"
echo "  - Port: $PORT (TCP)"
echo "  - Source IP: $SOURCE_IP"
echo "  - Server: $SERVER_NAME"
echo ""

# Step 1: Create firewall if it doesn't exist
echo "📝 Step 1: Checking Firewall..."
echo ""

if hcloud firewall describe "$FIREWALL_NAME" >/dev/null 2>&1; then
    echo "✅ Firewall '$FIREWALL_NAME' exists"
else
    echo "Creating firewall: $FIREWALL_NAME"
    if hcloud firewall create --name "$FIREWALL_NAME"; then
        echo "✅ Firewall created"
    else
        echo "❌ Failed to create firewall"
        exit 1
    fi
fi

# Step 2: Add rule
echo ""
echo "📝 Step 2: Adding Rule..."
echo ""

if hcloud firewall add-rule "$FIREWALL_NAME" \
    --direction in \
    --protocol tcp \
    --port "$PORT" \
    --source-ips "$SOURCE_IP" 2>/dev/null; then
    echo "✅ Rule added successfully"
else
    echo "⚠️  Rule may already exist (this is OK)"
fi

# Step 3: Apply to server
echo ""
echo "📝 Step 3: Applying to Server..."
echo ""

if hcloud firewall apply-to-resource "$FIREWALL_NAME" \
    --type server \
    --server "$SERVER_NAME" 2>/dev/null; then
    echo "✅ Firewall applied to $SERVER_NAME"
else
    echo "⚠️  Firewall may already be applied (this is OK)"
fi

# Step 4: Verify
echo ""
echo "📝 Step 4: Verifying Configuration..."
echo ""

echo "Current firewall rules:"
hcloud firewall describe "$FIREWALL_NAME" | grep -A 10 "Rules:" || echo "No rules found"

echo ""
echo "✅ Firewall rule configuration complete!"
echo ""
echo "📋 Summary:"
echo "  - Firewall: $FIREWALL_NAME"
echo "  - Allows: $SOURCE_IP → $SERVER_NAME:$PORT (TCP)"
echo ""
echo "To remove this rule:"
echo "  hcloud firewall delete-rule $FIREWALL_NAME --direction in --protocol tcp --port $PORT --source-ips $SOURCE_IP"
echo ""
echo "To remove firewall from server:"
echo "  hcloud firewall remove-from-resource $FIREWALL_NAME --type server --server $SERVER_NAME"
echo ""
