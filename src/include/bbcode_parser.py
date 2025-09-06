import bbcode


class BBCodeParser:
    def __init__(self):
        self.parser = bbcode.Parser()

        self._register_paragraph()
        self._register_headings()
        self._register_strikethrough()
        self._register_image()
        self._register_spoiler()
        self._register_ordered_list()
        self._register_carousel()
        self._register_video()
        self._register_table()

        self.parser.install_default_formatters()

    def _register_paragraph(self):
        self.parser.add_simple_formatter("p", "<p>%(value)s</p>")

    def _register_headings(self):
        # Steam uses 1-3, but might as well support up to 6
        for i in range(1, 7):
            self.parser.add_simple_formatter(
                f"h{i}", f"<h{i}>%(value)s</h{i}>"
            )

    def _register_strikethrough(self):
        self.parser.add_simple_formatter("s", "<s>%(value)s</s>")
        self.parser.add_simple_formatter("strike", "<s>%(value)s</s>")

    def _register_image(self):
        self.parser.add_simple_formatter(
            "img", '<img src="%(value)s"/>', replace_links=False
        )

    def _register_spoiler(self):
        self.parser.add_simple_formatter(
            "spoiler", "<details><summary>Spoiler</summary>%(value)s</details>"
        )

    def _register_ordered_list(self):
        def render_olist(tag_name, value, options, parent, context):
            return f"<ol>{value}</ol>"

        self.parser.add_formatter(
            "olist",
            render_olist,
            strip=True,
            transform_newlines=False,
            swallow_trailing_newline=True,
        )

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

    def _register_table(self):
        self.parser.add_simple_formatter(
            "table",
            "<table>%(value)s</table>",
            strip=True,
            swallow_trailing_newline=True,
            transform_newlines=False,
            replace_links=False,
            replace_cosmetic=False,
        )

        self.parser.add_simple_formatter(
            "thead",
            "<thead>%(value)s</thead>",
            strip=True,
            swallow_trailing_newline=True,
            transform_newlines=False,
            replace_links=False,
            replace_cosmetic=False,
        )

        self.parser.add_simple_formatter(
            "tbody",
            "<tbody>%(value)s</tbody>",
            strip=True,
            swallow_trailing_newline=True,
            transform_newlines=False,
            replace_links=False,
            replace_cosmetic=False,
        )

        self.parser.add_simple_formatter(
            "tfoot",
            "<tfoot>%(value)s</tfoot>",
            strip=True,
            swallow_trailing_newline=True,
            transform_newlines=False,
            replace_links=False,
            replace_cosmetic=False,
        )

        self.parser.add_simple_formatter(
            "tr",
            "<tr>%(value)s</tr>",
            strip=True,
            swallow_trailing_newline=True,
            transform_newlines=False,
            replace_links=False,
            replace_cosmetic=False,
        )

        self.parser.add_simple_formatter("th", "<th>%(value)s</th>")
        self.parser.add_simple_formatter("td", "<td>%(value)s</td>")

    def format(self, text: str) -> str:
        """Convert BBCode text to HTML."""
        return self.parser.format(text)
