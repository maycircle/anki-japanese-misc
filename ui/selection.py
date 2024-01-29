from abc import ABC, abstractmethod
import json
import re
from typing import Optional

from aqt.editor import Editor
from aqt.qt import *


class Selection(ABC):
    text: Optional[str]
    selectedText: Optional[str]

    @abstractmethod
    def modify(self, html: str, truncate: bool = False):
        pass


class EditorSelection(Selection):
    def __init__(self, editor: Editor):
        self._editor = editor
        self._getSelectedText()

    def _getSelectedText(self) -> None:
        if self._editor.currentField is None:
            self.text = None
            self._setSelectedText(None)
            return
        else:
            self.text = self._editor.note.fields[self._editor.currentField]

        if self._editor.note is None:
            self._setSelectedText(None)
            return

        self._setSelectedText(self._editor.web.selectedText())

    def _setSelectedText(self, elements):
        self.selectedText = elements
        if self.selectedText is not None:
            self.selectedText = convertMalformedSpaces(elements)

    def modify(self, html: str, truncate: bool = False):
        # only works with RichTextInput

        html = convertMalformedSpaces(html)

        if truncate:
            self._editor.web.eval("setFormat('selectAll');")
        self._editor.web.eval(
            "setFormat('insertHTML', %s);" % json.dumps(html))


# works with any contenteditable input controls, especially anki-editable
class PersistentSelection(EditorSelection):
    startOffset: Optional[int]
    endOffset: Optional[int]

    def __init__(self, editor: Editor, callback: Callable[[Editor, Selection], None]):
        super().__init__(editor)
        self.startOffset = None
        self.endOffset = None
        self._saveState(callback)

    def _saveState(self, callback, receivedData=None):
        js = """
{
  var selection = window.getSelection();
  var node = selection.anchorNode;
  if (node.nodeType !== Node.TEXT_NODE) {
      node = node.childNodes[selection.anchorOffset];
  } else {
    while (node.tagName !== "ANKI-EDITABLE") {
      node = node.parentNode;
    }
  }
  if (node !== undefined) {
    var editable = node;
    if (editable.shadowRoot) {
      selection = editable.shadowRoot.getSelection();
      editable = editable.shadowRoot.querySelector("anki-editable");
    }
    if (editable.childNodes.length > 0) {
      var earlyExit = false;
      var textNode = editable.childNodes[0];
      l1: while (textNode.nodeType !== Node.TEXT_NODE) {
        if (textNode.childNodes.length > 0) {
          textNode = textNode.childNodes[0];
          continue;
        }
        while (textNode.nextSibling == null) {
          textNode = textNode.parentNode;
          if (textNode == editable) {
            earlyExit = true;
            break l1;
          }
        }
        textNode = textNode.nextSibling;
      }

      if (!earlyExit) {
        var range = selection.getRangeAt(0);
        var i = 0;
        var node = textNode;
        while (node != range.startContainer) {
          i += node.textContent.length;

          if (node.nextSibling == null) {
            node = node.parentNode;
            if (node.nextSibling == null) {
              break;
            }
          }
          node = node.nextSibling;
          if (node.nodeType !== Node.TEXT_NODE && node.childNodes.length > 0) {
            node = node.childNodes[0];
          }
        }
        
        var start = i + range.startOffset;
        var end = start + range.cloneContents().textContent.length;
        JSON.parse(`{"start": ${start}, "end": ${end}}`);
      }
    }
  }
}
        """

        self._editor.web.page().runJavaScript(
            js, lambda x: self._receive(callback, x))

    def _loadState(self):
        js = f"""
{{
  var selection = window.getSelection();
  var editable = document.activeElement;
  if (editable.shadowRoot) {{
    editable = editable.shadowRoot.querySelector("anki-editable");
  }}
  var textNode = editable.childNodes[0];
  const start = {self.startOffset};
  const end = {self.endOffset};

  var iprev1 = 0;
  var i1 = 0;
  var startNode = textNode;
  var nextNode = textNode;
  while (i1 <= start) {{
    iprev1 = i1;
    i1 += nextNode.textContent.length;

    startNode = nextNode;
    if (nextNode.nextSibling == null) {{
      nextNode = nextNode.parentNode;
      if (nextNode.nextSibling == null) {{
        break;
      }}
    }}
    nextNode = nextNode.nextSibling;
    if (nextNode.nodeType !== Node.TEXT_NODE && nextNode.childNodes.length > 0) {{
      nextNode = nextNode.childNodes[0];
    }}
  }}

  var iprev2 = iprev1;
  var i2 = iprev1;
  var endNode = startNode;
  while (i2 <= end) {{
    iprev2 = i2;
    i2 += endNode.textContent.length;
    if (i2 > end) {{
      break;
    }}

    if (endNode.nextSibling == null) {{
      if (endNode.parentNode.nextSibling == null) {{
        break;
      }}
      endNode = endNode.parentNode;
    }}
    endNode = endNode.nextSibling;
    if (endNode.nodeType !== Node.TEXT_NODE && endNode.childNodes.length > 0) {{
      endNode = endNode.childNodes[0];
    }}
  }}

  selection.removeAllRanges();
  var range = document.createRange();
  range.setStart(startNode, start - iprev1);
  range.setEnd(endNode, end - iprev2);
  range.endOffset = end - iprev2;
  selection.addRange(range);
}}
        """

        self._editor.web.page().runJavaScript(js)

    def _receive(self, callback, data):
        if data is None:
            return

        self.startOffset = data["start"]
        self.endOffset = data["end"]
        callback(self._editor, self)
        self._loadState()


def convertMalformedSpaces(text: str) -> str:
    return re.sub(r'& ?nbsp ?;', ' ', text)
