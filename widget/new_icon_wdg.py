from pyasm.widget.icon_wdg import IconWdg


class CustomIconWdg(IconWdg):
    icons = IconWdg.icons

    icons.update({
        # Custom icons

        # 16x16 icons
        'ARROW_UP_SOURCE':     "/context/icons/custom/arrow_up_source.png",
        'ARROW_UP_EQUIPMENT':  "/context/icons/custom/arrow_up_equipment.png",
        'ARROW_OUT_SOURCE':    "/context/icons/custom/arrow_out_source.png",
        'ARROW_OUT_EQUIPMENT': "/context/icons/custom/arrow_out_equipment.png",

        # database icons
        'EQUIPMENT_ADD':       "/context/icons/custom/equipment_add.png",
        'FILE_ADD':            "/context/icons/custom/file_add.png",
        'GRAY_BOMB':           "/context/icons/custom/gray_bomb.png",
        'HACKUP':              "/context/icons/custom/hackup.png",
        'NORMAL_EDIT':         "/context/icons/custom/normal_edit.png",
        'PRIORITY':            "/context/icons/custom/priority.png",
        'QUICK_EDIT':          "/context/icons/custom/quick_edit.png",
        'RED_BOMB':            "/context/icons/custom/red_bomb.png",
        'REPORT_ERROR':        "/context/icons/custom/report_error.png",
        'REPURPOSE':           "/context/icons/custom/repurpose.png",
        'SOURCE_ADD_TAPE':     "/context/icons/custom/source_add_tape.png",
        'SOURCE_PORTAL':       "/context/icons/custom/source_portal.png",
        'TEMPLATE':            "/context/icons/custom/template.png",
        'TEMPLATE_DOWN':       "/context/icons/custom/template_down.png",
    })

    for key, value in icons.items():
        exec ("%s = '%s'" % (key, value))

    def __init__(self, name=None, icon=None, long=False, css='', right_margin='3px', width='', opacity=None, **kwargs):
        try:
            self.icon_path = eval("CustomIconWdg.%s" % icon.upper())
        except:
            self.icon_path = icon
        self.text = name
        self.long = long
        self.css = css
        self.right_margin = right_margin
        self.width = width
        self.kwargs = kwargs
        self.opacity = opacity
        self.size = kwargs.get("size")
        super(CustomIconWdg, self).__init__()
