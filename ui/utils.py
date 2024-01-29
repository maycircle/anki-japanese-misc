from html import escape
from typing import Callable, Optional

from aqt.editor import Editor

from .selection import PersistentSelection, Selection


def enhanceAllAnkiEditables(
    editor: Editor,
    content: str,
    id: str,
    callback: Optional[Callable[[bool], None]] = None
):
    escapeSeq = {"\\": "\\\\", '"': '\\"', "\n": "\\n"}

    escapedId = id.translate(id.maketrans(escapeSeq))
    escapedContent = content.translate(content.maketrans(escapeSeq))

    js = f"""
{{
  var success = false;
  var fields = document.querySelector(".fields");
  if (fields !== null) {{
    var richTextEditables = fields.querySelectorAll(".rich-text-editable");
    for (let i = 0; i < richTextEditables.length; i++) {{
      var root = richTextEditables[i].shadowRoot;
      const id = "{escapedId}";
      if (root.getElementById(id) === null) {{
        const content = "{escapedContent}";
        const elem = document.createElement("div");
        elem.innerHTML = content;
        elem.children[0].id = id;
        root.insertBefore(elem.children[0], root.children[0]);
        success = true;
      }}
    }}
  }}
  success;
}}
"""

    editor.web.page().runJavaScript(js, callback)  # type: ignore


def enhanceSelectedAnkiEditable(editor: Editor, content: str, id: str):
    escapeSeq = {"\\": "\\\\", '"': '\\"', "\n": "\\n"}

    escapedId = id.translate(id.maketrans(escapeSeq))
    escapedContent = content.translate(content.maketrans(escapeSeq))

    js = f"""
{{
  var selection = window.getSelection();
  var node = selection.anchorNode;
  if (node.nodeType !== Node.TEXT_NODE) {{
      node = node.childNodes[selection.anchorOffset];
  }} else {{
    while (node.tagName !== "ANKI-EDITABLE") {{
      node = node.parentNode;
    }}
    node = node.parentNode;
  }}
  if (node !== undefined) {{
    var root = node;
    if (root.shadowRoot) {{
      root = root.shadowRoot;
    }}
    const id = "{escapedId}";
    if (root.getElementById(id) === null) {{
      const content = "{escapedContent}";
      const elem = document.createElement("div");
      elem.innerHTML = content;
      elem.children[0].id = id;
      root.insertBefore(elem.children[0], root.children[0]);
    }}
  }}
}}
"""

    editor.web.page().runJavaScript(js)


def selection(editor: Editor, action: Callable[[Editor, Selection], None]):
    PersistentSelection(editor, action)
