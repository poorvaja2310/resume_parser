import os
import re
import fitz  # PyMuPDF
import docx
from pathlib import Path
from typing import Dict, Any, List, Optional


class ResumeParser:
    """Parse resumes (PDF/DOCX) into structured data with improved accuracy."""

    def __init__(self, model_path: Optional[str] = None, llm=None):
        self.model_path = model_path
        self.llm = llm

        # Precompile regex patterns for better performance
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
        self.phone_pattern = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?(?:\d{3})\)?[-.\s]?\d{3}[-.\s]?\d{4}")
        self.linkedin_pattern = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?", re.I)
        self.github_pattern = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?", re.I)
        
        # Enhanced skills vocabulary
        self.skills_vocab = {
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'Bash', 'PowerShell',
            
            # Web Technologies
            'HTML', 'CSS', 'SCSS', 'Sass', 'Less', 'React', 'Angular', 'Vue.js', 'Next.js', 'Nuxt.js', 'Svelte', 'jQuery', 'Bootstrap', 'Tailwind CSS', 'Material-UI', 'Chakra UI',
            
            # Backend Frameworks
            'Node.js', 'Express.js', 'Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot', 'Laravel', 'Rails', 'ASP.NET', '.NET Core', 'Gin', 'Echo',
            
            # Databases
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server', 'Cassandra', 'DynamoDB', 'Elasticsearch', 'Neo4j',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Jenkins', 'GitLab CI', 'GitHub Actions', 'CircleCI', 'Travis CI',
            
            # Data Science & ML
            'Machine Learning', 'Deep Learning', 'Data Science', 'TensorFlow', 'PyTorch', 'Keras', 'scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Jupyter', 'Apache Spark', 'Hadoop',
            
            # Tools & Others
            'Git', 'Linux', 'Unix', 'Windows', 'macOS', 'VS Code', 'IntelliJ', 'Eclipse', 'Vim', 'Emacs', 'Postman', 'Insomnia', 'Figma', 'Adobe XD', 'Photoshop', 'Illustrator'
        }

    # ------------------ Text Extraction ------------------ #
    def extract_text(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return self._extract_text_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return self._extract_text_from_docx(file_path)
        elif ext == ".txt":
            return self._extract_text_from_txt(file_path)
        return ""

    def _extract_text_from_pdf(self, file_path: str) -> str:
        try:
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text("text") for page in doc])
            doc.close()
            return self._clean_text(text)
        except Exception as e:
            print(f"PDF parsing error: {e}")
            return ""

    def _extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return self._clean_text(text)
        except Exception as e:
            print(f"DOCX parsing error: {e}")
            return ""

    def _extract_text_from_txt(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return self._clean_text(f.read())
        except Exception as e:
            print(f"TXT parsing error: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()

    # ------------------ Section Extraction ------------------ #
    def _extract_section(self, text: str, section_headers: List[str]) -> str:
        """Extract content under specific section headers"""
        lines = text.splitlines()
        section_start = None
        
        # Find section start
        for i, line in enumerate(lines):
            line_clean = re.sub(r'[^a-zA-Z\s]', '', line).strip().lower()
            for header in section_headers:
                header_clean = re.sub(r'[^a-zA-Z\s]', '', header).strip().lower()
                if header_clean in line_clean or line_clean.startswith(header_clean):
                    section_start = i
                    break
            if section_start is not None:
                break
        
        if section_start is None:
            return ""
        
        # Extract content until next section
        section_content = []
        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip()
            
            # Stop at next major section (all caps or common section headers)
            if self._is_section_header(line):
                break
                
            if line:  # Skip empty lines
                section_content.append(line)
        
        return "\n".join(section_content)

    def _is_section_header(self, line: str) -> bool:
        """Check if line is likely a section header"""
        line = line.strip()
        if not line:
            return False
            
        # Common section headers
        section_keywords = [
            'education', 'experience', 'work experience', 'employment', 'skills', 
            'technical skills', 'projects', 'certifications', 'achievements', 
            'summary', 'objective', 'profile', 'contact', 'references'
        ]
        
        line_lower = line.lower()
        
        # Check if it's all caps (common for section headers)
        if line.isupper() and len(line) > 2:
            return True
            
        # Check if it matches common section keywords
        for keyword in section_keywords:
            if keyword in line_lower:
                return True
                
        return False

    # ------------------ Enhanced Parsing Methods ------------------ #
    def parse_resume_text(self, text: str) -> Dict[str, Any]:
        return {
            "name": self._extract_name(text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "linkedin": self._extract_linkedin(text),
            "github": self._extract_github(text),
            "skills": self._extract_skills(text),
            "education": self._extract_education(text),
            "experience": self._extract_experience(text),
            "certifications": self._extract_certifications(text),
            "summary": self._extract_summary(text)
        }

    def _extract_name(self, text: str) -> str:
        """Enhanced name extraction with multiple strategies"""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        # Strategy 1: Look in first 10 lines for name patterns
        for line in lines[:10]:
            if self._is_likely_name_line(line):
                name = self._clean_name(line)
                if name and self._validate_name(name):
                    return name
        
        # Strategy 2: Look for name after "Name:" or similar labels
        name_labels = ['name:', 'full name:', 'candidate:', 'applicant:']
        for line in lines[:15]:
            line_lower = line.lower()
            for label in name_labels:
                if label in line_lower:
                    name_part = line[line_lower.find(label) + len(label):].strip()
                    name = self._clean_name(name_part)
                    if name and self._validate_name(name):
                        return name
        
        # Strategy 3: Extract from email prefix as fallback
        email = self._extract_email(text)
        if email != "Not Available":
            prefix = email.split("@")[0]
            name = re.sub(r'[^a-zA-Z\s]', ' ', prefix)
            name = re.sub(r'\s+', ' ', name).strip().title()
            if len(name.split()) >= 2:
                return name
        
        return "Not Available"

    def _is_likely_name_line(self, line: str) -> bool:
        """Check if line likely contains a name"""
        # Skip lines with obvious non-name content
        skip_patterns = [
            r'@', r'http', r'www\.', r'\.com', r'\.org', r'\.net',
            r'\d{3,}', r'resume', r'cv', r'curriculum',
            r'phone', r'email', r'address', r'contact'
        ]
        
        line_lower = line.lower()
        if any(re.search(pattern, line_lower) for pattern in skip_patterns):
            return False
        
        # Check for name-like patterns
        words = line.split()
        if 2 <= len(words) <= 4:
            # Most words should start with capital letters
            capitalized = sum(1 for word in words if word and word[0].isupper())
            return capitalized >= 2
        
        return False

    def _clean_name(self, name: str) -> str:
        """Clean and format name"""
        # Remove common prefixes and suffixes
        name = re.sub(r'\b(?:Mr\.?|Ms\.?|Mrs\.?|Dr\.?|Prof\.?)\s*', '', name, flags=re.I)
        name = re.sub(r'\s*(?:Jr\.?|Sr\.?|III?|IV)\s*$', '', name, flags=re.I)
        
        # Clean up spacing and capitalization
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Proper case formatting
        words = []
        for word in name.split():
            if word.isupper() or word.islower():
                words.append(word.capitalize())
            else:
                words.append(word)
        
        return ' '.join(words)

    def _validate_name(self, name: str) -> bool:
        """Validate if extracted text is a valid name"""
        if not name or len(name) < 3:
            return False
        
        words = name.split()
        if len(words) < 2 or len(words) > 4:
            return False
        
        # Check for job titles or technical terms
        job_terms = [
            'engineer', 'developer', 'manager', 'analyst', 'designer',
            'consultant', 'specialist', 'coordinator', 'director', 'lead',
            'senior', 'junior', 'associate', 'intern', 'freelance'
        ]
        
        name_lower = name.lower()
        if any(term in name_lower for term in job_terms):
            return False
        
        # Each word should be reasonable length for a name
        for word in words:
            if len(word) < 2 or len(word) > 20:
                return False
        
        return True

    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        match = self.email_pattern.search(text)
        return match.group(0) if match else "Not Available"

    def _extract_phone(self, text: str) -> str:
        """Extract phone number with better formatting"""
        match = self.phone_pattern.search(text)
        if match:
            phone = match.group(0)
            # Clean and format phone number
            phone = re.sub(r'[^\d+]', '', phone)
            if len(phone) >= 10:
                return phone
        return "Not Available"

    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn profile"""
        match = self.linkedin_pattern.search(text)
        return match.group(0) if match else "Not Available"

    def _extract_github(self, text: str) -> str:
        """Extract GitHub profile"""
        match = self.github_pattern.search(text)
        return match.group(0) if match else "Not Available"

    def _extract_skills(self, text: str) -> List[str]:
        """Enhanced skills extraction using section-based approach and vocabulary matching"""
        skills = set()
        
        # Strategy 1: Extract from skills section
        skills_section = self._extract_section(text, [
            'skills', 'technical skills', 'core competencies', 'technologies',
            'programming languages', 'tools', 'expertise'
        ])
        
        if skills_section:
            # Parse skills from section content
            skills.update(self._parse_skills_from_section(skills_section))
        
        # Strategy 2: Scan entire document for skill keywords
        text_lower = text.lower()
        for skill in self.skills_vocab:
            # Use word boundaries to avoid partial matches
            pattern = rf'\b{re.escape(skill.lower())}\b'
            if re.search(pattern, text_lower):
                skills.add(skill)
        
        # Strategy 3: Look for skill patterns (e.g., "5+ years of Python")
        skill_patterns = [
            r'(?:experience (?:with|in)|proficient (?:with|in)|skilled (?:with|in)|knowledge of)\s+([A-Za-z+#.\s]+)',
            r'(\w+(?:\.\w+)*)\s*(?:\([^)]*\))?\s*(?:programming|development|framework|library)',
            r'(?:years? of|experience with|worked with)\s+([A-Za-z+#.\s]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.I)
            for match in matches:
                potential_skills = re.split(r'[,;/&]', match)
                for skill in potential_skills:
                    skill = skill.strip()
                    if skill and len(skill) <= 30 and skill in self.skills_vocab:
                        skills.add(skill)
        
        result = sorted(list(skills)) if skills else ["Not Available"]
        return result

    def _parse_skills_from_section(self, section_text: str) -> set:
        """Parse skills from a dedicated skills section"""
        skills = set()
        
        # Split by common delimiters
        items = re.split(r'[,;•\n\t|/]', section_text)
        
        for item in items:
            item = item.strip()
            if not item:
                continue
                
            # Clean up common formatting
            item = re.sub(r'^\W+|\W+$', '', item)  # Remove leading/trailing punctuation
            item = re.sub(r'\s+', ' ', item)  # Normalize whitespace
            
            # Check if it's a known skill
            if item in self.skills_vocab:
                skills.add(item)
            else:
                # Check for partial matches or variations
                item_lower = item.lower()
                for skill in self.skills_vocab:
                    if skill.lower() == item_lower or skill.lower() in item_lower:
                        skills.add(skill)
                        break
        
        return skills

    def _extract_education(self, text: str) -> List[str]:
        """Enhanced education extraction"""
        education = []
        
        # Extract education section
        edu_section = self._extract_section(text, [
            'education', 'academic background', 'qualifications', 'degrees'
        ])
        
        if edu_section:
            education.extend(self._parse_education_from_section(edu_section))
        
        # Also scan entire document for degree patterns
        degree_patterns = [
            r'((?:Bachelor|Master|PhD|Doctorate|Associate|B\.?[A-Za-z]*|M\.?[A-Za-z]*|Ph\.?D\.?)[^,\n]*(?:in|of)\s+[^,\n]+)',
            r'((?:B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|MBA|Ph\.?D\.?)[^,\n]*)',
            r'([A-Za-z\s]+(?:University|College|Institute|School)[^,\n]*)'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.I)
            for match in matches:
                cleaned = re.sub(r'\s+', ' ', match.strip())
                if len(cleaned) > 5 and cleaned not in education:
                    education.append(cleaned)
        
        return education if education else ["Not Available"]

    def _parse_education_from_section(self, section_text: str) -> List[str]:
        """Parse education entries from education section"""
        education = []
        lines = [line.strip() for line in section_text.splitlines() if line.strip()]
        
        current_entry = []
        for line in lines:
            # Check if this line starts a new education entry
            if any(keyword in line.lower() for keyword in ['university', 'college', 'institute', 'school', 'bachelor', 'master', 'phd', 'degree']):
                if current_entry:
                    education.append(' '.join(current_entry))
                    current_entry = []
                current_entry.append(line)
            elif current_entry and len(line) > 3:
                current_entry.append(line)
        
        # Add the last entry
        if current_entry:
            education.append(' '.join(current_entry))
        
        return education

    def _extract_experience(self, text: str) -> List[str]:
        """Enhanced work experience extraction"""
        experience = []
        
        # Extract experience section
        exp_section = self._extract_section(text, [
            'experience', 'work experience', 'professional experience', 
            'employment', 'career history', 'work history'
        ])
        
        if exp_section:
            experience.extend(self._parse_experience_from_section(exp_section))
        
        # Also look for experience patterns throughout the document
        exp_patterns = [
            r'([A-Za-z\s]+(?:Engineer|Developer|Manager|Analyst|Designer|Consultant|Specialist)[^,\n]*(?:at|@)\s+[^,\n]+)',
            r'(\d{4}\s*[-–]\s*(?:\d{4}|Present|Current)[^,\n]*[A-Za-z][^,\n]*)'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.I)
            for match in matches:
                cleaned = re.sub(r'\s+', ' ', match.strip())
                if len(cleaned) > 10 and cleaned not in experience:
                    experience.append(cleaned)
        
        return experience if experience else ["Not Available"]

    def _parse_experience_from_section(self, section_text: str) -> List[str]:
        """Parse experience entries from experience section"""
        experience = []
        lines = [line.strip() for line in section_text.splitlines() if line.strip()]
        
        current_entry = []
        for line in lines:
            # Check if this line starts a new job entry (job title or company)
            if (any(keyword in line.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst', 'designer', 'consultant']) or
                re.search(r'\d{4}\s*[-–]\s*(?:\d{4}|present|current)', line.lower()) or
                any(keyword in line.lower() for keyword in ['company', 'corp', 'inc', 'ltd', 'llc'])):
                
                if current_entry:
                    experience.append(' '.join(current_entry))
                    current_entry = []
                current_entry.append(line)
            elif current_entry and len(line) > 5:
                current_entry.append(line)
        
        # Add the last entry
        if current_entry:
            experience.append(' '.join(current_entry))
        
        return experience

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        # Extract certifications section
        cert_section = self._extract_section(text, [
            'certifications', 'certificates', 'licenses', 'credentials'
        ])
        
        if cert_section:
            lines = [line.strip() for line in cert_section.splitlines() if line.strip()]
            for line in lines:
                if len(line) > 5:  # Filter out very short lines
                    certifications.append(line)
        
        # Look for certification patterns throughout document
        cert_patterns = [
            r'((?:AWS|Azure|Google|Microsoft|Oracle|Cisco|CompTIA)[^,\n]*(?:Certified|Certification)[^,\n]*)',
            r'((?:Certified|Certification)[^,\n]*(?:AWS|Azure|Google|Microsoft|Oracle|Cisco|CompTIA)[^,\n]*)'
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.I)
            for match in matches:
                cleaned = re.sub(r'\s+', ' ', match.strip())
                if cleaned not in certifications:
                    certifications.append(cleaned)
        
        return certifications if certifications else ["Not Available"]

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary or objective"""
        summary_section = self._extract_section(text, [
            'summary', 'professional summary', 'profile', 'objective',
            'career objective', 'about', 'overview'
        ])
        
        if summary_section:
            # Take first paragraph or first few sentences
            sentences = re.split(r'[.!?]+', summary_section)
            if sentences:
                summary = '. '.join(sentences[:3]).strip()
                if len(summary) > 20:
                    return summary + '.' if not summary.endswith('.') else summary
        
        # Fallback: look for summary-like content in first few paragraphs
        paragraphs = text.split('\n\n')
        for para in paragraphs[:3]:
            para = para.strip()
            if (len(para) > 50 and 
                any(keyword in para.lower() for keyword in ['experience', 'skilled', 'professional', 'passionate']) and
                not any(keyword in para.lower() for keyword in ['education', 'university', 'degree'])):
                return para[:300] + '...' if len(para) > 300 else para
        
        return "Not Available"

    def _llm_parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Optional LLM enhancement (if available)"""
        if not self.llm:
            return None
        try:
            prompt = f"""
Extract resume information as JSON with these exact keys:
name, email, phone, linkedin, github, skills, education, experience, certifications, summary

Resume text:
{text[:4000]}

Return only valid JSON:
"""
            result = self.llm(prompt, max_tokens=800, temperature=0.1)
            if isinstance(result, dict) and 'choices' in result:
                response_text = result['choices'][0]['text'].strip()
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    import json
                    return json.loads(json_match.group(0))
        except Exception as e:
            print(f"LLM parsing error: {e}")
        return None

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Main method to parse a resume file"""
        text = self.extract_text(file_path)
        if not text:
            return {"error": "Could not extract text", "file_path": file_path}

        # Parse using heuristic methods
        parsed = self.parse_resume_text(text)

        # Enhance with LLM if available
        llm_result = self._llm_parse(text)
        if llm_result:
            for key, value in llm_result.items():
                if key in parsed:
                    # Only override if LLM provides better data
                    if isinstance(value, list) and value and value != ["Not Available"]:
                        parsed[key] = value
                    elif isinstance(value, str) and value.strip() and value != "Not Available":
                        parsed[key] = value.strip()

        # Add metadata
        parsed["file_path"] = file_path
        parsed["text_length"] = len(text)
        parsed["filename"] = Path(file_path).name

        # Ensure all fields have values
        for key, value in parsed.items():
            if isinstance(value, str) and not value.strip():
                parsed[key] = "Not Available"
            elif isinstance(value, list) and not value:
                parsed[key] = ["Not Available"]
            elif value is None:
                parsed[key] = "Not Available"

        return parsed

    def parse_multiple_resumes(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Parse multiple resume files"""
        results = []
        for file_path in file_paths:
            print(f"Parsing: {file_path}")
            result = self.parse_resume(file_path)
            results.append(result)
        return results


# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Test with sample resume text
    sample_resume = """
    John Smith
    Software Engineer
    john.smith@email.com
    +1-555-123-4567
    linkedin.com/in/johnsmith
    github.com/johnsmith
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years in full-stack web development.
    Passionate about creating scalable applications and leading development teams.
    
    EDUCATION
    Bachelor of Science in Computer Science
    Stanford University, 2018-2022
    GPA: 3.8/4.0
    
    WORK EXPERIENCE
    Senior Software Engineer
    Tech Corp, San Francisco, CA
    2022-Present
    • Developed microservices using Python and Django
    • Led a team of 4 developers on React-based frontend projects
    • Implemented CI/CD pipelines using Docker and Kubernetes
    
    Software Developer
    StartupXYZ, Austin, TX
    2020-2022
    • Built REST APIs using Node.js and Express
    • Worked with PostgreSQL and Redis for data management
    • Collaborated with UX team on responsive web applications
    
    TECHNICAL SKILLS
    Programming Languages: Python, JavaScript, TypeScript, Java
    Frameworks: React, Django, Flask, Express.js, Spring Boot
    Databases: PostgreSQL, MongoDB, Redis, MySQL
    Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, Git
    
    CERTIFICATIONS
    AWS Certified Solutions Architect Associate
    Google Cloud Professional Developer
    """
    
    # Create temporary file for testing
    with open("test_resume.txt", "w") as f:
        f.write(sample_resume)
    
    try:
        result = parser.parse_resume("test_resume.txt")
        import json
        print(json.dumps(result, indent=2))
    finally:
        # Clean up
        if os.path.exists("test_resume.txt"):
            os.remove("test_resume.txt")