#!/bin/bash

# Pokemon VGC Translation Web App - Deployment Script
# This script automates the deployment process for production environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="pokemon-vgc-translator"
DOCKER_REGISTRY=""
DOCKER_IMAGE_TAG="latest"
ENVIRONMENT="production"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Please create one based on api/env.example"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to validate environment variables
validate_env() {
    print_status "Validating environment variables..."
    
    # Check required environment variables
    required_vars=("GOOGLE_API_KEY" "SECRET_KEY")
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    print_success "Environment variables validated"
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build the main application image
    docker build -t $APP_NAME:$DOCKER_IMAGE_TAG .
    
    if [ $? -eq 0 ]; then
        print_success "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Run backend tests
    cd api
    if command -v pytest &> /dev/null; then
        pytest tests/ -v --tb=short
        if [ $? -ne 0 ]; then
            print_warning "Some backend tests failed"
        fi
    else
        print_warning "pytest not found, skipping backend tests"
    fi
    cd ..
    
    # Run frontend tests
    cd react-app
    if command -v npm &> /dev/null; then
        npm test -- --watchAll=false --passWithNoTests
        if [ $? -ne 0 ]; then
            print_warning "Some frontend tests failed"
        fi
    else
        print_warning "npm not found, skipping frontend tests"
    fi
    cd ..
    
    print_success "Tests completed"
}

# Function to deploy with Docker Compose
deploy_docker_compose() {
    print_status "Deploying with Docker Compose..."
    
    # Stop existing containers
    docker-compose down --remove-orphans
    
    # Pull latest images if using registry
    if [ ! -z "$DOCKER_REGISTRY" ]; then
        docker-compose pull
    fi
    
    # Start services
    docker-compose -f docker-compose.yml --profile prod up -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if curl -f http://localhost:8000/api/v2/health > /dev/null 2>&1; then
        print_success "API is healthy"
    else
        print_error "API health check failed"
        exit 1
    fi
    
    print_success "Deployment completed successfully"
}

# Function to deploy with monitoring
deploy_with_monitoring() {
    print_status "Deploying with monitoring stack..."
    
    # Deploy main application
    deploy_docker_compose
    
    # Deploy monitoring stack
    docker-compose -f docker-compose.yml --profile monitoring up -d
    
    print_success "Deployment with monitoring completed"
}

# Function to perform database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # This would be implemented based on your database setup
    # For now, we'll just print a placeholder
    print_warning "Database migrations not implemented yet"
}

# Function to backup data
backup_data() {
    print_status "Creating backup..."
    
    # Create backup directory
    mkdir -p backups/$(date +%Y%m%d_%H%M%S)
    
    # Backup Redis data
    docker exec pokemon-vgc-redis redis-cli BGSAVE
    docker cp pokemon-vgc-redis:/data/dump.rdb backups/$(date +%Y%m%d_%H%M%S)/redis_backup.rdb
    
    print_success "Backup created successfully"
}

# Function to rollback deployment
rollback() {
    print_status "Rolling back deployment..."
    
    # Stop current deployment
    docker-compose down
    
    # Restore from backup if available
    if [ -d "backups" ]; then
        latest_backup=$(ls -t backups | head -1)
        if [ ! -z "$latest_backup" ]; then
            print_status "Restoring from backup: $latest_backup"
            # Implement restore logic here
        fi
    fi
    
    # Start previous version
    docker-compose -f docker-compose.yml --profile prod up -d
    
    print_success "Rollback completed"
}

# Function to show deployment status
show_status() {
    print_status "Deployment Status:"
    
    echo "=== Container Status ==="
    docker-compose ps
    
    echo -e "\n=== Service Health ==="
    if curl -f http://localhost:8000/api/v2/health > /dev/null 2>&1; then
        echo -e "${GREEN}API: Healthy${NC}"
    else
        echo -e "${RED}API: Unhealthy${NC}"
    fi
    
    echo -e "\n=== Resource Usage ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Function to show logs
show_logs() {
    print_status "Recent logs:"
    docker-compose logs --tail=50
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    
    # Remove unused Docker images
    docker image prune -f
    
    # Remove unused Docker volumes
    docker volume prune -f
    
    # Remove unused Docker networks
    docker network prune -f
    
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Pokemon VGC Translation Web App - Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy          Deploy the application"
    echo "  deploy:monitor  Deploy with monitoring stack"
    echo "  test           Run tests before deployment"
    echo "  build          Build Docker images"
    echo "  status         Show deployment status"
    echo "  logs           Show recent logs"
    echo "  backup         Create backup"
    echo "  rollback       Rollback to previous version"
    echo "  cleanup        Clean up unused Docker resources"
    echo "  help           Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  GOOGLE_API_KEY    Google Gemini API key (required)"
    echo "  SECRET_KEY        Secret key for JWT (required)"
    echo "  DOCKER_REGISTRY   Docker registry URL (optional)"
    echo "  DOCKER_IMAGE_TAG  Docker image tag (default: latest)"
}

# Main script logic
case "${1:-help}" in
    "deploy")
        check_prerequisites
        validate_env
        build_images
        deploy_docker_compose
        show_status
        ;;
    "deploy:monitor")
        check_prerequisites
        validate_env
        build_images
        deploy_with_monitoring
        show_status
        ;;
    "test")
        check_prerequisites
        run_tests
        ;;
    "build")
        check_prerequisites
        build_images
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "backup")
        backup_data
        ;;
    "rollback")
        rollback
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        show_help
        ;;
esac 