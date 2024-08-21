## Template variables


## Global domain metadata
The file `config.json` contains configuration data for domains. The top-level keys are the names of folders for each 
domain, and each domain contains global attributes therein, eg.
```json
{
    "output": "/path/to/whatever/nginx/sites/",
    "ntos.tech": {
        "template": "default.html",
        "author": "@ntoskrnl4",
        "default_og_image": "/static/banner.webp"
    }
}
```

## File-specific metadata
Per-page metadata can be stored in adjacent json files (eg. `page.md` would have `page.md.json`), or in inline 
metadata in the source file (`.md` only) (the file must start with a "`\`\`\`meta\n`" code block). The order of 
priority of metadata is as follows: Defaults > Domain > Sidecar > Inline.

## Data processing order:
[x] Staticfiles: copy straight to output folder

HTML:
[x] load metadata (`load_metadata`)
[x] load source (`load_source` and `load_template`)
[x] fill in variables (`fill_variables`)
[x] write to output (`write_output`)

Markdown:
[x] load metadata (`load_metadata`)
[x] load markdown (`load_source`)
[x] detect language, if lang metadata unset (`load_source`)
[x] parse inline metadata (`load_source`)
[x] render markdown to html (`render_to_html`)
[x] generate table of contents (`generate_toc`)
[x] fetch webpage title if metadata not set (`generate_toc`)
[x] look for the og:image in the article, if not overridden in metadata (`search_for_og_image`)
~~[ ] (Todo) render math to svg
[ ] (Todo) parse outgoing WebMentions
[ ] (Todo) scrape comments from twitter/fedi/custom comments solution?~~
[x] load template (`load_template`)
[x] fill in variables (`fill_variables`)
[x] write to output (`write_output`)

Todo:
- Set loading="lazy" attribute on all <img> and <iframe> in page content (sitegen)
- Pre-render hooks for other scripts to modify a page's html
- Pre-generate hooks for other scripts to modify the filesystem (eg. post listing, static rss file,..)
- speaking of, an RSS feed!
