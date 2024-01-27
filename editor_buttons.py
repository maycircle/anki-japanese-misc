from html import escape
from typing import Callable, Literal, Optional
from xml.etree.ElementTree import Element, tostring

from anki.notes import Note
from aqt import gui_hooks
from aqt import mw
from aqt.addcards import AddCards
from aqt.browser.browser import Browser
from aqt.editor import Editor
from aqt.qt import *
from aqt.utils import shortcut

from .svgelements.svgelements import svgelements

# buttons that will be disabled when user focuses on PlainTextInput
_addonButtonsPlainDisableIds = []
# --icon-size: 70% from Anki source
ICON_SIZE_PERCENTAGE = 70


# venv/Lib/site-packages/aqt/editor.py 226
# venv/Lib/site-packages/aqt/editor.py 279
def addButton(
    editor: Editor,
    icon: Optional[str],
    cmd: str,
    func: Callable[[Editor], None],
    tip: str = "",
    label: str = "",
    id: Optional[str] = None,
    toggleable: bool = False,
    keys: Optional[str] = None,
    disables: Union[Literal["always"], Literal["rich"],
                    Literal["never"], bool] = True,
    rightside: bool = True,
    borderRadius: Union[Literal["both"], Literal["left"],
                        Literal["right"], Literal["none"]] = "both",
) -> str:
    """ Assign func to bridge cmd, register shortcut, return button.

    (unlike original, has inline SVG support, animations and UX configuration)
    """

    if func:
        editor._links[cmd] = func
        if keys:
            def on_activated() -> None:
                func(editor)

            if toggleable:
                id = id or cmd

                def on_hotkey() -> None:
                    on_activated()
                    editor.web.eval(
                        f'toggleEditorButton(document.getElementById("{id}"));'
                    )
            else:
                on_hotkey = on_activated

            QShortcut(  # type: ignore
                QKeySequence(keys),
                editor.widget,
                activated=on_hotkey,
            )

    if icon:
        isabs = os.path.isabs(icon)
        isqrc = icon.startswith("qrc:/")

        if isabs and os.path.splitext(icon)[-1].lower() == ".svg":
            if not os.path.exists(icon):
                raise FileNotFoundError

            svg = svgelements.SVG.parse(icon)  # type: svgelements.SVG
            svg.width = 24
            svg.height = 24
            for element in svg.elements():
                if hasattr(element, "fill"):
                    delattr(element, "fill")
                delattr(element, "transform")

            root = svgelements._write_node(svg)  # type: Element
            root.set('style', " ".join([escape(x.strip()) for x in f"""
                position: absolute;
                width: {ICON_SIZE_PERCENTAGE}%;
                height: {ICON_SIZE_PERCENTAGE}%;
                top: calc((100% - {ICON_SIZE_PERCENTAGE}%) / 2);
                bottom: calc((100% - {ICON_SIZE_PERCENTAGE}%) / 2);
                left: calc((100% - {ICON_SIZE_PERCENTAGE}%) / 2);
                right: calc((100% - {ICON_SIZE_PERCENTAGE}%) / 2);
                fill: currentColor;
                vertical-align: unset;
            """.split('\n')]))
            imgelm = tostring(root, encoding="unicode")
        else:
            if isqrc:
                iconstr = icon
            elif isabs:
                iconstr = editor.resourceToData(icon)
            else:
                iconstr = f"/_anki/imgs/{icon}.png"
            imgelm = f"""<img class="topbut" src="{iconstr}">"""
    else:
        imgelm = ""

    if label or not imgelm:
        labelelm = label or cmd
    else:
        labelelm = ""

    if id:
        idstr = f"id={id}"
    else:
        idstr = ""

    if toggleable:
        toggleScript = "toggleEditorButton(this);"
    else:
        toggleScript = ""

    tip = shortcut(tip)

    if rightside:
        class_ = "linkb"
    else:
        class_ = "rounded"

    if disables == False or disables == "never":
        class_ += " perm"
    elif disables == "always":
        id = id or cmd
        idstr = f"id={id}"
        _addonButtonsPlainDisableIds.append(id)

    style = {}
    stylestr = ""
    if borderRadius == "left":
        style["border-top-right-radius"] = "0"
        style["border-bottom-right-radius"] = "0"
    elif borderRadius == "right":
        style["border-top-left-radius"] = "0"
        style["border-bottom-left-radius"] = "0"
    elif borderRadius == "none":
        style["border-radius"] = "0"
    if len(style) > 0:
        stylestr = 'style="'
        stylestr += escape(" ".join([f"{k}: {v};" for k, v in style.items()]))
        stylestr += '"'

    return """
        <button tabindex=-1
            {id}
            class="{class_}"
            type="button"
            title="{tip}"
            onclick="pycmd('{cmd}');{togglesc}return false;"
            onmousedown="window.event.preventDefault();"
            {style}
        >
            {imgelm}
            {labelelm}
        </button>
    """.format(
        id=idstr,
        class_=class_,
        tip=tip,
        cmd=cmd,
        togglesc=toggleScript,
        style=stylestr,
        imgelm=imgelm,
        labelelm=labelelm,
    )


def _editorDidFocusField(note: Note, currentField: int):
    """Disables addon buttons when user focuses on PlainTextInput"""

    js = f"""
{{
  var selection = window.getSelection();
  var node = selection.anchorNode.childNodes[selection.anchorOffset];
  const ids = [{", ".join([f'"{x}"' for x in _addonButtonsPlainDisableIds])}];
  if (node !== undefined && node.shadowRoot === null) {{
    for (var i = 0; i < ids.length; i++) {{
      var element = document.getElementById(ids[i]);
      element.setAttribute("disabled", "");
    }}
    true;
  }} else {{
    false;
  }}
}}
    """

    window = mw.app.activeWindow()
    if not isinstance(window, AddCards) and not isinstance(window, Browser):
        return
    editor = window.editor
    editor.web.page().runJavaScript(js)


gui_hooks.editor_did_focus_field.append(_editorDidFocusField)
