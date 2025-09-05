"""
Intelligent Job Matching Algorithm for Daniel Gillaspy
Specifically designed for oil & gas to tech transition profile
"""

import re
import math
import logging
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class CandidateProfile:
    """Daniel's specific professional profile"""
    name: str = "Daniel Gillaspy"
    years_experience: int = 20
    primary_industries: List[str] = None
    technical_skills: List[str] = None
    operational_skills: List[str] = None
    location: str = "Oklahoma City, OK"
    github_profile: str = "github.com/heyfinal"
    transition_context: str = "oil_gas_to_tech"
    physical_limitations: bool = True  # Post-ankle surgery
    salary_range: Tuple[int, int] = (65000, 150000)
    remote_preference: str = "hybrid"  # remote, hybrid, onsite
    
    def __post_init__(self):
        if self.primary_industries is None:
            self.primary_industries = [
                "Oil & Gas", "Energy", "Petroleum", "Drilling", "Operations", 
                "Field Services", "Well Services", "Production"
            ]
        
        if self.technical_skills is None:
            self.technical_skills = [
                "Python", "JavaScript", "AppleScript", "Bash", "Shell Scripting",
                "AI Automation", "Data Analysis", "Process Automation",
                "System Integration", "API Development", "Database Management",
                "Git", "GitHub", "macOS", "Linux", "Network Monitoring",
                "Data Extraction", "Report Generation", "Workflow Automation"
            ]
        
        if self.operational_skills is None:
            self.operational_skills = [
                "Drilling Operations", "Field Supervision", "Multi-rig Management",
                "Safety Management", "Contract Analysis", "Lease Review",
                "Compliance Tracking", "Cost Management", "Risk Assessment",
                "Operations Management", "Team Leadership", "Project Management",
                "Regulatory Compliance", "Asset Management", "Performance Optimization",
                "Quality Control", "Vendor Management", "Emergency Response"
            ]


class IntelligentJobMatcher:
    """Advanced job matching algorithm tailored for Daniel's profile"""
    
    def __init__(self, candidate_profile: CandidateProfile):
        self.profile = candidate_profile
        self.skill_synonyms = self._build_skill_synonyms()
        self.industry_bridge_keywords = self._build_industry_bridges()
        self.role_evolution_map = self._build_role_evolution_map()
        
    def calculate_match_score(self, job: Dict) -> Tuple[float, List[str]]:
        """Calculate comprehensive match score with reasoning"""
        
        # Initialize scoring components
        scores = {
            'technical_skills': 0.0,
            'industry_experience': 0.0,
            'role_transition': 0.0,
            'location_fit': 0.0,
            'salary_fit': 0.0,
            'remote_compatibility': 0.0,
            'company_fit': 0.0,
            'experience_level': 0.0,
            'growth_potential': 0.0
        }
        
        reasons = []
        
        # 1. Technical Skills Match (25% weight)
        tech_score, tech_reasons = self._score_technical_skills(job)
        scores['technical_skills'] = tech_score
        reasons.extend(tech_reasons)
        
        # 2. Industry Experience Relevance (20% weight)  
        industry_score, industry_reasons = self._score_industry_experience(job)
        scores['industry_experience'] = industry_score
        reasons.extend(industry_reasons)
        
        # 3. Role Transition Logic (20% weight)
        transition_score, transition_reasons = self._score_role_transition(job)
        scores['role_transition'] = transition_score
        reasons.extend(transition_reasons)
        
        # 4. Location & Remote Fit (10% weight)
        location_score, location_reasons = self._score_location_fit(job)
        scores['location_fit'] = location_score
        reasons.extend(location_reasons)
        
        # 5. Salary Alignment (10% weight)
        salary_score, salary_reasons = self._score_salary_fit(job)
        scores['salary_fit'] = salary_score
        reasons.extend(salary_reasons)
        
        # 6. Remote Work Compatibility (5% weight) 
        remote_score, remote_reasons = self._score_remote_compatibility(job)
        scores['remote_compatibility'] = remote_score
        reasons.extend(remote_reasons)
        
        # 7. Company Fit (5% weight)
        company_score, company_reasons = self._score_company_fit(job)
        scores['company_fit'] = company_score
        reasons.extend(company_reasons)
        
        # 8. Experience Level Match (3% weight)
        exp_score, exp_reasons = self._score_experience_level(job)
        scores['experience_level'] = exp_score
        reasons.extend(exp_reasons)
        
        # 9. Growth Potential (2% weight)
        growth_score, growth_reasons = self._score_growth_potential(job)
        scores['growth_potential'] = growth_score
        reasons.extend(growth_reasons)
        
        # Calculate weighted final score
        weights = {
            'technical_skills': 0.25,
            'industry_experience': 0.20,
            'role_transition': 0.20,
            'location_fit': 0.10,
            'salary_fit': 0.10,
            'remote_compatibility': 0.05,
            'company_fit': 0.05,
            'experience_level': 0.03,
            'growth_potential': 0.02
        }
        
        final_score = sum(scores[key] * weights[key] for key in scores)
        
        # Apply bonus/penalty adjustments
        final_score, bonus_reasons = self._apply_bonuses_penalties(job, final_score)
        reasons.extend(bonus_reasons)
        
        # Cap score at 1.0
        final_score = min(final_score, 1.0)
        
        logger.debug(f"Job match score: {final_score:.3f} for '{job.get('title')}' at {job.get('company')}")
        
        return final_score, reasons
    
    def _score_technical_skills(self, job: Dict) -> Tuple[float, List[str]]:
        """Score technical skills match"""
        job_text = self._get_job_text(job).lower()
        matched_skills = []
        reasons = []
        
        # Check each technical skill
        for skill in self.profile.technical_skills:
            skill_variations = self.skill_synonyms.get(skill.lower(), [skill.lower()])
            
            for variation in skill_variations:
                if variation in job_text:
                    matched_skills.append(skill)
                    reasons.append(f"Technical skill match: {skill}")
                    break
        
        # Calculate score based on percentage of skills matched
        if self.profile.technical_skills:
            score = len(matched_skills) / len(self.profile.technical_skills)
        else:
            score = 0.0
        
        # Bonus for high-value skills
        high_value_skills = ['python', 'automation', 'data analysis', 'api', 'database']
        high_value_matches = [skill for skill in matched_skills if skill.lower() in high_value_skills]
        
        if high_value_matches:
            score += 0.2  # 20% bonus
            reasons.append(f"High-value skills matched: {', '.join(high_value_matches)}")
        
        return min(score, 1.0), reasons
    
    def _score_industry_experience(self, job: Dict) -> Tuple[float, List[str]]:
        """Score relevance of oil & gas industry experience"""
        job_text = self._get_job_text(job).lower()
        company_name = job.get('company', '').lower()
        reasons = []
        score = 0.0
        
        # Direct industry match (highest score)
        oil_gas_keywords = [
            'oil', 'gas', 'petroleum', 'energy', 'drilling', 'upstream', 'downstream',
            'refinery', 'pipeline', 'well', 'reservoir', 'exploration', 'production'
        ]
        
        industry_matches = [kw for kw in oil_gas_keywords if kw in job_text or kw in company_name]
        
        if industry_matches:
            score = 0.9
            reasons.append(f"Direct O&G industry match: {', '.join(industry_matches)}")
        
        # Energy sector (related industry)
        elif any(kw in job_text or kw in company_name for kw in ['energy', 'utility', 'power', 'renewable']):
            score = 0.7
            reasons.append("Energy sector alignment with O&G background")
        
        # Industrial/Manufacturing (transferable)
        elif any(kw in job_text for kw in ['industrial', 'manufacturing', 'operations', 'plant', 'facility']):
            score = 0.5
            reasons.append("Industrial operations experience transferable")
        
        # Technology roles that value operational experience
        elif any(kw in job_text for kw in ['operational', 'field', 'technical', 'systems']):
            score = 0.4
            reasons.append("Operational expertise valued in technical role")
        
        # Bridge keywords that connect industries
        bridge_matches = [kw for kw in self.industry_bridge_keywords if kw in job_text]
        if bridge_matches:
            score = max(score, 0.6)
            reasons.append(f"Industry bridge concepts: {', '.join(bridge_matches)}")
        
        return score, reasons
    
    def _score_role_transition(self, job: Dict) -> Tuple[float, List[str]]:
        """Score how well the role fits transition from Drilling Consultant to target roles"""
        job_title = job.get('title', '').lower()
        job_text = self._get_job_text(job).lower()
        reasons = []
        
        # Check against role evolution map
        for source_role, target_roles in self.role_evolution_map.items():
            for target_role, keywords in target_roles.items():
                if any(kw in job_title for kw in keywords['title_keywords']):
                    # Check if job description matches
                    desc_matches = sum(1 for kw in keywords['description_keywords'] if kw in job_text)
                    
                    if desc_matches >= 2:  # At least 2 description keywords match
                        reasons.append(f"Role evolution match: Drilling Consultant → {target_role}")
                        return keywords['score'], reasons
        
        # Specific high-value transitions for Daniel
        if 'landman' in job_title:
            if any(kw in job_text for kw in ['lease', 'contract', 'mineral', 'rights']):
                reasons.append("Perfect transition: Field operations to Landman role")
                return 0.95, reasons
        
        if 'data analyst' in job_title:
            if any(kw in job_text for kw in ['operational', 'field', 'drilling', 'production']):
                reasons.append("Strong fit: Operations experience + data analysis")
                return 0.85, reasons
        
        if 'safety' in job_title:
            reasons.append("Natural fit: 20 years field safety experience")
            return 0.90, reasons
        
        if 'automation' in job_title or 'automation' in job_text:
            reasons.append("Direct match: AI automation experience")
            return 0.80, reasons
        
        return 0.3, ["General role transition potential"]  # Base score for any role
    
    def _score_location_fit(self, job: Dict) -> Tuple[float, List[str]]:
        """Score location compatibility"""
        location = job.get('location', '').lower()
        reasons = []
        
        # Perfect matches
        if any(city in location for city in ['oklahoma city', 'okc', 'edmond', 'norman']):
            reasons.append("Perfect location match: Oklahoma City area")
            return 1.0, reasons
        
        # Oklahoma state
        elif 'oklahoma' in location or 'ok' in location:
            reasons.append("Good location: Oklahoma state")
            return 0.8, reasons
        
        # Remote work
        elif job.get('remote_friendly') or any(kw in location for kw in ['remote', 'anywhere', 'virtual']):
            reasons.append("Remote work option available")
            return 0.9, reasons
        
        # Neighboring states (reasonable commute/relocation)
        elif any(state in location for state in ['texas', 'kansas', 'arkansas', 'colorado']):
            reasons.append("Regional location - possible relocation")
            return 0.4, reasons
        
        # Major energy hubs
        elif any(city in location for city in ['houston', 'dallas', 'denver', 'midland']):
            reasons.append("Major energy hub - worth considering")
            return 0.6, reasons
        
        return 0.2, ["Location requires relocation"]
    
    def _score_salary_fit(self, job: Dict) -> Tuple[float, List[str]]:
        """Score salary alignment with Daniel's range"""
        salary_min = job.get('salary_min')
        salary_max = job.get('salary_max')
        reasons = []
        
        target_min, target_max = self.profile.salary_range
        
        if not salary_min and not salary_max:
            return 0.5, ["Salary not specified"]
        
        # Use provided range or estimate
        job_min = salary_min or (salary_max * 0.8 if salary_max else target_min)
        job_max = salary_max or (salary_min * 1.3 if salary_min else target_max)
        
        # Calculate overlap with target range
        overlap_min = max(job_min, target_min)
        overlap_max = min(job_max, target_max)
        
        if overlap_min <= overlap_max:
            # Calculate percentage of overlap
            overlap_size = overlap_max - overlap_min
            target_range_size = target_max - target_min
            overlap_ratio = overlap_size / target_range_size
            
            reasons.append(f"Salary range overlap: ${overlap_min:,} - ${overlap_max:,}")
            return min(overlap_ratio * 1.2, 1.0), reasons
        
        # Check if job salary is above target range (good problem to have)
        elif job_min > target_max:
            reasons.append(f"Salary above target range: ${job_min:,}+")
            return 1.0, reasons
        
        # Job salary below target range
        else:
            gap = target_min - job_max
            if gap <= 10000:  # Within $10k
                reasons.append("Salary slightly below target but negotiable")
                return 0.6, reasons
            else:
                reasons.append(f"Salary significantly below target (${gap:,} gap)")
                return 0.2, reasons
    
    def _score_remote_compatibility(self, job: Dict) -> Tuple[float, List[str]]:
        """Score remote work compatibility (important post-surgery)"""
        job_text = self._get_job_text(job).lower()
        location = job.get('location', '').lower()
        reasons = []
        
        # Explicit remote work
        if (job.get('remote_friendly') or 
            any(kw in job_text for kw in ['remote', 'work from home', 'telecommute', 'virtual']) or
            any(kw in location for kw in ['remote', 'anywhere'])):
            reasons.append("Remote work explicitly available")
            return 1.0, reasons
        
        # Hybrid work indicators
        elif any(kw in job_text for kw in ['hybrid', 'flexible', 'home office', 'flexible schedule']):
            reasons.append("Hybrid/flexible work arrangement")
            return 0.8, reasons
        
        # Roles that are typically remote-friendly
        title = job.get('title', '').lower()
        if any(kw in title for kw in ['analyst', 'developer', 'consultant', 'coordinator', 'data']):
            reasons.append("Role type typically supports remote work")
            return 0.6, reasons
        
        # Office-based role
        elif any(kw in job_text for kw in ['on-site', 'office', 'in-person', 'facility']):
            reasons.append("Office-based position")
            return 0.3, reasons
        
        return 0.4, ["Remote work flexibility unclear"]
    
    def _score_company_fit(self, job: Dict) -> Tuple[float, List[str]]:
        """Score company culture and size fit"""
        company = job.get('company', '').lower()
        job_text = self._get_job_text(job).lower()
        reasons = []
        score = 0.5  # Base score
        
        # Oil & gas companies (cultural fit)
        oil_gas_companies = [
            'chesapeake', 'devon', 'continental', 'marathon', 'phillips 66',
            'conocophillips', 'exxon', 'chevron', 'bp', 'shell', 'oxy'
        ]
        
        if any(comp in company for comp in oil_gas_companies):
            score = 0.9
            reasons.append("Oil & gas company - strong cultural fit")
        
        # Energy/utility companies
        elif any(comp in company for comp in ['energy', 'gas', 'electric', 'utility', 'power']):
            score = 0.7
            reasons.append("Energy sector company - good cultural alignment")
        
        # Technology companies that value operational experience
        elif any(comp in company for comp in ['tech', 'software', 'data', 'analytics']):
            score = 0.6
            reasons.append("Technology company - values automation skills")
        
        # Company size indicators (mid-size preferred for versatility)
        if any(kw in job_text for kw in ['small team', 'growing company', 'startup']):
            score += 0.1
            reasons.append("Smaller company - values versatile experience")
        
        return min(score, 1.0), reasons
    
    def _score_experience_level(self, job: Dict) -> Tuple[float, List[str]]:
        """Score experience level match"""
        job_text = self._get_job_text(job).lower()
        title = job.get('title', '').lower()
        reasons = []
        
        # Senior level roles (best fit for 20+ years experience)
        if any(kw in title for kw in ['senior', 'sr.', 'lead', 'principal', 'manager', 'supervisor']):
            reasons.append("Senior level role matches 20+ years experience")
            return 0.9, reasons
        
        # Mid-level roles (acceptable for career transition)
        elif any(kw in title for kw in ['specialist', 'analyst', 'coordinator', 'consultant']):
            reasons.append("Mid-level role appropriate for career transition")
            return 0.7, reasons
        
        # Entry level (underutilizes experience but possible for career change)
        elif any(kw in title for kw in ['junior', 'entry', 'associate', 'trainee']):
            reasons.append("Entry level role - may underutilize experience")
            return 0.3, reasons
        
        # Check for experience requirements in description
        if '20+ years' in job_text or 'twenty years' in job_text:
            reasons.append("Experience requirement matches background exactly")
            return 1.0, reasons
        elif '15+ years' in job_text or '10+ years' in job_text:
            reasons.append("Experience requirement aligns with background")
            return 0.8, reasons
        
        return 0.6, ["Experience level requirements unclear"]
    
    def _score_growth_potential(self, job: Dict) -> Tuple[float, List[str]]:
        """Score potential for career growth"""
        job_text = self._get_job_text(job).lower()
        reasons = []
        
        # Growth indicators
        growth_keywords = [
            'career development', 'advancement', 'growth', 'leadership',
            'training', 'certification', 'education', 'mentor', 'promotion'
        ]
        
        matches = [kw for kw in growth_keywords if kw in job_text]
        
        if len(matches) >= 3:
            reasons.append(f"Strong growth indicators: {', '.join(matches[:3])}")
            return 0.9, reasons
        elif len(matches) >= 1:
            reasons.append(f"Growth potential mentioned: {', '.join(matches)}")
            return 0.6, reasons
        
        return 0.4, ["Growth potential unclear"]
    
    def _apply_bonuses_penalties(self, job: Dict, base_score: float) -> Tuple[float, List[str]]:
        """Apply final bonuses and penalties"""
        adjustments = []
        final_score = base_score
        
        # BONUSES
        
        # Perfect storm: Oil & gas + tech role
        if ('oil' in job.get('company', '').lower() or 'energy' in job.get('company', '').lower()):
            if any(kw in self._get_job_text(job).lower() for kw in ['data', 'automation', 'analyst', 'tech']):
                final_score += 0.15
                adjustments.append("BONUS: Oil & gas industry + technical role combination")
        
        # GitHub/portfolio value bonus
        if any(kw in self._get_job_text(job).lower() for kw in ['github', 'portfolio', 'coding', 'programming']):
            final_score += 0.10
            adjustments.append("BONUS: Values GitHub portfolio and coding skills")
        
        # Oklahoma City local company bonus
        if any(comp in job.get('company', '').lower() for comp in [
            'chesapeake', 'devon', 'continental', 'oxy', 'sandridge'
        ]):
            final_score += 0.05
            adjustments.append("BONUS: Major Oklahoma City employer")
        
        # PENALTIES
        
        # Physical demands penalty (post-ankle surgery)
        physical_keywords = ['field work', 'physical', 'travel', 'outdoor', 'lifting', 'standing']
        if any(kw in self._get_job_text(job).lower() for kw in physical_keywords):
            final_score -= 0.20
            adjustments.append("PENALTY: Physical demands incompatible with ankle recovery")
        
        # Overqualification penalty for very junior roles
        if any(kw in job.get('title', '').lower() for kw in ['intern', 'trainee', 'entry-level']):
            final_score -= 0.15
            adjustments.append("PENALTY: Role significantly below experience level")
        
        # MAJOR overqualification penalty for executive/senior roles beyond reach
        job_title_lower = job.get('title', '').lower()
        job_text_lower = self._get_job_text(job).lower()
        
        # Positions that would be overqualification for someone transitioning from field work
        overqualified_keywords = [
            'vice president', 'vp ', 'executive director', 'chief', 'ceo', 'cfo', 'cto',
            'senior director', 'managing director', 'general manager', 'division manager',
            'regional manager', 'senior business analyst', 'principal analyst',
            'senior consultant', 'principal consultant', 'senior manager'
        ]
        
        if any(kw in job_title_lower for kw in overqualified_keywords):
            final_score -= 0.40  # Heavy penalty
            adjustments.append("MAJOR PENALTY: Executive/senior role - overqualification for field-to-tech transition")
        
        # High salary roles that typically require MBA/advanced degrees
        if job.get('salary_max', 0) > 200000:
            # Check if it's a realistic high-paying technical role vs executive role
            if not any(tech_kw in job_text_lower for tech_kw in ['python', 'automation', 'technical', 'data', 'programming']):
                final_score -= 0.35  # Heavy penalty for high-salary non-technical roles
                adjustments.append("MAJOR PENALTY: High-salary executive role inappropriate for experience level")
        
        # MBA/advanced degree requirement penalty (Daniel doesn't have MBA)
        if any(kw in job_text_lower for kw in ['mba required', 'masters required', 'phd required', 'advanced degree required']):
            final_score -= 0.25
            adjustments.append("PENALTY: Advanced degree requirement not met")
        
        # Security clearance requirement penalty (hard to get)
        if any(kw in self._get_job_text(job).lower() for kw in ['clearance', 'security clearance', 'classified']):
            final_score -= 0.10
            adjustments.append("PENALTY: Security clearance requirement")
        
        return final_score, adjustments
    
    def _get_job_text(self, job: Dict) -> str:
        """Get combined text from job for analysis"""
        parts = [
            job.get('title', ''),
            job.get('description', ''),
            job.get('requirements', ''),
            job.get('benefits', ''),
        ]
        
        # Handle requirements and benefits as lists or strings
        text_parts = []
        for part in parts:
            if isinstance(part, list):
                text_parts.extend(str(item) for item in part)
            elif part:
                text_parts.append(str(part))
        
        return ' '.join(text_parts)
    
    def _build_skill_synonyms(self) -> Dict[str, List[str]]:
        """Build skill synonyms for better matching"""
        return {
            'python': ['python', 'py', 'django', 'flask', 'pandas', 'numpy'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'react', 'vue'],
            'automation': ['automation', 'automated', 'scripting', 'workflow', 'process automation'],
            'data analysis': ['data analysis', 'analytics', 'data analytics', 'business intelligence', 'bi'],
            'database': ['database', 'sql', 'mysql', 'postgresql', 'sqlite', 'mongodb'],
            'api': ['api', 'rest', 'json', 'web services', 'integration'],
            'git': ['git', 'github', 'version control', 'source control', 'gitlab'],
            'linux': ['linux', 'unix', 'bash', 'shell', 'command line'],
            'network monitoring': ['network', 'monitoring', 'networking', 'infrastructure']
        }
    
    def _build_industry_bridges(self) -> List[str]:
        """Build keywords that bridge oil & gas to tech"""
        return [
            'operational efficiency', 'process optimization', 'data-driven',
            'asset management', 'performance monitoring', 'compliance tracking',
            'cost optimization', 'risk management', 'regulatory compliance',
            'operational data', 'field data', 'production data'
        ]
    
    def _build_role_evolution_map(self) -> Dict[str, Dict[str, Dict]]:
        """Map role evolution from current experience to target roles"""
        return {
            'drilling_consultant': {
                'landman': {
                    'title_keywords': ['landman', 'land man', 'lease analyst'],
                    'description_keywords': ['lease', 'mineral rights', 'contract', 'title', 'oil gas lease'],
                    'score': 0.95
                },
                'data_analyst': {
                    'title_keywords': ['data analyst', 'business analyst', 'operations analyst'],
                    'description_keywords': ['data', 'analysis', 'operational', 'field data', 'production'],
                    'score': 0.85
                },
                'safety_coordinator': {
                    'title_keywords': ['safety', 'hse', 'safety coordinator', 'safety manager'],
                    'description_keywords': ['safety', 'compliance', 'regulations', 'osha', 'environmental'],
                    'score': 0.90
                },
                'it_specialist': {
                    'title_keywords': ['it specialist', 'systems analyst', 'technical consultant'],
                    'description_keywords': ['automation', 'systems', 'technical', 'integration', 'support'],
                    'score': 0.75
                },
                'automation_engineer': {
                    'title_keywords': ['automation', 'process engineer', 'systems engineer'],
                    'description_keywords': ['automation', 'process', 'optimization', 'efficiency', 'control'],
                    'score': 0.80
                }
            }
        }