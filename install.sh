#!/bin/bash

# Production Job Search System Installer
# Installs and configures the enterprise-grade job search system for Daniel Gillaspy

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# System paths
SYSTEM_DIR="/Users/daniel/workapps/production_job_system"
LOG_FILE="${SYSTEM_DIR}/install.log"
PYTHON_ENV="${SYSTEM_DIR}/venv"
SERVICE_NAME="com.daniel.jobsearch"
PLIST_PATH="${HOME}/Library/LaunchAgents/${SERVICE_NAME}.plist"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Production Job Search System Setup   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Logging function
log() {
    echo -e "$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "${LOG_FILE}" 2>/dev/null || true
}

# Check if running as correct user
check_user() {
    if [[ "$USER" != "daniel" ]]; then
        log "${RED}ERROR: This installer must be run as user 'daniel'${NC}"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log "${BLUE}Checking system requirements...${NC}"
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        log "${RED}ERROR: Python 3 is required but not installed${NC}"
        exit 1
    fi
    
    # Check Python version (3.8+)
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log "${RED}ERROR: Python 3.8+ required, found ${python_version}${NC}"
        exit 1
    fi
    
    # Check Chrome for Selenium (optional but recommended)
    if ! command -v "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" &> /dev/null; then
        log "${YELLOW}WARNING: Google Chrome not found - web scraping may be limited${NC}"
    fi
    
    log "${GREEN}✓ System requirements check passed${NC}"
}

# Install Python dependencies
install_dependencies() {
    log "${BLUE}Installing Python dependencies...${NC}"
    
    # Create virtual environment
    if [[ ! -d "${PYTHON_ENV}" ]]; then
        python3 -m venv "${PYTHON_ENV}"
        log "${GREEN}✓ Created Python virtual environment${NC}"
    fi
    
    # Activate virtual environment
    source "${PYTHON_ENV}/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r "${SYSTEM_DIR}/requirements.txt"
    
    # Install additional development tools
    pip install pytest black flake8 mypy
    
    log "${GREEN}✓ Python dependencies installed successfully${NC}"
}

# Setup database
setup_database() {
    log "${BLUE}Setting up database...${NC}"
    
    # Ensure database directory exists
    mkdir -p "/Users/daniel/databases"
    
    # Initialize database schema
    source "${PYTHON_ENV}/bin/activate"
    cd "${SYSTEM_DIR}"
    python3 -c "
from database import JobSearchDatabase
db = JobSearchDatabase()
print('Database schema initialized successfully')
"
    
    log "${GREEN}✓ Database setup completed${NC}"
}

# Configure API keys
configure_api_keys() {
    log "${BLUE}Configuring API keys...${NC}"
    
    # Create secure config directory
    CONFIG_DIR="/Users/daniel/.config/jobsearch"
    mkdir -p "${CONFIG_DIR}"
    chmod 700 "${CONFIG_DIR}"
    
    # Check if config already exists
    if [[ -f "${CONFIG_DIR}/api_keys.json" ]]; then
        log "${YELLOW}API configuration already exists${NC}"
        return
    fi
    
    # Interactive API key setup
    echo ""
    echo -e "${YELLOW}API Key Configuration:${NC}"
    echo "The system requires API keys for full functionality."
    echo "You can skip these now and add them later by editing:"
    echo "  ${CONFIG_DIR}/api_keys.json"
    echo ""
    
    # RapidAPI Key (JSearch)
    echo -e "${BLUE}RapidAPI Key (for JSearch API):${NC}"
    echo "1. Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch"
    echo "2. Subscribe to the free tier (1000 requests/month)"
    echo "3. Copy your API key"
    echo ""
    read -p "Enter your RapidAPI key (or press Enter to skip): " rapidapi_key
    
    # iCloud App Password
    echo ""
    echo -e "${BLUE}iCloud App Password (for email notifications):${NC}"
    echo "1. Go to https://appleid.apple.com/account/manage"
    echo "2. Generate an app-specific password"
    echo "3. Copy the password"
    echo ""
    read -s -p "Enter your iCloud app password (or press Enter to skip): " icloud_password
    echo ""
    
    # Create API keys file
    cat > "${CONFIG_DIR}/api_keys.json" << EOF
{
  "rapidapi_key": "${rapidapi_key:-null}",
  "icloud_password": "${icloud_password:-null}",
  "created": "$(date -Iseconds)",
  "notes": "Edit this file to update API keys"
}
EOF
    
    chmod 600 "${CONFIG_DIR}/api_keys.json"
    log "${GREEN}✓ API configuration saved securely${NC}"
}

# Install LaunchAgent for automation
install_launch_agent() {
    log "${BLUE}Installing LaunchAgent for automation...${NC}"
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "${HOME}/Library/LaunchAgents"
    
    # Create LaunchAgent plist
    cat > "${PLIST_PATH}" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${SERVICE_NAME}</string>
    
    <key>Program</key>
    <string>${PYTHON_ENV}/bin/python</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_ENV}/bin/python</string>
        <string>${SYSTEM_DIR}/main.py</string>
        <string>--daemon</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${SYSTEM_DIR}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>${SYSTEM_DIR}/logs/jobsearch.out</string>
    
    <key>StandardErrorPath</key>
    <string>${SYSTEM_DIR}/logs/jobsearch.err</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
        <key>PYTHONPATH</key>
        <string>${SYSTEM_DIR}</string>
    </dict>
</dict>
</plist>
EOF
    
    # Create logs directory
    mkdir -p "${SYSTEM_DIR}/logs"
    
    log "${GREEN}✓ LaunchAgent installed${NC}"
}

# Create main launcher script
create_main_launcher() {
    log "${BLUE}Creating main launcher script...${NC}"
    
    cat > "${SYSTEM_DIR}/main.py" << 'EOF'
#!/usr/bin/env python3
"""
Main launcher for Production Job Search System
Handles daemon mode, one-time runs, and web dashboard
"""

import argparse
import asyncio
import logging
import sys
import os
from pathlib import Path
import signal
import json
import uvicorn
from datetime import datetime

# Add system directory to path
sys.path.insert(0, str(Path(__file__).parent))

from automation_scheduler import ProductionJobScheduler
from web_dashboard import app
from database import JobSearchDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/daniel/workapps/production_job_system/logs/main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobSearchManager:
    """Main system manager"""
    
    def __init__(self):
        self.scheduler = None
        self.web_server = None
        self.running = False
        
    async def run_daemon(self):
        """Run in daemon mode with scheduler"""
        logger.info("Starting Job Search System in daemon mode...")
        
        try:
            # Initialize and start scheduler
            self.scheduler = ProductionJobScheduler()
            self.scheduler.start_scheduler()
            self.running = True
            
            logger.info("Daemon started successfully - waiting for schedule...")
            
            # Keep running
            while self.running:
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        finally:
            await self.shutdown()
    
    async def run_once(self):
        """Run job search once and exit"""
        logger.info("Running one-time job search...")
        
        try:
            scheduler = ProductionJobScheduler()
            await scheduler._run_daily_job_search()
            logger.info("One-time job search completed successfully")
        except Exception as e:
            logger.error(f"One-time job search failed: {e}")
            sys.exit(1)
    
    def run_web_dashboard(self, host="127.0.0.1", port=8000):
        """Run web dashboard"""
        logger.info(f"Starting web dashboard on {host}:{port}")
        
        try:
            uvicorn.run(app, host=host, port=port, log_level="info")
        except Exception as e:
            logger.error(f"Web dashboard error: {e}")
            sys.exit(1)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down Job Search System...")
        self.running = False
        
        if self.scheduler:
            self.scheduler.stop_scheduler()
        
        logger.info("Shutdown completed")
    
    def status(self):
        """Show system status"""
        try:
            db = JobSearchDatabase()
            stats = db.get_statistics()
            
            print("\n" + "="*50)
            print("  Job Search System Status")
            print("="*50)
            print(f"Total Jobs Found: {stats.get('total_jobs', 0)}")
            print(f"New Jobs (7 days): {stats.get('jobs_last_week', 0)}")
            print(f"Applications Sent: {stats.get('total_applications', 0)}")
            print(f"Average Match Score: {stats.get('avg_match_score', 0):.1%}")
            print(f"Highest Salary Found: ${stats.get('highest_salary', 0):,}")
            print("")
            
            # Check if LaunchAgent is loaded
            import subprocess
            result = subprocess.run(['launchctl', 'list', 'com.daniel.jobsearch'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ LaunchAgent: Running")
            else:
                print("❌ LaunchAgent: Not loaded")
            
            # Check database
            if Path("/Users/daniel/databases/productivity.db").exists():
                print("✅ Database: Connected")
            else:
                print("❌ Database: Not found")
            
            print("="*50)
            
        except Exception as e:
            print(f"Error getting status: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Production Job Search System')
    
    parser.add_argument('--daemon', action='store_true',
                       help='Run in daemon mode with scheduler')
    parser.add_argument('--once', action='store_true',
                       help='Run job search once and exit')
    parser.add_argument('--web', action='store_true',
                       help='Start web dashboard')
    parser.add_argument('--status', action='store_true',
                       help='Show system status')
    parser.add_argument('--host', default='127.0.0.1',
                       help='Web dashboard host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                       help='Web dashboard port (default: 8000)')
    
    args = parser.parse_args()
    
    manager = JobSearchManager()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        asyncio.create_task(manager.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Execute based on arguments
    if args.status:
        manager.status()
    elif args.daemon:
        asyncio.run(manager.run_daemon())
    elif args.once:
        asyncio.run(manager.run_once())
    elif args.web:
        manager.run_web_dashboard(args.host, args.port)
    else:
        # Default: show status and usage
        manager.status()
        print("\nUsage:")
        print("  python main.py --daemon     # Run as background service")
        print("  python main.py --once       # Run job search once")
        print("  python main.py --web        # Start web dashboard")
        print("  python main.py --status     # Show system status")

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "${SYSTEM_DIR}/main.py"
    log "${GREEN}✓ Main launcher created${NC}"
}

# Create command-line tools
create_cli_tools() {
    log "${BLUE}Creating command-line tools...${NC}"
    
    # Create jobsearch command
    cat > "/usr/local/bin/jobsearch" << EOF
#!/bin/bash
# Job Search System CLI Tool

SYSTEM_DIR="/Users/daniel/workapps/production_job_system"
PYTHON_ENV="\${SYSTEM_DIR}/venv"

# Activate virtual environment and run
source "\${PYTHON_ENV}/bin/activate"
cd "\${SYSTEM_DIR}"
python3 main.py "\$@"
EOF
    
    chmod +x "/usr/local/bin/jobsearch"
    
    # Create LaunchAgent management script
    cat > "${SYSTEM_DIR}/manage_service.sh" << EOF
#!/bin/bash
# LaunchAgent Management Script

PLIST_PATH="${PLIST_PATH}"
SERVICE_NAME="${SERVICE_NAME}"

case "\$1" in
    start)
        echo "Starting job search service..."
        launchctl load "\${PLIST_PATH}"
        ;;
    stop)
        echo "Stopping job search service..."
        launchctl unload "\${PLIST_PATH}"
        ;;
    restart)
        echo "Restarting job search service..."
        launchctl unload "\${PLIST_PATH}" 2>/dev/null || true
        sleep 2
        launchctl load "\${PLIST_PATH}"
        ;;
    status)
        launchctl list | grep "\${SERVICE_NAME}" || echo "Service not running"
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status}"
        exit 1
        ;;
esac
EOF
    
    chmod +x "${SYSTEM_DIR}/manage_service.sh"
    
    log "${GREEN}✓ CLI tools created${NC}"
}

# Create uninstaller
create_uninstaller() {
    log "${BLUE}Creating uninstaller...${NC}"
    
    cat > "${SYSTEM_DIR}/uninstall.sh" << EOF
#!/bin/bash
# Production Job Search System Uninstaller

echo "Uninstalling Production Job Search System..."

# Stop and remove LaunchAgent
launchctl unload "${PLIST_PATH}" 2>/dev/null || true
rm -f "${PLIST_PATH}"

# Remove CLI tool
rm -f "/usr/local/bin/jobsearch"

# Remove config directory (prompt first)
read -p "Remove configuration and API keys? (y/N): " remove_config
if [[ "\$remove_config" == "y" || "\$remove_config" == "Y" ]]; then
    rm -rf "/Users/daniel/.config/jobsearch"
fi

# Remove logs but keep database
read -p "Remove system logs? (y/N): " remove_logs
if [[ "\$remove_logs" == "y" || "\$remove_logs" == "Y" ]]; then
    rm -rf "${SYSTEM_DIR}/logs"
fi

echo "Uninstall completed. System directory remains at:"
echo "  ${SYSTEM_DIR}"
echo "Database remains at:"
echo "  /Users/daniel/databases/productivity.db"
EOF
    
    chmod +x "${SYSTEM_DIR}/uninstall.sh"
    log "${GREEN}✓ Uninstaller created${NC}"
}

# Final system test
test_system() {
    log "${BLUE}Testing system installation...${NC}"
    
    # Test Python environment
    source "${PYTHON_ENV}/bin/activate"
    
    # Test database connection
    cd "${SYSTEM_DIR}"
    python3 -c "
from database import JobSearchDatabase
db = JobSearchDatabase()
stats = db.get_statistics()
print('Database test passed')
"
    
    # Test main script
    python3 main.py --status > /dev/null
    
    log "${GREEN}✓ System tests passed${NC}"
}

# Show completion message
show_completion() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Installation Completed Successfully!  ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo ""
    echo -e "1. ${YELLOW}Add your API keys:${NC}"
    echo "   Edit: /Users/daniel/.config/jobsearch/api_keys.json"
    echo ""
    echo -e "2. ${YELLOW}Start the service:${NC}"
    echo "   ./manage_service.sh start"
    echo ""
    echo -e "3. ${YELLOW}Test the system:${NC}"
    echo "   jobsearch --once        # Run job search once"
    echo "   jobsearch --web         # Start web dashboard"
    echo "   jobsearch --status      # Check system status"
    echo ""
    echo -e "4. ${YELLOW}Web Dashboard:${NC}"
    echo "   http://127.0.0.1:8000"
    echo ""
    echo -e "${BLUE}System Directory:${NC} ${SYSTEM_DIR}"
    echo -e "${BLUE}Daily Schedule:${NC} 6:00 AM Central Time"
    echo -e "${BLUE}Log File:${NC} ${LOG_FILE}"
    echo ""
    echo -e "${GREEN}The system will automatically search for jobs daily at 6 AM!${NC}"
    echo ""
}

# Main installation flow
main() {
    log "${BLUE}Starting installation at $(date)${NC}"
    
    check_user
    check_requirements
    install_dependencies
    setup_database
    configure_api_keys
    install_launch_agent
    create_main_launcher
    create_cli_tools
    create_uninstaller
    test_system
    
    show_completion
    
    log "${GREEN}Installation completed successfully at $(date)${NC}"
}

# Run main installation
main