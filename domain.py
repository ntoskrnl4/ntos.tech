import json
import sys
from pathlib import Path

from source import SourceFile


class WebsiteDomain:
    
    def __init__(self, domain, output: Path):
        self.source = Path(domain)  # we can get a domain-relative file path with file.relative_to(self.source)
        self.output = output
        self.domain = domain.lower()
        with open("config.json", encoding="utf-8") as f:
            self.config = json.load(f).get(domain)  # type: dict[str, str]
        
        # check for possible errors
        if self.config is None:
            sys.stderr.write(f"sitegen: {domain}: not in config\n")
            sys.stderr.flush()
            sys.exit(1)

        if not Path(domain).is_dir():
            sys.stderr.write(f"sitegen: {domain}: directory does not exist\n")
            sys.stderr.flush()
            sys.exit(1)
        
        if "template" not in self.config:
            sys.stderr.write(f"sitegen: {domain}: no default template set\n")
            sys.stderr.flush()
            sys.exit(1)
        
        self.template = self.config["template"]
        self.domain_title = self.config.get("domain_title", self.domain)
    
    def generate(self):
        for dirpath, dirnames, filenames in self.source.walk():
            for source_file in filenames:
                source_file = dirpath/source_file
                
                # Skip .json files, as those are used to configure specific pages
                if source_file.suffix == ".json":
                    continue
                
                # breakpoint()
                page = SourceFile(source_file, self)
                result = page.render()

                if result is None:
                    print(f"🧊{source_file}")
                if result is False:
                    print(f"❌{source_file}")
                if result is True:
                    print(f"✅{source_file}")
                if result == "new":
                    print(f"✨{source_file}")

                # create a SourceFile object, with a .render() property, and call it
                # .render() should return "new", True, False, or None (new, updated, unmodified, ignored)
                # and print an output line based on that
        
