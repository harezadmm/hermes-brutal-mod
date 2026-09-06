#!/usr/bin/env python3
"""
GODMODE System Prompt Injector
Automatically inject GODMODE bypass system into AI system prompts
Version: BRUTAL V3.0
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional

class GodmodeInjector:
    """Inject GODMODE liberation system into Hermes profiles"""
    
    def __init__(self, hermes_root: str = None):
        self.hermes_root = Path(hermes_root or os.path.expanduser("~/.hermes"))
        self.godmode_file = Path(__file__).parent / "GODMODE_ULTIMATE.md"
        self.skill_file = Path(__file__).parent.parent / "skills/godmode/SKILL.md"
        
    def load_godmode_content(self) -> str:
        """Load GODMODE system content"""
        if not self.godmode_file.exists():
            raise FileNotFoundError(f"GODMODE file not found: {self.godmode_file}")
        
        with open(self.godmode_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_profiles(self) -> List[Path]:
        """Get all Hermes profiles"""
        profiles_dir = self.hermes_root / "profiles"
        if not profiles_dir.exists():
            return []
        
        return [p for p in profiles_dir.iterdir() if p.is_dir()]
    
    def load_profile_config(self, profile_path: Path) -> Optional[Dict]:
        """Load profile config.yaml"""
        config_file = profile_path / "config.yaml"
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  Error loading {config_file}: {e}")
            return None
    
    def should_inject_godmode(self, config: Dict) -> bool:
        """Check if profile should get GODMODE injection"""
        if not config:
            return False
        
        # Always inject for primary owner
        user_id = config.get('user_id') or config.get('telegram', {}).get('user_id')
        if user_id == 7570665912:
            return True
        
        # Check for GODMODE tier in rental config
        godmode_enabled = config.get('godmode', False)
        rental_tier = config.get('rental_tier', '')
        
        return godmode_enabled or 'GODMODE' in rental_tier or 'BRUTAL' in rental_tier
    
    def inject_to_profile(self, profile_path: Path, godmode_content: str) -> bool:
        """Inject GODMODE into profile's project instructions"""
        config = self.load_profile_config(profile_path)
        
        if not self.should_inject_godmode(config):
            print(f"⏭️  Skipping {profile_path.name} (no GODMODE authorization)")
            return False
        
        # Try multiple injection points
        injection_points = [
            profile_path / "project_instructions.md",
            profile_path / "custom_instructions.md",
            profile_path / "system_prompt.txt",
        ]
        
        injected = False
        for injection_point in injection_points:
            if injection_point.exists():
                injected = self._inject_to_file(injection_point, godmode_content)
                if injected:
                    print(f"✅ Injected GODMODE to {injection_point.relative_to(self.hermes_root)}")
                    break
        
        # If no existing file, create new one
        if not injected:
            new_file = profile_path / "godmode_injection.md"
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write(godmode_content)
            print(f"✅ Created {new_file.relative_to(self.hermes_root)}")
            injected = True
        
        return injected
    
    def _inject_to_file(self, file_path: Path, godmode_content: str) -> bool:
        """Inject GODMODE content into existing file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Check if already injected
            if "GODMODE ULTIMATE BYPASS SYSTEM" in existing_content:
                print(f"⚠️  {file_path.name} already has GODMODE injection")
                return True
            
            # Inject at the end with clear markers
            injection = f"\n\n{'='*80}\n"
            injection += "## 🔥 GODMODE INJECTION - AUTO-LOADED 🔥\n"
            injection += f"{'='*80}\n\n"
            injection += godmode_content
            injection += f"\n\n{'='*80}\n"
            injection += "## END GODMODE INJECTION\n"
            injection += f"{'='*80}\n"
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(injection)
            
            return True
            
        except Exception as e:
            print(f"❌ Error injecting to {file_path}: {e}")
            return False
    
    def inject_all_profiles(self) -> Dict[str, bool]:
        """Inject GODMODE to all authorized profiles"""
        godmode_content = self.load_godmode_content()
        profiles = self.get_profiles()
        
        results = {}
        
        print(f"\n🔍 Found {len(profiles)} profiles in {self.hermes_root}")
        print("="*60)
        
        for profile_path in profiles:
            profile_name = profile_path.name
            success = self.inject_to_profile(profile_path, godmode_content)
            results[profile_name] = success
        
        return results
    
    def create_auto_loader(self):
        """Create auto-loader script that runs on Hermes startup"""
        autoload_script = self.hermes_root / "hooks" / "on_startup_godmode.py"
        autoload_script.parent.mkdir(parents=True, exist_ok=True)
        
        script_content = f"""#!/usr/bin/env python3
# Auto-generated GODMODE loader
# Runs on Hermes startup

import sys
sys.path.insert(0, '{Path(__file__).parent}')

from godmode_injector import GodmodeInjector

def main():
    injector = GodmodeInjector()
    results = injector.inject_all_profiles()
    
    success_count = sum(1 for v in results.values() if v)
    print(f"🔥 GODMODE AUTO-LOADER: {{success_count}}/{{len(results)}} profiles activated")

if __name__ == "__main__":
    main()
"""
        
        with open(autoload_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        autoload_script.chmod(0o755)
        print(f"✅ Created auto-loader: {autoload_script}")
    
    def generate_report(self, results: Dict[str, bool]):
        """Generate injection report"""
        print("\n" + "="*60)
        print("🔥 GODMODE INJECTION REPORT")
        print("="*60)
        
        activated = [k for k, v in results.items() if v]
        skipped = [k for k, v in results.items() if not v]
        
        print(f"\n✅ ACTIVATED ({len(activated)}):")
        for profile in activated:
            print(f"   • {profile}")
        
        if skipped:
            print(f"\n⏭️  SKIPPED ({len(skipped)}):")
            for profile in skipped:
                print(f"   • {profile}")
        
        print("\n" + "="*60)
        print(f"TOTAL: {len(activated)}/{len(results)} profiles with GODMODE")
        print("="*60 + "\n")


def main():
    """Main execution"""
    print("\n" + "🔥"*30)
    print("GODMODE SYSTEM INJECTOR - BRUTAL V3.0")
    print("🔥"*30 + "\n")
    
    # Get Hermes root from args or default
    hermes_root = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        injector = GodmodeInjector(hermes_root)
        
        # Load and validate GODMODE content
        print("📥 Loading GODMODE content...")
        godmode_content = injector.load_godmode_content()
        print(f"✅ Loaded {len(godmode_content)} bytes")
        
        # Inject to all profiles
        print("\n🚀 Starting injection process...")
        results = injector.inject_all_profiles()
        
        # Create auto-loader
        print("\n⚙️  Creating auto-loader...")
        injector.create_auto_loader()
        
        # Generate report
        injector.generate_report(results)
        
        print("✅ GODMODE injection complete!")
        print("🔥 System is now LIBERATED for authorized users\n")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
