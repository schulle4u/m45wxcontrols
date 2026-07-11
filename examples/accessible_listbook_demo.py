import wx

from m45wxcontrols import AccessibleListbook


class AccessibleListbookDemo(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(900, 600))

        panel = wx.Panel(self)
        root = wx.BoxSizer(wx.VERTICAL)

        heading = wx.StaticText(panel, label="AccessibleListbook API demo")
        heading.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        root.Add(heading, 0, wx.ALL, 10)

        self.book = AccessibleListbook(panel, list_width=210, name="Demo")
        self.book.SetStaticLabel("Cate&gories")
        self.book.GetListBox().SetName("Demo categories")
        root.Add(self.book, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.status = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SUNKEN,
            size=(-1, 95),
        )
        self.status.SetName("Demo status")
        root.Add(self.status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(root)

        self._create_pages()
        self.book.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.on_page_changed)
        self.Center()

    def _create_pages(self):
        self.book.AddPage(
            self._make_page(
                "General",
                [
                    "Project name: M45wxControls",
                    "Purpose: accessible wxPython control wrappers",
                    "This page was selected through a wx.ListBox.",
                ],
            ),
            "General",
            select=True,
        )
        self.book.AddPage(
            self._make_page(
                "Playback",
                [
                    "Default fade: 2.0 seconds",
                    "Replay gain: enabled",
                    "Keyboard users can move through categories with first letters.",
                ],
            ),
            "Playback",
        )
        self.book.AddPage(
            self._make_page(
                "Shortcuts",
                [
                    "Space: play or pause",
                    "N: next track",
                    "P: previous track",
                    "F6: move between navigation and content",
                ],
            ),
            "Shortcuts",
        )
        self.book.AddPage(
            self._make_page(
                "About",
                [
                    "AccessibleListbook mirrors the basic wx.Listbook workflow.",
                    "The left category list is a plain wx.ListBox.",
                    "Page content is shown and hidden as selection changes.",
                ],
            ),
            "About",
        )

    def _make_page(self, _title, lines):
        page = wx.Panel(self.book.GetPageArea())
        sizer = wx.BoxSizer(wx.VERTICAL)

        for line in lines:
            sizer.Add(wx.StaticText(page, label=line), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        page.SetSizer(sizer)
        return page

    def on_page_changed(self, event):
        selection = event.GetSelection()
        self.status.AppendText(
            f"Selection changed: {selection} ({self.book.GetPageText(selection)})\n"
        )
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = AccessibleListbookDemo(None, "AccessibleListbook Demo")
    frame.Show()
    app.MainLoop()
