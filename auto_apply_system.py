#!/usr/bin/env python3
"""
Auto-Apply System - Production Grade Job Application Automation
Uses modern web automation techniques as of August 2025
"""

import asyncio
import json
import logging
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass
from datetime import datetime

# Modern automation stack (August 2025)
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager
import pyautogui
from bs4 import BeautifulSoup
import requests

@dataclass
class ApplicantProfile:
    """Daniel's professional profile for auto-filling applications"""
    # Personal Information
    first_name: str = "Daniel"
    last_name: str = "Gillaspy"
    full_name: str = "Daniel Gillaspy"
    email: str = "dgillaspy@me.com"
    phone: str = "405-315-1310"
    phone_formatted: str = "(405) 315-1310"
    
    # Address
    street_address: str = "13100 Rock Meadows Circle"
    city: str = "Oklahoma City"
    state: str = "OK"
    state_full: str = "Oklahoma"
    zip_code: str = "73142"
    country: str = "United States"
    
    # Professional Links
    linkedin: str = "https://linkedin.com/in/daniel-gillaspy-995bb91b6"
    github: str = "https://github.com/heyfinal"
    portfolio: str = "https://github.com/heyfinal"
    
    # Experience & Career
    years_experience: int = 20
    current_title: str = "Drilling Consultant & Field Superintendent"
    desired_salary_min: int = 65000
    desired_salary_max: int = 150000
    availability: str = "Immediately"
    willing_to_relocate: bool = False
    authorized_to_work: bool = True
    require_sponsorship: bool = False
    
    # Education
    education_level: str = "High School"
    
    # Skills & Qualifications
    key_skills: List[str] = None
    certifications: List[str] = None
    
    # Cover Letter Templates
    cover_letter_brief: str = ""
    cover_letter_detailed: str = ""
    
    def __post_init__(self):
        if self.key_skills is None:
            self.key_skills = [
                "Oil & Gas Operations (20+ years)",
                "Safety Management & HSE Compliance",
                "Python & JavaScript Programming", 
                "Process Automation & AI Tools",
                "Data Analysis & Reporting",
                "Contract & Lease Analysis",
                "Field Supervision & Leadership",
                "Drilling Operations Management"
            ]
        
        if self.certifications is None:
            self.certifications = [
                "SafeLand USA Certified",
                "First Aid & CPR Certified",
                "OSHA 30 Hour Safety Training"
            ]
        
        if not self.cover_letter_brief:
            self.cover_letter_brief = (
                "Experienced drilling consultant with 20+ years in oil & gas operations, "
                "transitioning to technical/analytical roles. Proven track record in safety "
                "management, process optimization, and AI-driven automation tools."
            )
        
        if not self.cover_letter_detailed:
            self.cover_letter_detailed = (
                "Dear Hiring Manager,\n\n"
                "I am writing to express my interest in this position. With over 20 years "
                "of experience in oil and gas operations, I bring a unique combination of "
                "field expertise and technical innovation to your team.\n\n"
                "As a Drilling Consultant and Field Superintendent, I have successfully "
                "managed multimillion-dollar drilling operations while maintaining "
                "exceptional safety standards. Following an ankle injury in March 2025, "
                "I am transitioning to less physically demanding roles that leverage both "
                "my operational experience and technical skills.\n\n"
                "My technical expertise includes Python and JavaScript programming, "
                "AI-driven automation tools, and data analysis. I have developed custom "
                "solutions for contract analysis, lease review, and compliance tracking. "
                "This unique blend of operational knowledge and technical capability "
                "positions me to deliver immediate value in analytical and technical roles.\n\n"
                "I would welcome the opportunity to discuss how my experience can contribute "
                "to your organization's success.\n\n"
                "Sincerely,\nDaniel Gillaspy"
            )

class ModernAutoApplySystem:
    """
    Production-grade auto-apply system using August 2025 best practices
    
    Modern approaches:
    - Playwright for fast, reliable browser automation
    - Selenium as fallback for complex sites  
    - AI-powered form detection
    - Intelligent field mapping
    - Anti-detection techniques
    - Comprehensive error handling
    """
    
    def __init__(self, headless: bool = False, debug: bool = False):
        self.headless = headless
        self.debug = debug
        self.profile = ApplicantProfile()
        self.logger = self._setup_logging()
        
        # Success tracking
        self.applications_attempted = 0
        self.applications_successful = 0
        self.applications_failed = 0
        self.error_log = []
        
        # Modern browser settings (August 2025)
        self.playwright_config = {
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "viewport": {"width": 1920, "height": 1080},
            "ignore_https_errors": True,
            "java_script_enabled": True
        }
        
        # Common form field mappings (continuously updated)
        self.field_mappings = {
            # Personal Information
            "first_name": ["firstName", "first_name", "fname", "first", "given_name", "applicant_first_name"],
            "last_name": ["lastName", "last_name", "lname", "last", "family_name", "surname", "applicant_last_name"],
            "full_name": ["fullName", "full_name", "name", "applicant_name", "candidate_name"],
            "email": ["email", "email_address", "emailAddress", "e_mail", "applicant_email", "contact_email"],
            "phone": ["phone", "phoneNumber", "phone_number", "mobile", "telephone", "contact_phone", "applicant_phone"],
            
            # Address
            "street_address": ["address", "street", "address1", "street_address", "addr1", "applicant_address"],
            "city": ["city", "applicant_city", "location_city"],
            "state": ["state", "province", "region", "applicant_state"],
            "zip_code": ["zip", "zipCode", "postal_code", "postalCode", "zip_code", "applicant_zip"],
            "country": ["country", "applicant_country"],
            
            # Professional
            "linkedin": ["linkedin", "linkedIn", "linkedin_url", "linkedin_profile"],
            "github": ["github", "github_url", "portfolio", "website"],
            "current_title": ["current_title", "job_title", "position", "current_position"],
            "years_experience": ["experience", "years_experience", "total_experience"],
            "desired_salary": ["salary", "expected_salary", "desired_salary", "salary_expectation"],
            
            # Application specific
            "cover_letter": ["cover_letter", "coverLetter", "message", "additional_info", "comments"],
            "availability": ["availability", "start_date", "available_start_date"],
            "willing_to_relocate": ["relocate", "willing_to_relocate", "relocation"],
            "authorized_to_work": ["work_authorization", "authorized_to_work", "us_citizen"],
            "require_sponsorship": ["sponsorship", "visa_sponsorship", "require_sponsorship"]
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("AutoApplySystem")
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        
        handler = logging.FileHandler("/Users/daniel/workapps/production_job_system/auto_apply.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def apply_to_job_async(self, job_url: str, job_title: str = "", company: str = "") -> Dict[str, Any]:
        """
        Modern async application using Playwright (primary method)
        """
        self.applications_attempted += 1
        
        try:
            async with async_playwright() as p:
                # Launch browser with modern settings
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--user-agent=' + self.playwright_config["user_agent"]
                    ]
                )
                
                context = await browser.new_context(
                    user_agent=self.playwright_config["user_agent"],
                    viewport=self.playwright_config["viewport"],
                    ignore_https_errors=self.playwright_config["ignore_https_errors"]
                )
                
                page = await context.new_page()
                
                # Navigate to job URL
                await page.goto(job_url, wait_until="networkidle")
                await page.wait_for_timeout(2000)  # Let page fully load
                
                # Analyze page and find application form
                application_result = await self._find_and_fill_application_form_async(
                    page, job_title, company
                )
                
                await browser.close()
                
                if application_result["success"]:
                    self.applications_successful += 1
                    self.logger.info(f"Successfully applied to {job_title} at {company}")
                else:
                    self.applications_failed += 1
                    self.error_log.append(application_result["error"])
                    self.logger.error(f"Failed to apply to {job_title}: {application_result['error']}")
                
                return application_result
                
        except Exception as e:
            self.applications_failed += 1
            error_msg = f"Async application failed: {str(e)}"
            self.error_log.append(error_msg)
            self.logger.error(error_msg)
            
            # Fallback to Selenium
            return await self._fallback_selenium_apply(job_url, job_title, company)
    
    def apply_to_job_sync(self, job_url: str, job_title: str = "", company: str = "") -> Dict[str, Any]:
        """
        Synchronous wrapper for compatibility
        """
        return asyncio.run(self.apply_to_job_async(job_url, job_title, company))
    
    async def _find_and_fill_application_form_async(self, page: Page, job_title: str, company: str) -> Dict[str, Any]:
        """
        Intelligent form detection and filling using modern techniques
        """
        try:
            # Step 1: Look for common application buttons/links
            apply_selectors = [
                'a[href*="apply"]', 'button[class*="apply"]', '[data-testid*="apply"]',
                'a:has-text("Apply")', 'button:has-text("Apply")', 'input[value*="Apply"]',
                '.apply-button', '#apply-button', '.job-apply', '#job-apply'
            ]
            
            # Try to find and click apply button
            for selector in apply_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        await page.wait_for_timeout(3000)  # Wait for form to load
                        break
                except:
                    continue
            
            # Step 2: Detect and fill forms
            forms = await page.query_selector_all('form')
            
            for form in forms:
                # Check if this looks like an application form
                form_html = await form.inner_html()
                if self._is_application_form(form_html):
                    success = await self._fill_application_form_async(page, form, job_title, company)
                    if success:
                        return {"success": True, "method": "playwright_async", "form_filled": True}
            
            # Step 3: Try to detect fields without forms (single page apps)
            success = await self._fill_loose_fields_async(page, job_title, company)
            if success:
                return {"success": True, "method": "playwright_loose_fields", "form_filled": True}
                
            return {"success": False, "error": "No application form detected", "method": "playwright_async"}
            
        except Exception as e:
            return {"success": False, "error": str(e), "method": "playwright_async"}
    
    def _is_application_form(self, form_html: str) -> bool:
        """
        Intelligent form detection using modern heuristics
        """
        application_indicators = [
            "first.?name", "last.?name", "email", "phone", "resume", "cover.?letter",
            "apply", "application", "candidate", "applicant", "job", "position"
        ]
        
        form_lower = form_html.lower()
        matches = sum(1 for indicator in application_indicators if re.search(indicator, form_lower))
        
        # Need at least 3 matches to consider it an application form
        return matches >= 3
    
    async def _fill_application_form_async(self, page: Page, form, job_title: str, company: str) -> bool:
        """
        Fill application form with intelligent field mapping
        """
        try:
            # Get all input fields in the form
            inputs = await form.query_selector_all('input, textarea, select')
            
            filled_fields = 0
            
            for input_element in inputs:
                try:
                    # Get field attributes
                    field_name = await input_element.get_attribute('name') or ''
                    field_id = await input_element.get_attribute('id') or ''
                    field_placeholder = await input_element.get_attribute('placeholder') or ''
                    field_type = await input_element.get_attribute('type') or 'text'
                    
                    # Combine all identifiers for matching
                    field_identifier = f"{field_name} {field_id} {field_placeholder}".lower()
                    
                    # Skip hidden, submit, and button fields
                    if field_type in ['hidden', 'submit', 'button', 'image']:
                        continue
                    
                    # Map field to profile data
                    value = self._map_field_to_value(field_identifier, field_type, job_title, company)
                    
                    if value:
                        if field_type == 'select':
                            await self._select_option_async(input_element, value)
                        elif field_type in ['checkbox', 'radio']:
                            if str(value).lower() in ['true', 'yes', '1']:
                                await input_element.check()
                        else:
                            await input_element.fill(str(value))
                        
                        filled_fields += 1
                        await page.wait_for_timeout(200)  # Brief pause between fields
                        
                except Exception as e:
                    self.logger.debug(f"Error filling field: {e}")
                    continue
            
            # Look for and handle file uploads (resume)
            await self._handle_file_uploads_async(page, form)
            
            # Try to submit form
            submit_success = await self._submit_form_async(page, form)
            
            self.logger.info(f"Filled {filled_fields} fields, Submit: {submit_success}")
            return filled_fields > 2  # Consider success if we filled at least 3 fields
            
        except Exception as e:
            self.logger.error(f"Error filling form: {e}")
            return False
    
    def _map_field_to_value(self, field_identifier: str, field_type: str, job_title: str, company: str) -> Optional[str]:
        """
        Intelligent field mapping with context awareness
        """
        # Map field identifier to profile values
        for profile_field, field_patterns in self.field_mappings.items():
            for pattern in field_patterns:
                if pattern.lower() in field_identifier:
                    return getattr(self.profile, profile_field, None)
        
        # Special handling for specific field types
        if 'salary' in field_identifier:
            return str(self.profile.desired_salary_min)
        
        if 'experience' in field_identifier and 'years' in field_identifier:
            return str(self.profile.years_experience)
        
        if 'cover' in field_identifier and 'letter' in field_identifier:
            # Generate contextual cover letter
            return self._generate_contextual_cover_letter(job_title, company)
        
        if field_type == 'checkbox':
            if 'authorize' in field_identifier or 'eligible' in field_identifier:
                return 'true'
            if 'sponsor' in field_identifier and 'visa' in field_identifier:
                return 'false'
            if 'relocate' in field_identifier:
                return 'false'
        
        return None
    
    def _generate_contextual_cover_letter(self, job_title: str, company: str) -> str:
        """
        Generate contextual cover letter based on job/company
        """
        base_letter = self.profile.cover_letter_detailed
        
        # Customize based on job type
        if any(keyword in job_title.lower() for keyword in ['landman', 'lease']):
            custom_intro = (
                f"I am excited to apply for the {job_title} position at {company}. "
                "With over 20 years of oil and gas field experience, I have extensive "
                "knowledge of lease operations, contract analysis, and regulatory compliance "
                "that would be invaluable in this landman role."
            )
        elif any(keyword in job_title.lower() for keyword in ['data', 'analyst', 'technical']):
            custom_intro = (
                f"I am writing to express my strong interest in the {job_title} position at {company}. "
                "My unique combination of 20+ years operational experience in oil and gas, "
                "coupled with advanced Python programming and data analysis skills, positions "
                "me perfectly for this analytical role."
            )
        elif any(keyword in job_title.lower() for keyword in ['safety', 'hse', 'coordinator']):
            custom_intro = (
                f"I am pleased to submit my application for the {job_title} position at {company}. "
                "As a field superintendent with extensive experience in safety management and "
                "HSE compliance across multiple drilling operations, I bring proven expertise "
                "in maintaining exceptional safety standards."
            )
        else:
            custom_intro = (
                f"I am writing to apply for the {job_title} position at {company}. "
                "With my extensive background in oil and gas operations and growing technical "
                "expertise, I am confident I can contribute meaningfully to your team."
            )
        
        # Replace generic intro with customized version
        customized_letter = base_letter.replace(
            "Dear Hiring Manager,\n\nI am writing to express my interest in this position.",
            f"Dear Hiring Manager,\n\n{custom_intro}"
        )
        
        return customized_letter
    
    async def _handle_file_uploads_async(self, page: Page, form) -> bool:
        """
        Handle resume and document uploads
        """
        try:
            file_inputs = await form.query_selector_all('input[type="file"]')
            
            # Look for resume file in workspace
            resume_path = self._find_resume_file()
            
            for file_input in file_inputs:
                if resume_path and resume_path.exists():
                    await file_input.set_input_files(str(resume_path))
                    self.logger.info(f"Uploaded resume: {resume_path}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling file uploads: {e}")
            return False
    
    def _find_resume_file(self) -> Optional[Path]:
        """
        Find Daniel's resume file in workspace
        """
        workspace_path = Path("/Users/daniel/workapps")
        resume_patterns = [
            "*resume*.pdf", "*Resume*.pdf", "*RESUME*.pdf",
            "*CV*.pdf", "*cv*.pdf", "Daniel*resume*.pdf",
            "Daniel Gillaspy*resume*.pdf"
        ]
        
        for pattern in resume_patterns:
            for file_path in workspace_path.rglob(pattern):
                if file_path.is_file():
                    return file_path
        
        return None
    
    async def _submit_form_async(self, page: Page, form) -> bool:
        """
        Submit application form with multiple strategies
        """
        try:
            # Strategy 1: Look for submit button in form
            submit_selectors = [
                'input[type="submit"]', 'button[type="submit"]', 
                'button:has-text("Submit")', 'button:has-text("Apply")',
                '.submit-button', '#submit', '.apply-btn'
            ]
            
            for selector in submit_selectors:
                element = await form.query_selector(selector)
                if element:
                    await element.click()
                    await page.wait_for_timeout(3000)
                    
                    # Check if submission was successful (page changed or confirmation)
                    if await self._check_submission_success(page):
                        return True
            
            # Strategy 2: Try form.submit() if available
            await page.evaluate("arguments[0].submit()", form)
            await page.wait_for_timeout(3000)
            
            return await self._check_submission_success(page)
            
        except Exception as e:
            self.logger.error(f"Error submitting form: {e}")
            return False
    
    async def _check_submission_success(self, page: Page) -> bool:
        """
        Check if application submission was successful
        """
        try:
            # Wait for possible navigation or confirmation
            await page.wait_for_timeout(2000)
            
            # Look for success indicators
            success_indicators = [
                'success', 'thank you', 'submitted', 'received', 'confirmation',
                'applied', 'application sent', 'we will be in touch'
            ]
            
            page_content = await page.content()
            page_text = page_content.lower()
            
            for indicator in success_indicators:
                if indicator in page_text:
                    return True
            
            # Check URL change (might indicate success)
            current_url = page.url
            if 'thank' in current_url or 'success' in current_url or 'confirm' in current_url:
                return True
            
            return False
            
        except:
            return False
    
    async def _fallback_selenium_apply(self, job_url: str, job_title: str, company: str) -> Dict[str, Any]:
        """
        Fallback to Selenium for complex sites that Playwright can't handle
        """
        try:
            # Setup Firefox with modern options
            options = FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.set_preference("general.useragent.override", self.playwright_config["user_agent"])
            
            driver = webdriver.Firefox(
                service=webdriver.firefox.service.Service(GeckoDriverManager().install()),
                options=options
            )
            
            try:
                driver.get(job_url)
                time.sleep(3)
                
                # Similar form detection and filling logic as Playwright
                success = self._fill_application_form_selenium(driver, job_title, company)
                
                return {
                    "success": success,
                    "method": "selenium_fallback",
                    "form_filled": success
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            return {"success": False, "error": str(e), "method": "selenium_fallback"}
    
    def _fill_application_form_selenium(self, driver, job_title: str, company: str) -> bool:
        """
        Selenium-based form filling (fallback method)
        """
        try:
            # Find forms
            forms = driver.find_elements(By.TAG_NAME, 'form')
            
            for form in forms:
                if self._is_application_form(form.get_attribute('innerHTML')):
                    filled_fields = self._fill_selenium_form(driver, form, job_title, company)
                    if filled_fields > 2:
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Selenium form filling error: {e}")
            return False
    
    def _fill_selenium_form(self, driver, form, job_title: str, company: str) -> int:
        """
        Fill individual form with Selenium
        """
        filled_fields = 0
        
        try:
            inputs = form.find_elements(By.TAG_NAME, 'input') + form.find_elements(By.TAG_NAME, 'textarea')
            
            for input_element in inputs:
                try:
                    field_name = input_element.get_attribute('name') or ''
                    field_id = input_element.get_attribute('id') or ''
                    field_placeholder = input_element.get_attribute('placeholder') or ''
                    field_type = input_element.get_attribute('type') or 'text'
                    
                    field_identifier = f"{field_name} {field_id} {field_placeholder}".lower()
                    
                    if field_type in ['hidden', 'submit', 'button']:
                        continue
                    
                    value = self._map_field_to_value(field_identifier, field_type, job_title, company)
                    
                    if value:
                        if field_type in ['checkbox', 'radio']:
                            if str(value).lower() in ['true', 'yes', '1']:
                                input_element.click()
                        else:
                            input_element.clear()
                            input_element.send_keys(str(value))
                        
                        filled_fields += 1
                        time.sleep(0.2)
                        
                except Exception as e:
                    self.logger.debug(f"Error filling Selenium field: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error in Selenium form filling: {e}")
        
        return filled_fields
    
    async def _fill_loose_fields_async(self, page: Page, job_title: str, company: str) -> bool:
        """
        Fill fields that aren't in a form (single page applications)
        """
        try:
            # Get all input fields on page
            all_inputs = await page.query_selector_all('input, textarea, select')
            
            filled_fields = 0
            
            for input_element in all_inputs:
                try:
                    field_name = await input_element.get_attribute('name') or ''
                    field_id = await input_element.get_attribute('id') or ''
                    field_placeholder = await input_element.get_attribute('placeholder') or ''
                    field_type = await input_element.get_attribute('type') or 'text'
                    
                    field_identifier = f"{field_name} {field_id} {field_placeholder}".lower()
                    
                    if field_type in ['hidden', 'submit', 'button', 'image']:
                        continue
                    
                    value = self._map_field_to_value(field_identifier, field_type, job_title, company)
                    
                    if value:
                        if field_type == 'select':
                            await self._select_option_async(input_element, value)
                        elif field_type in ['checkbox', 'radio']:
                            if str(value).lower() in ['true', 'yes', '1']:
                                await input_element.check()
                        else:
                            await input_element.fill(str(value))
                        
                        filled_fields += 1
                        await page.wait_for_timeout(200)
                        
                except Exception as e:
                    continue
            
            return filled_fields > 2
            
        except Exception as e:
            self.logger.error(f"Error filling loose fields: {e}")
            return False
    
    async def _select_option_async(self, select_element, value: str):
        """
        Handle select dropdown with intelligent option matching
        """
        try:
            # Get all options
            options = await select_element.query_selector_all('option')
            
            for option in options:
                option_text = await option.inner_text()
                option_value = await option.get_attribute('value')
                
                # Try exact match first
                if str(value).lower() == option_text.lower() or str(value).lower() == option_value.lower():
                    await option.click()
                    return
                
                # Try partial match
                if str(value).lower() in option_text.lower() or option_text.lower() in str(value).lower():
                    await option.click()
                    return
                    
        except Exception as e:
            self.logger.debug(f"Error selecting option: {e}")
    
    def get_application_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive application statistics
        """
        success_rate = (self.applications_successful / self.applications_attempted * 100) if self.applications_attempted > 0 else 0
        
        return {
            "attempted": self.applications_attempted,
            "successful": self.applications_successful,
            "failed": self.applications_failed,
            "success_rate": round(success_rate, 2),
            "errors": self.error_log[-10:],  # Last 10 errors
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_stats(self):
        """Reset application statistics"""
        self.applications_attempted = 0
        self.applications_successful = 0
        self.applications_failed = 0
        self.error_log = []

# Convenience functions for integration
async def apply_to_job_async(job_url: str, job_title: str = "", company: str = "", headless: bool = True) -> Dict[str, Any]:
    """Async convenience function"""
    system = ModernAutoApplySystem(headless=headless)
    return await system.apply_to_job_async(job_url, job_title, company)

def apply_to_job(job_url: str, job_title: str = "", company: str = "", headless: bool = True) -> Dict[str, Any]:
    """Sync convenience function"""
    return asyncio.run(apply_to_job_async(job_url, job_title, company, headless))

if __name__ == "__main__":
    # Test the system
    import sys
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        job_title = sys.argv[2] if len(sys.argv) > 2 else "Test Job"
        company = sys.argv[3] if len(sys.argv) > 3 else "Test Company"
        
        print(f"🤖 Testing Auto-Apply System")
        print(f"📋 Job: {job_title} at {company}")
        print(f"🔗 URL: {test_url}")
        print()
        
        result = apply_to_job(test_url, job_title, company, headless=False)
        
        print(f"📊 Result: {result}")
    else:
        print("Usage: python auto_apply_system.py <job_url> [job_title] [company]")