import wx
from m45wxcontrols import AccessibleSpinCtrl

class AccessibleSpinDemo(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800, 600))

        panel = wx.Panel(self)
        
        # Create the custom control (it's a sizer)
        self.crossfade_ctrl = AccessibleSpinCtrl(
            panel, 
            label_text="Crossfade duration:", 
            initial_val=2.0,
            min_val=0.5,
            max_val=10.0,
            inc=0.1
        )

        # Layout management
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add a label for accessibility/clarity
        label = wx.StaticText(panel, label="Select crossfade duration")
        label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        sizer.Add(label, 0, wx.ALL, 10)
        
        sizer.Add(self.crossfade_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(sizer)
        self.Center()

if __name__ == "__main__":
    app = wx.App()
    frame = AccessibleSpinDemo(None, "AccessibleSpin Demo")
    frame.Show()
    app.MainLoop()