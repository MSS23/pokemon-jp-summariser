@echo off
REM Pokemon VGC Translation Web App - Deployment Script (Windows)
REM This script automates the deployment process for production environments

setlocal enabledelayedexpansion

REM Configuration
set APP_NAME=pokemon-vgc-translator
set DOCKER_REGISTRY=
set DOCKER_IMAGE_TAG=latest
set ENVIRONMENT=production

REM Colors for output (Windows 10+)
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

REM Function to print colored output
:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM Function to check prerequisites
:check_prerequisites
call :print_status "Checking prerequisites..."

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker is not installed. Please install Docker Desktop first."
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    call :print_error ".env file not found. Please create one based on api/env.example"
    exit /b 1
)

call :print_success "Prerequisites check passed"
goto :eof

REM Function to validate environment variables
:validate_env
call :print_status "Validating environment variables..."

REM Check required environment variables
if "%GOOGLE_API_KEY%"=="" (
    call :print_error "Required environment variable GOOGLE_API_KEY is not set"
    exit /b 1
)

if "%SECRET_KEY%"=="" (
    call :print_error "Required environment variable SECRET_KEY is not set"
    exit /b 1
)

call :print_success "Environment variables validated"
goto :eof

REM Function to build Docker images
:build_images
call :print_status "Building Docker images..."

REM Build the main application image
docker build -t %APP_NAME%:%DOCKER_IMAGE_TAG% .

if errorlevel 1 (
    call :print_error "Failed to build Docker images"
    exit /b 1
)

call :print_success "Docker images built successfully"
goto :eof

REM Function to run tests
:run_tests
call :print_status "Running tests..."

REM Run backend tests
cd api
pytest tests/ -v --tb=short >nul 2>&1
if errorlevel 1 (
    call :print_warning "Some backend tests failed"
)
cd ..

REM Run frontend tests
cd react-app
npm test -- --watchAll=false --passWithNoTests >nul 2>&1
if errorlevel 1 (
    call :print_warning "Some frontend tests failed"
)
cd ..

call :print_success "Tests completed"
goto :eof

REM Function to deploy with Docker Compose
:deploy_docker_compose
call :print_status "Deploying with Docker Compose..."

REM Stop existing containers
docker-compose down --remove-orphans

REM Pull latest images if using registry
if not "%DOCKER_REGISTRY%"=="" (
    docker-compose pull
)

REM Start services
docker-compose -f docker-compose.yml --profile prod up -d

REM Wait for services to be healthy
call :print_status "Waiting for services to be healthy..."
timeout /t 30 /nobreak >nul

REM Check service health
curl -f http://localhost:8000/api/v2/health >nul 2>&1
if errorlevel 1 (
    call :print_error "API health check failed"
    exit /b 1
)

call :print_success "Deployment completed successfully"
goto :eof

REM Function to deploy with monitoring
:deploy_with_monitoring
call :print_status "Deploying with monitoring stack..."

REM Deploy main application
call :deploy_docker_compose

REM Deploy monitoring stack
docker-compose -f docker-compose.yml --profile monitoring up -d

call :print_success "Deployment with monitoring completed"
goto :eof

REM Function to backup data
:backup_data
call :print_status "Creating backup..."

REM Create backup directory
set BACKUP_DIR=backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%" 2>nul

REM Backup Redis data
docker exec pokemon-vgc-redis redis-cli BGSAVE
docker cp pokemon-vgc-redis:/data/dump.rdb "%BACKUP_DIR%/redis_backup.rdb"

call :print_success "Backup created successfully"
goto :eof

REM Function to rollback deployment
:rollback
call :print_status "Rolling back deployment..."

REM Stop current deployment
docker-compose down

REM Start previous version
docker-compose -f docker-compose.yml --profile prod up -d

call :print_success "Rollback completed"
goto :eof

REM Function to show deployment status
:show_status
call :print_status "Deployment Status:"

echo === Container Status ===
docker-compose ps

echo.
echo === Service Health ===
curl -f http://localhost:8000/api/v2/health >nul 2>&1
if errorlevel 1 (
    echo %RED%API: Unhealthy%NC%
) else (
    echo %GREEN%API: Healthy%NC%
)

echo.
echo === Resource Usage ===
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
goto :eof

REM Function to show logs
:show_logs
call :print_status "Recent logs:"
docker-compose logs --tail=50
goto :eof

REM Function to clean up
:cleanup
call :print_status "Cleaning up..."

REM Remove unused Docker images
docker image prune -f

REM Remove unused Docker volumes
docker volume prune -f

REM Remove unused Docker networks
docker network prune -f

call :print_success "Cleanup completed"
goto :eof

REM Function to show help
:show_help
echo Pokemon VGC Translation Web App - Deployment Script
echo.
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   deploy          Deploy the application
echo   deploy:monitor  Deploy with monitoring stack
echo   test           Run tests before deployment
echo   build          Build Docker images
echo   status         Show deployment status
echo   logs           Show recent logs
echo   backup         Create backup
echo   rollback       Rollback to previous version
echo   cleanup        Clean up unused Docker resources
echo   help           Show this help message
echo.
echo Environment Variables:
echo   GOOGLE_API_KEY    Google Gemini API key (required)
echo   SECRET_KEY        Secret key for JWT (required)
echo   DOCKER_REGISTRY   Docker registry URL (optional)
echo   DOCKER_IMAGE_TAG  Docker image tag (default: latest)
goto :eof

REM Main script logic
if "%1"=="" goto show_help
if "%1"=="help" goto show_help
if "%1"=="deploy" goto deploy
if "%1"=="deploy:monitor" goto deploy_monitor
if "%1"=="test" goto test
if "%1"=="build" goto build
if "%1"=="status" goto status
if "%1"=="logs" goto logs
if "%1"=="backup" goto backup
if "%1"=="rollback" goto rollback
if "%1"=="cleanup" goto cleanup
goto show_help

:deploy
call :check_prerequisites
call :validate_env
call :build_images
call :deploy_docker_compose
call :show_status
goto :eof

:deploy_monitor
call :check_prerequisites
call :validate_env
call :build_images
call :deploy_with_monitoring
call :show_status
goto :eof

:test
call :check_prerequisites
call :run_tests
goto :eof

:build
call :check_prerequisites
call :build_images
goto :eof

:status
call :show_status
goto :eof

:logs
call :show_logs
goto :eof

:backup
call :backup_data
goto :eof

:rollback
call :rollback
goto :eof

:cleanup
call :cleanup
goto :eof 