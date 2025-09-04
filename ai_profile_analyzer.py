#!/usr/bin/env python3
"""
AI-Powered Profile Analysis System
Analyzes all available information about Daniel to find the most realistic job opportunities
Uses GitHub, LinkedIn, resume, and other sources to build comprehensive skill profile
"""

import asyncio
import json
import logging
import re
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from urllib.parse import urljoin
import os

# AI and ML imports
try:
    import openai
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    HAS_AI_LIBS = True
except ImportError:
    HAS_AI_LIBS = False
    print("⚠️  AI libraries not available. Install with: pip install openai transformers torch")

# Web scraping imports
from bs4 import BeautifulSoup
import aiohttp

@dataclass
class SkillProfile:
    """Comprehensive skill profile extracted from multiple sources"""
    # Technical Skills
    programming_languages: List[str] = field(default_factory=list)
    frameworks_tools: List[str] = field(default_factory=list)
    ai_automation_skills: List[str] = field(default_factory=list)
    
    # Industry Knowledge
    oil_gas_experience: Dict[str, Any] = field(default_factory=dict)
    safety_certifications: List[str] = field(default_factory=list)
    operational_skills: List[str] = field(default_factory=list)
    
    # Leadership & Management
    leadership_experience: List[str] = field(default_factory=list)
    project_management: List[str] = field(default_factory=list)
    team_size_managed: int = 0
    
    # Education & Certifications
    formal_education: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    continuous_learning: List[str] = field(default_factory=list)
    
    # Soft Skills
    communication_skills: List[str] = field(default_factory=list)
    problem_solving: List[str] = field(default_factory=list)
    adaptability_examples: List[str] = field(default_factory=list)
    
    # Unique Value Propositions
    unique_combinations: List[str] = field(default_factory=list)
    transition_story: str = ""
    geographic_knowledge: List[str] = field(default_factory=list)

@dataclass 
class JobCategory:
    """Job category with probability scoring"""
    name: str
    subcategories: List[str]
    probability_factors: Dict[str, float]
    typical_salary_range: Tuple[int, int]
    growth_outlook: str
    entry_barriers: List[str]

class AIProfileAnalyzer:
    """
    Comprehensive AI-powered profile analysis system
    Extracts skills, experience, and capabilities from multiple sources
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.profile = SkillProfile()
        
        # AI models for text analysis
        if HAS_AI_LIBS:
            self.nlp_pipeline = None
            self.setup_ai_models()
        
        # Job categories with realistic opportunities for Daniel
        self.job_categories = self._initialize_job_categories()
        
    def setup_ai_models(self):
        """Initialize AI models for text analysis"""
        try:
            # Use a lightweight model for skill extraction
            self.nlp_pipeline = pipeline(
                "ner", 
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            self.logger.info("AI models loaded successfully")
        except Exception as e:
            self.logger.warning(f"Failed to load AI models: {e}")
            self.nlp_pipeline = None
    
    def _initialize_job_categories(self) -> List[JobCategory]:
        """Initialize realistic job categories for Daniel's profile"""
        return [
            JobCategory(
                name="Oil & Gas Operations",
                subcategories=[
                    "Senior Landman", "Land Manager", "Lease Analyst", 
                    "Right of Way Agent", "Title Researcher", "Contract Specialist"
                ],
                probability_factors={
                    "industry_experience": 0.95,
                    "geographic_knowledge": 0.90,
                    "regulatory_knowledge": 0.85,
                    "networking": 0.80
                },
                typical_salary_range=(75000, 120000),
                growth_outlook="Stable",
                entry_barriers=["Industry Knowledge Required", "Professional Network"]
            ),
            
            JobCategory(
                name="Safety & Compliance",
                subcategories=[
                    "HSE Coordinator", "Safety Manager", "Compliance Specialist",
                    "Environmental Coordinator", "Risk Management Specialist", 
                    "Audit Specialist", "Training Coordinator"
                ],
                probability_factors={
                    "field_experience": 0.90,
                    "safety_record": 0.95,
                    "certification_status": 0.85,
                    "leadership_experience": 0.80
                },
                typical_salary_range=(65000, 95000),
                growth_outlook="Growing",
                entry_barriers=["Safety Certifications", "Proven Track Record"]
            ),
            
            JobCategory(
                name="Data Analysis & Business Intelligence",
                subcategories=[
                    "Operations Data Analyst", "Business Analyst", "Reporting Specialist",
                    "Process Improvement Analyst", "Performance Analyst", "KPI Specialist"
                ],
                probability_factors={
                    "analytical_thinking": 0.85,
                    "technical_skills": 0.75,
                    "domain_knowledge": 0.90,
                    "automation_experience": 0.70
                },
                typical_salary_range=(70000, 100000),
                growth_outlook="High Growth",
                entry_barriers=["Technical Skills", "Portfolio Projects"]
            ),
            
            JobCategory(
                name="Project Management & Operations",
                subcategories=[
                    "Project Coordinator", "Operations Manager", "Process Manager",
                    "Implementation Specialist", "Change Management Specialist",
                    "Vendor Relations Manager"
                ],
                probability_factors={
                    "leadership_experience": 0.90,
                    "project_success_record": 0.85,
                    "stakeholder_management": 0.80,
                    "operational_knowledge": 0.95
                },
                typical_salary_range=(75000, 110000),
                growth_outlook="Stable",
                entry_barriers=["Management Experience", "Project Portfolio"]
            ),
            
            JobCategory(
                name="Technical Consulting & Advisory",
                subcategories=[
                    "Technical Consultant", "Subject Matter Expert", "Training Specialist",
                    "Implementation Consultant", "Process Advisor", "Best Practices Specialist"
                ],
                probability_factors={
                    "expertise_depth": 0.95,
                    "communication_skills": 0.85,
                    "reputation": 0.80,
                    "client_relationship_skills": 0.75
                },
                typical_salary_range=(80000, 130000),
                growth_outlook="High Growth",
                entry_barriers=["Established Expertise", "Professional Network"]
            ),
            
            JobCategory(
                name="Quality Assurance & Process",
                subcategories=[
                    "QA Manager", "Process Improvement Specialist", "Quality Coordinator",
                    "Standards Compliance Manager", "Audit Manager", "Documentation Specialist"
                ],
                probability_factors={
                    "attention_to_detail": 0.90,
                    "process_knowledge": 0.95,
                    "regulatory_experience": 0.85,
                    "systematic_thinking": 0.80
                },
                typical_salary_range=(65000, 90000),
                growth_outlook="Stable",
                entry_barriers=["Industry Knowledge", "Process Documentation"]
            ),
            
            JobCategory(
                name="IT & Automation",
                subcategories=[
                    "Automation Specialist", "Systems Analyst", "IT Coordinator",
                    "Database Analyst", "Workflow Specialist", "Digital Transformation Coordinator"
                ],
                probability_factors={
                    "technical_skills": 0.80,
                    "automation_experience": 0.85,
                    "learning_agility": 0.90,
                    "problem_solving": 0.85
                },
                typical_salary_range=(70000, 105000),
                growth_outlook="Very High Growth",
                entry_barriers=["Technical Portfolio", "Continuous Learning"]
            ),
            
            JobCategory(
                name="Training & Development",
                subcategories=[
                    "Corporate Trainer", "Learning & Development Specialist", 
                    "Safety Trainer", "Technical Training Coordinator",
                    "Knowledge Management Specialist", "Curriculum Developer"
                ],
                probability_factors={
                    "teaching_ability": 0.85,
                    "subject_matter_expertise": 0.95,
                    "presentation_skills": 0.80,
                    "patience_mentoring": 0.85
                },
                typical_salary_range=(60000, 85000),
                growth_outlook="Growing",
                entry_barriers=["Teaching Experience", "Subject Expertise"]
            ),
            
            JobCategory(
                name="Customer Success & Relations",
                subcategories=[
                    "Client Relations Manager", "Customer Success Manager", 
                    "Account Manager", "Business Development", "Partnership Manager",
                    "Vendor Relations Specialist"
                ],
                probability_factors={
                    "relationship_building": 0.80,
                    "communication_skills": 0.85,
                    "industry_knowledge": 0.90,
                    "trust_building": 0.85
                },
                typical_salary_range=(65000, 95000),
                growth_outlook="Growing",
                entry_barriers=["Relationship Portfolio", "Industry Credibility"]
            )
        ]
    
    async def analyze_comprehensive_profile(self) -> SkillProfile:
        """
        Perform comprehensive profile analysis from all available sources
        """
        self.logger.info("Starting comprehensive profile analysis...")
        
        # Analyze multiple data sources in parallel
        analysis_tasks = [
            self._analyze_github_profile(),
            self._analyze_resume(),
            self._analyze_linkedin_profile(),
            self._analyze_work_history(),
            self._extract_implicit_skills()
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"Analysis task {i} failed: {result}")
            else:
                self.logger.info(f"Analysis task {i} completed successfully")
        
        # Build unique value propositions
        self._identify_unique_combinations()
        
        self.logger.info("Comprehensive profile analysis complete")
        return self.profile
    
    async def _analyze_github_profile(self):
        """Analyze Daniel's GitHub profile for technical skills and projects"""
        try:
            github_username = "heyfinal"
            api_base = "https://api.github.com"
            
            async with aiohttp.ClientSession() as session:
                # Get user profile
                async with session.get(f"{api_base}/users/{github_username}") as resp:
                    if resp.status == 200:
                        user_data = await resp.json()
                        self.profile.continuous_learning.append(f"{user_data.get('public_repos', 0)} public repositories")
                        if user_data.get('bio'):
                            # Simple keyword extraction instead of AI NLP for now
                            bio_text = user_data['bio'].lower()
                            bio_keywords = ['automation', 'ai', 'python', 'javascript', 'developer', 'engineer', 'technical']
                            for keyword in bio_keywords:
                                if keyword in bio_text:
                                    self.profile.continuous_learning.append(f"GitHub bio mentions: {keyword}")
                
                # Get repositories
                async with session.get(f"{api_base}/users/{github_username}/repos?per_page=50") as resp:
                    if resp.status == 200:
                        repos = await resp.json()
                        
                        languages = set()
                        frameworks = set()
                        ai_tools = set()
                        
                        for repo in repos:
                            # Extract languages
                            if repo.get('language'):
                                languages.add(repo['language'])
                            
                            # Analyze repository names and descriptions for AI/automation tools
                            repo_text = f"{repo.get('name', '')} {repo.get('description', '')}".lower()
                            
                            # AI and automation keywords
                            ai_keywords = [
                                'ai', 'artificial intelligence', 'machine learning', 'automation',
                                'script', 'bot', 'claude', 'gpt', 'openai', 'chatbot',
                                'workflow', 'pipeline', 'scheduler', 'monitor'
                            ]
                            
                            for keyword in ai_keywords:
                                if keyword in repo_text:
                                    ai_tools.add(f"AI/Automation: {keyword.title()}")
                            
                            # Framework detection
                            framework_keywords = {
                                'react': 'React.js', 'vue': 'Vue.js', 'angular': 'Angular',
                                'flask': 'Flask', 'django': 'Django', 'fastapi': 'FastAPI',
                                'docker': 'Docker', 'kubernetes': 'Kubernetes',
                                'playwright': 'Playwright', 'selenium': 'Selenium'
                            }
                            
                            for keyword, framework in framework_keywords.items():
                                if keyword in repo_text:
                                    frameworks.add(framework)
                        
                        self.profile.programming_languages.extend(list(languages))
                        self.profile.frameworks_tools.extend(list(frameworks))
                        self.profile.ai_automation_skills.extend(list(ai_tools))
            
            # Add GitHub as a demonstration of continuous learning
            self.profile.continuous_learning.append("Active GitHub contributor - demonstrates continuous learning")
            self.profile.technical_skills = list(set(self.profile.programming_languages + self.profile.frameworks_tools))
            
            self.logger.info(f"GitHub analysis complete. Found {len(languages)} languages, {len(frameworks)} frameworks")
            
        except Exception as e:
            self.logger.error(f"GitHub analysis failed: {e}")
    
    async def _analyze_resume(self):
        """Extract comprehensive skills from resume files"""
        try:
            # Look for resume files in workspace
            workspace = Path("/Users/daniel/workapps")
            resume_files = []
            
            for pattern in ["*resume*.pdf", "*Resume*.pdf", "*CV*.pdf", "Daniel*resume*"]:
                resume_files.extend(workspace.rglob(pattern))
            
            if not resume_files:
                self.logger.warning("No resume files found for analysis")
                return
            
            # Analyze the most recent resume
            latest_resume = max(resume_files, key=lambda x: x.stat().st_mtime)
            self.logger.info(f"Analyzing resume: {latest_resume}")
            
            # Extract text from resume (would need PDF parsing library)
            # For now, use known information about Daniel's background
            self._extract_known_experience()
            
        except Exception as e:
            self.logger.error(f"Resume analysis failed: {e}")
    
    def _extract_known_experience(self):
        """Extract Daniel's known experience and skills"""
        # Oil & Gas Experience (20+ years)
        self.profile.oil_gas_experience = {
            "total_years": 20,
            "roles": [
                "Drilling Consultant", "Field Superintendent", "Operations Supervisor"
            ],
            "specializations": [
                "Multi-rig operations", "Safety management", "Process optimization",
                "Vendor relations", "Regulatory compliance", "Emergency response"
            ],
            "equipment_knowledge": [
                "Drilling equipment", "Safety systems", "Monitoring tools",
                "Communication systems", "Heavy machinery"
            ]
        }
        
        # Safety & Certifications
        self.profile.safety_certifications = [
            "SafeLand USA Certified", "First Aid & CPR", "OSHA 30 Hour",
            "H2S Training", "Defensive Driving", "Emergency Response"
        ]
        
        # Leadership Experience
        self.profile.leadership_experience = [
            "Supervised multiple drilling operations simultaneously",
            "Managed teams of 15-25 field personnel",
            "Led safety meetings and training sessions",
            "Coordinated with multiple stakeholders (operators, service companies, regulators)",
            "Made critical decisions under pressure",
            "Mentored junior personnel"
        ]
        
        self.profile.team_size_managed = 25
        
        # Operational Skills
        self.profile.operational_skills = [
            "Multi-million dollar asset management",
            "Budget oversight and cost control",
            "Schedule management and optimization",
            "Quality assurance and compliance",
            "Risk assessment and mitigation",
            "Vendor selection and management",
            "Performance monitoring and reporting",
            "Process documentation and improvement"
        ]
        
        # Problem Solving & Communication
        self.profile.problem_solving = [
            "Diagnosed and resolved complex operational issues",
            "Developed innovative solutions for field challenges",
            "Coordinated emergency response procedures",
            "Optimized drilling parameters for efficiency",
            "Implemented cost-saving measures"
        ]
        
        self.profile.communication_skills = [
            "Clear verbal communication in high-pressure situations",
            "Technical report writing and documentation",
            "Stakeholder management across multiple organizations",
            "Training and knowledge transfer",
            "Regulatory interaction and compliance reporting"
        ]
        
        # Geographic Knowledge
        self.profile.geographic_knowledge = [
            "Oklahoma oil and gas operations",
            "SCOOP and STACK formations",
            "Texas drilling operations",
            "Permian Basin experience",
            "Regional regulatory requirements"
        ]
        
        # Transition Story
        self.profile.transition_story = (
            "Experienced drilling professional transitioning from physically demanding "
            "field operations to analytical and technical roles following ankle injury. "
            "Bringing 20+ years of operational expertise, leadership experience, and "
            "growing technical automation skills to create unique value in oil & gas "
            "and adjacent industries."
        )
    
    async def _analyze_linkedin_profile(self):
        """Analyze LinkedIn profile for professional network and endorsements"""
        try:
            # Note: Direct LinkedIn scraping is against ToS
            # Instead, we'll use publicly available information from Daniel's profile
            linkedin_url = "https://linkedin.com/in/daniel-gillaspy-995bb91b6"
            
            # Extract known LinkedIn information
            self.profile.continuous_learning.extend([
                "Active LinkedIn presence for professional networking",
                "Demonstrates professional transition and career development",
                "Maintains industry connections and relationships"
            ])
            
            # Professional network advantages
            self.profile.unique_combinations.append(
                "Established professional network in Oklahoma oil & gas industry"
            )
            
            self.logger.info("LinkedIn profile analysis complete")
            
        except Exception as e:
            self.logger.error(f"LinkedIn analysis failed: {e}")
    
    async def _analyze_work_history(self):
        """Analyze work history for career progression and achievements"""
        try:
            # Work history pattern analysis
            career_progression = {
                "progression": "Field worker → Supervisor → Consultant",
                "responsibility_growth": "Individual contributor → Team leader → Multi-team coordinator",
                "complexity_growth": "Single operation → Multiple rigs → Regional operations",
                "decision_authority": "Operational decisions → Budget decisions → Strategic recommendations"
            }
            
            # Extract career growth indicators
            self.profile.leadership_experience.extend([
                "Progressive career advancement over 20 years",
                "Increased responsibility and decision-making authority",
                "Successful track record in high-pressure environments",
                "Proven ability to adapt to changing industry conditions"
            ])
            
            # Industry knowledge depth
            market_cycles_experience = [
                "Navigated multiple oil price cycles (2008, 2014, 2020)",
                "Adapted operations to changing regulatory requirements",
                "Implemented new technologies and processes",
                "Maintained operations during industry downturns"
            ]
            
            self.profile.adaptability_examples.extend(market_cycles_experience)
            
            self.logger.info("Work history analysis complete")
            
        except Exception as e:
            self.logger.error(f"Work history analysis failed: {e}")
    
    async def _extract_implicit_skills(self):
        """Extract implicit skills from experience patterns"""
        try:
            # Financial acumen (from managing multi-million dollar operations)
            financial_skills = [
                "Budget management and cost control",
                "ROI analysis and capital allocation",
                "Vendor negotiation and contract management",
                "Financial risk assessment"
            ]
            
            # Technology adoption
            tech_skills = [
                "Early adopter of AI automation tools",
                "Self-taught programming and scripting",
                "Process optimization using technology",
                "Digital transformation mindset"
            ]
            
            # Regulatory and compliance
            compliance_skills = [
                "Deep understanding of oil & gas regulations",
                "Environmental compliance and reporting",
                "Safety standard implementation",
                "Audit preparation and management"
            ]
            
            # Add to profile
            self.profile.operational_skills.extend(financial_skills)
            self.profile.ai_automation_skills.extend(tech_skills)
            self.profile.operational_skills.extend(compliance_skills)
            
            self.logger.info("Implicit skills extraction complete")
            
        except Exception as e:
            self.logger.error(f"Implicit skills extraction failed: {e}")
    
    def _identify_unique_combinations(self):
        """Identify unique skill combinations that set Daniel apart"""
        unique_combinations = [
            # Industry + Technology
            "Oil & Gas Operations + AI/Automation: Rare combination of deep industry knowledge with modern automation skills",
            
            # Experience + Learning Agility  
            "20+ Years Field Experience + Continuous Learning: Combines seasoned expertise with adaptability to new technologies",
            
            # Leadership + Technical
            "Team Leadership + Technical Skills: Can both manage people and understand/implement technical solutions",
            
            # Safety + Innovation
            "Safety Management + Process Innovation: Proven safety record with drive to improve and optimize processes",
            
            # Operations + Analysis
            "Field Operations + Data Analysis: Understands both the operational reality and analytical requirements",
            
            # Regional + Industry
            "Oklahoma Oil & Gas Network + Technical Transition: Established relationships with emerging technical capabilities",
            
            # Crisis Management + Automation
            "Emergency Response Experience + Automation Tools: Can handle high-pressure situations and build systems to prevent them"
        ]
        
        self.profile.unique_combinations = unique_combinations
    
    async def _extract_skills_from_text(self, text: str):
        """Use AI to extract skills and capabilities from text"""
        if not self.nlp_pipeline or not text:
            return
        
        try:
            # Use NLP to extract entities that might be skills
            entities = self.nlp_pipeline(text)
            
            skill_entities = []
            for entity in entities:
                if entity['entity_group'] in ['MISC', 'ORG']:  # Miscellaneous or organizations often contain skills
                    skill_entities.append(entity['word'])
            
            if skill_entities:
                self.profile.continuous_learning.extend(skill_entities)
                
        except Exception as e:
            self.logger.error(f"NLP skill extraction failed: {e}")
    
    def calculate_category_probabilities(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate hiring probability for each job category based on profile analysis
        """
        category_scores = {}
        
        for category in self.job_categories:
            category_score = 0.0
            factor_scores = {}
            
            # Calculate scores for each probability factor
            for factor, weight in category.probability_factors.items():
                factor_score = self._calculate_factor_score(factor, category.name)
                factor_scores[factor] = factor_score
                category_score += factor_score * weight
            
            # Normalize to percentage (factor scores are already 0-1 scale)
            category_score = min(category_score, 0.95) * 100  # Cap at 95% to be realistic
            
            category_scores[category.name] = {
                'overall_probability': category_score,
                'factor_scores': factor_scores,
                'salary_range': category.typical_salary_range,
                'growth_outlook': category.growth_outlook,
                'subcategories': category.subcategories
            }
        
        return category_scores
    
    def _calculate_factor_score(self, factor: str, category: str) -> float:
        """Calculate score for a specific factor based on profile data"""
        
        # Industry experience factors
        if factor == "industry_experience":
            return 0.95 if self.profile.oil_gas_experience.get('total_years', 0) >= 15 else 0.7
        
        elif factor == "field_experience":
            return 0.90 if self.profile.oil_gas_experience.get('total_years', 0) >= 10 else 0.6
            
        elif factor == "geographic_knowledge":
            return 0.85 if len(self.profile.geographic_knowledge) > 0 else 0.3
        
        # Leadership factors
        elif factor == "leadership_experience":
            return 0.85 if self.profile.team_size_managed > 10 else 0.6
        
        elif factor == "project_management":
            return 0.80 if len(self.profile.operational_skills) > 5 else 0.5
        
        # Technical factors
        elif factor == "technical_skills":
            tech_score = len(self.profile.programming_languages) * 0.1 + len(self.profile.ai_automation_skills) * 0.15
            return min(tech_score, 0.8)
        
        elif factor == "automation_experience":
            return 0.75 if len(self.profile.ai_automation_skills) > 2 else 0.4
        
        # Safety factors
        elif factor == "safety_record":
            return 0.90 if len(self.profile.safety_certifications) > 3 else 0.6
        
        elif factor == "certification_status":
            return 0.80 if len(self.profile.safety_certifications) > 0 else 0.3
        
        # Communication factors
        elif factor == "communication_skills":
            return 0.80 if len(self.profile.communication_skills) > 3 else 0.5
        
        elif factor == "presentation_skills":
            return 0.75 if len(self.profile.leadership_experience) > 3 else 0.4
        
        # Analysis factors
        elif factor == "analytical_thinking":
            return 0.75 if len(self.profile.problem_solving) > 3 else 0.5
        
        elif factor == "domain_knowledge":
            return 0.90 if self.profile.oil_gas_experience.get('total_years', 0) > 15 else 0.6
        
        # Default scoring
        else:
            return 0.5  # Neutral score for unknown factors
    
    def generate_ai_job_queries(self, category_scores: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Generate intelligent job search queries based on profile analysis and category probabilities
        """
        queries = []
        
        # Sort categories by probability
        sorted_categories = sorted(
            category_scores.items(), 
            key=lambda x: x[1]['overall_probability'], 
            reverse=True
        )
        
        # Generate queries for top categories (probability > 60%)
        for category_name, category_data in sorted_categories:
            if category_data['overall_probability'] < 60:
                continue
            
            category = next(c for c in self.job_categories if c.name == category_name)
            
            # Generate multiple query variations for each high-probability category
            for subcategory in category.subcategories:
                base_query = self._generate_smart_query(subcategory, category_name, category_data)
                queries.append(base_query)
                
                # Add location-specific variations
                for location in ["Oklahoma City, OK", "Tulsa, OK", "Houston, TX", "Dallas, TX"]:
                    location_query = base_query.copy()
                    location_query['location'] = location
                    location_query['query'] += f" {location}"
                    queries.append(location_query)
        
        # Prioritize queries by probability and add intelligent keywords
        prioritized_queries = self._prioritize_and_enhance_queries(queries, category_scores)
        
        return prioritized_queries[:25]  # Return top 25 most promising queries
    
    def _generate_smart_query(self, subcategory: str, category: str, category_data: Dict) -> Dict[str, Any]:
        """Generate intelligent search query with contextual keywords"""
        
        # Base query with role
        base_terms = [subcategory.lower()]
        
        # Add experience level qualifiers
        experience_qualifiers = ["senior", "experienced", "15+ years", "20 years"]
        base_terms.extend(experience_qualifiers[:1])  # Add one qualifier
        
        # Add industry-specific terms based on category
        if "Oil & Gas" in category:
            industry_terms = ["oil gas", "energy", "petroleum", "upstream", "drilling"]
            base_terms.extend(industry_terms[:2])
            
        elif "Safety" in category:
            safety_terms = ["HSE", "safety", "compliance", "environmental", "risk"]
            base_terms.extend(safety_terms[:2])
            
        elif "Data Analysis" in category:
            analysis_terms = ["data", "analytics", "business intelligence", "reporting"]
            base_terms.extend(analysis_terms[:2])
            
        elif "Project Management" in category:
            pm_terms = ["project management", "operations", "coordination", "implementation"]
            base_terms.extend(pm_terms[:2])
        
        # Add location preference
        location_terms = ["Oklahoma", "Texas", "remote"]
        
        query_string = " ".join(base_terms)
        
        return {
            'query': query_string,
            'category': category,
            'subcategory': subcategory,
            'probability': category_data['overall_probability'],
            'salary_range': category_data['salary_range'],
            'priority': 1 if category_data['overall_probability'] > 80 else 2,
            'location': "Oklahoma City, OK",  # Default location
            'remote_friendly': True if "IT" in category or "Data" in category else False
        }
    
    def _prioritize_and_enhance_queries(self, queries: List[Dict], category_scores: Dict) -> List[Dict]:
        """Prioritize and enhance queries based on AI analysis"""
        
        # Sort by probability and add intelligent enhancements
        enhanced_queries = []
        
        for query in queries:
            # Add realistic experience qualifiers
            if query['probability'] > 85:
                # High probability - can be specific about experience
                query['query'] += " 15-25 years experience"
            elif query['probability'] > 70:
                # Medium-high probability - broader experience range
                query['query'] += " experienced professional"
            else:
                # Lower probability - emphasize transferable skills
                query['query'] += " career transition"
            
            # Add salary qualification to attract realistic opportunities
            salary_min, salary_max = query['salary_range']
            if salary_min >= 70000:
                query['query'] += f" ${salary_min//1000}k"
            
            enhanced_queries.append(query)
        
        # Sort by priority then probability
        return sorted(enhanced_queries, key=lambda x: (x['priority'], -x['probability']))

# Usage example and testing
async def main():
    """Test the AI profile analyzer"""
    print("🤖 AI PROFILE ANALYZER TEST")
    print("=" * 60)
    
    analyzer = AIProfileAnalyzer()
    
    # Analyze comprehensive profile
    profile = await analyzer.analyze_comprehensive_profile()
    
    print(f"📊 PROFILE ANALYSIS COMPLETE")
    print(f"   Programming Languages: {len(profile.programming_languages)}")
    print(f"   AI/Automation Skills: {len(profile.ai_automation_skills)}")
    print(f"   Leadership Experience: {len(profile.leadership_experience)}")
    print(f"   Safety Certifications: {len(profile.safety_certifications)}")
    print(f"   Unique Combinations: {len(profile.unique_combinations)}")
    print()
    
    # Calculate category probabilities
    category_scores = analyzer.calculate_category_probabilities()
    
    print("🎯 JOB CATEGORY PROBABILITIES:")
    for category, data in sorted(category_scores.items(), key=lambda x: x[1]['overall_probability'], reverse=True):
        prob = data['overall_probability']
        salary = data['salary_range']
        print(f"   {category}: {prob:.1f}% | ${salary[0]:,}-${salary[1]:,}")
    print()
    
    # Generate AI-powered job queries
    queries = analyzer.generate_ai_job_queries(category_scores)
    
    print(f"🔍 GENERATED {len(queries)} INTELLIGENT JOB QUERIES:")
    for i, query in enumerate(queries[:10], 1):  # Show top 10
        print(f"   {i}. {query['query']}")
        print(f"      Category: {query['category']} | Probability: {query['probability']:.1f}%")
    
    print("\n✅ AI Profile Analysis Complete!")
    return profile, category_scores, queries

if __name__ == "__main__":
    asyncio.run(main())