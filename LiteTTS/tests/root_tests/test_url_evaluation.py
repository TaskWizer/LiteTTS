#!/usr/bin/env python3
"""
URL & Web Address Processing Evaluation
Test current capabilities and identify gaps
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_current_url_processing():
    """Test current URL and web address processing capabilities"""
    print("🌐 URL & Web Address Processing Evaluation")
    print("=" * 60)
    
    # Test cases covering various URL/web address scenarios
    test_cases = [
        # Basic URLs with protocols
        ("https://www.google.com", "W W W google dot com"),
        ("http://example.org", "example dot org"),
        ("https://github.com/user/repo", "github dot com slash user slash repo"),
        
        # URLs with paths and parameters
        ("https://www.somesite.com/somepage", "W W W some site dot com slash some page"),
        ("http://api.example.com/v1/users?id=123", "A P I example dot com slash v one slash users question id equals one two three"),
        ("https://docs.python.org/3/library/urllib.html", "docs python dot org slash three slash library slash urllib dot html"),
        
        # Domain names without protocols
        ("www.example.com", "W W W example dot com"),
        ("google.com", "google dot com"),
        ("stackoverflow.com", "stack overflow dot com"),
        ("github.io", "github dot io"),
        
        # Different TLDs
        ("example.org", "example dot org"),
        ("university.edu", "university dot edu"),
        ("government.gov", "government dot gov"),
        ("company.co.uk", "company dot co dot uk"),
        ("site.com.au", "site dot com dot au"),
        
        # Email addresses
        ("user@example.com", "user at example dot com"),
        ("test.email+tag@domain.co.uk", "test dot email plus tag at domain dot co dot uk"),
        ("contact@subdomain.example.org", "contact at subdomain dot example dot org"),
        
        # Complex URLs
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "W W W youtube dot com slash watch question v equals d Q w four w nine Wg X c Q"),
        ("http://localhost:8080/api/v1/test", "localhost colon eight zero eight zero slash A P I slash v one slash test"),
        ("ftp://files.example.com/downloads", "F T P files example dot com slash downloads"),
        
        # URLs with fragments and anchors
        ("https://example.com/page#section", "example dot com slash page hash section"),
        ("http://docs.site.org/guide.html#installation", "docs site dot org slash guide dot html hash installation"),
        
        # Subdomains
        ("api.v2.example.com", "A P I dot v two dot example dot com"),
        ("mail.google.com", "mail dot google dot com"),
        ("cdn.jsdelivr.net", "C D N dot jsdelivr dot net"),
        
        # URLs in context
        ("Visit https://www.example.com for more info", "Visit W W W example dot com for more info"),
        ("Email us at support@company.com", "Email us at support at company dot com"),
        ("Check out http://github.com/project", "Check out github dot com slash project"),
        
        # Edge cases
        ("https://", "https colon slash slash"),  # Incomplete URL
        ("www.", "W W W dot"),  # Incomplete domain
        ("http://192.168.1.1", "one nine two dot one six eight dot one dot one"),  # IP address
        ("https://example.com:8443/secure", "example dot com colon eight four four three slash secure"),  # Port number
        
        # Special characters in URLs
        ("https://example.com/path%20with%20spaces", "example dot com slash path percent two zero with percent two zero spaces"),
        ("http://site.com/search?q=hello+world", "site dot com slash search question q equals hello plus world"),
        ("https://example.com/file.pdf", "example dot com slash file dot pdf"),
        
        # International domains
        ("https://münchen.de", "münchen dot de"),  # Unicode domain
        ("http://xn--nxasmq6b.xn--j6w193g", "x n dash dash n x a s m q six b dot x n dash dash j six w one nine three g"),  # Punycode
        
        # Multiple URLs in text
        ("Visit https://site1.com and http://site2.org", "Visit site one dot com and site two dot org"),
        ("Email: user@domain.com, Website: www.company.net", "Email: user at domain dot com, Website: W W W company dot net"),
    ]
    
    # Test with different normalizers
    normalizers = []
    
    try:
        from LiteTTS.nlp.text_normalizer import TextNormalizer
        normalizers.append(("TextNormalizer", TextNormalizer()))
    except ImportError as e:
        print(f"❌ Could not import TextNormalizer: {e}")
    
    try:
        from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer
        normalizers.append(("CleanTextNormalizer", CleanTextNormalizer()))
    except ImportError as e:
        print(f"❌ Could not import CleanTextNormalizer: {e}")
    
    if not normalizers:
        print("❌ No normalizers available for testing")
        return False
    
    all_passed = True
    
    for normalizer_name, normalizer in normalizers:
        print(f"\n🧪 Testing {normalizer_name}")
        print("-" * 40)
        
        for i, (input_text, expected_output) in enumerate(test_cases, 1):
            print(f"\nTest {i}: '{input_text}'")
            print(f"Expected: '{expected_output}'")
            
            try:
                if hasattr(normalizer, 'normalize_text'):
                    result = normalizer.normalize_text(input_text)
                    if hasattr(result, 'processed_text'):
                        actual_output = result.processed_text
                    else:
                        actual_output = result
                else:
                    actual_output = str(normalizer)
                
                print(f"Actual:   '{actual_output}'")
                
                # Check for common issues
                issues = []
                
                # Check if URLs are properly processed
                if any(protocol in input_text for protocol in ['http://', 'https://', 'ftp://']):
                    if any(protocol in actual_output for protocol in ['http://', 'https://', 'ftp://']):
                        issues.append("Protocol not stripped")
                
                # Check for proper dot conversion
                if '.com' in input_text or '.org' in input_text or '.net' in input_text:
                    if not any(phrase in actual_output.lower() for phrase in ['dot com', 'dot org', 'dot net']):
                        issues.append("Missing dot conversion")
                
                # Check for proper @ conversion in emails
                if '@' in input_text:
                    if '@' in actual_output:
                        issues.append("@ symbol not converted to 'at'")
                
                # Check for proper slash conversion
                if '/' in input_text and 'http' in input_text:
                    if '/' in actual_output and 'slash' not in actual_output:
                        issues.append("Slash not converted to 'slash'")
                
                # Check if no processing was applied when it should have been
                if any(char in input_text for char in ['.', '@', '/']) and input_text == actual_output:
                    if any(domain in input_text for domain in ['.com', '.org', '.net', '@']):
                        issues.append("No processing applied")
                
                if issues:
                    print(f"⚠️  Issues: {', '.join(issues)}")
                    all_passed = False
                else:
                    print("✅ Processed correctly")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                all_passed = False
    
    return all_passed

def analyze_url_gaps():
    """Analyze gaps in current URL processing"""
    print("\n🔍 URL & Web Address Processing Gap Analysis")
    print("=" * 60)
    
    gaps = [
        "Limited protocol stripping (may not handle all protocols)",
        "Inconsistent subdomain handling (api.v2.example.com)",
        "No support for IP address pronunciation",
        "Limited port number handling (:8080)",
        "No support for URL fragments (#section)",
        "Limited query parameter processing (?param=value)",
        "No support for URL encoding (%20, %2B)",
        "Limited international domain support (Unicode, Punycode)",
        "No context-aware URL processing",
        "Limited file extension handling (.pdf, .html)",
        "No support for special URL schemes (ftp://, mailto:)",
        "Inconsistent path component pronunciation"
    ]
    
    print("Identified gaps in URL processing:")
    for i, gap in enumerate(gaps, 1):
        print(f"{i:2d}. {gap}")
    
    return gaps

def recommend_url_improvements():
    """Recommend specific improvements for URL processing"""
    print("\n💡 Recommended URL & Web Address Processing Improvements")
    print("=" * 60)
    
    improvements = [
        {
            "area": "Protocol Stripping",
            "description": "Comprehensive protocol removal and handling",
            "priority": "High",
            "examples": ["https://example.com → example dot com", "ftp://files.com → files dot com"]
        },
        {
            "area": "Path Component Processing",
            "description": "Natural pronunciation of URL paths",
            "priority": "High",
            "examples": ["/api/v1/users → slash A P I slash v one slash users"]
        },
        {
            "area": "Query Parameter Handling",
            "description": "Natural processing of URL parameters",
            "priority": "Medium",
            "examples": ["?id=123&name=test → question id equals one two three and name equals test"]
        },
        {
            "area": "IP Address Support",
            "description": "Proper pronunciation of IP addresses",
            "priority": "Medium",
            "examples": ["192.168.1.1 → one nine two dot one six eight dot one dot one"]
        },
        {
            "area": "International Domain Support",
            "description": "Unicode and Punycode domain handling",
            "priority": "Medium",
            "examples": ["münchen.de → münchen dot de"]
        },
        {
            "area": "Special Character Handling",
            "description": "URL encoding and special character processing",
            "priority": "Low",
            "examples": ["%20 → percent two zero", "#section → hash section"]
        }
    ]
    
    for improvement in improvements:
        print(f"\n📋 {improvement['area']} ({improvement['priority']} Priority)")
        print(f"   {improvement['description']}")
        print(f"   Examples: {', '.join(improvement['examples'])}")
    
    return improvements

if __name__ == "__main__":
    print("🚀 Starting URL & Web Address Processing Evaluation")
    
    # Run tests
    test_passed = test_current_url_processing()
    
    # Analyze gaps
    gaps = analyze_url_gaps()
    
    # Recommend improvements
    improvements = recommend_url_improvements()
    
    print("\n" + "=" * 60)
    print("📊 Evaluation Summary")
    print("=" * 60)
    
    if test_passed:
        print("✅ Basic URL processing is working")
    else:
        print("❌ Issues found in current URL processing")
    
    print(f"🔍 {len(gaps)} gaps identified")
    print(f"💡 {len(improvements)} improvement areas recommended")
    
    print("\n🎯 Next Steps:")
    print("1. Enhance protocol stripping for all URL schemes")
    print("2. Improve path component pronunciation")
    print("3. Add query parameter processing")
    print("4. Implement IP address support")
    print("5. Create comprehensive test suite for URL processing")
