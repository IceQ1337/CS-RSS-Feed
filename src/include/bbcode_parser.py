import bbcode


class BBCodeParser:
    def __init__(self):
        self.parser = bbcode.Parser()

        self._register_carousel()
        self._register_video()

    def _register_carousel(self):
        def render_carousel(tag_name, value, options, parent, context):
            # Just drop the [carousel] tag, keep inner content (img tags)
            return value

        self.parser.add_formatter("carousel", render_carousel, strip=True)

    def _register_video(self):
        def render_video(tag_name, value, options, parent, context):
            webm = options.get("webm")
            mp4 = options.get("mp4")
            poster = options.get("poster")

            sources = []

            if mp4:
                sources.append(f'<source src="{mp4}" type="video/mp4">')

            if webm:
                sources.append(f'<source src="{webm}" type="video/webm">')

            if not sources:
                return ""

            sources_html = "\n".join(sources)

            return f"""
            <video controls poster="{poster or ''}">
                {sources_html}
            </video>
            """

        self.parser.add_formatter("video", render_video, standalone=True)

    def format(self, text: str) -> str:
        """Convert BBCode text to HTML."""
        return self.parser.format(text)
