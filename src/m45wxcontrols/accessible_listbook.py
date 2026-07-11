"""
Accessible listbook control backed by wx.ListBox.
"""
import wx


class AccessibleListbook(wx.Panel):
    """
    Accessible wx.Listbook-style control using wx.ListBox for page selection.

    The category list is a plain wx.ListBox, which is easier to use with
    screen readers on platforms where wx.ListCtrl accessibility is limited.
    Pages are ordinary wx.Window instances that are shown when their matching
    list entry is selected.
    """

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
        name="AccessibleListbook",
        list_width=180,
    ):
        """
        Initialize the accessible listbook.

        Args:
            parent: Parent wx window.
            id: Window id.
            pos: Initial position.
            size: Initial size.
            style: wx.Panel style flags.
            name: Control name.
            list_width: Width of the category list in pixels.
        """
        super().__init__(parent, id=id, pos=pos, size=size, style=style, name=name)

        self._pages = []
        self._page_texts = []
        self._page_images = []
        self._selection = wx.NOT_FOUND
        self._changing_selection = False

        self.list_label = wx.StaticText(self, label="Cate&gories")
        self.listbox = wx.ListBox(self, style=wx.LB_SINGLE | wx.BORDER_SUNKEN)
        self.listbox.SetName(f"{name} categories")
        self.page_area = wx.Panel(self, style=wx.TAB_TRAVERSAL)

        self._page_sizer = wx.BoxSizer(wx.VERTICAL)
        self.page_area.SetSizer(self._page_sizer)

        left = wx.BoxSizer(wx.VERTICAL)
        left.Add(self.list_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        left.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 5)

        root = wx.BoxSizer(wx.HORIZONTAL)
        root.Add(left, 0, wx.EXPAND)
        root.SetItemMinSize(left, list_width, -1)
        root.Add(self.page_area, 1, wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM, 5)
        self.SetSizer(root)

        self.listbox.Bind(wx.EVT_LISTBOX, self._on_listbox_selection)

    def AddPage(self, page, text, select=False, imageId=wx.NOT_FOUND):
        """
        Add a page to the end of the control.

        Args:
            page: wx.Window displayed as page content.
            text: Label shown in the category list.
            select: Whether to select the new page immediately.
            imageId: Stored for Listbook API compatibility. Images are not
                displayed by wx.ListBox.

        Returns:
            bool: True when the page was added.
        """
        return self.InsertPage(self.GetPageCount(), page, text, select, imageId)

    def InsertPage(self, index, page, text, select=False, imageId=wx.NOT_FOUND):
        """
        Insert a page at a specific index.
        """
        index = max(0, min(index, self.GetPageCount()))
        self._prepare_page(page)

        self._pages.insert(index, page)
        self._page_texts.insert(index, str(text))
        self._page_images.insert(index, imageId)
        self.listbox.Insert(str(text), index)
        self._page_sizer.Insert(index, page, 1, wx.EXPAND)
        page.Hide()

        if self._selection == wx.NOT_FOUND or select:
            self.ChangeSelection(index)
        elif index <= self._selection:
            self._selection += 1
            self.listbox.SetSelection(self._selection)

        self.Layout()
        return True

    def DeletePage(self, index):
        """
        Delete and destroy a page.

        Returns:
            bool: True when a page was deleted.
        """
        page = self.RemovePage(index)
        if page is None:
            return False
        page.Destroy()
        return True

    def RemovePage(self, index):
        """
        Remove a page without destroying it.

        Returns:
            wx.Window | None: Removed page, or None for an invalid index.
        """
        if not self._is_valid_index(index):
            return None

        page = self._pages.pop(index)
        del self._page_texts[index]
        del self._page_images[index]
        self.listbox.Delete(index)
        self._page_sizer.Detach(page)
        page.Hide()

        if not self._pages:
            self._selection = wx.NOT_FOUND
            self.listbox.SetSelection(wx.NOT_FOUND)
        elif index == self._selection:
            self._selection = wx.NOT_FOUND
            self.ChangeSelection(min(index, self.GetPageCount() - 1))
        elif index < self._selection:
            self._selection -= 1
            self.listbox.SetSelection(self._selection)

        self.Layout()
        return page

    def DeleteAllPages(self):
        """
        Delete and destroy all pages.
        """
        for page in self._pages:
            self._page_sizer.Detach(page)
            page.Destroy()
        self._pages.clear()
        self._page_texts.clear()
        self._page_images.clear()
        self.listbox.Clear()
        self._selection = wx.NOT_FOUND
        self.Layout()

    def GetPage(self, index):
        """
        Return the page at index, or None when the index is invalid.
        """
        if not self._is_valid_index(index):
            return None
        return self._pages[index]

    def GetCurrentPage(self):
        """
        Return the currently selected page, or None when no page is selected.
        """
        return self.GetPage(self._selection)

    def GetPageCount(self):
        """
        Return the number of pages.
        """
        return len(self._pages)

    def GetPageText(self, index):
        """
        Return a page label.
        """
        if not self._is_valid_index(index):
            return ""
        return self._page_texts[index]

    def SetPageText(self, index, text):
        """
        Set a page label.

        Returns:
            bool: True when the label was updated.
        """
        if not self._is_valid_index(index):
            return False
        self._page_texts[index] = str(text)
        self.listbox.SetString(index, str(text))
        return True

    def GetPageImage(self, index):
        """
        Return the stored image id for API compatibility.
        """
        if not self._is_valid_index(index):
            return wx.NOT_FOUND
        return self._page_images[index]

    def SetPageImage(self, index, imageId):
        """
        Store an image id for API compatibility.

        wx.ListBox does not display images, but callers can still keep their
        Listbook-oriented code paths intact.
        """
        if not self._is_valid_index(index):
            return False
        self._page_images[index] = imageId
        return True

    def GetSelection(self):
        """
        Return the selected page index, or wx.NOT_FOUND.
        """
        return self._selection

    def SetSelection(self, index):
        """
        Select a page and emit listbook page changing/changed events.

        Returns:
            int: Previously selected index, or wx.NOT_FOUND if selection failed.
        """
        return self._set_selection(index, emit_events=True)

    def ChangeSelection(self, index):
        """
        Select a page without emitting page changing/changed events.

        Returns:
            int: Previously selected index, or wx.NOT_FOUND if selection failed.
        """
        return self._set_selection(index, emit_events=False)

    def AdvanceSelection(self, forward=True):
        """
        Move selection to the next or previous page.
        """
        count = self.GetPageCount()
        if count == 0:
            return

        if self._selection == wx.NOT_FOUND:
            self.SetSelection(0)
            return

        step = 1 if forward else -1
        self.SetSelection((self._selection + step) % count)

    def GetStaticLabel(self):
        """
        Return the text shown above the category list.
        """
        return self.list_label.GetLabel()

    def SetStaticLabel(self, label):
        """
        Set the text shown above the category list.

        This is useful for localized applications because wx.Panel itself does
        not accept a label argument.
        """
        self.list_label.SetLabel(str(label))
        self.Layout()

    def GetListBox(self):
        """
        Return the wx.ListBox used for category navigation.
        """
        return self.listbox

    def GetPageArea(self):
        """
        Return the panel that owns page windows.
        """
        return self.page_area

    def SetListWidth(self, width):
        """
        Set the fixed width of the category list.
        """
        item = self.GetSizer().GetItem(self.listbox)
        if item is not None:
            item.SetMinSize(width, -1)
            self.Layout()

    def _prepare_page(self, page):
        """
        Ensure a page belongs to the internal page area.
        """
        if page.GetParent() is not self.page_area:
            page.Reparent(self.page_area)

    def _is_valid_index(self, index):
        """
        Return whether index points to an existing page.
        """
        return 0 <= index < self.GetPageCount()

    def _set_selection(self, index, emit_events, sync_listbox=True):
        """
        Internal selection implementation.
        """
        if not self._is_valid_index(index):
            return wx.NOT_FOUND

        old_selection = self._selection
        if index == old_selection:
            if sync_listbox:
                self.listbox.SetSelection(index)
            return old_selection

        if emit_events and not self._send_book_event(
            wx.wxEVT_LISTBOOK_PAGE_CHANGING,
            index,
            old_selection,
        ):
            if sync_listbox:
                self.listbox.SetSelection(old_selection)
            return wx.NOT_FOUND

        self._show_page(index, sync_listbox=sync_listbox)

        if emit_events:
            self._send_book_event(wx.wxEVT_LISTBOOK_PAGE_CHANGED, index, old_selection)

        return old_selection

    def _show_page(self, index, sync_listbox=True):
        """
        Show one page and hide the previously selected page.
        """
        old_selection = self._selection
        self._changing_selection = True
        self.page_area.Freeze()
        try:
            if self._is_valid_index(old_selection):
                self._pages[old_selection].Hide()
            self._pages[index].Show()
            self._selection = index
            if sync_listbox:
                self.listbox.SetSelection(index)
            self.page_area.Layout()
        finally:
            self.page_area.Thaw()
            self._changing_selection = False

    def _send_book_event(self, event_type, selection, old_selection):
        """
        Send a wx.BookCtrlEvent and report whether it was allowed.
        """
        event = wx.BookCtrlEvent(event_type, self.GetId(), selection, old_selection)
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)
        return event.IsAllowed()

    def _on_listbox_selection(self, event):
        """
        Select pages when users move through the listbox.
        """
        if self._changing_selection:
            return

        previous = self._selection
        selected = event.GetSelection()
        result = self._set_selection(selected, emit_events=True, sync_listbox=False)
        if result == wx.NOT_FOUND and previous != wx.NOT_FOUND:
            self.listbox.SetSelection(previous)
