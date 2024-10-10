import bs4
import hashlib
import json
import langdetect
import mistune.toc
import os
import shutil

from datetime import datetime
from pathlib import Path
from parser import parser  # `parser` used to be a stdlib in 2.6(!), but dw it'll find ./parser.py


class SourceFile:
    def __init__(self, fp: Path, domain: "WebsiteDomain"):
        self.fp = fp
        self.domain = domain
        self.metadata = {} | domain.config  # this duplicates the dict, instead of copying the pointer

        # Target output path
        self.metadata["target"] = fp.relative_to(domain.source)

        if self.fp.suffix in [".html", ".md"]:

            if (domain.source / self.metadata["target"]).with_suffix("").is_dir():
                # nginx is fucking stupid so if the file has same name as directory, it has to go in there instead
                self.metadata["target"] = self.metadata["target"].with_suffix("") / "index.html"
            else:
                # If it is a normal file location/extension/etc., just make it target the same filename as .html
                self.metadata["target"] = self.metadata["target"].with_suffix(".html")

        meta_fp = self.fp.with_suffix(self.fp.suffix + ".json")
        if meta_fp.is_file():
            with open(meta_fp, "r", encoding="utf-8") as f:
                self.metadata |= json.load(f)
        
        self.source = None
        self.rendered = None
        self.md_ast = None
        self.rendered_toc = ""
        
        self.load_source()
        self.load_metadata()

    def load_source(self):
        if self.fp.suffix not in [".html", ".md"]:
            return

        if self.fp.suffix == ".html":
            self.source = self.fp.read_text("utf-8")
            return
        
        # If it's a markdown file, do our full processing on it
        self.source = self.fp.read_text("utf-8")
        # If no language specified, detect from content (or from inline metadata)
        if self.metadata.get("lang") is None:
            self.metadata["lang"] = langdetect.detect(self.source)

        # If the file has inline metadata, extract that out + update
        if self.source.startswith("```meta\n"):
            self.source = self.source[8:]

            line, self.source = self.source.split("\n", 1)
            while line != "```":  # Iterate through the fenced metablock and set key:val pairs in it
                key, val = line.split(":", 1)
                self.metadata[key.strip().lower()] = val.strip()
                line, self.source = self.source.split("\n", 1)
        
        if self.metadata.get("description") is None:
            # We need to get the description from the first paragraph of the text (ignoring headers, etc)
            intro = ""
            intro_length = 255  # How long the intro will be
            for line in self.source.split("\n"):
                if not (line.startswith("#") or line.startswith("<img")):
                    intro += line.strip() + " "
                if len(intro) >= intro_length:
                    break
            self.metadata["description"] = intro[:intro_length].strip()
    
    def load_metadata(self):
        if self.fp.with_suffix(self.fp.suffix + ".json").is_file():
            with open(self.fp.with_suffix(self.fp.suffix + ".json"), "r", encoding="utf-8") as f:
                self.metadata |= json.load(f)
    
    def render_to_html(self):
        if self.fp.suffix != ".md":
            # Direct HTML ones we render (copy) later in load_template
            return
        
        self.source, self.md_ast = parser.parse(self.source)
    
    def generate_toc(self):
        # If the TOC/outline doesn't exist, then just skip this step
        if self.md_ast is None:
            return
        if len(self.md_ast.env["toc_items"]) == 0:
            return

        # If the first item of the ToC is the title....
        if self.md_ast.env["toc_items"][0][0] == 1:
            if self.metadata.get("title") is None:
                self.metadata["title"] = self.md_ast.env["toc_items"][0][2]  # set it as the page title (if not already)
            self.md_ast.env["toc_items"].pop(0)  # ...and then pop it, so it doesn't end up in the TOC
        
        self.rendered_toc = mistune.toc.render_toc_ul(self.md_ast.env["toc_items"])
    
    def search_for_og_image(self):
        if self.metadata.get("og_image"):  # if the og:image is already set, skip
            return
        if self.fp.suffix not in [".html", ".md"]:  # don't try to find og:image for staticfiles lmao
            return
        
        soup = bs4.BeautifulSoup(self.source, "html5lib")
        self.metadata["og_image"] = (self.metadata.get("og_image")
                                  or soup.find("img", class_="og_image")
                                  or soup.find("img")
                                  or self.domain.config.get("default_og_image")
                                  or "")  # If we didn't find ANYTHING, just set it to an empty string
        
        if isinstance(self.metadata["og_image"], bs4.Tag):  # if we found something in the article, grab the url
            self.metadata["og_image"] = str(self.metadata["og_image"]["src"])
    
    def load_template(self):
        if self.fp.suffix not in [".html", ".md"]:
            # staticfiles don't have a template
            return

        if self.fp.suffix == ".html":
            # Direct HTML files just need to copy the contents to the output
            self.rendered = self.source
            return

        # Now we're on to the markdowns
        if self.metadata.get("template") is None:
                raise NotImplementedError(f"No template specified for markdown file {self.fp} (this shouldn't happen?)")

        self.rendered = ("_templates" / Path(self.metadata["template"])).read_text(encoding="utf-8")
    
    def fill_helper(self, find, repl):
        self.rendered = self.rendered.replace(find, repl)
    
    def fill_variables(self):
        if self.fp.suffix not in [".html", ".md"]:
            return
        
        self.fill_helper("{_template_page_title}", self.metadata.get("title", ""))
        self.fill_helper("{_template_page_description}", self.metadata.get("description", ""))
        # Todo: og:image (share image) should default to /static/banner.webp or the first image of the article
        self.fill_helper("{_template_target_url}",
                         f"https://{self.domain.domain}/{self.metadata['target'].with_suffix('')}")
        
        self.fill_helper("{_template_etag}", hashlib.sha1(self.fp.read_bytes()).hexdigest()[:12])
        self.fill_helper("{_template_mtime}", str(datetime.fromtimestamp(int(self.fp.stat().st_mtime))))
        self.fill_helper("{_template_template}", self.metadata["template"])
        
        if self.md_ast is not None:  # the ToC only applies for markdown content, not the plain html
            self.fill_helper("{_template_toc_content}", mistune.toc.render_toc_ul(self.md_ast.env["toc_items"]))
        self.fill_helper("{_template_main_content}", self.source)
    
    def write_output(self):
        if self.fp.suffix == ".json":
            return None  # Skip .json metadatas
        
        target_fp = Path(self.domain.output / self.metadata["target"])
        os.makedirs(target_fp.parent, exist_ok=True)  # make sure the output folder actually exists first
        
        if self.fp.suffix not in [".html", ".md"]:
            shutil.copy2(self.fp, target_fp)
            return None  # None because file was skipped / staticfile
        
        # continuing execution only if this was webpage content we parsed (not a staticfile)
        target_fp = target_fp.with_suffix(".html")  # don't forget to set the extension
        if target_fp.is_file():
            # check the sha1 of the target file. We can safely read into memory b/c staticfiles are handled above
            target_sha = hashlib.sha512(target_fp.read_bytes())
            source_sha = hashlib.sha512(self.rendered.encode("utf-8"))
            if target_sha.hexdigest() == source_sha.hexdigest():
                return False  # This page exists, and wasn't updated, so False
            
            target_fp.write_text(self.rendered, encoding="utf-8")
            return True  # Page was updated, so True
        
        # this is a new page!
        target_fp.write_text(self.rendered, encoding="utf-8")
        return "new"  # Page was newly created
    
    def render(self):
        self.render_to_html()
        self.generate_toc()
        self.search_for_og_image()
        self.load_template()
        self.fill_variables()
        return self.write_output()
