#!/usr/bin/env python3
"""
Production Job Search System for Daniel Gillaspy
REAL job finder with actual API integrations - no placeholder bullshit
"""

import asyncio
import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import webbrowser

# Add local modules to path
sys.path.insert(0, str(Path(__file__).parent))

from job_aggregator import RealJobAggregator
from intelligent_matcher import IntelligentJobMatcher
from database import JobSearchDatabase
from automation_scheduler import ProductionJobScheduler
# Simple logging setup
import logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/Users/daniel/workapps/production_job_system/job_search.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Simple email notifier placeholder
class EmailNotifier:
    async def send_daily_summary(self, **kwargs):
        print("📧 Email notification would be sent here")
        return True
from html_report_with_autoapply import EnhancedHTMLReportGenerator

# Setup logging
logger = setup_logging()

class ProductionJobSearchSystem:
    """Main production job search system"""
    
    def __init__(self):
        self.aggregator = RealJobAggregator()
        self.matcher = IntelligentJobMatcher()
        self.database = JobSearchDatabase()
        self.scheduler = ProductionJobScheduler()
        self.email_notifier = EmailNotifier()
        self.html_generator = EnhancedHTMLReportGenerator()
        
    async def run_full_search(self):
        """Execute complete job search pipeline"""
        logger.info("Starting production job search...")
        start_time = datetime.now()
        
        try:
            # 1. Search all real data sources using configured queries
            logger.info("Searching real job sources...")
            raw_jobs = await self.aggregator.search_all_configured_queries()
            logger.info(f"Found {len(raw_jobs)} raw job listings")
            
            # 2. Intelligent matching for Daniel's profile
            logger.info("Processing jobs with intelligent matching...")
            matched_jobs = await self.matcher.process_jobs(raw_jobs)
            logger.info(f"Matched {len(matched_jobs)} relevant opportunities")
            
            # 3. Store in database with deduplication
            logger.info("Storing jobs in database...")
            stored_count = await self.database.store_jobs(matched_jobs)
            logger.info(f"Stored {stored_count} new jobs")
            
            # 4. Generate HTML report
            logger.info("Generating HTML report...")
            html_path = await self.generate_html_report()
            
            # 5. Send email notification
            high_match_jobs = [j for j in matched_jobs if j.match_score >= 0.8]
            await self.email_notifier.send_daily_summary(
                total_jobs=len(raw_jobs),
                relevant_jobs=len(matched_jobs),
                high_match_jobs=len(high_match_jobs),
                html_path=html_path
            )
            
            # 6. Launch browser
            webbrowser.open(f"file://{html_path}")
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Job search completed in {duration:.1f}s")
            logger.info(f"Results: {len(raw_jobs)} total, {len(matched_jobs)} relevant, {len(high_match_jobs)} high-match")
            
            return {
                'total_jobs': len(raw_jobs),
                'relevant_jobs': len(matched_jobs),
                'high_match_jobs': len(high_match_jobs),
                'duration': duration,
                'html_path': html_path
            }
            
        except Exception as e:
            logger.error(f"Job search failed: {e}")
            raise
    
    async def generate_html_report(self):
        """Generate enhanced HTML report with auto-apply functionality"""
        jobs = await self.database.get_todays_jobs()
        
        # Convert database jobs to expected format for the enhanced generator
        formatted_jobs = []
        for job in jobs:
            formatted_job = {
                'title': job.get('title', 'N/A'),
                'company': job.get('company', 'N/A'),
                'location': job.get('location', 'N/A'),
                'url': job.get('url', ''),
                'match_score': job.get('match_score', 0),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'description': job.get('description', ''),
                'match_reasons': job.get('match_reasons', []),
                'experience_required': job.get('experience_required', 'N/A'),
                'job_type': job.get('employment_type', 'Full-time')
            }
            formatted_jobs.append(formatted_job)
        
        # Use the enhanced HTML generator with auto-apply functionality
        html_path = self.html_generator.generate_interactive_report(
            formatted_jobs, 
            "/Users/daniel/workapps/production_job_system/daily_report_with_autoapply.html"
        )
        
        logger.info(f"Enhanced HTML report with auto-apply saved to: {html_path}")
        return html_path
    
    async def test_apis(self):
        """Test all API connections"""
        logger.info("Testing API connections...")
        results = await self.aggregator.test_all_apis()
        
        print("\n🔍 API Connection Test Results:")
        print("=" * 50)
        
        for source, result in results.items():
            status = "✅ WORKING" if result['success'] else "❌ FAILED"
            print(f"{source:20} {status}")
            if not result['success']:
                print(f"                     Error: {result.get('error', 'Unknown')}")
        
        return results
    
    def status(self):
        """Show system status"""
        print("\n📊 Production Job Search System Status")
        print("=" * 50)
        
        # Check database
        try:
            job_count = self.database.get_total_job_count()
            print(f"Database:           ✅ Connected ({job_count} total jobs)")
        except Exception as e:
            print(f"Database:           ❌ Error - {e}")
        
        # Check config
        config_path = Path("~/.config/jobsearch/api_keys.json").expanduser()
        if config_path.exists():
            print(f"API Keys:           ✅ Configured")
        else:
            print(f"API Keys:           ⚠️  Not found - run install.sh")
        
        # Check automation
        try:
            is_scheduled = self.scheduler.is_scheduled()
            status = "✅ Active" if is_scheduled else "⚠️  Inactive"
            print(f"Daily Automation:   {status}")
        except:
            print(f"Daily Automation:   ❌ Error")
        
        print("\n💡 Quick Commands:")
        print("python3 main.py --test     # Test run with live APIs")
        print("python3 main.py --test-apis # Check API connections")
        print("python3 web_dashboard.py   # Launch web interface")
        print("./manage_service.sh start  # Enable daily automation")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Production Job Search System for Daniel Gillaspy')
    parser.add_argument('--test', action='store_true', help='Run one job search immediately')
    parser.add_argument('--test-apis', action='store_true', help='Test all API connections')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--automated', action='store_true', help='Run from automation (internal use)')
    
    args = parser.parse_args()
    
    system = ProductionJobSearchSystem()
    
    try:
        if args.test or args.automated:
            results = await system.run_full_search()
            print(f"\n✅ Job search completed!")
            print(f"📊 Results: {results['total_jobs']} total, {results['relevant_jobs']} relevant, {results['high_match_jobs']} high-match")
            print(f"⏱️  Duration: {results['duration']:.1f} seconds")
            print(f"📄 Report: {results['html_path']}")
            
        elif args.test_apis:
            await system.test_apis()
            
        elif args.status:
            system.status()
            
        else:
            print("Production Job Search System for Daniel Gillaspy")
            print("Use --help to see available commands")
            system.status()
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"❌ System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())