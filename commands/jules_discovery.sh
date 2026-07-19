#!/bin/bash
set -e
# Discover Jules tooling capabilities
echo "Available Jules Tooling Commands (commands/):"
ls -1 commands/ | grep -v jules_discovery.sh | sed 's/^/- /'
echo ""
echo "For detailed workflows, see docs/runbooks/"
