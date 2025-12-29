#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ports to check
POSTGRES_PORT=5433
REDIS_PORT=6379
API_PORT=8000
FRONTEND_PORT=3000

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Quilent Development Environment     ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    local service=$2
    local pid=$(lsof -ti :$port 2>/dev/null)

    if [ -n "$pid" ]; then
        echo -e "${YELLOW}Port $port ($service): IN USE (PID: $pid)${NC}"
        return 1
    else
        echo -e "${GREEN}Port $port ($service): Available${NC}"
        return 0
    fi
}

# Function to stop process on port
stop_port() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null)

    if [ -n "$pids" ]; then
        echo -e "${YELLOW}Stopping processes on port $port...${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null
        sleep 1
        echo -e "${GREEN}Stopped.${NC}"
    fi
}

# Check all ports
echo -e "${BLUE}Checking port availability...${NC}"
echo ""

ports_in_use=0

check_port $POSTGRES_PORT "PostgreSQL" || ports_in_use=1
check_port $REDIS_PORT "Redis" || ports_in_use=1
check_port $API_PORT "API" || ports_in_use=1
check_port $FRONTEND_PORT "Frontend" || ports_in_use=1

echo ""

# If ports are in use, ask what to do
if [ $ports_in_use -eq 1 ]; then
    echo -e "${YELLOW}Some ports are already in use.${NC}"
    echo ""
    echo "What would you like to do?"
    echo "  1) Stop all and restart fresh"
    echo "  2) Stop only conflicting services"
    echo "  3) Keep running (use existing services)"
    echo "  4) Exit"
    echo ""
    read -p "Enter choice [1-4]: " choice

    case $choice in
        1)
            echo ""
            echo -e "${YELLOW}Stopping all services...${NC}"

            # Stop Docker containers
            docker-compose down 2>/dev/null

            # Stop processes on all ports
            stop_port $POSTGRES_PORT
            stop_port $REDIS_PORT
            stop_port $API_PORT
            stop_port $FRONTEND_PORT

            echo -e "${GREEN}All services stopped.${NC}"
            echo ""

            # Start fresh
            echo -e "${BLUE}Starting Docker services...${NC}"
            docker-compose up -d postgres redis api

            echo ""
            echo -e "${BLUE}Running database migrations...${NC}"
            sleep 3  # Wait for services to be ready
            docker-compose exec -T api alembic upgrade head

            echo ""
            echo -e "${GREEN}Backend services started!${NC}"
            echo ""
            echo -e "${BLUE}To start frontend, run in a new terminal:${NC}"
            echo "  cd services/govbids && pnpm dev"
            ;;
        2)
            echo ""
            echo "Select which services to stop:"

            # Check and offer to stop each service
            if lsof -ti :$POSTGRES_PORT >/dev/null 2>&1; then
                read -p "Stop PostgreSQL (port $POSTGRES_PORT)? [y/N]: " stop_pg
                [ "$stop_pg" = "y" ] || [ "$stop_pg" = "Y" ] && stop_port $POSTGRES_PORT
            fi

            if lsof -ti :$REDIS_PORT >/dev/null 2>&1; then
                read -p "Stop Redis (port $REDIS_PORT)? [y/N]: " stop_redis
                [ "$stop_redis" = "y" ] || [ "$stop_redis" = "Y" ] && stop_port $REDIS_PORT
            fi

            if lsof -ti :$API_PORT >/dev/null 2>&1; then
                read -p "Stop API (port $API_PORT)? [y/N]: " stop_api
                [ "$stop_api" = "y" ] || [ "$stop_api" = "Y" ] && stop_port $API_PORT
            fi

            if lsof -ti :$FRONTEND_PORT >/dev/null 2>&1; then
                read -p "Stop Frontend (port $FRONTEND_PORT)? [y/N]: " stop_fe
                [ "$stop_fe" = "y" ] || [ "$stop_fe" = "Y" ] && stop_port $FRONTEND_PORT
            fi

            echo ""
            echo -e "${GREEN}Selected services stopped.${NC}"
            ;;
        3)
            echo ""
            echo -e "${GREEN}Keeping existing services running.${NC}"
            echo ""
            echo -e "${BLUE}Current services:${NC}"
            echo "  PostgreSQL: http://localhost:$POSTGRES_PORT"
            echo "  Redis:      localhost:$REDIS_PORT"
            echo "  API:        http://localhost:$API_PORT"
            echo "  API Docs:   http://localhost:$API_PORT/docs"
            echo "  Frontend:   http://localhost:$FRONTEND_PORT"
            ;;
        4)
            echo ""
            echo -e "${YELLOW}Exiting without changes.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
else
    # All ports available, start services
    echo -e "${GREEN}All ports available!${NC}"
    echo ""

    read -p "Start Docker services? [Y/n]: " start_services

    if [ "$start_services" != "n" ] && [ "$start_services" != "N" ]; then
        echo ""
        echo -e "${BLUE}Starting Docker services...${NC}"
        docker-compose up -d postgres redis api

        echo ""
        echo -e "${BLUE}Waiting for services to be ready...${NC}"
        sleep 5

        echo ""
        echo -e "${BLUE}Running database migrations...${NC}"
        docker-compose exec -T api alembic upgrade head

        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}   Backend services started!           ${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo -e "${BLUE}Services:${NC}"
        echo "  PostgreSQL: localhost:$POSTGRES_PORT"
        echo "  Redis:      localhost:$REDIS_PORT"
        echo "  API:        http://localhost:$API_PORT"
        echo "  API Docs:   http://localhost:$API_PORT/docs"
        echo ""
        echo -e "${BLUE}To start frontend, run in a new terminal:${NC}"
        echo "  cd services/govbids && pnpm dev"
    fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Useful Commands                     ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "  View logs:     docker-compose logs -f api"
echo "  Stop all:      docker-compose down"
echo "  Restart API:   docker-compose restart api"
echo "  DB shell:      docker-compose exec postgres psql -U quilent"
echo ""
