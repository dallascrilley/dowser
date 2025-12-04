#!/bin/bash
# Health check for Real News PR Hetzner + Coolify infrastructure
# Usage: bash health_check.sh

set -euo pipefail

echo "=== Real News PR Infrastructure Health Check ==="
echo "Generated: $(date)"
echo ""

# Check if required commands are available
command -v coolify >/dev/null 2>&1 || { echo "❌ coolify CLI not found"; exit 1; }
command -v hcloud >/dev/null 2>&1 || { echo "❌ hcloud CLI not found"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "❌ jq not found"; exit 1; }

echo "## Coolify-Managed Servers"
echo ""

# Get Coolify servers
COOLIFY_SERVERS=$(coolify servers list --json 2>/dev/null || echo "[]")

if [ "$COOLIFY_SERVERS" = "[]" ]; then
    echo "❌ No Coolify servers found or authentication failed"
else
    echo "$COOLIFY_SERVERS" | jq -r '.[] | "- \(.name): \(if .is_reachable then "✅ Reachable" else "❌ Unreachable" end) | \(if .is_usable then "✅ Usable" else "❌ Not Usable" end)"'
fi

echo ""
echo "## All Hetzner Servers"
echo ""

# Get Hetzner servers
HCLOUD_SERVERS=$(hcloud server list -o json 2>/dev/null || echo "[]")

if [ "$HCLOUD_SERVERS" = "[]" ]; then
    echo "❌ No Hetzner servers found or authentication failed"
else
    echo "$HCLOUD_SERVERS" | jq -r '.[] | "- \(.name) (\(.server_type.name)): \(if .status == "running" then "✅ Running" else "❌ \(.status)" end) | IP: \(.public_net.ipv4.ip) | Location: \(.datacenter.location.name)"'
fi

echo ""
echo "## Resource Summary"
echo ""

# Calculate totals
TOTAL_CORES=$(echo "$HCLOUD_SERVERS" | jq '[.[] | .server_type.cores] | add')
TOTAL_RAM=$(echo "$HCLOUD_SERVERS" | jq '[.[] | .server_type.memory] | add')
TOTAL_DISK=$(echo "$HCLOUD_SERVERS" | jq '[.[] | .server_type.disk] | add')

echo "- Total vCPUs: $TOTAL_CORES"
echo "- Total RAM: ${TOTAL_RAM}GB"
echo "- Total Disk: ${TOTAL_DISK}GB"

echo ""
echo "## Quick Actions"
echo ""
echo "- Check specific server: coolify servers get <UUID>"
echo "- View container status: ssh root@<IP> 'docker ps'"
echo "- Check logs: ssh root@<IP> 'docker logs <container>'"
echo ""
