#!/bin/bash
# Code Review Pre-commit Check
# This script warns if code review hasn't been done recently

REVIEW_STATUS_FILE=".code-review-status"
YELLOW='\033[1;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if review status file exists
if [ ! -f "$REVIEW_STATUS_FILE" ]; then
    echo -e "${YELLOW}⚠️  WARNING: No code review status found${NC}"
    echo ""
    echo "It looks like code hasn't been reviewed yet."
    echo ""
    echo "To run a code review:"
    echo "  1. Ask Claude Code: 'review the code'"
    echo "  2. Or run: ./scripts/mark-reviewed.sh"
    echo ""
    echo -e "${YELLOW}Commit will proceed, but please schedule a code review.${NC}"
    echo ""
    exit 0  # Warning only, don't block commit
fi

# Read last review date
LAST_REVIEW=$(cat "$REVIEW_STATUS_FILE" | grep "last_reviewed:" | cut -d' ' -f2)
LAST_REVIEWER=$(cat "$REVIEW_STATUS_FILE" | grep "reviewer:" | cut -d' ' -f2-)
REVIEW_STATUS=$(cat "$REVIEW_STATUS_FILE" | grep "status:" | cut -d' ' -f2)

# Calculate days since review
if [ -n "$LAST_REVIEW" ]; then
    LAST_REVIEW_EPOCH=$(date -j -f "%Y-%m-%d" "$LAST_REVIEW" "+%s" 2>/dev/null || date -d "$LAST_REVIEW" "+%s" 2>/dev/null)
    CURRENT_EPOCH=$(date "+%s")
    DAYS_SINCE=$(( (CURRENT_EPOCH - LAST_REVIEW_EPOCH) / 86400 ))

    if [ "$DAYS_SINCE" -gt 7 ]; then
        echo -e "${YELLOW}⚠️  WARNING: Code review is ${DAYS_SINCE} days old${NC}"
        echo ""
        echo "Last reviewed: $LAST_REVIEW by $LAST_REVIEWER"
        echo "Status: $REVIEW_STATUS"
        echo ""
        echo "Consider scheduling a new code review."
        echo ""
    elif [ "$REVIEW_STATUS" == "issues_found" ]; then
        echo -e "${YELLOW}⚠️  WARNING: Previous review found issues${NC}"
        echo ""
        echo "Last reviewed: $LAST_REVIEW by $LAST_REVIEWER"
        echo "Check CODE_REVIEW.md for outstanding issues."
        echo ""
    else
        echo -e "${GREEN}✓ Code review up to date ($LAST_REVIEW by $LAST_REVIEWER)${NC}"
    fi
fi

exit 0  # Always allow commit (warning only)
