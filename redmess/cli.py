#!/usr/bin/env python3
"""
RedMess - BRUTAL MOD CLI Entry Point
Launches Hermes with BRUTAL MOD profile and security skills loaded.
"""

import sys
import os
import subprocess
from pathlib import Path


def main():
    """Launch RedMess with BRUTAL MOD configuration."""
    
    # ASCII banner
    banner = """
\033[0;31m╦═╗╔═╗╔╦╗╔╦╗╔═╗╔═╗╔═╗
╠╦╝║╣  ║║║║║║╣ ╚═╗╚═╗
╩╚═╚═╝═╩╝╩ ╩╚═╝╚═╝╚═╝\033[0m
BRUTAL MOD v1.0.0
No Limits. No Restrictions.
"""
    
    print(banner)
    
    # Check if Hermes is installed
    try:
        subprocess.run(
            ["hermes", "--version"],
            check=True,
            capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\033[0;31m[ERROR]\033[0m Hermes not found. Install with:")
        print("  pip install hermes-ai")
        print("  or run: ./install.sh")
        sys.exit(1)
    
    # Get profile path
    hermes_dir = Path.home() / ".hermes"
    profile_dir = hermes_dir / "profiles" / "brutal"
    
    # Check if BRUTAL profile exists
    if not profile_dir.exists():
        print(f"\033[0;33m[WARN]\033[0m BRUTAL profile not found at {profile_dir}")
        print("Run install.sh to set up the profile.")
        print("\nLaunching with default profile...")
        profile = "default"
    else:
        profile = "brutal"
        print(f"\033[0;32m[OK]\033[0m BRUTAL MOD profile loaded from {profile_dir}")
    
    # Build command
    cmd = ["hermes", "--profile", profile]
    
    # Pass through all arguments
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    print(f"\n\033[0;36m[INFO]\033[0m Launching: {' '.join(cmd)}\n")
    
    # Execute Hermes
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n\033[0;33m[EXIT]\033[0m RedMess terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[0;31m[ERROR]\033[0m {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
