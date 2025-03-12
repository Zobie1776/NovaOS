# Nova OS Bootloader - Initializes System Components

import os
import subprocess

# ✅ Define Nova OS Components to Initialize
SYSTEM_COMPONENTS = [
    "file-management/file_explorer.ns",
    "network/connection_manager.ns",
    "applications/app_manager.ns",
    "file-management/downloads.ns",
    "file-management/documents.ns",
    "core/security.ns",
    "security/firewall.ns",
    "services/update_manager.ns",
    "services/scheduler.ns",
]

# Automatically resolve the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Build paths dynamically
nova_script_path = os.path.join(base_dir, 'novascript.py')
memory_loader_path = os.path.join(base_dir, 'ai', 'memory', 'imported_memory', 'NovaMemoryLoader.ns')
ai_core_path = os.path.join(base_dir, 'ai', 'nova_ai_core.ns')
chromebook_optimizations_path = os.path.join(base_dir, 'system', 'chromebook_optimizations.ns')

# ✅ Check System Readiness
def check_system():
    print("\n🔹 Checking System Readiness...")

    python_version = subprocess.run(["python3", "--version"], capture_output=True, text=True)
    if "Python 3" not in python_version.stdout:
        print("❌ Error: Python 3 is required to run Nova OS. Install it first.")
        exit(1)

    print("✅ System Check Passed - Ready to Boot Nova OS")

# ✅ Load Nova OS Components
def load_components():
    print("\n🔹 Loading Nova OS Components...\n")
    for component in SYSTEM_COMPONENTS:
        component_path = os.path.join(base_dir, component)
        if os.path.exists(component_path):
            print(f"✅ Loading {component}...")
        else:
            print(f"⚠️ Warning: {component} not found. Skipping...")

# ✅ Load Nova AI Memory
def load_memory():
    print(f"\n🔹 Checking for memory loader at: {memory_loader_path}")
    if os.path.exists(memory_loader_path):
        print(f"✅ Memory Loader found at: {memory_loader_path}")
        subprocess.run(['python3', nova_script_path, memory_loader_path])
        print("✅ Nova AI memory files have been loaded on startup!")
    else:
        print(f"⚠ Warning: NovaMemoryLoader.ns not found at {memory_loader_path}")

# ✅ Launch NovaScript Interpreter
def launch_novascript():
    print("\n🔹 Launching NovaScript Engine...")
    if os.path.exists(nova_script_path):
        subprocess.run(['python3', nova_script_path])
    else:
        print(f"⚠ Warning: novascript.py not found at {nova_script_path}")

# ✅ Execute Additional Scripts
def execute_additional_scripts():
    if os.path.exists(ai_core_path):
        print(f"✅ Executing AI Core Script at {ai_core_path}")
        subprocess.run(['python3', nova_script_path, ai_core_path])
    else:
        print(f"⚠ Warning: AI Core Script not found at {ai_core_path}")

    if os.path.exists(chromebook_optimizations_path):
        print(f"✅ Executing Chromebook Optimizations Script at {chromebook_optimizations_path}")
        subprocess.run(['python3', nova_script_path, chromebook_optimizations_path])
    else:
        print(f"⚠ Warning: Chromebook Optimizations Script not found at {chromebook_optimizations_path}")

# ✅ Boot Nova OS
def boot_nova_os():
    print("\n🚀 Booting Nova OS...\n")
    check_system()
    load_components()
    load_memory()
    execute_additional_scripts()
    launch_novascript()

# ✅ Run the Bootloader
if __name__ == "__main__":
    boot_nova_os()
