These templates are shared across all sites. Simply use them in the website source.

Run this command to check all variables currently used across all templates:

    grep -hoG "{_template_[a-z0-9_]*}" *.html | sort | uniq

* `{_template_etag}`: First 12char of SHA1 of the source file
* `{_template_main_content}`: This gets filled with rendered markdown representing the actual content of interest
* `{_template_mtime}`: Filesystem modification time of the source file
* `{_template_og_image}`: URL of the og:image metadata
* `{_template_og_image_alt}`: (Todo) Alt text of the og:image metadata. Should be the alt= of the <img>
* `{_template_og_image_height}`: (Todo) Height of the og:image. Should be autodetected by sitegen
* `{_template_og_image_mime}`: (Todo) Mime type of the og:image (eg. image/webp). Should be autodetected by sitegen
* `{_template_og_image_width}`: (Todo) Width of the og:image. Should be autodetected by sitegen
* `{_template_page_description}`: Short summary/description of the page's content (eg. opener of an article)
* `{_template_page_title}`: Title of the page. Used for browser title and share-card title 
* `{_template_target_url}`: URL that this page will be rendered at
* `{_template_template}`: Filename of the template that was used to render this page
* `{_template_toc_content}`: Rendered HTML for the table of contents listing

## Page metadata variables

## Domain metadata variables
