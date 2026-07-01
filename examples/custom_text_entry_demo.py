import wx
from m45wxcontrols import CustomTextEntryDialog

class TextEntryDemo(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800, 600))

        dlg = CustomTextEntryDialog(
            parent,
            "Enter stream URL:",
            "Load Stream",
            default_value = "https://",
            ok_label="Go!", cancel_label="Not yet"
        )
        dlg.Center()
        
        if dlg.ShowModal() == wx.ID_OK:
            wx.MessageBox("Failed to load stream. This is just a demonstration.", "Error"), wx.OK | wx.ICON_ERROR

        dlg.Destroy()
        

if __name__ == "__main__":
    app = wx.App()
    frame = TextEntryDemo(None, "Text Entry Demo")
    frame.Close()
    app.MainLoop()