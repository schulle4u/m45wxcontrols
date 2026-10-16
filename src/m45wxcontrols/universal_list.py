"""
Universal list class to choose between ListCtrl and DataViewListCtrl
"""
from contextlib import contextmanager
import sys

import wx
import wx.dataview as dv


class UniversalListCtrl:
    """
    Cross-platform list wrapper with optional checkbox support.

    By default, wx.ListCtrl is used on Windows, while wx.dataview.DataViewListCtrl is used
    on Linux and macOS for better accessibility. The wrapper normalizes list
    operations used by applications so callers do not need to branch on the
    active control type.
    """

    EVT_ITEM_CHECKED = wx.NewEventType()

    def __init__(
        self,
        parent,
        size=wx.DefaultSize,
        style=wx.LC_REPORT | wx.BORDER_SUNKEN,
        checkboxes=False,
        list_type="auto"
    ):
        """
        Initialize universal list control.

        Args:
            parent: Parent wx window.
            size: Initial control size.
            style: wx style flags applied to the underlying list control.
            checkboxes: Whether rows should support checked/unchecked state.
            list_type: Control type: "auto" selects by platform (default),
                "dataview" forces DataViewListCtrl, and "list" forces wx.ListCtrl.

        Raises:
            ValueError: If list_type is not "auto", "dataview", or "list".
        """
        if list_type not in ("auto", "dataview", "list"):
            raise ValueError('list_type must be "auto", "dataview", or "list"')

        # Automatically use DataViewListCtrl on Linux and macOS for accessibility.
        self.use_dataview = list_type == "dataview" or (
            list_type == "auto"
            and (sys.platform.startswith('linux') or sys.platform == 'darwin')
        )
        self.checkboxes = checkboxes
        self._checkbox_column = None
        self._row_data = []

        if self.use_dataview:
            self.control = dv.DataViewListCtrl(parent, style=style, size=size)
        else:
            self.control = wx.ListCtrl(parent, style=style, size=size)
            if self.checkboxes:
                self.control.EnableCheckBoxes()

    def _format_row(self, entry):
        """
        Convert row values into the representation expected by the active
        control.
        """
        return [
            bool(item) if col_idx == self._checkbox_column else str(item)
            for col_idx, item in enumerate(entry)
        ]

    def _is_valid_row(self, index):
        """
        Return whether a row index points to an existing row.
        """
        return 0 <= index < self.GetItemCount()

    def InsertColumn(self, col, heading, width=wx.LIST_AUTOSIZE, checkbox=False):
        """
        Insert a column in the underlying control.

        Args:
            col: Zero-based column index.
            heading: Text shown in the column header.
            width: Column width or wx autosize constant.
            checkbox: Whether this column stores checkbox/toggle values.
        """
        if self.use_dataview:
            if checkbox:
                self.control.AppendToggleColumn(
                    heading,
                    mode=dv.DATAVIEW_CELL_ACTIVATABLE,
                    width=width
                )
                self._checkbox_column = col
            else:
                self.control.AppendTextColumn(heading, width=width)
        else:
            self.control.InsertColumn(col, heading, width=width)
            if checkbox:
                self._checkbox_column = col

    def Append(self, entry):
        """
        Adds a row to the list.
        'entry' must be a list or tuple of values matching the column count.

        Args:
            entry: Sequence of row values. Checkbox columns should contain
                truthy or falsy values; text columns are converted to strings.
        """
        if self.use_dataview:
            # DataViewListCtrl.AppendItem expects exactly one argument: a sequence
            # Keep toggle columns as bool and format text columns as strings.
            self.control.AppendItem(self._format_row(entry))
        else:
            # ListCtrl: Insert the first item, then set sub-items
            index = self.control.GetItemCount()
            if self._checkbox_column == 0:
                self.control.InsertItem(index, "")
                self.control.CheckItem(index, bool(entry[0]))
                text_start_col = 1
            else:
                self.control.InsertItem(index, str(entry[0]))
                text_start_col = 1
            for col_idx in range(text_start_col, len(entry)):
                self.control.SetItem(index, col_idx, str(entry[col_idx]))

        self._row_data.append(None)

    def AppendRow(self, entry, data=None):
        """
        Append a row and optionally attach application data to it.

        Args:
            entry: Sequence of row values.
            data: Optional application-specific object associated with the row.
        """
        self.Append(entry)
        self.SetRowData(self.GetItemCount() - 1, data)

    def InsertRow(self, index, entry, data=None):
        """
        Insert a row at a specific index.

        Args:
            index: Zero-based insertion index. Values outside the list are
                clamped to the beginning or end.
            entry: Sequence of row values.
            data: Optional application-specific object associated with the row.
        """
        index = max(0, min(index, self.GetItemCount()))

        if self.use_dataview:
            self.control.InsertItem(index, self._format_row(entry))
        else:
            if self._checkbox_column == 0:
                self.control.InsertItem(index, "")
                self.control.CheckItem(index, bool(entry[0]))
                text_start_col = 1
            else:
                self.control.InsertItem(index, str(entry[0]))
                text_start_col = 1
            for col_idx in range(text_start_col, len(entry)):
                self.control.SetItem(index, col_idx, str(entry[col_idx]))

        self._row_data.insert(index, data)

    def DeleteRow(self, index):
        """
        Delete a row by index.

        Args:
            index: Zero-based row index to delete.

        Returns:
            bool: True when a row was deleted, otherwise False.
        """
        if not self._is_valid_row(index):
            return False

        self.control.DeleteItem(index)
        if index < len(self._row_data):
            del self._row_data[index]
        return True

    def DeleteAllItems(self):
        """
        Delete all rows from the list.
        """
        self.control.DeleteAllItems()
        self._row_data.clear()

    def Clear(self):
        """
        Delete all rows from the list.
        """
        self.DeleteAllItems()

    def GetItemText(self, row, col=0):
        """
        Return the text shown in a cell.

        Args:
            row: Zero-based row index.
            col: Zero-based column index.

        Returns:
            str: Cell text, or an empty string for invalid rows.
        """
        if not self._is_valid_row(row):
            return ""

        if self.use_dataview:
            if col == self._checkbox_column:
                return str(self.control.GetToggleValue(row, col))
            return self.control.GetTextValue(row, col)
        return self.control.GetItemText(row, col)

    def SetItemText(self, row, col, text):
        """
        Set the text/value shown in a cell.

        Args:
            row: Zero-based row index.
            col: Zero-based column index.
            text: New cell value. Checkbox columns interpret this as bool.
        """
        if not self._is_valid_row(row):
            return

        if col == self._checkbox_column:
            self.SetChecked(row, bool(text))
        elif self.use_dataview:
            self.control.SetTextValue(str(text), row, col)
        else:
            self.control.SetItem(row, col, str(text))

    def GetRow(self, row):
        """
        Return all cell values for a row.

        Args:
            row: Zero-based row index.

        Returns:
            list: Row values. Checkbox columns are returned as bool values.
        """
        if not self._is_valid_row(row):
            return []

        values = []
        for col in range(self.GetColumnCount()):
            if col == self._checkbox_column:
                values.append(self.IsChecked(row))
            else:
                values.append(self.GetItemText(row, col))
        return values

    def SetRow(self, row, values):
        """
        Replace the visible values in an existing row.

        Args:
            row: Zero-based row index.
            values: Sequence of new row values.
        """
        if not self._is_valid_row(row):
            return

        for col, value in enumerate(values):
            self.SetItemText(row, col, value)

    def SetRowData(self, row, data):
        """
        Associate arbitrary application data with a row.

        Args:
            row: Zero-based row index.
            data: Application-specific object to store.
        """
        if not self._is_valid_row(row):
            return

        while len(self._row_data) < self.GetItemCount():
            self._row_data.append(None)
        self._row_data[row] = data

    def GetRowData(self, row):
        """
        Return application data associated with a row.

        Args:
            row: Zero-based row index.

        Returns:
            object: Stored row data, or None when no data is stored.
        """
        if not self._is_valid_row(row) or row >= len(self._row_data):
            return None
        return self._row_data[row]

    def Bind(self, event_type, handler):
        """
        Unifies binding for common list events.

        Args:
            event_type: wx event binder or UniversalListCtrl event type.
            handler: Callable that receives the normalized event.
        """
        if event_type == wx.EVT_LIST_ITEM_SELECTED:
            if self.use_dataview:
                # Map DataView selection to List selection logic
                self.control.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED,
                                  lambda evt: self._handle_selection(evt, handler))
            else:
                self.control.Bind(wx.EVT_LIST_ITEM_SELECTED, handler)

        elif event_type in [wx.EVT_CONTEXT_MENU, wx.EVT_CHAR_HOOK]:
            # These are standard wx.Window events, no mapping needed
            self.control.Bind(event_type, handler)

        elif event_type == self.EVT_ITEM_CHECKED:
            if self.use_dataview:
                self.control.Bind(
                    dv.EVT_DATAVIEW_ITEM_VALUE_CHANGED,
                    lambda evt: self._handle_check(evt, handler)
                )
            else:
                self.control.Bind(
                    wx.EVT_LIST_ITEM_CHECKED,
                    lambda evt: self._handle_check(evt, handler)
                )
                self.control.Bind(
                    wx.EVT_LIST_ITEM_UNCHECKED,
                    lambda evt: self._handle_check(evt, handler)
                )

        else:
            # Fallback for other events
            self.control.Bind(event_type, handler)

    def _handle_selection(self, evt, user_handler):
        """
        Internal helper to normalize DataViewEvent so it feels
        closer to a ListEvent for the handler.

        Args:
            evt: Native DataView selection event.
            user_handler: Original event handler supplied by the caller.
        """
        # Accessibility: Ensure screen reader focus remains stable
        # while processing selection logic.
        if self.use_dataview:
            item = evt.GetItem()
            if item.IsOk():
                # We can inject a 'GetIndex' method into the event object
                # to mimic ListEvent if necessary, or just call the handler.
                evt.GetIndex = lambda: self.control.ItemToRow(item)

        user_handler(evt)

    def _handle_check(self, evt, user_handler):
        """
        Normalize checkbox/toggle events across ListCtrl and DataViewListCtrl.

        Args:
            evt: Native checkbox or DataView value-changed event.
            user_handler: Original event handler supplied by the caller.
        """
        row = -1
        checked = False

        if self.use_dataview:
            if evt.GetColumn() != self._checkbox_column:
                evt.Skip()
                return
            item = evt.GetItem()
            if item.IsOk():
                row = self.control.ItemToRow(item)
                checked = self.control.GetToggleValue(row, self._checkbox_column)
        else:
            row = evt.GetIndex()
            checked = self.control.IsItemChecked(row)

        evt.GetIndex = lambda: row
        evt.IsChecked = lambda: checked
        user_handler(evt)

    def GetSelectedRow(self):
        """
        Return the currently selected row index.

        Returns:
            int: Selected row index, or -1 when no row is selected.
        """
        if self.use_dataview:
            item = self.control.GetSelection()
            return self.control.ItemToRow(item) if item.IsOk() else -1
        else:
            return self.control.GetFirstSelected()

    def GetSelectedRows(self):
        """
        Return all selected row indices.

        Returns:
            list[int]: Selected row indices.
        """
        if self.use_dataview:
            selections = self.control.GetSelections()
            return [
                self.control.ItemToRow(item)
                for item in selections
                if item.IsOk()
            ]

        rows = []
        row = self.control.GetFirstSelected()
        while row != -1:
            rows.append(row)
            row = self.control.GetNextSelected(row)
        return rows

    def IsSelected(self, index):
        """
        Return whether a row is currently selected.
        """
        if not self._is_valid_row(index):
            return False

        if self.use_dataview:
            item = self.control.RowToItem(index)
            return item.IsOk() and self.control.IsSelected(item)
        return self.control.GetItemState(index, wx.LIST_STATE_SELECTED) != 0

    def GetItemCount(self):
        """
        Return the total number of items in the list.

        Returns:
            int: Number of rows in the underlying control.
        """
        return self.control.GetItemCount()

    def SelectRow(self, index):
        """
        Selects and focuses a row by index.

        Args:
            index: Zero-based row index to select.
        """
        if index < 0 or index >= self.GetItemCount():
            return

        if self.use_dataview:
            # Try to avoid ATK noise
            if self.control.GetColumnCount() > 0:
                item = self.control.RowToItem(index)
                if item.IsOk():
                    self.control.Select(item)
                    self.control.EnsureVisible(item)
        else:
            self.control.Select(index)
            self.control.Focus(index)

    def SelectRows(self, indices):
        """
        Select multiple rows.

        Args:
            indices: Iterable of zero-based row indices.
        """
        self.ClearSelection()
        for index in indices:
            if not self._is_valid_row(index):
                continue
            if self.use_dataview:
                item = self.control.RowToItem(index)
                if item.IsOk():
                    self.control.Select(item)
            else:
                self.control.Select(index)

    def ClearSelection(self):
        """
        Clear the current row selection.
        """
        if self.use_dataview:
            self.control.UnselectAll()
        else:
            for index in self.GetSelectedRows():
                self.control.Select(index, False)

    def SetFocus(self):
        """
        Move keyboard focus to list control.
        """
        self.control.SetFocus()

    def FocusRow(self, index):
        """
        Move keyboard focus to a row without changing its checked state.
        """
        if not self._is_valid_row(index):
            return

        if self.use_dataview:
            item = self.control.RowToItem(index)
            if item.IsOk():
                self.control.SetCurrentItem(item)
                self.control.EnsureVisible(item)
        else:
            self.control.Focus(index)

    def EnsureVisible(self, index):
        """
        Scroll a row into view.
        """
        if not self._is_valid_row(index):
            return

        if self.use_dataview:
            item = self.control.RowToItem(index)
            if item.IsOk():
                self.control.EnsureVisible(item)
        else:
            self.control.EnsureVisible(index)

    def GetFocusedRow(self):
        """
        Return the row that currently has keyboard focus.

        Returns:
            int: Focused row index, or -1 when no row has focus.
        """
        if self.use_dataview:
            item = self.control.GetCurrentItem()
            return self.control.ItemToRow(item) if item.IsOk() else -1
        return self.control.GetFocusedItem()

    def GetColumnCount(self):
        """
        Return the number of columns.
        """
        return self.control.GetColumnCount()

    def SetColumnWidth(self, col, width):
        """
        Set the width of a column.
        """
        if col < 0 or col >= self.GetColumnCount():
            return

        if self.use_dataview:
            self.control.GetColumn(col).SetWidth(width)
        else:
            self.control.SetColumnWidth(col, width)

    def GetColumnWidth(self, col):
        """
        Return the width of a column.
        """
        if col < 0 or col >= self.GetColumnCount():
            return 0

        if self.use_dataview:
            return self.control.GetColumn(col).GetWidth()
        return self.control.GetColumnWidth(col)

    def AutosizeColumn(self, col):
        """
        Resize a column to fit its content.
        """
        if col < 0 or col >= self.GetColumnCount():
            return

        self.SetColumnWidth(col, wx.LIST_AUTOSIZE)

    def Freeze(self):
        """
        Freeze visual updates for batch changes.
        """
        self.control.Freeze()

    def Thaw(self):
        """
        Resume visual updates after batch changes.
        """
        self.control.Thaw()

    @contextmanager
    def batch_update(self):
        """
        Context manager that freezes the control during multiple updates.
        """
        self.Freeze()
        try:
            yield self
        finally:
            self.Thaw()

    def SetChecked(self, index, checked):
        """
        Set a row checkbox/toggle value without changing selection.

        Args:
            index: Zero-based row index to update.
            checked: New checked state.
        """
        if self._checkbox_column is None or index < 0 or index >= self.GetItemCount():
            return

        if self.use_dataview:
            self.control.SetToggleValue(bool(checked), index, self._checkbox_column)
        else:
            self.control.CheckItem(index, bool(checked))

    def IsChecked(self, index):
        """
        Return the row checkbox/toggle state.

        Args:
            index: Zero-based row index to inspect.

        Returns:
            bool: True when the row is checked, otherwise False.
        """
        if self._checkbox_column is None or index < 0 or index >= self.GetItemCount():
            return False

        if self.use_dataview:
            return self.control.GetToggleValue(index, self._checkbox_column)
        return self.control.IsItemChecked(index)

    def GetControl(self):
        """
        Return the wrapped wx control.

        Returns:
            wx.Window: Underlying wx.ListCtrl or DataViewListCtrl instance.
        """
        return self.control
