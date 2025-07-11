@echo off
REM Beach Volleyball Simulator - Development Script for Windows
REM This script helps you quickly start the application in different modes

setlocal enabledelayedexpansion

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check for docker-compose
docker-compose version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Docker Compose is not available. Please install Docker Compose.
        exit /b 1
    ) else (
        set DOCKER_COMPOSE=docker compose
    )
) else (
    set DOCKER_COMPOSE=docker-compose
)

if "%1"=="" goto help
if "%1"=="start" goto start_full
if "%1"=="up" goto start_full
if "%1"=="backend" goto start_backend
if "%1"=="frontend" goto start_frontend
if "%1"=="stop" goto stop_services
if "%1"=="down" goto stop_services
if "%1"=="restart" goto restart_services
if "%1"=="logs" goto show_logs
if "%1"=="test" goto run_tests
if "%1"=="clean" goto cleanup
if "%1"=="help" goto help
if "%1"=="-h" goto help
if "%1"=="--help" goto help

echo [ERROR] Unknown command: %1
echo.
goto help

:start_full
echo [INFO] Starting Beach Volleyball Simulator (Full Stack)...
%DOCKER_COMPOSE% up --build -d
timeout /t 5 /nobreak >nul
echo.
echo 🚀 Beach Volleyball Simulator is ready!
echo.
echo 📊 Frontend (Analytics Dashboard): http://localhost:3000
echo 🔧 Backend API Documentation: http://localhost:8000/docs
echo 🔍 API Redoc Documentation: http://localhost:8000/redoc
echo 📈 Health Check: http://localhost:8000/health
echo.
echo 🛑 To stop all services: dev.bat stop
echo 📋 To view logs: dev.bat logs
echo 🔄 To restart: dev.bat restart
goto end

:start_backend
echo [INFO] Starting Backend Only...
%DOCKER_COMPOSE% up --build backend db redis -d
echo [SUCCESS] Backend services started!
echo 🔧 API Documentation: http://localhost:8000/docs
echo 📈 Health Check: http://localhost:8000/health
goto end

:start_frontend
echo [INFO] Starting Frontend Development Mode...
cd frontend
if not exist "node_modules" (
    echo [INFO] Installing frontend dependencies...
    npm install
)
echo [INFO] Starting frontend development server...
npm run dev
goto end

:stop_services
echo [INFO] Stopping all services...
%DOCKER_COMPOSE% down
echo [SUCCESS] All services stopped!
goto end

:restart_services
echo [INFO] Restarting services...
call :stop_services
timeout /t 2 /nobreak >nul
call :start_full
goto end

:show_logs
if "%2"=="" (
    echo [INFO] Showing logs for all services...
    %DOCKER_COMPOSE% logs -f
) else (
    echo [INFO] Showing logs for %2...
    %DOCKER_COMPOSE% logs -f %2
)
goto end

:run_tests
echo [INFO] Running tests...
echo [INFO] Running backend tests...
%DOCKER_COMPOSE% exec backend python -m pytest tests/ -v
echo [SUCCESS] Tests completed!
goto end

:cleanup
echo [WARNING] This will remove all containers, volumes, and images for this project.
set /p confirm="Are you sure? (y/N): "
if /i "!confirm!"=="y" (
    echo [INFO] Cleaning up...
    %DOCKER_COMPOSE% down -v --rmi all --remove-orphans
    echo [SUCCESS] Cleanup completed!
) else (
    echo [INFO] Cleanup cancelled.
)
goto end

:help
echo Beach Volleyball Simulator - Development Helper
echo.
echo Usage: dev.bat [COMMAND]
echo.
echo Commands:
echo   start, up       Start the full application (frontend + backend + databases)
echo   backend         Start only backend services (API + databases)
echo   frontend        Start only frontend in development mode
echo   stop, down      Stop all running services
echo   restart         Restart all services
echo   logs [service]  Show logs (optionally for specific service)
echo   test            Run all tests
echo   clean           Clean up all containers and volumes
echo   help            Show this help message
echo.
echo Examples:
echo   dev.bat start          # Start everything
echo   dev.bat backend        # Backend development
echo   dev.bat frontend       # Frontend development
echo   dev.bat logs backend   # Show backend logs only
echo   dev.bat test           # Run tests
echo.
echo Services:
echo   - Frontend: http://localhost:3000 (Analytics Dashboard)
echo   - Backend API: http://localhost:8000/docs (API Documentation)
echo   - Database: PostgreSQL on port 5432
echo   - Redis: Cache on port 6379
goto end

:end
