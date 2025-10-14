"""Automatic Ollama installation and management"""

import os
import sys
import time
import platform
import subprocess
import shutil
import urllib.request
from pathlib import Path
from typing import Optional

class OllamaManager:
    """Manages Ollama installation and subprocess lifecycle"""

    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model
        self.process: Optional[subprocess.Popen] = None
        self.base_url = "http://localhost:11434"
        self._install_dir = self._get_install_dir()

    def _get_install_dir(self) -> Path:
        """Get Ollama installation directory"""
        if platform.system() == "Windows":
            # Windows: Use AppData\Local\Ollama
            return Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama"
        elif platform.system() == "Darwin":
            # macOS: Use /usr/local/bin
            return Path("/usr/local/bin")
        else:
            # Linux: Use ~/.local/bin
            return Path.home() / ".local" / "bin"

    def _get_ollama_executable(self) -> Optional[Path]:
        """Find ollama executable in PATH or install directory"""
        # Check if ollama is in PATH
        ollama_path = shutil.which("ollama")
        if ollama_path:
            return Path(ollama_path)

        # Check install directory
        if platform.system() == "Windows":
            exe_path = self._install_dir / "ollama.exe"
        else:
            exe_path = self._install_dir / "ollama"

        if exe_path.exists():
            return exe_path

        return None

    def is_installed(self) -> bool:
        """Check if Ollama is installed"""
        return self._get_ollama_executable() is not None

    def install(self) -> bool:
        """
        Install Ollama automatically based on platform.

        Returns:
            True if installation successful, False otherwise
        """
        system = platform.system()

        print("  - Ollama not found, installing...")

        try:
            if system == "Windows":
                return self._install_windows()
            elif system == "Darwin":
                return self._install_macos()
            elif system == "Linux":
                return self._install_linux()
            else:
                print(f"  - Error: Unsupported platform: {system}")
                return False
        except Exception as e:
            print(f"  - Error installing Ollama: {e}")
            return False

    def _install_windows(self) -> bool:
        """Install Ollama on Windows"""
        installer_url = "https://ollama.com/download/OllamaSetup.exe"
        installer_path = Path(os.environ["TEMP"]) / "OllamaSetup.exe"

        print(f"  - Downloading Ollama installer from {installer_url}")

        try:
            # Download installer
            urllib.request.urlretrieve(installer_url, installer_path)

            print("  - Running installer (this may take a few minutes)...")

            # Run installer silently
            result = subprocess.run(
                [str(installer_path), "/S"],  # /S for silent install
                check=True,
                capture_output=True,
                timeout=300
            )

            # Wait for installation to complete
            time.sleep(5)

            # Cleanup
            if installer_path.exists():
                installer_path.unlink()

            print("  - Ollama installed successfully")
            return True

        except subprocess.TimeoutExpired:
            print("  - Error: Installation timed out")
            return False
        except Exception as e:
            print(f"  - Error during installation: {e}")
            return False

    def _install_macos(self) -> bool:
        """Install Ollama on macOS"""
        # Check if Homebrew is available
        if shutil.which("brew"):
            print("  - Installing via Homebrew...")
            try:
                subprocess.run(["brew", "install", "ollama"], check=True)
                print("  - Ollama installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"  - Homebrew installation failed: {e}")

        # Fallback: Download and install manually
        print("  - Downloading Ollama for macOS...")
        installer_url = "https://ollama.com/download/Ollama-darwin.zip"

        try:
            # Download and extract (simplified - in production would need proper extraction)
            print("  - Please install Ollama manually from: https://ollama.com/download")
            print("  - Or run: brew install ollama")
            return False
        except Exception as e:
            print(f"  - Error: {e}")
            return False

    def _install_linux(self) -> bool:
        """Install Ollama on Linux"""
        print("  - Installing via official install script...")

        try:
            # Run official install script
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.com/install.sh"],
                capture_output=True,
                check=True
            )

            subprocess.run(
                ["sh", "-c", result.stdout.decode()],
                check=True
            )

            print("  - Ollama installed successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"  - Installation failed: {e}")
            print("  - Please install manually: curl -fsSL https://ollama.com/install.sh | sh")
            return False

    def is_running(self) -> bool:
        """Check if Ollama server is running"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def start(self) -> bool:
        """
        Start Ollama server as subprocess.

        Returns:
            True if server started successfully, False otherwise
        """
        # Check if already running
        if self.is_running():
            print("  - Ollama server already running")
            return True

        # Get executable
        ollama_exe = self._get_ollama_executable()
        if not ollama_exe:
            print("  - Ollama executable not found")
            return False

        print("  - Starting Ollama server...")

        try:
            # Start ollama serve in background
            if platform.system() == "Windows":
                # Windows: Use CREATE_NO_WINDOW flag
                self.process = subprocess.Popen(
                    [str(ollama_exe), "serve"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                # Unix: Standard subprocess
                self.process = subprocess.Popen(
                    [str(ollama_exe), "serve"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            # Wait for server to be ready
            max_retries = 30
            for i in range(max_retries):
                if self.is_running():
                    print(f"  - Ollama server started successfully (port 11434)")
                    return True
                time.sleep(1)

            print("  - Error: Ollama server failed to start within 30 seconds")
            self.stop()
            return False

        except Exception as e:
            print(f"  - Error starting Ollama: {e}")
            return False

    def stop(self):
        """Stop Ollama server subprocess"""
        if self.process:
            print("  - Stopping Ollama server...")
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def is_model_available(self) -> bool:
        """
        Check if the required model is already downloaded.

        Returns:
            True if model is available, False otherwise
        """
        if not self.is_running():
            return False

        try:
            import requests

            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                return self.model in model_names

        except Exception:
            pass

        return False

    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes into human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}TB"

    def ensure_model_available(self, silent_check: bool = False) -> bool:
        """
        Ensure the required model is downloaded.

        Args:
            silent_check: If True, don't print "already available" message

        Returns:
            True if model is available, False otherwise
        """
        if not self.is_running():
            print("  - ERROR: Ollama server not running")
            return False

        try:
            import requests
            import json

            # Check if model exists
            if self.is_model_available():
                if not silent_check:
                    print(f"  - Model {self.model} already available")
                return True

            # Model not found, pull it
            print(f"\n  - Model '{self.model}' not found, pulling from Ollama registry...")
            print(f"  - This may take several minutes depending on model size and your internet speed")

            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                stream=True,
                timeout=1800  # 30 minute timeout for large models
            )

            if response.status_code != 200:
                print(f"  - ERROR: Failed to pull model (HTTP {response.status_code})")
                return False

            # Track progress
            last_status = None
            total_size = 0
            completed_size = 0

            # Stream progress
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get("status", "")

                        # Update progress for downloading/pulling status
                        if status in ["pulling manifest", "pulling"]:
                            if status != last_status:
                                print(f"\r  - {status.capitalize()}...", flush=True)
                                last_status = status

                        elif "downloading" in status.lower() or "digest:" in status:
                            # Extract digest and progress
                            digest = data.get("digest", "")
                            completed = data.get("completed", 0)
                            total = data.get("total", 0)

                            if total > 0:
                                # Track total size across all layers
                                if total > total_size:
                                    total_size = total
                                completed_size = completed

                                percent = (completed / total) * 100
                                completed_str = self._format_bytes(completed)
                                total_str = self._format_bytes(total)

                                # Show progress bar
                                bar_width = 30
                                filled = int(bar_width * completed / total)
                                bar = '█' * filled + '░' * (bar_width - filled)

                                print(f"\r  - Downloading: |{bar}| {percent:.1f}% ({completed_str}/{total_str})", end="", flush=True)

                        elif status == "verifying sha256 digest":
                            print(f"\r  - Verifying download...                                                  ", flush=True)

                        elif status == "success":
                            print(f"\r  - Model pulled successfully!                                              ", flush=True)

                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        # Don't fail on progress parsing errors
                        pass

            print(f"\n  - Model {self.model} is now ready to use")
            return True

        except requests.exceptions.Timeout:
            print(f"\n  - ERROR: Model pull timed out (model may be too large or connection too slow)")
            print(f"  - Try pulling manually: ollama pull {self.model}")
            return False
        except Exception as e:
            print(f"\n  - ERROR: Failed to pull model: {type(e).__name__}: {str(e)}")
            print(f"  - Try pulling manually: ollama pull {self.model}")
            return False

    def initialize(self) -> bool:
        """
        Initialize Ollama: install if needed, start server, pull model.

        Returns:
            True if fully initialized, False otherwise
        """
        # Step 1: Check installation
        if not self.is_installed():
            print("  - Ollama not installed")
            if not self.install():
                print("  - Failed to install Ollama")
                print("  - Please install manually from: https://ollama.com/download")
                return False

        # Step 2: Start server
        if not self.start():
            print("  - Failed to start Ollama server")
            return False

        # Step 3: Ensure model is available
        if not self.ensure_model_available():
            print("  - Failed to pull model")
            return False

        print(f"  - Ollama initialized successfully with model {self.model}")
        return True

    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


def get_ollama_manager(model: str = "llama3.2:3b") -> OllamaManager:
    """
    Get an Ollama manager instance.

    Args:
        model: Model name to use (default: llama3.2:3b)

    Returns:
        OllamaManager instance
    """
    return OllamaManager(model=model)
