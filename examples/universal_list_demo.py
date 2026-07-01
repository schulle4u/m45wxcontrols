import wx
from m45wxcontrols import UniversalListCtrl

class UniversalListDemo(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800, 600))

        panel = wx.Panel(self)
        
        # Initialize the UniversalListCtrl
        self.list = UniversalListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN, checkboxes=True)

        # 1. Add some columns
        # Column 0: String
        self.list.InsertColumn(0, "ID", width=40)
        # Column 1: String
        self.list.InsertColumn(1, "Task", width=170)
        # Column 2: String (could also be integer, but we use text for simplicity)
        self.list.InsertColumn(2, "Priority", width=100)
        
        # 2. Add sample data
        # Each row is a list/tuple matching the column count and types
        data = [
            ("1", "Initialize Project", "High"),
            ("2", "Design UI Layout", "Medium"),
            ("3", "Write Documentation", "Low"),
            ("4", "Refactor Core Logic", "High")
        ]

        for entry in data:
            self.list.Append(entry)

        # Layout management
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add a label for accessibility/clarity
        label = wx.StaticText(panel, label="Project Task Overview")
        label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        sizer.Add(label, 0, wx.ALL, 10)
        
        # We must call an extra GetControl() method to select Underlying wx.ListCtrl or DataViewListCtrl instance
        list_control = self.list.GetControl()
        list_control.SetLabel("Project Task Overview")
        list_control.SetName("Project Task Overview")
        sizer.Add(list_control, 1, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        self.Center()

if __name__ == "__main__":
    app = wx.App()
    frame = UniversalListDemo(None, "UniversalList Demo")
    frame.Show()
    app.MainLoop()