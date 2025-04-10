import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

class RequestParser:
    """
    A simplified NLP engine for parsing pentest requests and extracting key information.
    This lightweight implementation uses basic NLP techniques to identify URLs, credentials,
    and scope information from natural language requests.
    """
    
    def __init__(self):
        """Initialize the RequestParser with necessary NLTK resources."""
        # Download required NLTK resources if not already present
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        
        # Regular expressions for extracting information
        self.url_pattern = re.compile(
            r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w%!.~\'*,;:=+()@/]*)*'
        )
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        )
        self.credential_pattern = re.compile(
            r'(?:username|user|login|email|password|pass|pwd|credential)[s]?[\s:]+([^\s,;]+)'
        )
    
    def parse_request(self, text):
        """
        Parse the request text and extract key information.
        
        Args:
            text (str): The natural language request text
            
        Returns:
            dict: Extracted information including request_type, urls, credentials, and scope
        """
        result = {
            'request_type': self._identify_request_type(text),
            'urls': self._extract_urls(text),
            'credentials': self._extract_credentials(text),
            'scope': self._extract_scope(text),
            'priority': self._identify_priority(text)
        }
        return result
    
    def _identify_request_type(self, text):
        """Identify the type of pentest request (web, mobile, API)."""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['api', 'endpoint', 'rest', 'graphql']):
            return 'api'
        elif any(term in text_lower for term in ['mobile', 'android', 'ios', 'app']):
            return 'mobile'
        else:
            return 'web'  # Default to web
    
    def _extract_urls(self, text):
        """Extract URLs from the request text."""
        return self.url_pattern.findall(text)
    
    def _extract_credentials(self, text):
        """Extract credentials from the request text."""
        credentials = {}
        
        # Extract email/username and password pairs
        email_matches = self.email_pattern.findall(text)
        if email_matches:
            credentials['email'] = email_matches[0]
        
        # Look for credential patterns
        cred_matches = self.credential_pattern.findall(text)
        
        # Process lines that might contain credentials
        lines = text.split('\n')
        for line in lines:
            if ':' in line and ('user' in line.lower() or 'pass' in line.lower() or 'login' in line.lower()):
                parts = line.split(':', 1)
                key = parts[0].strip().lower()
                value = parts[1].strip()
                
                if 'user' in key or 'email' in key or 'login' in key:
                    credentials['username'] = value
                elif 'pass' in key:
                    credentials['password'] = value
        
        # If we found credentials in the regex pattern but not in structured format
        if not credentials and cred_matches:
            # Try to pair them as username/password
            if len(cred_matches) >= 2:
                credentials['username'] = cred_matches[0]
                credentials['password'] = cred_matches[1]
        
        return credentials
    
    def _extract_scope(self, text):
        """Extract the scope of the pentest from the request text."""
        # Look for scope indicators
        scope_indicators = ['scope', 'focus on', 'test', 'check', 'examine']
        
        lines = text.split('\n')
        scope_text = []
        
        # Check if any line contains scope indicators
        for line in lines:
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in scope_indicators):
                # Remove the indicator and keep the rest as scope
                for indicator in scope_indicators:
                    if indicator in line_lower:
                        # Extract the part after the indicator
                        parts = line_lower.split(indicator, 1)
                        if len(parts) > 1:
                            scope_text.append(parts[1].strip())
                        break
        
        # If no explicit scope found, try to extract it from context
        if not scope_text:
            # Tokenize and remove stop words
            tokens = word_tokenize(text.lower())
            filtered_tokens = [w for w in tokens if w not in self.stop_words and w not in string.punctuation]
            
            # Look for keywords that might indicate scope
            scope_keywords = ['checkout', 'payment', 'login', 'authentication', 'admin', 'user', 'profile', 'api']
            found_keywords = [kw for kw in scope_keywords if kw in filtered_tokens]
            
            if found_keywords:
                scope_text = [f"Focus on {', '.join(found_keywords)} functionality"]
        
        return ' '.join(scope_text) if scope_text else "General pentest - no specific scope defined"
    
    def _identify_priority(self, text):
        """Identify the priority level of the request."""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['urgent', 'critical', 'emergency', 'asap', 'immediately']):
            return 'critical'
        elif any(term in text_lower for term in ['high', 'important', 'priority']):
            return 'high'
        elif any(term in text_lower for term in ['low', 'minor', 'when possible']):
            return 'low'
        else:
            return 'medium'  # Default priority
    
    def generate_clarification_questions(self, parsed_request):
        """
        Generate clarification questions based on the parsed request.
        
        Args:
            parsed_request (dict): The parsed request information
            
        Returns:
            list: List of clarification questions
        """
        questions = []
        
        # Check if URL is missing
        if not parsed_request['urls']:
            questions.append("What is the target URL or application you'd like to test?")
        
        # Check if credentials are missing
        if not parsed_request['credentials']:
            questions.append("Do you have test credentials we should use for the pentest?")
        
        # Check if scope is too general
        if parsed_request['scope'] == "General pentest - no specific scope defined":
            questions.append("Could you specify which parts of the application you'd like us to focus on?")
        
        # Add environment question
        questions.append("Is this a production environment or a pre-production/staging environment?")
        
        # Add timeline question
        questions.append("Do you have a specific deadline for when you need the results?")
        
        return questions
