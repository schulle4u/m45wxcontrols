# M45wxControls
Special controls for wxPython by M45Development

This package contains custom wrappers for existing wxPython controls, primarily to work around GUI limitations and solve accessibility issues. As these modules were built for my own projects, the supported features are likely to be incomplete. However, feel free to open an issue or contribute missing features as a pull request. 

## Installation

Until official PyPI packages are available, Grab the latest whl from the releases page and install it into your project environment. Then import one of the provided controls, e.g.: 

```
from m45wxcontrols import AccessibleSpinCtrl, CustomTextEntryDialog, UniversalListCtrl
```

## Controls

### AccessibleSpinCtrl
An accessible floating-point spin control composed of wx widgets. Can be used as a more accessible alternative to `wx.SpinCtrlDouble`.

The control exposes a labeled text field as the primary interaction point and keeps a wx.SpinButton in sync for mouse users. Arrow keys on the text field adjust the value directly, which makes the widget easier to use with screen readers. 

The following arguments are available: 

* `parent`: Parent wx window that owns the child controls.
* `label_text`: Label shown next to the text field and used as its accessible name.
* `initial_val`: Initial numeric value displayed in the control.
* `min_val`: Minimum allowed value.
* `max_val`: Maximum allowed value.
* `inc`: Increment used by the spin button and Up/Down arrow keys.

### CustomTextEntryDialog
Custom text entry dialog with translatable button labels.

The dialog mirrors the simple wx.TextEntryDialog workflow while allowing callers to provide localized OK and Cancel labels.

The following arguments are available: 

* `parent`: Parent window (MainFrame)
* `message`: text input message
* `caption`: text input caption
* `default_value`: optional default value
* `ok_label`: optional OK button label (default: `&OK`)
* `cancel_label`: optional cancel button label (default: `&Cancel`)

### UniversalListCtrl
Cross-platform list wrapper with optional checkbox support.

`wx.ListCtrl` is used on Windows, while `wx.dataview.DataViewListCtrl` is used on Linux and macOS for better accessibility. The wrapper normalizes a small subset of common list operations.

The following arguments are available: 

* `parent`: Parent wx window.
* `size`: Initial control size (default: `wx.DefaultSize`).
* `style`: wx style flags applied to the underlying list control (default: `wx.LC_REPORT | wx.BORDER_SUNKEN`).
* `checkboxes`: Whether rows should support checked/unchecked state (default: False).
* `force_dataview`: Force DataViewListCtrl even on platforms that would normally use wx.ListCtrl (default: False).

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

