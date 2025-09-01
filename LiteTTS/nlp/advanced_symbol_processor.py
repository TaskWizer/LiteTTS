#!/usr/bin/env python3
"""
Advanced symbol and punctuation processor for TTS
Fixes asterisk→astrisk, quotation marks→'in quat', apostrophes→'x 27' issues
"""

import re
import html
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AdvancedSymbolProcessor:
    """Advanced symbol and punctuation processing for natural TTS pronunciation"""
    
    def __init__(self):
        self.symbol_mappings = self._load_symbol_mappings()
        self.quote_patterns = self._load_quote_patterns()
        self.markdown_symbols = self._load_markdown_symbols()
        self.punctuation_rules = self._load_punctuation_rules()
        
        # Configuration
        self.preserve_markdown = False
        self.handle_quotes_naturally = True
        self.fix_html_entities = True
        
    def _load_symbol_mappings(self) -> Dict[str, str]:
        """Load symbol-to-word mappings with pronunciation fixes"""
        return {
            # Mathematical and logical symbols
            '&': ' and ',
            '+': ' plus ',
            '=': ' equals ',
            '%': ' percent',
            '@': ' at ',
            '#': ' hash ',

            # FIXED: Asterisk pronunciation - ensure it's pronounced correctly
            '*': ' asterisk ',  # Not "astrisk"

            # Currency symbols (basic - advanced currency processor handles complex cases)
            '$': ' dollar ',
            '€': ' euro ',
            '£': ' pound ',
            '¥': ' yen ',
            '₹': ' rupee ',
            '₽': ' ruble ',
            '₩': ' won ',
            '¢': ' cent ',
            '₦': ' naira ',
            '₨': ' rupee ',
            '₪': ' shekel ',
            '₫': ' dong ',
            '₡': ' colon ',
            '₢': ' cruzeiro ',
            '₣': ' franc ',
            '₤': ' lira ',
            '₥': ' mill ',
            '₧': ' peseta ',
            '₨': ' rupee ',
            '₩': ' won ',
            '₪': ' shekel ',
            '₫': ' dong ',

            # Special characters (ENHANCED)
            '©': ' copyright ',
            '®': ' registered trademark ',
            '™': ' trademark ',
            '°': ' degrees ',
            '§': ' section ',
            '¶': ' paragraph ',
            '†': ' dagger ',
            '‡': ' double dagger ',
            '•': ' bullet ',
            '‰': ' per mille ',
            '‱': ' per ten thousand ',

            # Mathematical symbols (ENHANCED)
            '±': ' plus or minus ',
            '×': ' times ',
            '÷': ' divided by ',
            '≠': ' not equal to ',
            '≤': ' less than or equal to ',
            '≥': ' greater than or equal to ',
            '≈': ' approximately equal to ',
            '∞': ' infinity ',
            '∑': ' sum ',
            '∏': ' product ',
            '∫': ' integral ',
            '∂': ' partial derivative ',
            '∆': ' delta ',
            '∇': ' nabla ',
            '√': ' square root ',
            '∛': ' cube root ',
            '∜': ' fourth root ',

            # Other common symbols
            '~': ' approximately ',
            '^': ' caret ',
            '|': ' pipe ',
            '\\': ' backslash ',
            '/': ' slash ',

            # Arrows and directional symbols (ENHANCED)
            '→': ' right arrow ',
            '←': ' left arrow ',
            '↑': ' up arrow ',
            '↓': ' down arrow ',
            '↗': ' up right arrow ',
            '↘': ' down right arrow ',
            '↙': ' down left arrow ',
            '↖': ' up left arrow ',
            '⇒': ' double right arrow ',
            '⇐': ' double left arrow ',
            '⇑': ' double up arrow ',
            '⇓': ' double down arrow ',
            '↔': ' left right arrow ',
            '⇔': ' double left right arrow ',
            
            # Mathematical symbols
            '±': ' plus or minus ',
            '×': ' times ',
            '÷': ' divided by ',
            '≈': ' approximately ',
            '≠': ' not equal to ',
            '≤': ' less than or equal to ',
            '≥': ' greater than or equal to ',
            '∞': ' infinity ',
        }
    
    def _load_quote_patterns(self) -> List[Tuple[str, str]]:
        """Load quote handling patterns to prevent 'in quat' issues"""
        return [
            # HTML entities for quotes
            (r'&quot;', ''),  # Remove HTML quote entities
            (r'&#34;', ''),   # Remove numeric HTML quote entities
            (r'&#x22;', ''),  # Remove hex HTML quote entities
            
            # Various quote types - remove them naturally
            (r'"([^"]*)"', r'\1'),  # Remove double quotes around text
            # (r'[''"]([^''"]*)[''"]', r'\1'),  # Remove smart quotes around text - DISABLED due to regex issues
            (r'`([^`]*)`', r'\1'),  # Remove backticks around text
            
            # Standalone quotes
            (r'\s*"\s*', ' '),  # Remove standalone double quotes
            # Smart quote patterns disabled due to regex syntax issues
            # (r'\s*'\s*', ' '),  # Remove standalone smart quotes
            # (r'\s*'\s*', ' '),  # Remove standalone smart quotes
            (r'\s*`\s*', ' '),  # Remove standalone backticks
        ]
    
    def _load_markdown_symbols(self) -> Dict[str, str]:
        """Load markdown symbol handling"""
        return {
            # Markdown formatting - handle based on preserve_markdown setting
            '**': '',  # Bold markers
            '__': '',  # Bold markers
            '*': '',   # Italic markers (single asterisk in markdown context)
            '_': '',   # Italic markers
            '~~': '',  # Strikethrough markers
            '`': '',   # Code markers
            
            # Markdown structural elements
            '#': '',   # Headers (when at start of line)
            '-': '',   # List items (when at start of line)
            '+': '',   # List items (when at start of line)
            '>': '',   # Blockquotes (when at start of line)
        }
    
    def _load_punctuation_rules(self) -> List[Tuple[str, str]]:
        """Load punctuation normalization rules (ENHANCED)"""
        return [
            # Multiple punctuation normalization (ENHANCED)
            (r'\.{3,}', ' ellipsis '),  # Multiple dots to spoken ellipsis
            (r'\?{2,}', '?'),    # Multiple question marks to single
            (r'!{2,}', '!'),     # Multiple exclamation marks to single
            (r'[.]{2}(?![.])', '..'),  # Two dots to two dots (not ellipsis)

            # Advanced dash and hyphen handling (NEW)
            (r'—', ' em dash '),  # Em dash
            (r'–', ' en dash '),  # En dash
            (r'−', ' minus '),    # Minus sign (different from hyphen)
            (r'‒', ' figure dash '),  # Figure dash
            (r'―', ' horizontal bar '),  # Horizontal bar

            # Advanced quotation marks (ENHANCED) - using escape sequences
            (r'\u201c', ''),  # Left double quotation mark
            (r'\u201d', ''),  # Right double quotation mark
            (r'\u2018', ''),  # Left single quotation mark
            (r'\u2019', ''),  # Right single quotation mark
            (r'\u201a', ''),  # Single low-9 quotation mark
            (r'\u201e', ''),  # Double low-9 quotation mark
            (r'\u2039', ''),  # Single left-pointing angle quotation mark
            (r'\u203a', ''),  # Single right-pointing angle quotation mark
            (r'\u00ab', ''),  # Left-pointing double angle quotation mark
            (r'\u00bb', ''),  # Right-pointing double angle quotation mark

            # Spacing around punctuation (ENHANCED)
            (r'\s*,\s*', ', '),  # Normalize comma spacing
            (r'\s*;\s*', '; '),  # Normalize semicolon spacing
            (r'\s*:\s*', ': '),  # Normalize colon spacing
            (r'\s*\.\s*', '. '), # Normalize period spacing

            # Parentheses and brackets spacing (ENHANCED)
            (r'\s*\(\s*', ' ('), # Normalize opening parenthesis
            (r'\s*\)\s*', ') '), # Normalize closing parenthesis
            (r'\s*\[\s*', ' ['), # Normalize opening bracket
            (r'\s*\]\s*', '] '), # Normalize closing bracket
            (r'\s*\{\s*', ' {'), # Normalize opening brace
            (r'\s*\}\s*', '} '), # Normalize closing brace

            # Advanced punctuation combinations (NEW)
            (r'[.]{2,3}[!?]', '.'),  # Ellipsis followed by exclamation/question
            (r'[!?][.]{2,3}', '.'),  # Exclamation/question followed by ellipsis
            (r'[!?]{1}[.]{1,}', '.'), # Mixed punctuation cleanup

            # Special spacing rules (NEW)
            (r'\s{2,}', ' '),    # Multiple spaces to single space
            (r'^\s+', ''),       # Remove leading whitespace
            (r'\s+$', ''),       # Remove trailing whitespace
        ]
    
    def process_symbols(self, text: str) -> str:
        """Process symbols and punctuation for natural TTS pronunciation"""
        logger.debug(f"Processing symbols in: {text[:100]}...")
        
        # Step 1: Handle HTML entities first (critical for apostrophe issues)
        if self.fix_html_entities:
            text = self._fix_html_entities(text)
        
        # Step 2: Handle quotes naturally to prevent "in quat" issues
        if self.handle_quotes_naturally:
            text = self._process_quotes(text)
        
        # Step 3: Handle markdown symbols if needed
        if self.preserve_markdown:
            text = self._preserve_markdown_context(text)
        else:
            text = self._remove_markdown_symbols(text)
        
        # Step 4: Process regular symbols
        text = self._process_regular_symbols(text)
        
        # Step 5: Normalize punctuation
        text = self._normalize_punctuation(text)
        
        # Step 6: Clean up whitespace
        text = self._clean_whitespace(text)
        
        logger.debug(f"Symbol processing result: {text[:100]}...")
        return text
    
    def _fix_html_entities(self, text: str) -> str:
        """Fix HTML entities that cause pronunciation issues"""
        # Handle specific problematic entities
        html_fixes = {
            '&#x27;': "'",  # Apostrophe that causes "x 27" pronunciation
            '&#39;': "'",   # Apostrophe
            '&apos;': "'",  # Apostrophe
            '&quot;': '',   # Quote - remove to prevent "in quat"
            '&#34;': '',    # Quote - remove to prevent "in quat"
            '&#x22;': '',   # Quote - remove to prevent "in quat"
            '&amp;': ' and ',  # Ampersand
            '&lt;': ' less than ',
            '&gt;': ' greater than ',
            '&nbsp;': ' ',  # Non-breaking space
        }
        
        for entity, replacement in html_fixes.items():
            text = text.replace(entity, replacement)
        
        # Use html.unescape for any remaining entities
        try:
            text = html.unescape(text)
        except Exception as e:
            logger.warning(f"HTML unescape failed: {e}")
        
        return text
    
    def _process_quotes(self, text: str) -> str:
        """Process quotes to prevent 'in quat' pronunciation issues"""
        for pattern, replacement in self.quote_patterns:
            text = re.sub(pattern, replacement, text)
        return text
    
    def _preserve_markdown_context(self, text: str) -> str:
        """Preserve markdown context while handling symbols"""
        # This is a more complex function that would analyze markdown structure
        # For now, implement basic preservation
        
        # Detect if we're in a markdown context
        has_markdown = any(marker in text for marker in ['**', '__', '*', '_', '`', '#'])
        
        if has_markdown:
            # Handle asterisks in markdown context differently
            # Single asterisk in markdown is italic, double is bold
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold markers
            text = re.sub(r'(?<!\*)\*(?!\*)([^*]+)\*(?!\*)', r'\1', text)  # Remove italic markers
            
            # Handle other markdown elements
            text = re.sub(r'`([^`]+)`', r'\1', text)  # Remove code markers
            text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # Remove header markers
        
        return text
    
    def _remove_markdown_symbols(self, text: str) -> str:
        """Remove markdown symbols when not preserving markdown"""
        for symbol, replacement in self.markdown_symbols.items():
            if symbol == '*':
                # Special handling for asterisk - check if it's markdown or standalone
                # If it's surrounded by word characters, it's likely markdown
                text = re.sub(r'\*([^*\s]+)\*', r'\1', text)  # Remove italic markers
                text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold markers
                # Standalone asterisks will be handled in regular symbol processing
            elif symbol == '-':
                # Special handling for hyphens - preserve ticker symbols like T-S-L-A
                # Only remove hyphens that are markdown list markers (at start of line)
                text = re.sub(r'^-\s+', '', text, flags=re.MULTILINE)  # Remove list markers
                text = re.sub(r'\n-\s+', '\n', text)  # Remove list markers after newlines
                # Preserve hyphens in ticker symbols and other contexts
            else:
                text = text.replace(symbol, replacement)

        return text
    
    def _process_regular_symbols(self, text: str) -> str:
        """Process regular symbols using the symbol mappings"""
        for symbol, replacement in self.symbol_mappings.items():
            if symbol == '*':
                # Special handling for asterisk to ensure correct pronunciation
                # Only replace standalone asterisks, not those in markdown
                text = re.sub(r'(?<!\*)\*(?!\*)', replacement, text)
            else:
                text = text.replace(symbol, replacement)
        
        return text
    
    def _normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation for better TTS pronunciation"""
        for pattern, replacement in self.punctuation_rules:
            text = re.sub(pattern, replacement, text)
        return text
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace after symbol processing"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)  # Ensure space after punctuation
        
        return text
    
    def analyze_symbols(self, text: str) -> Dict[str, List[str]]:
        """Analyze symbols in text and return information"""
        info = {
            'html_entities': [],
            'quotes': [],
            'markdown_symbols': [],
            'regular_symbols': [],
            'problematic_patterns': []
        }
        
        # Find HTML entities
        html_entities = re.findall(r'&[a-zA-Z]+;|&#\d+;|&#x[0-9a-fA-F]+;', text)
        info['html_entities'] = html_entities
        
        # Find quotes
        quotes = re.findall(r'["\'\`]', text)
        info['quotes'] = quotes
        
        # Find markdown symbols
        markdown_patterns = re.findall(r'\*+|_+|`+|#+', text)
        info['markdown_symbols'] = markdown_patterns
        
        # Find regular symbols
        regular_symbols = re.findall(r'[&+=%@#~^|\\/<>]', text)
        info['regular_symbols'] = regular_symbols
        
        # Find problematic patterns
        if '&#x27;' in text:
            info['problematic_patterns'].append('HTML apostrophe entity (causes x 27 pronunciation)')
        if '&quot;' in text:
            info['problematic_patterns'].append('HTML quote entity (causes in quat pronunciation)')
        if re.search(r'\*(?!\*)', text):
            info['problematic_patterns'].append('Standalone asterisk (may cause astrisk pronunciation)')
        
        return info
    
    def set_configuration(self, preserve_markdown: bool = None, 
                         handle_quotes_naturally: bool = None,
                         fix_html_entities: bool = None):
        """Set configuration options"""
        if preserve_markdown is not None:
            self.preserve_markdown = preserve_markdown
        if handle_quotes_naturally is not None:
            self.handle_quotes_naturally = handle_quotes_naturally
        if fix_html_entities is not None:
            self.fix_html_entities = fix_html_entities
        
        logger.info(f"Symbol processor configuration updated: "
                   f"preserve_markdown={self.preserve_markdown}, "
                   f"handle_quotes_naturally={self.handle_quotes_naturally}, "
                   f"fix_html_entities={self.fix_html_entities}")

    def process_context_aware_symbols(self, text: str) -> str:
        """Process symbols with context awareness (ENHANCED)"""
        logger.debug(f"Processing context-aware symbols in: {text[:100]}...")

        # Mathematical context detection
        text = self._process_mathematical_context(text)

        # File path context detection
        text = self._process_file_path_context(text)

        # URL context detection
        text = self._process_url_context(text)

        # Programming context detection
        text = self._process_programming_context(text)

        return text

    def _process_mathematical_context(self, text: str) -> str:
        """Process symbols in mathematical context"""
        # Detect mathematical expressions
        math_patterns = [
            (r'(\d+)\s*\+\s*(\d+)', r'\1 plus \2'),  # 2 + 3
            (r'(\d+)\s*-\s*(\d+)', r'\1 minus \2'),  # 5 - 2
            (r'(\d+)\s*\*\s*(\d+)', r'\1 times \2'), # 4 * 6
            (r'(\d+)\s*/\s*(\d+)', r'\1 divided by \2'), # 8 / 2
            (r'(\d+)\s*=\s*(\d+)', r'\1 equals \2'), # 10 = 10
            (r'(\d+)\s*%', r'\1 percent'),           # 50%
            (r'(\d+)°', r'\1 degrees'),              # 90°
        ]

        for pattern, replacement in math_patterns:
            text = re.sub(pattern, replacement, text)

        return text

    def _process_file_path_context(self, text: str) -> str:
        """Process symbols in file path context"""
        # Detect file paths and handle appropriately
        file_path_patterns = [
            # Windows paths: C:\folder\file.txt
            (r'([A-Z]):\\([^\\]+\\)*([^\\]+\.[a-zA-Z0-9]+)',
             lambda m: f"{m.group(1)} drive {m.group(0).replace('\\', ' backslash ').replace('.', ' dot ')}"),

            # Unix paths: /home/user/file.txt
            (r'/([^/\s]+/)*([^/\s]+\.[a-zA-Z0-9]+)',
             lambda m: m.group(0).replace('/', ' slash ').replace('.', ' dot ')),
        ]

        for pattern, replacement in file_path_patterns:
            if callable(replacement):
                text = re.sub(pattern, replacement, text)
            else:
                text = re.sub(pattern, replacement, text)

        return text

    def _process_url_context(self, text: str) -> str:
        """Process symbols in URL context"""
        # Detect URLs and handle appropriately
        url_patterns = [
            # HTTP/HTTPS URLs
            (r'https?://([^/\s]+)(/[^\s]*)?',
             lambda m: f"website {m.group(1).replace('.', ' dot ')}{' with path' if m.group(2) else ''}"),

            # Email addresses
            (r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
             lambda m: f"{m.group(1).replace('.', ' dot ')} at {m.group(2).replace('.', ' dot ')}"),
        ]

        for pattern, replacement in url_patterns:
            text = re.sub(pattern, replacement, text)

        return text

    def _process_programming_context(self, text: str) -> str:
        """Process symbols in programming context"""
        # Detect programming constructs
        programming_patterns = [
            # Function calls: function()
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\(\)', r'\1 function'),

            # Array access: array[index]
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^\]]+)\]', r'\1 array index \2'),

            # Object properties: object.property
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)', r'\1 dot \2'),
        ]

        for pattern, replacement in programming_patterns:
            text = re.sub(pattern, replacement, text)

        return text

    def analyze_symbol_complexity(self, text: str) -> Dict[str, any]:
        """Analyze text for symbol processing complexity (ENHANCED)"""
        analysis = {
            'symbol_count': 0,
            'html_entities': [],
            'special_characters': [],
            'mathematical_expressions': [],
            'file_paths': [],
            'urls': [],
            'programming_constructs': [],
            'complexity_score': 0,
            'processing_recommendations': []
        }

        # Count symbols
        symbols = set(char for char in text if not char.isalnum() and not char.isspace())
        analysis['symbol_count'] = len(symbols)

        # Detect HTML entities
        html_entities = re.findall(r'&[a-zA-Z0-9#x]+;', text)
        analysis['html_entities'] = html_entities

        # Detect special characters
        special_chars = [char for char in text if ord(char) > 127]
        analysis['special_characters'] = list(set(special_chars))

        # Detect mathematical expressions
        math_patterns = [r'\d+\s*[+\-*/=]\s*\d+', r'\d+%', r'\d+°']
        for pattern in math_patterns:
            matches = re.findall(pattern, text)
            analysis['mathematical_expressions'].extend(matches)

        # Detect file paths
        file_patterns = [r'[A-Z]:\\[^\\]+', r'/[^/\s]+/[^/\s]+']
        for pattern in file_patterns:
            matches = re.findall(pattern, text)
            analysis['file_paths'].extend(matches)

        # Detect URLs
        url_patterns = [r'https?://[^\s]+', r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}']
        for pattern in url_patterns:
            matches = re.findall(pattern, text)
            analysis['urls'].extend(matches)

        # Calculate complexity score
        analysis['complexity_score'] = (
            len(analysis['html_entities']) * 3 +
            len(analysis['special_characters']) * 2 +
            len(analysis['mathematical_expressions']) * 2 +
            len(analysis['file_paths']) * 2 +
            len(analysis['urls']) * 2 +
            analysis['symbol_count']
        )

        # Generate recommendations
        if analysis['html_entities']:
            analysis['processing_recommendations'].append('Enable HTML entity processing')
        if analysis['special_characters']:
            analysis['processing_recommendations'].append('Use enhanced symbol mappings')
        if analysis['mathematical_expressions']:
            analysis['processing_recommendations'].append('Enable mathematical context processing')
        if analysis['file_paths'] or analysis['urls']:
            analysis['processing_recommendations'].append('Enable context-aware processing')

        return analysis
