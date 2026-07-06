import wx

from m45wxcontrols import UniversalListCtrl


SAMPLE_TRACKS = [
    {
        "id": "trk-001",
        "played": False,
        "title": "Opening Theme",
        "artist": "Demo Ensemble",
        "duration": "02:41",
        "status": "Queued",
    },
    {
        "id": "trk-002",
        "played": True,
        "title": "Late Night Walk",
        "artist": "Synth Avenue",
        "duration": "04:18",
        "status": "Played",
    },
    {
        "id": "trk-003",
        "played": False,
        "title": "Quiet Room",
        "artist": "M45 Sessions",
        "duration": "03:36",
        "status": "Queued",
    },
    {
        "id": "trk-004",
        "played": False,
        "title": "Signal Return",
        "artist": "Control Surface",
        "duration": "05:02",
        "status": "Queued",
    },
]


class UniversalListDemo(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(920, 620))

        self.next_track_number = len(SAMPLE_TRACKS) + 1
        panel = wx.Panel(self)

        self.list = UniversalListCtrl(
            panel,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN,
            checkboxes=True,
            force_dataview=False,
        )
        self._create_columns()

        list_control = self.list.GetControl()
        list_control.SetLabel("Playlist demo list")
        list_control.SetName("Playlist demo list")

        self.status = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SUNKEN,
            size=(-1, 115),
        )
        self.status.SetName("Demo status")

        self._bind_events()
        self._create_layout(panel, list_control)
        self.populate_list()
        self.Center()

    def _create_columns(self):
        self.list.InsertColumn(0, "Played", width=70, checkbox=True)
        self.list.InsertColumn(1, "Title", width=220)
        self.list.InsertColumn(2, "Artist", width=180)
        self.list.InsertColumn(3, "Duration", width=90)
        self.list.InsertColumn(4, "Status", width=120)

    def _bind_events(self):
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selection_changed)
        self.list.Bind(UniversalListCtrl.EVT_ITEM_CHECKED, self.on_item_checked)

    def _create_layout(self, panel, list_control):
        root = wx.BoxSizer(wx.VERTICAL)

        heading = wx.StaticText(panel, label="UniversalListCtrl API demo")
        heading.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        root.Add(heading, 0, wx.ALL, 10)
        root.Add(list_control, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        buttons = wx.FlexGridSizer(cols=4, hgap=8, vgap=8)
        buttons.AddGrowableCol(0, 1)
        buttons.AddGrowableCol(1, 1)
        buttons.AddGrowableCol(2, 1)
        buttons.AddGrowableCol(3, 1)

        actions = [
            ("Append row", self.on_append_row),
            ("Insert before selection", self.on_insert_row),
            ("Delete selection", self.on_delete_selection),
            ("Toggle played", self.on_toggle_played),
            ("Update selected row", self.on_update_selected),
            ("Show row data", self.on_show_row_data),
            ("Select first two", self.on_select_first_two),
            ("Clear selection", self.on_clear_selection),
            ("Ensure last visible", self.on_ensure_last_visible),
            ("Autosize columns", self.on_autosize_columns),
            ("Clear list", self.on_clear_list),
            ("Reload sample data", self.on_reload_sample_data),
        ]

        for label, handler in actions:
            button = wx.Button(panel, label=label)
            button.Bind(wx.EVT_BUTTON, handler)
            buttons.Add(button, 1, wx.EXPAND)

        root.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        root.Add(wx.StaticText(panel, label="Status"), 0, wx.LEFT | wx.RIGHT, 10)
        root.Add(self.status, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(root)

    def populate_list(self):
        with self.list.batch_update():
            self.list.Clear()
            for track in SAMPLE_TRACKS:
                self.list.AppendRow(self._track_to_row(track), data=track.copy())

        self.list.SelectRow(0)
        self.log("Loaded sample data with Clear(), AppendRow(), SetRowData() and batch_update().")

    def _track_to_row(self, track):
        return [
            track["played"],
            track["title"],
            track["artist"],
            track["duration"],
            track["status"],
        ]

    def _new_track(self, title_prefix="New Track"):
        number = self.next_track_number
        self.next_track_number += 1
        return {
            "id": f"trk-{number:03d}",
            "played": False,
            "title": f"{title_prefix} {number}",
            "artist": "Generated Example",
            "duration": "03:00",
            "status": "Queued",
        }

    def selected_rows(self):
        return self.list.GetSelectedRows()

    def first_selected_row(self):
        selected = self.selected_rows()
        return selected[0] if selected else -1

    def log(self, message):
        self.status.AppendText(message + "\n")

    def on_selection_changed(self, event):
        row = event.GetIndex()
        self.log(f"Selection changed: GetSelectedRow() -> {self.list.GetSelectedRow()}, event row -> {row}")
        event.Skip()

    def on_item_checked(self, event):
        row = event.GetIndex()
        checked = event.IsChecked()
        data = self.list.GetRowData(row)
        if data is not None:
            data["played"] = checked
            data["status"] = "Played" if checked else "Queued"
            self.list.SetRowData(row, data)
            self.list.SetItemText(row, 4, data["status"])
        self.log(f"Checkbox changed: row {row}, IsChecked() -> {checked}")

    def on_append_row(self, event):
        track = self._new_track()
        self.list.AppendRow(self._track_to_row(track), data=track)
        row = self.list.GetItemCount() - 1
        self.list.SelectRow(row)
        self.list.EnsureVisible(row)
        self.log(f"AppendRow(): added {track['id']} at row {row}")

    def on_insert_row(self, event):
        row = self.first_selected_row()
        if row == -1:
            row = 0
        track = self._new_track("Inserted Track")
        self.list.InsertRow(row, self._track_to_row(track), data=track)
        self.list.SelectRow(row)
        self.log(f"InsertRow(): inserted {track['id']} at row {row}")

    def on_delete_selection(self, event):
        rows = self.selected_rows()
        if not rows:
            self.log("DeleteRow(): no selected rows")
            return

        for row in sorted(rows, reverse=True):
            self.list.DeleteRow(row)
        self.log(f"DeleteRow(): removed rows {rows}")

    def on_toggle_played(self, event):
        rows = self.selected_rows()
        if not rows:
            self.log("SetChecked(): no selected rows")
            return

        for row in rows:
            self.list.SetChecked(row, not self.list.IsChecked(row))
        self.log(f"SetChecked()/IsChecked(): toggled rows {rows}")

    def on_update_selected(self, event):
        row = self.first_selected_row()
        if row == -1:
            self.log("SetRow(): no selected row")
            return

        values = self.list.GetRow(row)
        values[4] = "Updated"
        self.list.SetRow(row, values)

        data = self.list.GetRowData(row)
        if data is not None:
            data["status"] = "Updated"
            self.list.SetRowData(row, data)

        self.log(f"GetRow()/SetRow(): row {row} now has status 'Updated'")

    def on_show_row_data(self, event):
        row = self.first_selected_row()
        if row == -1:
            self.log("GetRowData(): no selected row")
            return

        self.log(f"GetRowData({row}) -> {self.list.GetRowData(row)}")
        self.log(f"GetItemText({row}, 1) -> {self.list.GetItemText(row, 1)}")

    def on_select_first_two(self, event):
        rows = [row for row in (0, 1) if row < self.list.GetItemCount()]
        self.list.SelectRows(rows)
        self.log(f"SelectRows({rows}); GetSelectedRows() -> {self.list.GetSelectedRows()}")

    def on_clear_selection(self, event):
        self.list.ClearSelection()
        self.log("ClearSelection(): selection cleared")

    def on_ensure_last_visible(self, event):
        row = self.list.GetItemCount() - 1
        if row < 0:
            self.log("EnsureVisible(): list is empty")
            return

        self.list.SelectRow(row)
        self.list.FocusRow(row)
        self.list.EnsureVisible(row)
        self.log(f"SelectRow()/FocusRow()/EnsureVisible(): moved to row {row}")

    def on_autosize_columns(self, event):
        for col in range(self.list.GetColumnCount()):
            self.list.AutosizeColumn(col)
        self.log("AutosizeColumn(): resized all columns")

    def on_clear_list(self, event):
        self.list.Clear()
        self.log("Clear(): removed all rows")

    def on_reload_sample_data(self, event):
        self.populate_list()


if __name__ == "__main__":
    app = wx.App()
    frame = UniversalListDemo(None, "UniversalListCtrl Demo")
    frame.Show()
    app.MainLoop()
