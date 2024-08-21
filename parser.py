import mistune
import mistune.toc
import pygments
import pygments.formatters
import pygments.lexers
import string


slug_replacements = {
    " ": "-",
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "ß": "ss",
    "c++": "cpp",
    "c#": "c-sharp",
}


# We intentionally use the mutable cache[] to keep track of slugs so far, and use the index to clear() it
def heading_gen(token: dict, index: int, cache: list[str] = []) -> str:
    """
    Generate the HTML ID for the headings (for anchoring and the ToC)

    :param token: A token object
    :param index:
    :return: A string clearly denoting the given header
    """
    # First, check the cache to see if we've been invoked across instances - if so, reset the cache
    # Index is just the zero-indexed index of what heading this is (linearly down the article, irrespective of tree)
    # Thus, the first heading (title) should be zero, etc. and as a result, within one article parsing, index should
    # equal the length of the cache
    if index < len(cache):
        cache.clear()  # Have to do this because the default argument is one object; setting cache = [] is a *new* list
    
    title = token["text"]  # type: str
    title = title.lower()
    for test, replace in slug_replacements.items():
        title = title.replace(test, replace)
    title = "".join([x for x in title if x in string.ascii_lowercase + string.digits + "_-"])[:32]
    
    modified = title
    if title in cache:  # If this exact title has been used before, just add a counter to the slug and return that
        modified = title + f"-{cache.count(title)}"
    
    cache.append(title)
    
    return modified


class HighlightRenderer(mistune.HTMLRenderer):
    def __init__(self):
        super().__init__(escape=False)
        
    def block_code(self, code, info=None):
        if info:
            lexer = pygments.lexers.get_lexer_by_name(info, stripall=True)
            formatter = pygments.formatters.HtmlFormatter(cssclass='highlight')
            return pygments.highlight(code, lexer, formatter)
        return '<div class="highlight"><pre>' + mistune.escape(code) + '</pre></div>'


parser = mistune.create_markdown(
        renderer=HighlightRenderer(),
        escape=False,
        plugins=[
            "strikethrough",
            "footnotes",
            "table",
            "url",
            "task_lists",
            "spoiler"
        ]
)
mistune.toc.add_toc_hook(parser, max_level=4, heading_id=heading_gen)
