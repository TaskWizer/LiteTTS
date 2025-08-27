#!/usr/bin/env python3
"""
Configuration validation and optimization script
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

def validate_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Validate and analyze configuration"""
    
    config_file = Path(config_path)
    if not config_file.exists():
        return {"error": f"Config file not found: {config_path}"}
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        return {"error": f"Failed to parse config: {e}"}
    
    issues = []
    recommendations = []
    
    # Validate model configuration
    model_config = config.get("model", {})
    default_variant = model_config.get("default_variant", "")
    
    if not default_variant.endswith(".onnx"):
        issues.append("Model default_variant should end with .onnx")
    
    if default_variant == "model_uint8.onnx":
        recommendations.append("Consider using model_q4f16.onnx for better performance/quality balance")
    
    # Validate performance configuration
    perf_config = config.get("performance", {})
    max_retry_attempts = perf_config.get("max_retry_attempts", 3)
    
    if max_retry_attempts > 3:
        recommendations.append(f"max_retry_attempts is {max_retry_attempts}, consider reducing to 2-3 for better performance")
    
    timeout_seconds = perf_config.get("timeout_seconds", 30)
    if timeout_seconds < 10:
        issues.append(f"timeout_seconds is {timeout_seconds}, should be at least 10 seconds")
    
    # Validate cache configuration
    cache_config = config.get("cache", {})
    if not cache_config.get("enabled", True):
        recommendations.append("Cache is disabled, enabling it can significantly improve performance")
    
    audio_cache_mb = cache_config.get("audio_memory_cache_mb", 256)
    if audio_cache_mb < 128:
        recommendations.append(f"audio_memory_cache_mb is {audio_cache_mb}MB, consider increasing to 256MB+ for better caching")
    
    # Validate server configuration
    server_config = config.get("server", {})
    port = server_config.get("port", 8080)
    
    if port < 1024 and port != 80 and port != 443:
        issues.append(f"Port {port} requires root privileges, consider using port >= 1024")
    
    workers = server_config.get("workers", 1)
    if workers > 1:
        recommendations.append("Multiple workers may not improve performance for TTS workloads, consider using 1 worker")
    
    # Check for missing sections
    required_sections = ["model", "voice", "audio", "server", "performance", "cache"]
    for section in required_sections:
        if section not in config:
            issues.append(f"Missing required configuration section: {section}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "recommendations": recommendations,
        "config_summary": {
            "model_variant": default_variant,
            "cache_enabled": cache_config.get("enabled", False),
            "server_port": port,
            "max_retries": max_retry_attempts,
            "timeout": timeout_seconds,
            "audio_cache_mb": audio_cache_mb
        }
    }

def optimize_config(config_path: str = "config.json", backup: bool = True) -> Dict[str, Any]:
    """Apply recommended optimizations to configuration"""
    
    config_file = Path(config_path)
    if not config_file.exists():
        return {"error": f"Config file not found: {config_path}"}
    
    # Create backup if requested
    if backup:
        backup_path = config_file.with_suffix('.json.backup')
        config_file.rename(backup_path)
        print(f"📁 Backup created: {backup_path}")
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        return {"error": f"Failed to parse config: {e}"}
    
    changes = []
    
    # Optimize model configuration
    if config.get("model", {}).get("default_variant") == "model_uint8.onnx":
        config["model"]["default_variant"] = "model_q4f16.onnx"
        changes.append("Changed model variant to q4f16 for better performance")
    
    # Optimize performance configuration
    if config.get("performance", {}).get("max_retry_attempts", 3) > 3:
        config["performance"]["max_retry_attempts"] = 2
        changes.append("Reduced max_retry_attempts to 2")
    
    if not config.get("performance", {}).get("preload_models", False):
        config["performance"]["preload_models"] = True
        changes.append("Enabled model preloading")
    
    # Optimize cache configuration
    if not config.get("cache", {}).get("enabled", True):
        config["cache"]["enabled"] = True
        changes.append("Enabled caching")
    
    if config.get("cache", {}).get("audio_memory_cache_mb", 256) < 256:
        config["cache"]["audio_memory_cache_mb"] = 256
        changes.append("Increased audio cache to 256MB")
    
    # Save optimized configuration
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "changes": changes,
            "config_path": str(config_file)
        }
    except Exception as e:
        return {"error": f"Failed to save config: {e}"}

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate and optimize Kokoro TTS configuration")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    parser.add_argument("--optimize", action="store_true", help="Apply optimizations")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backup when optimizing")
    
    args = parser.parse_args()
    
    print("🔧 Kokoro TTS Configuration Validator")
    print("=" * 50)
    
    # Validate configuration
    result = validate_config(args.config)
    
    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)
    
    print(f"📋 Configuration Summary:")
    summary = result["config_summary"]
    print(f"  Model Variant: {summary['model_variant']}")
    print(f"  Cache Enabled: {summary['cache_enabled']}")
    print(f"  Server Port: {summary['server_port']}")
    print(f"  Max Retries: {summary['max_retries']}")
    print(f"  Timeout: {summary['timeout']}s")
    print(f"  Audio Cache: {summary['audio_cache_mb']}MB")
    
    if result["issues"]:
        print(f"\n❌ Issues Found ({len(result['issues'])}):")
        for issue in result["issues"]:
            print(f"  • {issue}")
    else:
        print(f"\n✅ No critical issues found")
    
    if result["recommendations"]:
        print(f"\n💡 Recommendations ({len(result['recommendations'])}):")
        for rec in result["recommendations"]:
            print(f"  • {rec}")
    
    # Apply optimizations if requested
    if args.optimize:
        print(f"\n🔧 Applying optimizations...")
        opt_result = optimize_config(args.config, backup=not args.no_backup)
        
        if "error" in opt_result:
            print(f"❌ Optimization failed: {opt_result['error']}")
            sys.exit(1)
        
        if opt_result["changes"]:
            print(f"✅ Applied {len(opt_result['changes'])} optimizations:")
            for change in opt_result["changes"]:
                print(f"  • {change}")
            print(f"📁 Updated: {opt_result['config_path']}")
        else:
            print("✅ Configuration already optimal")
    
    print(f"\n🎯 Overall Status: {'✅ Valid' if result['valid'] else '⚠️ Needs Attention'}")

if __name__ == "__main__":
    main()