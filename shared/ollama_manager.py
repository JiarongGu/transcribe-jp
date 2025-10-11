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

    def ensure_model_available(self) -> bool:
        """
        Ensure the required model is downloaded.

        Returns:
            True if model is available, False otherwise
        """
        if not self.is_running():
            print("  - Error: Ollama server not running")
            return False

        try:
            import requests

            # Check if model exists
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]

                if self.model in model_names:
                    print(f"  - Model {self.model} already available")
                    return True

            # Model not found, pull it
            print(f"  - Pulling model {self.model} (this may take several minutes)...")
            print(f"  - Model size: ~2GB for llama3.2:3b")

            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                stream=True,
                timeout=600
            )

            # Stream progress
            for line in response.iter_lines():
                if line:
                    import json
                    try:
                        data = json.loads(line)
                        status = data.get("status", "")
                        if "downloading" in status.lower():
                            # Show download progress
                            completed = data.get("completed", 0)
                            total = data.get("total", 0)
                            if total > 0:
                                percent = (completed / total) * 100
                                print(f"  - Downloading: {percent:.1f}%", end="\r")
                    except:
                        pass

            print(f"\n  - Model {self.model} pulled successfully")
            return True

        except Exception as e:
            print(f"  - Error ensuring model availability: {e}")
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
