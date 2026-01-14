import markdownify

class MarkdownParser:
    def __init__(self):
        pass

    def parse(self, html):
        return markdownify.markdownify(html).strip()
        