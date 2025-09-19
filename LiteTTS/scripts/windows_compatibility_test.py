#!/usr/bin/env python3
"""
Windows 10 Compatibility Test Script for LiteTTS

This script validates that all Windows compatibility fixes are working correctly.
Run this script on Windows 10 to verify the application will work properly.
"""

import sys
import os
import platform
import warnings
import tempfile
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import subprocess
import time

# Add project root to path
sys.path.insert(0, '.')

class WindowsCompatibilityTester:
    """Comprehensive Windows compatibility testing"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.failed_tests: List[str] = []
        self.warnings_captured: List[str] = []
        
        # Setup logging to capture warnings
        self.setup_test_logging()
    
    def setup_test_logging(self):
        """Setup logging to capture warnings and test output"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Capture warnings
        def warning_handler(message, category, filename, lineno, file=None, line=None):
            warning_str = f"{category.__name__}: {message} ({filename}:{lineno})"
            self.warnings_captured.append(warning_str)
            print(f"WARNING CAPTURED: {warning_str}")
        
        warnings.showwarning = warning_handler
    
    def log_test_result(self, test_name: str, passed: bool, details: str = "", error: str = ""):
        """Log a test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "error": error,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"      Details: {details}")
        if error:
            print(f"      Error: {error}")
        
        if not passed:
            self.failed_tests.append(test_name)
    
    def test_platform_detection(self) -> bool:
        """Test that we're running on Windows"""
        try:
            is_windows = platform.system() == "Windows"
            version = platform.version()
            
            self.log_test_result(
                "Platform Detection",
                is_windows,
                f"Platform: {platform.system()}, Version: {version}",
                "" if is_windows else "Not running on Windows"
            )
            return is_windows
        except Exception as e:
            self.log_test_result("Platform Detection", False, "", str(e))
            return False
    
    def test_unicode_encoding_detection(self) -> bool:
        """Test Unicode encoding detection logic"""
        try:
            from LiteTTS.utils.platform_emojis import is_windows_with_encoding_issues
            
            # Test the detection function
            has_encoding_issues = is_windows_with_encoding_issues()
            
            # Test emoji encoding
            test_emoji = '🚀'
            stdout_encoding = getattr(sys.stdout, 'encoding', 'unknown')
            
            try:
                test_emoji.encode(stdout_encoding)
                can_encode = True
            except UnicodeEncodeError:
                can_encode = False
            
            self.log_test_result(
                "Unicode Encoding Detection",
                True,  # Always pass if function works
                f"Encoding issues detected: {has_encoding_issues}, "
                f"Stdout encoding: {stdout_encoding}, "
                f"Can encode emoji: {can_encode}"
            )
            return True
            
        except Exception as e:
            self.log_test_result("Unicode Encoding Detection", False, "", str(e))
            return False
    
    def test_console_configuration(self) -> bool:
        """Test Windows console configuration"""
        try:
            from LiteTTS.startup import configure_windows_console
            
            # Test console configuration
            result = configure_windows_console()
            
            # Test console output
            test_message = "Test message with emoji: 🚀 📋 ✅"
            try:
                print(test_message)
                console_output_works = True
            except UnicodeEncodeError:
                console_output_works = False
            
            self.log_test_result(
                "Console Configuration",
                result and console_output_works,
                f"Configuration result: {result}, Console output works: {console_output_works}"
            )
            return result and console_output_works
            
        except Exception as e:
            self.log_test_result("Console Configuration", False, "", str(e))
            return False
    
    def test_file_encoding_operations(self) -> bool:
        """Test file operations with UTF-8 encoding"""
        try:
            # Test writing and reading UTF-8 files
            test_content = "Test content with Unicode: 🚀 📋 ✅ 中文 العربية"
            
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
                f.write(test_content)
                temp_file = f.name
            
            # Test reading the file
            with open(temp_file, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            # Clean up
            os.unlink(temp_file)
            
            success = read_content == test_content
            
            self.log_test_result(
                "File Encoding Operations",
                success,
                f"Content match: {success}, Length: {len(read_content)}"
            )
            return success
            
        except Exception as e:
            self.log_test_result("File Encoding Operations", False, "", str(e))
            return False
    
    def test_json_file_operations(self) -> bool:
        """Test JSON file operations with UTF-8 encoding"""
        try:
            # Test JSON with Unicode content
            test_data = {
                "message": "Test with Unicode: 🚀 📋 ✅",
                "languages": ["English", "中文", "العربية", "Русский"],
                "emoji": "🎉"
            }
            
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
                temp_file = f.name
            
            # Test reading the JSON file
            with open(temp_file, 'r', encoding='utf-8') as f:
                read_data = json.load(f)
            
            # Clean up
            os.unlink(temp_file)
            
            success = read_data == test_data
            
            self.log_test_result(
                "JSON File Operations",
                success,
                f"Data match: {success}, Keys: {list(read_data.keys())}"
            )
            return success
            
        except Exception as e:
            self.log_test_result("JSON File Operations", False, "", str(e))
            return False
    
    def test_warning_suppression(self) -> bool:
        """Test that pkg_resources warnings are suppressed"""
        try:
            # Clear captured warnings
            self.warnings_captured.clear()
            
            # Try to trigger pkg_resources warning (if perth is available)
            try:
                import perth
                # This should not generate warnings due to our suppression
            except ImportError:
                # perth not available, that's fine
                pass
            
            # Check for pkg_resources warnings
            pkg_warnings = [w for w in self.warnings_captured if 'pkg_resources' in w.lower()]
            
            success = len(pkg_warnings) == 0
            
            self.log_test_result(
                "Warning Suppression",
                success,
                f"Total warnings: {len(self.warnings_captured)}, "
                f"pkg_resources warnings: {len(pkg_warnings)}"
            )
            return success
            
        except Exception as e:
            self.log_test_result("Warning Suppression", False, "", str(e))
            return False
    
    def test_logging_system(self) -> bool:
        """Test that logging system works with emojis"""
        try:
            from LiteTTS.logging_config import setup_logging
            from LiteTTS.utils.platform_emojis import format_log_message
            
            # Setup logging
            setup_logging(level="DEBUG")
            
            # Test logging with emojis
            logger = logging.getLogger("test_logger")
            
            # This should not raise UnicodeEncodeError
            logger.info(format_log_message('rocket', 'Test message with emoji'))
            logger.info("Direct emoji test: 🚀 📋 ✅")
            
            self.log_test_result(
                "Logging System",
                True,
                "Logging with emojis completed without errors"
            )
            return True
            
        except Exception as e:
            self.log_test_result("Logging System", False, "", str(e))
            return False
    
    def test_import_system(self) -> bool:
        """Test that core LiteTTS modules can be imported"""
        try:
            modules_to_test = [
                'LiteTTS.config',
                'LiteTTS.utils.platform_emojis',
                'LiteTTS.startup',
                'LiteTTS.logging_config'
            ]
            
            imported_modules = []
            failed_imports = []
            
            for module in modules_to_test:
                try:
                    __import__(module)
                    imported_modules.append(module)
                except ImportError as e:
                    failed_imports.append(f"{module}: {e}")
            
            success = len(failed_imports) == 0
            
            self.log_test_result(
                "Import System",
                success,
                f"Imported: {len(imported_modules)}, Failed: {len(failed_imports)}",
                "; ".join(failed_imports) if failed_imports else ""
            )
            return success
            
        except Exception as e:
            self.log_test_result("Import System", False, "", str(e))
            return False
    
    def run_all_tests(self) -> Tuple[bool, Dict[str, Any]]:
        """Run all Windows compatibility tests"""
        print("=" * 60)
        print("🪟 Windows 10 Compatibility Test Suite")
        print("=" * 60)
        print()
        
        # Run all tests
        tests = [
            self.test_platform_detection,
            self.test_unicode_encoding_detection,
            self.test_console_configuration,
            self.test_file_encoding_operations,
            self.test_json_file_operations,
            self.test_warning_suppression,
            self.test_logging_system,
            self.test_import_system
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_test_result(test_name, False, "", f"Test execution failed: {e}")
            print()  # Add spacing between tests
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['passed']])
        failed_tests = total_tests - passed_tests
        
        success = failed_tests == 0
        
        summary = {
            "overall_success": success,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "failed_test_names": self.failed_tests,
            "warnings_captured": self.warnings_captured,
            "test_results": self.test_results
        }
        
        print("=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if success:
            print("🎉 ALL TESTS PASSED! LiteTTS should work correctly on Windows 10.")
        else:
            print("❌ SOME TESTS FAILED. Please review the failures above.")
            print("Failed tests:", ", ".join(self.failed_tests))
        
        print()
        print(f"Warnings captured: {len(self.warnings_captured)}")
        if self.warnings_captured:
            print("Warnings:")
            for warning in self.warnings_captured[:5]:  # Show first 5
                print(f"  - {warning}")
            if len(self.warnings_captured) > 5:
                print(f"  ... and {len(self.warnings_captured) - 5} more")
        
        return success, summary

def main():
    """Main test execution"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print(__doc__)
        return
    
    tester = WindowsCompatibilityTester()
    success, summary = tester.run_all_tests()
    
    # Save results to file
    results_file = Path("test_results") / "windows_compatibility_results.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
