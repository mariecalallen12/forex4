#!/bin/bash

# ================================================================
# NOTIFICATION SETUP SCRIPT
# Digital Utopia Platform - Slack/Discord Integration
# ================================================================

set -e

echo "================================================================"
echo "   Digital Utopia Platform - Notification Setup"
echo "================================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "This script will help you setup notifications for CI/CD."
echo ""
echo "Choose notification service:"
echo "  1) Slack"
echo "  2) Discord"
echo "  3) Both"
echo "  4) Skip"
echo ""
read -p "Enter choice (1-4): " NOTIF_CHOICE

# ================================================================
# SLACK SETUP
# ================================================================
setup_slack() {
    echo ""
    echo -e "${BLUE}=== Slack Setup ===${NC}"
    echo ""
    echo "Follow these steps to get Slack webhook:"
    echo ""
    echo "1. Go to: https://api.slack.com/apps"
    echo "2. Click 'Create New App' → 'From scratch'"
    echo "3. App Name: 'GitHub CI/CD Bot'"
    echo "4. Select your workspace"
    echo "5. In 'Incoming Webhooks', toggle ON"
    echo "6. Click 'Add New Webhook to Workspace'"
    echo "7. Select channel (e.g., #deployments)"
    echo "8. Copy the Webhook URL"
    echo ""
    read -p "Paste Slack Webhook URL: " SLACK_WEBHOOK
    
    if [ -z "$SLACK_WEBHOOK" ]; then
        echo -e "${YELLOW}Skipped Slack setup${NC}"
        return
    fi
    
    echo ""
    echo -e "${GREEN}✓ Slack webhook received${NC}"
    echo ""
    echo "Add this to GitHub Secrets:"
    echo "  Repository → Settings → Secrets → Actions"
    echo "  Name: SLACK_WEBHOOK"
    echo "  Value: $SLACK_WEBHOOK"
    echo ""
    
    # Test webhook
    read -p "Test webhook now? (y/n): " TEST_SLACK
    if [ "$TEST_SLACK" = "y" ]; then
        echo "Sending test message..."
        curl -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d '{
                "text": "🚀 GitHub CI/CD Bot is now connected!",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*GitHub CI/CD Bot*\n✅ Successfully connected to Digital Utopia Platform"
                        }
                    }
                ]
            }'
        echo ""
        echo -e "${GREEN}✓ Test message sent!${NC}"
    fi
}

# ================================================================
# DISCORD SETUP
# ================================================================
setup_discord() {
    echo ""
    echo -e "${BLUE}=== Discord Setup ===${NC}"
    echo ""
    echo "Follow these steps to get Discord webhook:"
    echo ""
    echo "1. Open your Discord server"
    echo "2. Go to Server Settings → Integrations"
    echo "3. Click 'Webhooks' → 'New Webhook'"
    echo "4. Name: 'GitHub CI/CD Bot'"
    echo "5. Select channel (e.g., #deployments)"
    echo "6. Copy Webhook URL"
    echo ""
    read -p "Paste Discord Webhook URL: " DISCORD_WEBHOOK
    
    if [ -z "$DISCORD_WEBHOOK" ]; then
        echo -e "${YELLOW}Skipped Discord setup${NC}"
        return
    fi
    
    echo ""
    echo -e "${GREEN}✓ Discord webhook received${NC}"
    echo ""
    echo "Add this to GitHub Secrets:"
    echo "  Repository → Settings → Secrets → Actions"
    echo "  Name: DISCORD_WEBHOOK"
    echo "  Value: $DISCORD_WEBHOOK"
    echo ""
    
    # Test webhook
    read -p "Test webhook now? (y/n): " TEST_DISCORD
    if [ "$TEST_DISCORD" = "y" ]; then
        echo "Sending test message..."
        curl -X POST "$DISCORD_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d '{
                "content": "🚀 **GitHub CI/CD Bot** is now connected!",
                "embeds": [{
                    "title": "Connection Successful",
                    "description": "Digital Utopia Platform CI/CD notifications are now active.",
                    "color": 3066993
                }]
            }'
        echo ""
        echo -e "${GREEN}✓ Test message sent!${NC}"
    fi
}

# ================================================================
# MAIN LOGIC
# ================================================================
case $NOTIF_CHOICE in
    1)
        setup_slack
        ;;
    2)
        setup_discord
        ;;
    3)
        setup_slack
        setup_discord
        ;;
    4)
        echo -e "${YELLOW}Skipped notification setup${NC}"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# ================================================================
# WORKFLOW MODIFICATION INSTRUCTIONS
# ================================================================
echo ""
echo "================================================================"
echo "              WORKFLOW MODIFICATION NEEDED"
echo "================================================================"
echo ""
echo "To enable notifications in workflows:"
echo ""
echo "1. Edit .github/workflows/deploy.yml"
echo ""
echo "2. Find and uncomment these lines in post-deployment job:"
echo ""
echo "   # - name: Notify Team"
echo "   #   uses: 8398a7/action-slack@v3"
echo "   #   with:"
echo "   #     status: \${{ job.status }}"
echo "   #     webhook_url: \${{ secrets.SLACK_WEBHOOK }}"
echo ""
echo "3. For Discord, add similar step with Discord webhook action"
echo ""
echo "4. Commit and push changes"
echo ""
echo "================================================================"
echo "              SETUP COMPLETE"
echo "================================================================"
echo ""
echo -e "${GREEN}✓ Notification setup completed${NC}"
echo ""
echo "Don't forget to:"
echo "  1. Add webhooks to GitHub Secrets"
echo "  2. Modify workflow files to enable notifications"
echo "  3. Test with a deployment"
echo ""
