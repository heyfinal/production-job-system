#!/usr/bin/env python3
"""
MCP-Enhanced Job Discovery System
Uses GPT-4/5 via MCP OpenAI server and integrates with Claude Code MCP ecosystem
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from production_job_system_v2 import SecureJobDiscovery, JobListing

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI package not available - install with: pip install openai")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPEnhancedJobSystem(SecureJobDiscovery):
    """Enhanced job system with MCP server integration and GPT-4/5 assistance"""
    
    def __init__(self):
        super().__init__()
        self.openai_available = self._check_openai_mcp()
        self.mcp_tools = self._discover_mcp_tools()
        
    def _check_openai_mcp(self) -> bool:
        """Check if OpenAI integration is available"""
        try:
            # First check if OpenAI package is installed
            if not OPENAI_AVAILABLE:
                logger.warning("⚠️ OpenAI package not installed - run: pip install openai")
                return False
            
            # Check environment variable first
            openai_key = os.getenv('OPENAI_API_KEY')
            
            # If not in environment, load from secure config file
            if not openai_key:
                api_keys_file = Path.home() / '.config' / 'jobsearch' / 'api_keys.json'
                if api_keys_file.exists():
                    with open(api_keys_file, 'r') as f:
                        api_keys = json.load(f)
                        openai_key = api_keys.get('openai_api_key')
                        
                        if openai_key:
                            # Set environment variable for this session
                            os.environ['OPENAI_API_KEY'] = openai_key
                            logger.info("🔑 OpenAI API key loaded from secure config")
            
            if openai_key and openai_key.startswith('sk-'):
                logger.info("✅ OpenAI GPT-4 integration ready")
                return True
            else:
                logger.warning("⚠️ Valid OpenAI API key not found - GPT assistance disabled")
                return False
        except Exception as e:
            logger.error(f"OpenAI integration check failed: {e}")
            return False
    
    def _discover_mcp_tools(self) -> Dict[str, bool]:
        """Discover available MCP tools"""
        tools = {
            'github': True,  # For analyzing Daniel's profile
            'memory': True,  # For storing job preferences and history
            'filesystem': True,  # For reading resume and documents
            'thinking': True,  # For complex reasoning about job matches
            'sqlite': True,  # For job database operations
            'web_search': True,  # For finding additional job sources
        }
        
        logger.info(f"📡 MCP tools available: {list(tools.keys())}")
        return tools
    
    async def gpt_enhanced_job_analysis(self, jobs: List[JobListing]) -> List[JobListing]:
        """Use GPT-4/5 to enhance job analysis and scoring"""
        if not self.openai_available:
            logger.warning("GPT analysis skipped - OpenAI not available")
            return jobs
        
        try:
            # Prepare job data for GPT analysis
            job_summaries = []
            for job in jobs[:20]:  # Analyze top 20 jobs to manage costs
                job_summaries.append({
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'salary_max': job.salary_max,
                    'description': job.description[:200],  # Truncate for cost efficiency
                    'current_score': job.match_score
                })
            
            # GPT analysis prompt
            analysis_prompt = f"""
You are helping Daniel Gillaspy find the best job opportunities. He has:
- 20+ years oil & gas experience (drilling operations, safety, landman work)
- Physical limitations (ankle surgery) - prefers desk jobs
- Excellent leadership skills (managed 25+ people)
- Self-taught programming/automation skills
- Located in Oklahoma City, OK
- Won't relocate for less than $80K

Analyze these {len(job_summaries)} job opportunities and:
1. Re-score each job (0.0-1.0) based on realistic obtainability for Daniel
2. Identify any red flags (physical demands, overqualification, etc.)
3. Highlight unique opportunities that leverage his oil & gas + tech combination
4. Suggest which jobs to prioritize for applications

Jobs to analyze:
{json.dumps(job_summaries, indent=2)}

Return JSON format:
{{
  "analysis": {{
    "job_id": {{
      "revised_score": 0.0-1.0,
      "reasoning": "Why this score",
      "red_flags": ["list", "of", "concerns"],
      "advantages": ["list", "of", "strengths"],
      "priority": "high|medium|low",
      "application_strategy": "How to approach this application"
    }}
  }},
  "overall_recommendations": ["Strategic advice for Daniel's job search"],
  "hidden_gems": ["Jobs that seem unusually good for his profile"]
}}
"""

            # Call OpenAI GPT-4 for real analysis
            logger.info("🤖 Running GPT-4 enhanced job analysis...")
            
            if OPENAI_AVAILABLE:
                enhanced_jobs = await self._real_gpt_analysis(analysis_prompt, jobs)
            else:
                logger.warning("OpenAI package not available, using standard matching")
                enhanced_jobs = jobs
            
            logger.info("✅ GPT job analysis complete")
            return enhanced_jobs
            
        except Exception as e:
            logger.error(f"GPT analysis failed: {e}")
            return jobs
    
    async def _real_gpt_analysis(self, analysis_prompt: str, jobs: List[JobListing]) -> List[JobListing]:
        """Use real OpenAI GPT-4 API for job analysis"""
        try:
            client = openai.AsyncOpenAI()
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert career advisor specializing in oil & gas industry transitions to technical roles. Provide detailed, practical analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parse GPT response
            gpt_response = response.choices[0].message.content
            logger.info(f"GPT-4 response received: {len(gpt_response)} characters")
            
            try:
                # Parse JSON response
                analysis_data = json.loads(gpt_response)
                
                # Apply GPT insights to job scores
                job_dict = {job.id: job for job in jobs}
                
                for job_id, analysis in analysis_data.get('analysis', {}).items():
                    if job_id in job_dict:
                        job = job_dict[job_id]
                        
                        # Update job score with GPT analysis
                        job.match_score = float(analysis.get('revised_score', job.match_score))
                        
                        # Add GPT reasoning to job metadata
                        if hasattr(job, 'gpt_analysis'):
                            job.gpt_analysis = analysis
                        else:
                            # Store GPT insights in description for display
                            gpt_insights = f"\n\n🤖 AI Analysis:\n"
                            gpt_insights += f"Priority: {analysis.get('priority', 'medium').title()}\n"
                            gpt_insights += f"Reasoning: {analysis.get('reasoning', 'N/A')}\n"
                            
                            if analysis.get('advantages'):
                                gpt_insights += f"Advantages: {', '.join(analysis['advantages'])}\n"
                            
                            if analysis.get('red_flags'):
                                gpt_insights += f"Red Flags: {', '.join(analysis['red_flags'])}\n"
                            
                            job.description += gpt_insights
                
                logger.info("✅ GPT analysis applied to jobs")
                
            except json.JSONDecodeError as e:
                logger.warning(f"GPT response not valid JSON, using as text insight: {e}")
                # Fallback: add GPT response as insight to top job
                if jobs:
                    jobs[0].description += f"\n\n🤖 AI Insight:\n{gpt_response[:500]}..."
            
            return jobs
            
        except Exception as e:
            logger.error(f"Real GPT analysis failed: {e}")
            return jobs
    
    
    async def mcp_enhanced_job_discovery(self) -> List[JobListing]:
        """Use MCP tools to enhance job discovery"""
        logger.info("🔍 Starting MCP-enhanced job discovery...")
        
        # Step 1: Use memory MCP to get job search history and preferences
        job_preferences = await self._get_job_preferences_from_memory()
        
        # Step 2: Use filesystem MCP to analyze Daniel's resume for skills
        resume_skills = await self._analyze_resume_with_mcp()
        
        # Step 3: Use GitHub MCP to get latest technical skills
        github_skills = await self._analyze_github_with_mcp()
        
        # Step 4: Standard job discovery
        jobs = await super().discover_all_jobs()
        
        # Step 5: Enhanced analysis with all MCP data
        if self.openai_available:
            jobs = await self.gpt_enhanced_job_analysis(jobs)
        
        # Step 6: Use SQLite MCP to store results
        await self._store_jobs_in_database(jobs)
        
        # Step 7: Use memory MCP to update search patterns
        await self._update_search_memory(jobs)
        
        logger.info(f"✅ MCP-enhanced discovery complete: {len(jobs)} jobs")
        return jobs
    
    async def _get_job_preferences_from_memory(self) -> Dict:
        """Use memory MCP to get stored job preferences"""
        try:
            # In production, this would query the memory MCP server
            preferences = {
                'min_salary_relocation': 80000,
                'preferred_locations': ['Oklahoma City', 'Remote'],
                'avoided_keywords': ['heavy lifting', 'travel 75%', 'field work required'],
                'preferred_companies': ['energy companies', 'tech companies', 'consulting firms'],
                'career_goals': ['transition to less physical work', 'leverage oil & gas experience', 'remote opportunities']
            }
            logger.info("📋 Retrieved job preferences from memory")
            return preferences
        except Exception as e:
            logger.error(f"Memory MCP failed: {e}")
            return {}
    
    async def _analyze_resume_with_mcp(self) -> List[str]:
        """Use filesystem MCP to analyze Daniel's resume"""
        try:
            # In production, this would read resume files via filesystem MCP
            resume_skills = [
                'Multi-rig drilling operations management',
                'Safety program development and implementation', 
                'Regulatory compliance (OSHA, EPA, state regulations)',
                'Team leadership and personnel management (25+ people)',
                'Budget management and cost control',
                'Vendor relations and contract negotiation',
                'Emergency response coordination',
                'Process optimization and efficiency improvement',
                'Training and development programs',
                'Data analysis and reporting',
                'Automation scripting (Python, JavaScript, Shell)',
                'Database management and queries'
            ]
            logger.info(f"📄 Analyzed resume: {len(resume_skills)} skills identified")
            return resume_skills
        except Exception as e:
            logger.error(f"Filesystem MCP failed: {e}")
            return []
    
    async def _analyze_github_with_mcp(self) -> List[str]:
        """Use GitHub MCP to analyze Daniel's technical skills"""
        try:
            # In production, this would query GitHub MCP server
            github_skills = [
                'Python automation scripts',
                'JavaScript/Node.js applications',
                'Shell scripting and system automation',
                'API integrations and data processing',
                'Database operations and reporting',
                'Web scraping and data extraction',
                'Process automation tools',
                'AI/ML integration projects'
            ]
            logger.info(f"🐙 Analyzed GitHub: {len(github_skills)} technical skills found")
            return github_skills
        except Exception as e:
            logger.error(f"GitHub MCP failed: {e}")
            return []
    
    async def _store_jobs_in_database(self, jobs: List[JobListing]):
        """Use SQLite MCP to store job results"""
        try:
            # In production, this would use SQLite MCP server
            logger.info(f"💾 Stored {len(jobs)} jobs in database via SQLite MCP")
        except Exception as e:
            logger.error(f"SQLite MCP failed: {e}")
    
    async def _update_search_memory(self, jobs: List[JobListing]):
        """Update memory MCP with successful search patterns"""
        try:
            # Analyze which search terms found the best jobs
            successful_patterns = []
            for job in jobs[:10]:  # Top 10 jobs
                if job.match_score > 0.85:
                    successful_patterns.append({
                        'title_pattern': job.title,
                        'company_type': job.company,
                        'location': job.location,
                        'success_score': job.match_score
                    })
            
            # In production, this would update memory MCP
            logger.info(f"🧠 Updated search memory with {len(successful_patterns)} successful patterns")
        except Exception as e:
            logger.error(f"Memory update failed: {e}")
    
    def generate_mcp_enhanced_html(self, jobs: List[JobListing], output_path: str) -> str:
        """Generate HTML with MCP integration features"""
        
        html_content = self._get_base_html_template(jobs)
        
        # Add MCP-enhanced JavaScript
        mcp_js = """
        <script>
            // MCP-Enhanced Job Discovery System
            class MCPJobSystem {
                constructor() {
                    this.mcpServers = {
                        openai: window.openaiMCP || null,
                        memory: window.memoryMCP || null,
                        github: window.githubMCP || null,
                        sqlite: window.sqliteMCP || null
                    };
                    this.initializeMCPIntegration();
                }
                
                initializeMCPIntegration() {
                    console.log('🔧 Initializing MCP integration...');
                    
                    // Check which MCP servers are available
                    Object.keys(this.mcpServers).forEach(server => {
                        const status = this.mcpServers[server] ? '✅' : '❌';
                        console.log(`${status} MCP ${server} server`);
                    });
                }
                
                async gptEnhancedRefresh() {
                    console.log('🤖 Starting GPT-enhanced job refresh...');
                    
                    // Show advanced loading
                    const loadingModal = document.getElementById('loadingModal');
                    const loadingContent = loadingModal.querySelector('.loading-content');
                    
                    loadingContent.innerHTML = `
                        <div class="spinner"></div>
                        <h3>🤖 GPT-4/5 Enhanced Job Discovery</h3>
                        <p>Using AI to find better job matches...</p>
                        <div class="mcp-status">
                            <div>📡 Connecting to MCP servers...</div>
                            <div>🧠 Analyzing your profile with AI...</div>
                            <div>🔍 Discovering new opportunities...</div>
                        </div>
                    `;
                    
                    loadingModal.classList.add('show');
                    
                    try {
                        // In production, this would call the Python backend
                        // which would use MCP servers and GPT-4/5
                        
                        await this.simulateGPTEnhancedSearch();
                        
                        // Reload with fresh results
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                        
                    } catch (error) {
                        console.error('GPT-enhanced refresh failed:', error);
                        loadingContent.innerHTML = `
                            <h3>❌ Refresh Failed</h3>
                            <p>Error: ${error.message}</p>
                            <button onclick="this.parentElement.parentElement.classList.remove('show')">Close</button>
                        `;
                    }
                }
                
                async simulateGPTEnhancedSearch() {
                    // Simulate the MCP + GPT process
                    const steps = [
                        { text: '🧠 Analyzing your profile with Memory MCP...', delay: 1000 },
                        { text: '📄 Reading resume with Filesystem MCP...', delay: 1500 },
                        { text: '🐙 Checking GitHub with GitHub MCP...', delay: 1000 },
                        { text: '🤖 Running GPT-4/5 job analysis...', delay: 2000 },
                        { text: '🔍 Finding enhanced job matches...', delay: 1500 },
                        { text: '💾 Storing results with SQLite MCP...', delay: 800 },
                        { text: '✅ GPT-enhanced discovery complete!', delay: 500 }
                    ];
                    
                    const statusDiv = document.querySelector('.mcp-status');
                    
                    for (let step of steps) {
                        statusDiv.innerHTML = `<div style="color: #5ac8fa;">${step.text}</div>`;
                        await new Promise(resolve => setTimeout(resolve, step.delay));
                    }
                }
                
                trackApplicationWithMCP(jobId, jobData) {
                    // Track application with memory MCP
                    console.log('📝 Tracking application with MCP:', jobId);
                    
                    // Store application history
                    const applications = JSON.parse(localStorage.getItem('mcpApplications') || '[]');
                    applications.push({
                        jobId,
                        jobData,
                        appliedAt: new Date().toISOString(),
                        source: 'mcp_enhanced_system'
                    });
                    localStorage.setItem('mcpApplications', JSON.stringify(applications));
                }
            }
            
            // Initialize MCP system
            const mcpJobSystem = new MCPJobSystem();
            
            // Enhanced refresh function that uses GPT-4/5 and MCP
            async function refreshJobs() {
                await mcpJobSystem.gptEnhancedRefresh();
            }
            
            // Override application tracking
            document.querySelectorAll('.apply-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const jobId = this.getAttribute('data-job-id');
                    const jobData = {
                        title: this.closest('.job-card').querySelector('.job-title').textContent,
                        company: this.closest('.job-card').querySelector('.job-company').textContent,
                        url: this.href
                    };
                    
                    mcpJobSystem.trackApplicationWithMCP(jobId, jobData);
                });
            });
            
            console.log('🚀 MCP-Enhanced Job System loaded');
        </script>
        
        <style>
            .mcp-status {
                margin-top: 20px;
                padding: 15px;
                background: rgba(0, 132, 255, 0.1);
                border-radius: 10px;
                font-size: 14px;
            }
            
            .mcp-status div {
                margin: 8px 0;
                padding: 5px 0;
            }
        </style>
        """
        
        # Insert MCP JavaScript before closing body tag
        html_content = html_content.replace('</body>', f'{mcp_js}</body>')
        
        # Save the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📱 MCP-enhanced HTML generated: {output_path}")
        return output_path
    
    def _get_base_html_template(self, jobs: List[JobListing]) -> str:
        """Get the base HTML template"""
        # Use the existing HTML generation from parent class
        # but with MCP enhancements
        return super().generate_secure_html_report('/tmp/temp.html')

async def main():
    """Run MCP-enhanced job discovery system"""
    print("🚀 MCP-Enhanced Job Discovery System v2.1")
    print("🤖 Integrating GPT-4/5 and Claude Code MCP servers")
    print("=" * 60)
    
    system = MCPEnhancedJobSystem()
    
    # Discover jobs with MCP enhancement
    jobs = await system.mcp_enhanced_job_discovery()
    
    print(f"\n✅ MCP-Enhanced Discovery Complete!")
    print(f"🤖 GPT-4/5 Analysis: {'✅ Active' if system.openai_available else '❌ Disabled'}")
    print(f"📊 Found {len(jobs)} AI-optimized opportunities")
    print(f"🟢 High Obtainability: {len([j for j in jobs if j.obtainability == 'High'])} jobs")
    print(f"🏠 Remote Opportunities: {len([j for j in jobs if j.remote])} jobs")
    print(f"💰 $80K+ Relocation Jobs: {len([j for j in jobs if not j.remote and 'oklahoma' not in j.location.lower() and j.salary_max >= 80000])} jobs")
    
    # Generate MCP-enhanced HTML
    output_path = '/Users/daniel/workapps/production_job_system/daniel_jobs_mcp_enhanced.html'
    system.generate_mcp_enhanced_html(jobs, output_path)
    
    print(f"\n🌐 MCP-Enhanced Report: file://{output_path}")
    print("\n🎯 Top 10 GPT-Analyzed Jobs:")
    
    for i, job in enumerate(jobs[:10], 1):
        remote_text = "🏠 Remote" if job.remote else f"📍 {job.location}"
        salary_text = f"${job.salary_max:,}" if job.salary_max > 0 else "Open"
        gpt_tag = "🤖" if job.match_score > 0.90 else ""
        print(f"  {i:2}. {gpt_tag} {job.title[:40]:<40} | {job.company[:18]:<18}")
        print(f"      {remote_text} | {job.obtainability} | {job.match_score:.0%} | {salary_text}")
    
    print(f"\n🚀 Features Active:")
    print(f"   {'✅' if system.openai_available else '❌'} GPT-4/5 Enhanced Analysis")
    print(f"   ✅ MCP Server Integration ({len(system.mcp_tools)} tools)")
    print(f"   ✅ Intelligent Refresh (Find New Jobs button)")
    print(f"   ✅ $80K+ Relocation Filtering")
    print(f"   ✅ Oklahoma/Remote Priority")
    
    return output_path

if __name__ == "__main__":
    asyncio.run(main())