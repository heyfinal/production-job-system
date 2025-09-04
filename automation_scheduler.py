"""
Production Automation Scheduler for Daily Job Search System
Runs at 6am daily and manages comprehensive job search workflow
"""

import asyncio
import logging
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, List, Optional
import json
import subprocess
import schedule
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import JobSearchDatabase
from job_aggregator import RealJobAggregator, JobSearchQuery
from intelligent_matcher import IntelligentJobMatcher, CandidateProfile
# from web_dashboard import create_daily_report  # Temporarily disabled due to syntax error

logger = logging.getLogger(__name__)

class ProductionJobScheduler:
    """Production-grade job search automation scheduler"""
    
    def __init__(self, config_path: str = "/Users/daniel/workapps/production_job_system/config.json"):
        self.config = self._load_config(config_path)
        self.db = JobSearchDatabase()
        self.scheduler = AsyncIOScheduler()
        self.candidate_profile = CandidateProfile()
        self.matcher = IntelligentJobMatcher(self.candidate_profile)
        
        # Performance tracking
        self.search_stats = {
            'last_run': None,
            'total_jobs_found': 0,
            'new_jobs_today': 0,
            'high_match_jobs': 0,
            'errors': []
        }
        
    def _load_config(self, config_path: str) -> Dict:
        """Load system configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Config file not found, using production defaults")
            return {
                "search_schedule": {
                    "daily_time": "06:00",
                    "timezone": "America/Chicago",
                    "retry_attempts": 3,
                    "retry_delay_minutes": 30
                },
                "search_queries": [
                    {"keywords": "Landman oil gas", "location": "Oklahoma City, OK"},
                    {"keywords": "Data Analyst energy", "location": "Oklahoma City, OK"}, 
                    {"keywords": "IT Specialist automation", "location": "Oklahoma City, OK"},
                    {"keywords": "Safety Coordinator oil gas", "location": "Oklahoma City, OK"},
                    {"keywords": "Operations Analyst energy", "location": "Oklahoma City, OK"},
                    {"keywords": "Technical Consultant", "location": "Oklahoma City, OK", "remote": True},
                    {"keywords": "Process Automation Engineer", "location": "Oklahoma City, OK", "remote": True},
                    {"keywords": "Python Developer remote", "location": "Oklahoma City, OK", "remote": True}
                ],
                "notification_settings": {
                    "email_enabled": True,
                    "email_address": "dgillaspy@me.com",
                    "slack_enabled": True,
                    "minimum_match_score": 0.6,
                    "daily_summary": True
                },
                "performance_limits": {
                    "max_jobs_per_search": 50,
                    "max_total_daily_jobs": 200,
                    "max_execution_time_minutes": 30,
                    "api_rate_limit_delay": 1.0
                },
                "api_keys": {
                    "rapidapi_key": None,  # User must provide
                    "serpapi_key": None,   # Optional
                    "smtp_password": None  # For email notifications
                }
            }
    
    def start_scheduler(self):
        """Start the production job scheduler"""
        logger.info("Starting production job search scheduler...")
        
        # Schedule daily job search at 6 AM Central Time
        self.scheduler.add_job(
            self._run_daily_job_search,
            trigger=CronTrigger(
                hour=6, 
                minute=0,
                timezone=self.config["search_schedule"]["timezone"]
            ),
            id='daily_job_search',
            max_instances=1,
            coalesce=True,
            misfire_grace_time=1800  # 30 minutes grace period
        )
        
        # Schedule hourly health check
        self.scheduler.add_job(
            self._health_check,
            trigger=CronTrigger(minute=0),  # Every hour on the hour
            id='hourly_health_check',
            max_instances=1
        )
        
        # Schedule weekly cleanup
        self.scheduler.add_job(
            self._weekly_cleanup,
            trigger=CronTrigger(day_of_week=0, hour=2),  # Sundays at 2 AM
            id='weekly_cleanup'
        )
        
        # Start scheduler
        self.scheduler.start()
        logger.info("Job scheduler started successfully")
    
    async def _run_daily_job_search(self):
        """Main daily job search execution with comprehensive error handling"""
        start_time = datetime.now()
        logger.info("=== Starting Daily Job Search ===")
        
        try:
            # Initialize search statistics
            self.search_stats = {
                'start_time': start_time.isoformat(),
                'total_jobs_found': 0,
                'new_jobs_today': 0,
                'high_match_jobs': 0,
                'errors': [],
                'search_queries_executed': 0,
                'sources_contacted': set(),
                'processing_time': 0
            }
            
            # Check API key availability
            if not self.config["api_keys"]["rapidapi_key"]:
                logger.warning("RapidAPI key not configured - limited search capabilities")
            
            # Initialize job aggregator
            aggregator = RealJobAggregator(self.config["api_keys"])
            
            # Execute search queries in parallel batches to manage load
            all_found_jobs = []
            query_batch_size = 3  # Process 3 queries at a time
            
            search_queries = [
                JobSearchQuery(
                    keywords=q["keywords"],
                    location=q["location"],
                    remote=q.get("remote", False),
                    salary_min=self.candidate_profile.salary_range[0],
                    salary_max=self.candidate_profile.salary_range[1]
                ) 
                for q in self.config["search_queries"]
            ]
            
            # Process queries in batches
            for i in range(0, len(search_queries), query_batch_size):
                batch = search_queries[i:i + query_batch_size]
                logger.info(f"Processing query batch {i//query_batch_size + 1}")
                
                # Execute batch
                batch_tasks = [aggregator.search_all_sources(query) for query in batch]
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        error_msg = f"Query failed: {batch[j].keywords} - {result}"
                        logger.error(error_msg)
                        self.search_stats['errors'].append(error_msg)
                    else:
                        all_found_jobs.extend(result)
                        self.search_stats['search_queries_executed'] += 1
                
                # Rate limiting between batches
                await asyncio.sleep(self.config["performance_limits"]["api_rate_limit_delay"])
            
            logger.info(f"Found {len(all_found_jobs)} total raw jobs")
            
            # Process and score jobs
            processed_jobs = await self._process_and_score_jobs(all_found_jobs)
            
            # Store jobs in database
            new_jobs_count = await self._store_jobs(processed_jobs)
            
            # Generate daily report
            report_path = await self._generate_daily_report()
            
            # Send notifications
            await self._send_notifications(new_jobs_count, report_path)
            
            # Update statistics
            end_time = datetime.now()
            self.search_stats['processing_time'] = (end_time - start_time).total_seconds()
            self.search_stats['total_jobs_found'] = len(all_found_jobs)
            self.search_stats['new_jobs_today'] = new_jobs_count
            
            # Log completion
            logger.info(f"=== Daily Job Search Complete ===")
            logger.info(f"Total jobs found: {len(all_found_jobs)}")
            logger.info(f"New jobs stored: {new_jobs_count}")
            logger.info(f"Processing time: {self.search_stats['processing_time']:.1f} seconds")
            
            # Update system configuration
            self._update_system_stats()
            
        except Exception as e:
            logger.error(f"Daily job search failed: {e}")
            self.search_stats['errors'].append(f"Critical failure: {e}")
            
            # Retry logic
            retry_count = getattr(self._run_daily_job_search, '_retry_count', 0)
            max_retries = self.config["search_schedule"]["retry_attempts"]
            
            if retry_count < max_retries:
                retry_count += 1
                self._run_daily_job_search._retry_count = retry_count
                
                retry_delay = self.config["search_schedule"]["retry_delay_minutes"]
                logger.info(f"Scheduling retry {retry_count}/{max_retries} in {retry_delay} minutes")
                
                self.scheduler.add_job(
                    self._run_daily_job_search,
                    'date',
                    run_date=datetime.now() + timedelta(minutes=retry_delay),
                    id=f'retry_job_search_{retry_count}',
                    max_instances=1
                )
            else:
                logger.error("Max retries exceeded - sending failure notification")
                await self._send_failure_notification(str(e))
    
    async def _process_and_score_jobs(self, raw_jobs: List[Dict]) -> List[Dict]:
        """Process and score jobs with intelligent matching"""
        logger.info(f"Processing and scoring {len(raw_jobs)} jobs...")
        
        processed_jobs = []
        high_match_count = 0
        
        for job in raw_jobs:
            try:
                # Calculate match score
                match_score, match_reasons = self.matcher.calculate_match_score(job)
                
                # Add scoring information
                job['match_score'] = match_score
                job['match_reasons'] = match_reasons
                
                # Filter by minimum score
                min_score = self.config["notification_settings"]["minimum_match_score"]
                if match_score >= min_score:
                    processed_jobs.append(job)
                    
                    if match_score >= 0.8:
                        high_match_count += 1
                
            except Exception as e:
                logger.warning(f"Error processing job: {e}")
                continue
        
        self.search_stats['high_match_jobs'] = high_match_count
        logger.info(f"Processed {len(processed_jobs)} jobs above minimum score threshold")
        logger.info(f"Found {high_match_count} high-match jobs (>80% score)")
        
        return processed_jobs
    
    async def _store_jobs(self, jobs: List[Dict]) -> int:
        """Store jobs in database and return count of new jobs"""
        new_jobs_count = 0
        
        for job in jobs:
            try:
                # Store job (database handles deduplication)
                job_id = self.db.store_job(job)
                
                if job_id:  # New job was inserted
                    new_jobs_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to store job: {e}")
                continue
        
        return new_jobs_count
    
    async def _generate_daily_report(self) -> str:
        """Generate HTML daily report"""
        try:
            # Get recent jobs from database
            recent_jobs = self.db.get_recent_jobs(days=1)
            
            # Generate report HTML
            report_path = "/Users/daniel/workapps/production_job_system/daily_report.html"
            
            with open(report_path, 'w') as f:
                html_content = create_daily_report(
                    jobs=recent_jobs,
                    stats=self.search_stats,
                    candidate_profile=self.candidate_profile
                )
                f.write(html_content)
            
            logger.info(f"Daily report generated: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
            return None
    
    async def _send_notifications(self, new_jobs_count: int, report_path: str):
        """Send email and Slack notifications"""
        
        # Email notification
        if self.config["notification_settings"]["email_enabled"]:
            await self._send_email_notification(new_jobs_count, report_path)
        
        # Slack notification
        if self.config["notification_settings"]["slack_enabled"]:
            await self._send_slack_notification(new_jobs_count)
    
    async def _send_email_notification(self, new_jobs_count: int, report_path: str):
        """Send email notification with daily report"""
        try:
            email_address = self.config["notification_settings"]["email_address"]
            smtp_password = self.config["api_keys"].get("smtp_password")
            
            if not smtp_password:
                logger.warning("SMTP password not configured - skipping email")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['To'] = email_address
            msg['Subject'] = f"Daily Job Search Report - {new_jobs_count} New Opportunities"
            
            # Email body
            body = f"""
Daily Job Search Complete!

Summary:
- New jobs found today: {new_jobs_count}
- High-match jobs (>80%): {self.search_stats.get('high_match_jobs', 0)}
- Total processing time: {self.search_stats.get('processing_time', 0):.1f} seconds
- Search queries executed: {self.search_stats.get('search_queries_executed', 0)}

Top Job Matches:
{self._format_top_jobs_for_email()}

View full report: {report_path}

Best regards,
Your Automated Job Search System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML report if it exists
            if report_path and Path(report_path).exists():
                with open(report_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="daily_job_report_{datetime.now().strftime("%Y%m%d")}.html"'
                    )
                    msg.attach(part)
            
            # Send email
            server = smtplib.SMTP('smtp.icloud.com', 587)  # iCloud SMTP for @me.com
            server.starttls()
            server.login(email_address, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info("Email notification sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_slack_notification(self, new_jobs_count: int):
        """Send Slack notification using MCP slack server"""
        try:
            # This would integrate with the existing Slack MCP server
            message = f"""
🎯 **Daily Job Search Complete!**

📊 **Results:**
• New jobs found: {new_jobs_count}
• High-match jobs: {self.search_stats.get('high_match_jobs', 0)}
• Processing time: {self.search_stats.get('processing_time', 0):.1f}s

🔍 **Sources searched:** {len(self.search_stats.get('sources_contacted', set()))}
📈 **Success rate:** {((self.search_stats.get('search_queries_executed', 0) - len(self.search_stats.get('errors', []))) / max(self.search_stats.get('search_queries_executed', 1), 1) * 100):.1f}%

View full report at: /Users/daniel/workapps/production_job_system/daily_report.html
            """
            
            # Use subprocess to call Claude Code with slack MCP integration
            subprocess.run([
                'echo', message, '|', 'claude', '--mcp-server', 'slack', '--send-message'
            ], shell=True, capture_output=True)
            
            logger.info("Slack notification sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_failure_notification(self, error_message: str):
        """Send failure notification when job search completely fails"""
        try:
            if self.config["notification_settings"]["email_enabled"]:
                email_address = self.config["notification_settings"]["email_address"]
                smtp_password = self.config["api_keys"].get("smtp_password")
                
                if smtp_password:
                    msg = MIMEText(f"""
ALERT: Daily Job Search Failed

The automated job search system encountered a critical failure:

Error: {error_message}

Timestamp: {datetime.now().isoformat()}
Max retries exceeded: {self.config["search_schedule"]["retry_attempts"]}

Please check the system logs and restart the service if necessary.

System Location: /Users/daniel/workapps/production_job_system/
                    """)
                    
                    msg['Subject'] = "🚨 Job Search System Failure Alert"
                    msg['From'] = email_address
                    msg['To'] = email_address
                    
                    server = smtplib.SMTP('smtp.icloud.com', 587)
                    server.starttls()
                    server.login(email_address, smtp_password)
                    server.send_message(msg)
                    server.quit()
                    
                    logger.info("Failure notification sent")
                    
        except Exception as e:
            logger.error(f"Failed to send failure notification: {e}")
    
    def _format_top_jobs_for_email(self) -> str:
        """Format top job matches for email body"""
        try:
            recent_jobs = self.db.get_recent_jobs(days=1)
            if not recent_jobs:
                return "No new jobs found today."
            
            # Sort by match score and take top 5
            top_jobs = sorted(recent_jobs, key=lambda x: x.get('match_score', 0), reverse=True)[:5]
            
            formatted_jobs = []
            for job in top_jobs:
                score = job.get('match_score', 0) * 100
                salary = ""
                if job.get('salary_min') and job.get('salary_max'):
                    salary = f" | ${job['salary_min']:,} - ${job['salary_max']:,}"
                
                formatted_jobs.append(
                    f"• {job.get('title', 'N/A')} at {job.get('company', 'N/A')} ({score:.0f}% match){salary}"
                )
            
            return "\n".join(formatted_jobs)
            
        except Exception as e:
            logger.error(f"Error formatting top jobs: {e}")
            return "Error formatting job list"
    
    async def _health_check(self):
        """Hourly system health check"""
        try:
            # Check database connectivity
            stats = self.db.get_statistics()
            
            # Check disk space
            import shutil
            total, used, free = shutil.disk_usage("/Users/daniel/workapps")
            free_gb = free / (1024**3)
            
            # Log health status
            if free_gb < 1:  # Less than 1GB free
                logger.warning(f"Low disk space: {free_gb:.1f}GB remaining")
            
            # Log system events
            self.db.log_system_event(
                level="INFO",
                module="scheduler",
                message="Health check completed",
                details={
                    "free_disk_gb": free_gb,
                    "total_jobs": stats.get('total_jobs', 0),
                    "scheduler_running": self.scheduler.running
                }
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.db.log_system_event(
                level="ERROR",
                module="scheduler",
                message="Health check failed",
                details={"error": str(e)}
            )
    
    async def _weekly_cleanup(self):
        """Weekly maintenance and cleanup"""
        try:
            logger.info("Starting weekly maintenance...")
            
            # Archive old jobs (older than 90 days)
            conn = self.db.get_connection()
            archived_count = conn.execute("""
                UPDATE jobs 
                SET is_active = FALSE 
                WHERE scraped_date < date('now', '-90 days') 
                AND is_active = TRUE
            """).rowcount
            conn.commit()
            conn.close()
            
            # Clean up old log entries (older than 30 days)
            conn = self.db.get_connection()
            logs_deleted = conn.execute("""
                DELETE FROM system_logs 
                WHERE timestamp < datetime('now', '-30 days')
            """).rowcount
            conn.commit()
            conn.close()
            
            # Vacuum database for performance
            conn = self.db.get_connection()
            conn.execute("VACUUM")
            conn.close()
            
            logger.info(f"Weekly cleanup complete: {archived_count} jobs archived, {logs_deleted} logs deleted")
            
        except Exception as e:
            logger.error(f"Weekly cleanup failed: {e}")
    
    def _update_system_stats(self):
        """Update system configuration with latest statistics"""
        try:
            # Update system config table
            conn = self.db.get_connection()
            
            updates = [
                ('last_search_run', datetime.now().isoformat()),
                ('total_jobs_found', str(self.search_stats['total_jobs_found'])),
            ]
            
            for key, value in updates:
                conn.execute("""
                    INSERT OR REPLACE INTO system_config (key, value, updated_date)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, value))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update system stats: {e}")
    
    def stop_scheduler(self):
        """Stop the scheduler gracefully"""
        logger.info("Stopping job scheduler...")
        self.scheduler.shutdown(wait=True)
        logger.info("Job scheduler stopped")

# Main execution function
async def main():
    """Main function to run the production job scheduler"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/Users/daniel/workapps/production_job_system/scheduler.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create and start scheduler
    scheduler = ProductionJobScheduler()
    scheduler.start_scheduler()
    
    try:
        # Keep the scheduler running
        while True:
            await asyncio.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        scheduler.stop_scheduler()

if __name__ == "__main__":
    asyncio.run(main())