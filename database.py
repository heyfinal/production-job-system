"""
Production Database Schema for Job Search System
Extends Daniel's existing productivity.db with comprehensive job tracking
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class JobSearchDatabase:
    """Production-grade database manager for job search system"""
    
    def __init__(self, db_path: str = "/Users/daniel/databases/productivity.db"):
        self.db_path = db_path
        self.ensure_database_exists()
        self.setup_schema()
        
    def ensure_database_exists(self):
        """Ensure database file and directory exist"""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
        return conn
    
    def setup_schema(self):
        """Create all required tables with production-grade schema"""
        conn = self.get_connection()
        try:
            # Enhanced jobs table with comprehensive tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    salary_currency TEXT DEFAULT 'USD',
                    employment_type TEXT, -- full-time, part-time, contract, internship
                    experience_level TEXT, -- entry, mid, senior, executive
                    description TEXT,
                    requirements TEXT,
                    benefits TEXT,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    source_job_id TEXT, -- Original job ID from source
                    posted_date TIMESTAMP,
                    scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_date TIMESTAMP,
                    match_score REAL DEFAULT 0.0,
                    match_reasons TEXT, -- JSON array of matching criteria
                    status TEXT DEFAULT 'new', -- new, reviewed, applied, rejected, expired
                    priority INTEGER DEFAULT 3, -- 1=high, 2=medium, 3=normal, 4=low
                    remote_friendly BOOLEAN DEFAULT FALSE,
                    visa_sponsorship BOOLEAN DEFAULT FALSE,
                    application_deadline TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    metadata TEXT -- JSON for additional fields
                )
            """)
            
            # Companies table for tracking company information
            conn.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    industry TEXT,
                    size TEXT, -- startup, small, medium, large, enterprise
                    headquarters_location TEXT,
                    website TEXT,
                    description TEXT,
                    is_oil_gas_related BOOLEAN DEFAULT FALSE,
                    is_tech_focused BOOLEAN DEFAULT FALSE,
                    glassdoor_rating REAL,
                    employee_count_min INTEGER,
                    employee_count_max INTEGER,
                    founded_year INTEGER,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Job applications tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    application_method TEXT, -- website, email, linkedin, recruiter
                    cover_letter_used TEXT, -- file path or template name
                    resume_version TEXT,
                    status TEXT DEFAULT 'submitted', -- submitted, acknowledged, interviewing, offered, rejected, withdrawn
                    recruiter_contact TEXT,
                    follow_up_date TIMESTAMP,
                    interview_dates TEXT, -- JSON array of interview dates
                    salary_offered INTEGER,
                    notes TEXT,
                    response_received BOOLEAN DEFAULT FALSE,
                    rejection_reason TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
                )
            """)
            
            # Search queries for tracking what searches are performed
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT NOT NULL,
                    source TEXT NOT NULL, -- indeed, linkedin, rapidapi, etc.
                    location TEXT,
                    remote_filter BOOLEAN DEFAULT FALSE,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    date_posted_filter TEXT, -- today, 3days, week, month
                    results_count INTEGER DEFAULT 0,
                    new_jobs_found INTEGER DEFAULT 0,
                    execution_time_seconds REAL,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Job matching criteria for intelligent scoring
            conn.execute("""
                CREATE TABLE IF NOT EXISTS matching_criteria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    criteria_type TEXT NOT NULL, -- skill_match, location_match, salary_match, etc.
                    criteria_value TEXT,
                    score REAL NOT NULL, -- 0.0 to 1.0
                    weight REAL DEFAULT 1.0,
                    description TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
                )
            """)
            
            # System logs for monitoring and debugging
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL, -- INFO, WARNING, ERROR, CRITICAL
                    module TEXT,
                    message TEXT NOT NULL,
                    details TEXT, -- JSON for structured data
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Configuration table for system settings
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    description TEXT,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create performance indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_scraped_date ON jobs(scraped_date)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_match_score ON jobs(match_score DESC)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_salary ON jobs(salary_max DESC)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source)",
                "CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id)",
                "CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status)",
                "CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)",
                "CREATE INDEX IF NOT EXISTS idx_search_queries_date ON search_queries(created_date)",
                "CREATE INDEX IF NOT EXISTS idx_matching_criteria_job_id ON matching_criteria(job_id)",
                "CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp)",
            ]
            
            for index_sql in indexes:
                conn.execute(index_sql)
            
            # Insert default configuration
            default_configs = [
                ('last_search_run', '1970-01-01 00:00:00', 'Timestamp of last successful job search'),
                ('total_jobs_found', '0', 'Total number of jobs found since system start'),
                ('total_applications_sent', '0', 'Total number of applications submitted'),
                ('search_frequency_hours', '24', 'How often to run job searches (in hours)'),
                ('max_jobs_per_search', '100', 'Maximum number of jobs to process per search'),
                ('min_match_score', '0.3', 'Minimum match score to consider a job relevant'),
            ]
            
            for key, value, description in default_configs:
                conn.execute("""
                    INSERT OR IGNORE INTO system_config (key, value, description) 
                    VALUES (?, ?, ?)
                """, (key, value, description))
            
            conn.commit()
            logger.info("Database schema setup completed successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Database schema setup failed: {e}")
            raise
        finally:
            conn.close()
    
    def store_job(self, job_data: Dict) -> int:
        """Store a single job with proper validation and deduplication"""
        conn = self.get_connection()
        try:
            # Check if job already exists by URL
            existing = conn.execute(
                "SELECT id FROM jobs WHERE url = ?", (job_data['url'],)
            ).fetchone()
            
            if existing:
                # Update existing job with new information
                job_id = existing['id']
                conn.execute("""
                    UPDATE jobs SET
                        title = ?, company = ?, location = ?, salary_min = ?, salary_max = ?,
                        employment_type = ?, experience_level = ?, description = ?,
                        requirements = ?, benefits = ?, source = ?, source_job_id = ?,
                        posted_date = ?, updated_date = CURRENT_TIMESTAMP,
                        expires_date = ?, match_score = ?, match_reasons = ?,
                        remote_friendly = ?, visa_sponsorship = ?, application_deadline = ?,
                        metadata = ?
                    WHERE id = ?
                """, (
                    job_data['title'], job_data['company'], job_data.get('location'),
                    job_data.get('salary_min'), job_data.get('salary_max'),
                    job_data.get('employment_type'), job_data.get('experience_level'),
                    job_data.get('description'), job_data.get('requirements'),
                    job_data.get('benefits'), job_data['source'], job_data.get('source_job_id'),
                    job_data.get('posted_date'), job_data.get('expires_date'),
                    job_data.get('match_score', 0.0), 
                    json.dumps(job_data.get('match_reasons', [])),
                    job_data.get('remote_friendly', False),
                    job_data.get('visa_sponsorship', False),
                    job_data.get('application_deadline'),
                    json.dumps(job_data.get('metadata', {})),
                    job_id
                ))
            else:
                # Insert new job
                cursor = conn.execute("""
                    INSERT INTO jobs (
                        title, company, location, salary_min, salary_max, employment_type,
                        experience_level, description, requirements, benefits, url, source,
                        source_job_id, posted_date, expires_date, match_score, match_reasons,
                        remote_friendly, visa_sponsorship, application_deadline, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_data['title'], job_data['company'], job_data.get('location'),
                    job_data.get('salary_min'), job_data.get('salary_max'),
                    job_data.get('employment_type'), job_data.get('experience_level'),
                    job_data.get('description'), job_data.get('requirements'),
                    job_data.get('benefits'), job_data['url'], job_data['source'],
                    job_data.get('source_job_id'), job_data.get('posted_date'),
                    job_data.get('expires_date'), job_data.get('match_score', 0.0),
                    json.dumps(job_data.get('match_reasons', [])),
                    job_data.get('remote_friendly', False),
                    job_data.get('visa_sponsorship', False),
                    job_data.get('application_deadline'),
                    json.dumps(job_data.get('metadata', {}))
                ))
                job_id = cursor.lastrowid
            
            # Store or update company information
            self._store_company_info(conn, job_data['company'], job_data)
            
            conn.commit()
            return job_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to store job: {e}")
            raise
        finally:
            conn.close()
    
    def _store_company_info(self, conn: sqlite3.Connection, company_name: str, job_data: Dict):
        """Store or update company information"""
        # Check if company exists
        existing = conn.execute(
            "SELECT id FROM companies WHERE name = ?", (company_name,)
        ).fetchone()
        
        if not existing:
            # Extract company info from job data if available
            conn.execute("""
                INSERT INTO companies (name, is_oil_gas_related, is_tech_focused)
                VALUES (?, ?, ?)
            """, (
                company_name,
                self._is_oil_gas_company(company_name),
                self._is_tech_company(company_name)
            ))
    
    def _is_oil_gas_company(self, company_name: str) -> bool:
        """Determine if company is oil & gas related"""
        oil_gas_keywords = [
            'energy', 'oil', 'gas', 'petroleum', 'drilling', 'exploration',
            'chevron', 'exxon', 'bp', 'shell', 'conocophillips', 'marathon',
            'devon', 'chesapeake', 'continental', 'pioneer', 'oxy', 'kinder morgan'
        ]
        company_lower = company_name.lower()
        return any(keyword in company_lower for keyword in oil_gas_keywords)
    
    def _is_tech_company(self, company_name: str) -> bool:
        """Determine if company is tech-focused"""
        tech_keywords = [
            'tech', 'software', 'digital', 'data', 'analytics', 'automation',
            'microsoft', 'google', 'amazon', 'apple', 'meta', 'ibm', 'oracle'
        ]
        company_lower = company_name.lower()
        return any(keyword in company_lower for keyword in tech_keywords)
    
    def get_recent_jobs(self, days: int = 7, min_score: float = 0.3) -> List[Dict]:
        """Get recent jobs above minimum match score"""
        conn = self.get_connection()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor = conn.execute("""
                SELECT j.*, c.industry, c.size as company_size, c.glassdoor_rating
                FROM jobs j
                LEFT JOIN companies c ON j.company = c.name
                WHERE j.scraped_date >= ? 
                AND j.match_score >= ?
                AND j.is_active = TRUE
                ORDER BY j.match_score DESC, j.salary_max DESC
            """, (cutoff_date, min_score))
            
            jobs = []
            for row in cursor.fetchall():
                job = dict(row)
                # Parse JSON fields
                if job['match_reasons']:
                    job['match_reasons'] = json.loads(job['match_reasons'])
                if job['metadata']:
                    job['metadata'] = json.loads(job['metadata'])
                jobs.append(job)
            
            return jobs
            
        finally:
            conn.close()
    
    def record_search_query(self, query_data: Dict):
        """Record search query execution for monitoring"""
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO search_queries (
                    query_text, source, location, remote_filter, salary_min, salary_max,
                    date_posted_filter, results_count, new_jobs_found, execution_time_seconds,
                    success, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                query_data['query_text'], query_data['source'], query_data.get('location'),
                query_data.get('remote_filter', False), query_data.get('salary_min'),
                query_data.get('salary_max'), query_data.get('date_posted_filter'),
                query_data.get('results_count', 0), query_data.get('new_jobs_found', 0),
                query_data.get('execution_time_seconds'), query_data.get('success', True),
                query_data.get('error_message')
            ))
            conn.commit()
        finally:
            conn.close()
    
    def log_system_event(self, level: str, module: str, message: str, details: Dict = None):
        """Log system events for monitoring"""
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO system_logs (level, module, message, details)
                VALUES (?, ?, ?, ?)
            """, (level, module, message, json.dumps(details) if details else None))
            conn.commit()
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict:
        """Get comprehensive system statistics"""
        conn = self.get_connection()
        try:
            stats = {}
            
            # Job statistics
            job_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN status = 'new' THEN 1 END) as new_jobs,
                    COUNT(CASE WHEN status = 'applied' THEN 1 END) as applied_jobs,
                    COUNT(CASE WHEN scraped_date >= date('now', '-7 days') THEN 1 END) as jobs_last_week,
                    AVG(match_score) as avg_match_score,
                    MAX(salary_max) as highest_salary
                FROM jobs WHERE is_active = TRUE
            """).fetchone()
            stats.update(dict(job_stats))
            
            # Application statistics
            app_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_applications,
                    COUNT(CASE WHEN status = 'submitted' THEN 1 END) as pending_applications,
                    COUNT(CASE WHEN status = 'interviewing' THEN 1 END) as interviewing,
                    COUNT(CASE WHEN status = 'offered' THEN 1 END) as offers_received
                FROM applications
            """).fetchone()
            stats.update(dict(app_stats))
            
            return stats
            
        finally:
            conn.close()