#!/usr/bin/env python3
"""
Windows Startup Validator for LiteTTS

This script validates that LiteTTS can start up correctly on Windows 10
without the Unicode encoding errors and other Windows-specific issues.
"""

import sys
import os
import platform
import warnings
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, '.')

class WindowsStartupValidator:
    """Validates Windows startup process"""
    
    def __init__(self):
        self.validation_results: Dict[str, Any] = {}
        self.startup_log: List[str] = []
        
    def log_step(self, step: str, success: bool, details: str = ""):
        """Log a validation step"""
        status = "✅" if success else "❌"
        message = f"{status} {step}"
        if details:
            message += f": {details}"
        
        print(message)
        self.startup_log.append(message)
        self.validation_results[step] = {
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
    
    def validate_environment(self) -> bool:
        """Validate the Windows environment"""
        print("🔍 Validating Windows Environment...")
        
        # Check platform
        is_windows = platform.system() == "Windows"
        self.log_step("Windows Platform", is_windows, f"Platform: {platform.system()}")
        
        if not is_windows:
            return False
        
        # Check Python version
        python_version = sys.version_info
        python_ok = python_version >= (3, 8)
        self.log_step(
            "Python Version", 
            python_ok, 
            f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        )
        
        # Check console encoding
        stdout_encoding = getattr(sys.stdout, 'encoding', 'unknown')
        stderr_encoding = getattr(sys.stderr, 'encoding', 'unknown')
        self.log_step(
            "Console Encoding", 
            True, 
            f"stdout: {stdout_encoding}, stderr: {stderr_encoding}"
        )
        
        return is_windows and python_ok
    
    def validate_early_imports(self) -> bool:
        """Validate that early imports work without warnings"""
        print("\n📦 Validating Early Imports...")
        
        # Capture warnings
        captured_warnings = []
        def warning_handler(message, category, filename, lineno, file=None, line=None):
            captured_warnings.append(f"{category.__name__}: {message}")
        
        old_showwarning = warnings.showwarning
        warnings.showwarning = warning_handler
        
        try:
            # Test critical early imports
            import warnings as warnings_module
            self.log_step("Warnings Module", True)
            
            # Test platform emoji utilities
            from LiteTTS.utils.platform_emojis import is_windows_with_encoding_issues, format_log_message
            encoding_issues = is_windows_with_encoding_issues()
            self.log_step("Platform Emojis", True, f"Encoding issues detected: {encoding_issues}")
            
            # Test startup module
            from LiteTTS.startup import configure_windows_console
            console_result = configure_windows_console()
            self.log_step("Windows Console Config", console_result, f"Configuration result: {console_result}")
            
            # Test deprecation warnings
            from LiteTTS.utils.deprecation_warnings import initialize_warning_suppression
            initialize_warning_suppression()
            self.log_step("Warning Suppression", True)
            
            # Check for pkg_resources warnings
            pkg_warnings = [w for w in captured_warnings if 'pkg_resources' in w]
            self.log_step(
                "pkg_resources Warnings", 
                len(pkg_warnings) == 0, 
                f"Found {len(pkg_warnings)} pkg_resources warnings"
            )
            
            return len(pkg_warnings) == 0
            
        except Exception as e:
            self.log_step("Early Imports", False, str(e))
            return False
        finally:
            warnings.showwarning = old_showwarning
    
    def validate_emoji_display(self) -> bool:
        """Validate that emojis can be displayed without errors"""
        print("\n🎨 Validating Emoji Display...")
        
        try:
            from LiteTTS.utils.platform_emojis import format_log_message, get_emoji
            
            # Test various emojis
            test_emojis = [
                ('rocket', '🚀'),
                ('clipboard', '📋'),
                ('check', '✅'),
                ('folder', '📁'),
                ('chart', '📊')
            ]
            
            emoji_results = []
            for name, emoji in test_emojis:
                try:
                    # Test emoji display
                    safe_emoji = get_emoji(name, f'[{name.upper()}]')
                    message = format_log_message(name, f"Test message with {name}")
                    
                    # Try to print it
                    print(f"  {message}")
                    emoji_results.append(True)
                    
                except UnicodeEncodeError as e:
                    emoji_results.append(False)
                    print(f"  ❌ Failed to display {name}: {e}")
            
            success = all(emoji_results)
            self.log_step(
                "Emoji Display", 
                success, 
                f"{sum(emoji_results)}/{len(emoji_results)} emojis displayed successfully"
            )
            
            return success
            
        except Exception as e:
            self.log_step("Emoji Display", False, str(e))
            return False
    
    def validate_file_operations(self) -> bool:
        """Validate file operations work with UTF-8"""
        print("\n📁 Validating File Operations...")
        
        try:
            # Test config file reading
            config_files = [
                "config/settings.json",
                "config.json"
            ]
            
            config_found = False
            for config_file in config_files:
                if Path(config_file).exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        config_found = True
                        self.log_step("Config File Reading", True, f"Successfully read {config_file}")
                        break
                    except Exception as e:
                        self.log_step("Config File Reading", False, f"Failed to read {config_file}: {e}")
            
            if not config_found:
                self.log_step("Config File Reading", True, "No config files found (using defaults)")
            
            # Test HTML file reading (dashboard)
            dashboard_file = Path("static/dashboard/index.html")
            if dashboard_file.exists():
                try:
                    with open(dashboard_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    self.log_step("HTML File Reading", True, f"Read {len(html_content)} characters")
                except Exception as e:
                    self.log_step("HTML File Reading", False, str(e))
                    return False
            else:
                self.log_step("HTML File Reading", True, "Dashboard file not found (optional)")
            
            return True
            
        except Exception as e:
            self.log_step("File Operations", False, str(e))
            return False
    
    def validate_logging_system(self) -> bool:
        """Validate logging system works without Unicode errors"""
        print("\n📝 Validating Logging System...")
        
        try:
            from LiteTTS.logging_config import setup_logging
            import logging
            
            # Setup logging
            setup_logging(level="INFO")
            
            # Test logging with emojis
            logger = logging.getLogger("startup_validator")
            
            # These should not raise UnicodeEncodeError
            logger.info("🚀 Testing emoji logging")
            logger.info("📋 Testing clipboard emoji")
            logger.info("✅ Testing check mark emoji")
            
            self.log_step("Logging System", True, "Emoji logging completed without errors")
            return True
            
        except Exception as e:
            self.log_step("Logging System", False, str(e))
            return False
    
    def validate_core_imports(self) -> bool:
        """Validate core LiteTTS modules can be imported"""
        print("\n🔧 Validating Core Imports...")
        
        try:
            # Test core module imports
            from LiteTTS.config import config
            self.log_step("Config Module", True)
            
            from LiteTTS import __version__
            self.log_step("Package Version", True, f"Version: {__version__}")
            
            # Test optional imports
            try:
                from LiteTTS.audio.watermarking import WatermarkingManager
                self.log_step("Watermarking Module", True)
            except ImportError:
                self.log_step("Watermarking Module", True, "Optional module not available")
            
            return True
            
        except Exception as e:
            self.log_step("Core Imports", False, str(e))
            return False
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete Windows startup validation"""
        print("🪟 Windows Startup Validation for LiteTTS")
        print("=" * 50)
        
        # Run validation steps
        steps = [
            self.validate_environment,
            self.validate_early_imports,
            self.validate_emoji_display,
            self.validate_file_operations,
            self.validate_logging_system,
            self.validate_core_imports
        ]
        
        all_passed = True
        for step in steps:
            try:
                result = step()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"❌ Validation step failed: {e}")
                all_passed = False
        
        # Generate summary
        print("\n" + "=" * 50)
        print("📊 Validation Summary")
        print("=" * 50)
        
        passed_count = sum(1 for r in self.validation_results.values() if r['success'])
        total_count = len(self.validation_results)
        
        print(f"Steps Passed: {passed_count}/{total_count}")
        print(f"Overall Success: {'✅ YES' if all_passed else '❌ NO'}")
        
        if all_passed:
            print("\n🎉 Windows startup validation PASSED!")
            print("LiteTTS should start correctly on Windows 10.")
        else:
            print("\n❌ Windows startup validation FAILED!")
            print("Please review the failed steps above.")
            
            # Show failed steps
            failed_steps = [k for k, v in self.validation_results.items() if not v['success']]
            if failed_steps:
                print(f"Failed steps: {', '.join(failed_steps)}")
        
        # Save results
        results = {
            "overall_success": all_passed,
            "passed_steps": passed_count,
            "total_steps": total_count,
            "validation_results": self.validation_results,
            "startup_log": self.startup_log,
            "platform": platform.platform(),
            "python_version": sys.version,
            "timestamp": time.time()
        }
        
        results_file = Path("test_results") / "windows_startup_validation.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return results

def main():
    """Main validation execution"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print(__doc__)
        return
    
    validator = WindowsStartupValidator()
    results = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_success'] else 1)

if __name__ == "__main__":
    main()
