import os
import shutil
from contextlib import suppress

from codex_django.cli.commands.init import handle_init

# Clean up sandbox (safely)
sandbox_path = "sandbox_v2"
if os.path.exists(sandbox_path):
    with suppress(Exception):
        shutil.rmtree(sandbox_path)

print("Running handle_init for test_multi_v2...")
handle_init(
    name="test_multi_v2",
    base_dir=os.getcwd(),
    target_dir=sandbox_path,
    dev_mode=False,
    multilingual=True,
    languages=["en", "ru", "uk"],
    overwrite=True,
)

settings_path = os.path.join(
    sandbox_path, "src", "test_multi_v2", "core", "settings", "modules", "internationalization.py"
)
if os.path.exists(settings_path):
    print(f"\nContents of {settings_path}:")
    with open(settings_path) as f:
        print(f.read())
else:
    print(f"\nERROR: {settings_path} not found!")
