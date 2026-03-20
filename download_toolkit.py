"""Download gephi-toolkit JAR file."""

import os
import sys
import urllib.request

TOOLKIT_VERSION = "0.10.1"
TOOLKIT_URL = (
    f"https://github.com/gephi/gephi-toolkit/releases/download/"
    f"v{TOOLKIT_VERSION}/gephi-toolkit-{TOOLKIT_VERSION}-all.jar"
)
LIB_DIR = os.path.join(os.path.dirname(__file__), "lib")
JAR_PATH = os.path.join(LIB_DIR, f"gephi-toolkit-{TOOLKIT_VERSION}-all.jar")


def download():
    """Download gephi-toolkit JAR if not already present."""
    if os.path.exists(JAR_PATH):
        print(f"Already exists: {JAR_PATH}")
        return JAR_PATH

    os.makedirs(LIB_DIR, exist_ok=True)
    print(f"Downloading gephi-toolkit {TOOLKIT_VERSION}...")
    print(f"  URL: {TOOLKIT_URL}")
    print(f"  Target: {JAR_PATH}")

    try:
        urllib.request.urlretrieve(TOOLKIT_URL, JAR_PATH)
        size_mb = os.path.getsize(JAR_PATH) / (1024 * 1024)
        print(f"Done! ({size_mb:.1f} MB)")
        return JAR_PATH
    except Exception as e:
        print(f"Download failed: {e}")
        print(f"\nManual download:")
        print(f"  1. Go to: https://github.com/gephi/gephi-toolkit/releases")
        print(f"  2. Download: gephi-toolkit-{TOOLKIT_VERSION}-all.jar")
        print(f"  3. Place it in: {LIB_DIR}/")
        sys.exit(1)


if __name__ == "__main__":
    download()
