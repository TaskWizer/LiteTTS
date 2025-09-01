#!/usr/bin/env python3
"""
Dynamic voice model downloader with HuggingFace API integration
"""

import os
import hashlib
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass
import logging
import json
import re

logger = logging.getLogger(__name__)

@dataclass
class DownloadProgress:
    """Download progress information"""
    filename: str
    downloaded_bytes: int
    total_bytes: int
    percentage: float
    speed_mbps: float = 0.0

@dataclass
class VoiceFileInfo:
    """Information about a voice file from HuggingFace"""
    name: str
    path: str
    size: int
    sha: str
    download_url: str

class VoiceDownloader:
    """Downloads and manages voice models from HuggingFace with dynamic discovery"""

    def __init__(self, voices_dir: str = None, config=None):
        # Use configuration if voices_dir not provided
        if voices_dir is None:
            try:
                from ..config import config as default_config
                voices_dir = default_config.paths.voices_dir
            except ImportError:
                voices_dir = "LiteTTS/voices"  # Fallback

        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = config
        if config:
            self.hf_repo = config.repository.huggingface_repo
            self.hf_base_url = config.repository.base_url
            self.voices_path = config.repository.voices_path
            self.auto_discovery = config.voice.auto_discovery
            self.cache_discovery = config.voice.cache_discovery
            self.cache_expiry_hours = config.voice.discovery_cache_hours
        else:
            # Fallback defaults
            self.hf_repo = "onnx-community/Kokoro-82M-v1.0-ONNX"
            self.hf_base_url = "https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main"
            self.voices_path = "voices"
            self.auto_discovery = True
            self.cache_discovery = True
            self.cache_expiry_hours = 24

        self.hf_api_url = f"https://huggingface.co/api/repos/{self.hf_repo}"

        # Cache for discovered voice files
        self.discovered_voices: Dict[str, VoiceFileInfo] = {}
        self.discovery_cache_file = self.voices_dir / "discovery_cache.json"

        # Load cached discovery data
        if self.cache_discovery:
            self._load_discovery_cache()

        # Discover voices if auto-discovery is enabled and cache is empty or expired
        if self.auto_discovery and (not self.discovered_voices or self._is_cache_expired()):
            self.discover_voices_from_huggingface()

    def _load_discovery_cache(self) -> None:
        """Load discovery cache from JSON file"""
        if not self.discovery_cache_file.exists():
            return

        try:
            with open(self.discovery_cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check cache version and structure
            if 'voices' in cache_data and 'timestamp' in cache_data:
                self.discovered_voices = {
                    name: VoiceFileInfo(**info)
                    for name, info in cache_data['voices'].items()
                }
                logger.info(f"Loaded discovery cache with {len(self.discovered_voices)} voices")

        except Exception as e:
            logger.warning(f"Failed to load discovery cache: {e}")
            self.discovered_voices = {}

    def _save_discovery_cache(self) -> None:
        """Save discovery cache to JSON file"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'voices': {
                    name: {
                        'name': info.name,
                        'path': info.path,
                        'size': info.size,
                        'sha': info.sha,
                        'download_url': info.download_url
                    }
                    for name, info in self.discovered_voices.items()
                }
            }

            with open(self.discovery_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            logger.debug(f"Saved discovery cache with {len(self.discovered_voices)} voices")

        except Exception as e:
            logger.error(f"Failed to save discovery cache: {e}")

    def _is_cache_expired(self) -> bool:
        """Check if discovery cache is expired"""
        if not self.discovery_cache_file.exists():
            return True

        try:
            with open(self.discovery_cache_file, 'r') as f:
                cache_data = json.load(f)

            if 'timestamp' not in cache_data:
                return True

            cache_age_hours = (time.time() - cache_data['timestamp']) / 3600
            return cache_age_hours > self.cache_expiry_hours

        except Exception:
            return True

    def discover_voices_from_huggingface(self) -> bool:
        """Discover ALL voice files from HuggingFace repository automatically"""
        logger.info(f"🔍 Auto-discovering ALL voices from HuggingFace repository: {self.hf_repo}")

        try:
            # Get repository tree from HuggingFace API
            tree_url = f"https://huggingface.co/api/models/{self.hf_repo}/tree/main/{self.voices_path}"
            response = requests.get(tree_url, timeout=30)
            response.raise_for_status()

            repo_data = response.json()
            voice_files = []

            # Find ALL .bin files automatically (no hardcoded lists)
            for item in repo_data:
                if (item.get('type') == 'file' and
                    item.get('path', '').endswith('.bin')):
                    voice_files.append(item)

            # Process discovered voice files
            self.discovered_voices = {}
            for file_info in voice_files:
                voice_name = Path(file_info['path']).stem

                # Create VoiceFileInfo object
                # For LFS files, use the actual file hash from lfs.oid instead of git oid
                lfs_info = file_info.get('lfs', {})
                actual_hash = lfs_info.get('oid', file_info.get('oid', ''))
                actual_size = lfs_info.get('size', file_info.get('size', 0))

                voice_info = VoiceFileInfo(
                    name=voice_name,
                    path=file_info['path'],
                    size=actual_size,
                    sha=actual_hash,
                    download_url=f"{self.hf_base_url}/{file_info['path']}"
                )

                self.discovered_voices[voice_name] = voice_info

            logger.info(f"🎭 Auto-discovered {len(self.discovered_voices)} voice files from HuggingFace")

            # Log discovered voices for transparency
            voice_names = sorted(self.discovered_voices.keys())
            logger.info(f"📋 Available voices: {', '.join(voice_names[:10])}" +
                       (f" and {len(voice_names) - 10} more..." if len(voice_names) > 10 else ""))

            # Save to cache if caching is enabled
            if self.cache_discovery:
                self._save_discovery_cache()
            return True

        except Exception as e:
            logger.error(f"❌ Failed to auto-discover voices from HuggingFace: {e}")
            logger.error(f"🔧 Check network connection or repository access: {self.hf_repo}")
            return False

    def get_available_voice_names(self) -> List[str]:
        """Get list of all available voice names from HuggingFace"""
        return sorted(list(self.discovered_voices.keys()))

    def download_voice(self, voice_name: str,
                      progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> bool:
        """Download a specific voice model (.bin file directly)"""
        if voice_name not in self.discovered_voices:
            logger.error(f"Unknown voice: {voice_name}. Available voices: {list(self.discovered_voices.keys())}")
            return False

        voice_info = self.discovered_voices[voice_name]
        bin_path = self.voices_dir / f"{voice_name}.bin"

        # Check if .bin file already exists and is valid
        if bin_path.exists():
            if self._validate_file_integrity(bin_path, voice_info):
                logger.info(f"Voice {voice_name} (.bin) already exists and is valid, skipping download")
                return True
            else:
                logger.warning(f"Voice {voice_name} (.bin) exists but validation failed, re-downloading")

        # Download the .bin file directly
        url = voice_info.download_url

        try:
            logger.info(f"Downloading {voice_name} from {url}")

            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', voice_info.size))
            downloaded_size = 0
            start_time = time.time()

            with open(bin_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        if progress_callback and total_size > 0:
                            elapsed_time = time.time() - start_time
                            speed_mbps = (downloaded_size / (1024 * 1024)) / max(elapsed_time, 0.001)

                            progress = DownloadProgress(
                                filename=voice_name,
                                downloaded_bytes=downloaded_size,
                                total_bytes=total_size,
                                percentage=(downloaded_size / total_size) * 100,
                                speed_mbps=speed_mbps
                            )
                            progress_callback(progress)

            # Validate downloaded .bin file
            if self._validate_file_integrity(bin_path, voice_info):
                logger.info(f"Successfully downloaded {voice_name}.bin")
                return True
            else:
                logger.error(f"Downloaded file {voice_name} failed validation")
                bin_path.unlink()
                return False

        except Exception as e:
            logger.error(f"Failed to download {voice_name}: {e}")
            if bin_path.exists():
                bin_path.unlink()  # Remove partial download
            return False

    def download_all_voices(self,
                           progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> Dict[str, bool]:
        """Download all available voices"""
        results = {}

        for voice_name in self.discovered_voices.keys():
            results[voice_name] = self.download_voice(voice_name, progress_callback)

        successful = sum(1 for success in results.values() if success)
        total = len(results)

        logger.info(f"Completed downloading {successful}/{total} voices successfully")
        return results

    def download_default_voices(self,
                               progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> Dict[str, bool]:
        """Download default voices (backward compatibility) - now downloads ALL voices"""
        logger.info("📥 Downloading ALL available voices (simplified voice management)")
        return self.download_all_voices(progress_callback)



    def is_voice_downloaded(self, voice_name: str) -> bool:
        """Check if a voice is already downloaded"""
        if voice_name not in self.discovered_voices:
            return False

        local_path = self.voices_dir / f"{voice_name}.bin"
        if not local_path.exists():
            return False

        voice_info = self.discovered_voices[voice_name]
        return self._validate_file_integrity(local_path, voice_info)

    def get_downloaded_voices(self) -> List[str]:
        """Get list of downloaded voices"""
        downloaded = []

        for voice_name in self.discovered_voices.keys():
            if self.is_voice_downloaded(voice_name):
                downloaded.append(voice_name)

        return sorted(downloaded)

    def get_missing_voices(self) -> List[str]:
        """Get list of voices that need to be downloaded"""
        missing = []

        for voice_name in self.discovered_voices.keys():
            if not self.is_voice_downloaded(voice_name):
                missing.append(voice_name)

        return sorted(missing)

    def _validate_file_integrity(self, file_path: Path, voice_info: VoiceFileInfo) -> bool:
        """Validate file integrity against expected size and hash"""
        try:
            # Check file size
            actual_size = file_path.stat().st_size
            if voice_info.size > 0 and actual_size != voice_info.size:
                logger.warning(f"File size mismatch for {voice_info.name}: expected {voice_info.size}, got {actual_size}")
                return False

            # Check SHA hash if available
            if voice_info.sha and voice_info.sha != "":
                actual_hash = self._calculate_file_hash(file_path)
                if actual_hash != voice_info.sha:
                    logger.warning(f"Hash mismatch for {voice_info.name}: expected {voice_info.sha}, got {actual_hash}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating file integrity for {voice_info.name}: {e}")
            return False

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)

        return hash_sha256.hexdigest()

    def get_voice_file_path(self, voice_name: str) -> Optional[Path]:
        """Get local file path for a voice"""
        if voice_name not in self.discovered_voices:
            return None

        local_path = self.voices_dir / f"{voice_name}.bin"
        return local_path if local_path.exists() else None

    def get_download_info(self) -> Dict[str, Dict]:
        """Get download information for all voices"""
        info = {}

        for voice_name, voice_info in self.discovered_voices.items():
            local_path = self.voices_dir / f"{voice_name}.bin"

            info[voice_name] = {
                'downloaded': self.is_voice_downloaded(voice_name),
                'local_path': str(local_path),
                'file_exists': local_path.exists(),
                'file_size': local_path.stat().st_size if local_path.exists() else 0,
                'expected_size': voice_info.size,
                'remote_url': voice_info.download_url,
                'sha': voice_info.sha
            }

        return info

    def cleanup_invalid_files(self) -> List[str]:
        """Remove invalid or corrupted voice files"""
        cleaned = []

        for voice_name, voice_info in self.discovered_voices.items():
            local_path = self.voices_dir / f"{voice_name}.bin"

            if local_path.exists() and not self._validate_file_integrity(local_path, voice_info):
                logger.info(f"Removing invalid file: {local_path}")
                local_path.unlink()
                cleaned.append(voice_name)

        return cleaned

    def refresh_discovery(self) -> bool:
        """Force refresh of voice discovery from HuggingFace"""
        logger.info("Forcing refresh of voice discovery")

        # Clear cache
        if self.discovery_cache_file.exists():
            self.discovery_cache_file.unlink()

        self.discovered_voices = {}

        # Rediscover voices
        return self.discover_voices_from_huggingface()

    def get_discovery_stats(self) -> Dict:
        """Get statistics about voice discovery"""
        return {
            'total_discovered': len(self.discovered_voices),
            'total_downloaded': len(self.get_downloaded_voices()),
            'total_missing': len(self.get_missing_voices()),
            'cache_file_exists': self.discovery_cache_file.exists(),
            'cache_expired': self._is_cache_expired(),
            'repository': self.hf_repo
        }