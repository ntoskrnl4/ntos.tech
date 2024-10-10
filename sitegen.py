#!/usr/bin/python3

# Todo:
#  This is the main entrypoint script
#  No args, it will regenerate all sites in the master configuration file (mapping of paths, folder > output)
#  Iterate through tree, render every file, place in output
#  JSON for metadata, *if necessary* (override default template, title, etc. og-desc can be contents of first ~128bytes)
#  staticfiles: copy as-is i guess?
#  pygments keeps track of every style ever rendered, light and dark, and places into a code-dark and code-light .css in staticfiles
#   (note this means that staticfiles will have to be processed last, this can just be done by reordering the path list when iterating through top-level directory tree)

import sys

# i know for a fact we're going to need 3.12 features (namely pathlib.Path.walk)
if sys.version_info.minor < 12:
    sys.stderr.write("sitegen: Requires Python 3.12+\n")
    sys.stderr.flush()
    sys.exit(1)

import json

from domain import WebsiteDomain
from pathlib import Path


try:
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)  # type: dict[str, str | dict[str, str]]
except Exception as e:
    # If it doesn't exist or is malformed, return an error
    sys.stderr.write("sitegen: Invalid or missing config.json\n\n")
    sys.stderr.flush()
    raise e from None
    
# If the output directory isn't set, we can't do anything, so error out
output = config.get("output")
if output is None:
    sys.stderr.write("sitegen: No output directory configured\n")
    sys.stderr.flush()
    sys.exit(1)

# If the output directory is part of the current directory, it may cause recursion/overwrite issues
output = Path(output)
if output.resolve().is_relative_to(Path().resolve()):
    sys.stderr.write("sitegen: Output directory may not be part of the current directory\n")
    sys.stderr.flush()
    sys.exit(1)
    

if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.stdout.write("""Usage: sitegen <domain | -a>

domain      A specific domain to regenerate
-a          (not implemented) Regenerate all domains

Currently configured domains:
""")
        for domain in (config.keys() - {"output"}):
            sys.stdout.write(f" - {domain}\n")

        sys.stdout.flush()
        sys.exit(0)
    
    if sys.argv[1] != "-a":
        website = WebsiteDomain(sys.argv[1], output/sys.argv[1])
        website.generate()
        exit(0)
    
    domains = config.keys() - {"output"}
    for x in domains:
        website = WebsiteDomain(x, output/x)
        website.generate()
