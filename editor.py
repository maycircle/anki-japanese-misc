import os
import re
from typing import Callable, Optional, Union
import weakref

from anki.hooks import addHook
from anki.notes import Note
from aqt import gui_hooks
from aqt.editor import Editor

from .editor_buttons import addButton
from .globals import ADDON_ROOT_PATH, config
from .selection import Selection
from .utils import enhanceAllAnkiEditables, selection
from .webview import _getPitchAccentStylesheet

# weak reference to current instance of `aqt.editor.Editor` for hooks that
# don't accept it as a paramater
_editor = None  # type: Optional[weakref.ReferenceType[Editor]]
_editorInjectedStyles = False


def setupEditorButtons(buttons: list[str], editor: Editor) -> list[str]:
    addPitch1Button = addButton(
        editor,
        os.path.join(ADDON_ROOT_PATH, "icons", "add_pitch_1.svg"),
        "addPitch1",
        lambda e: selection(e, addPitch1),
        "Add opening pitch",
        disables="always",
        borderRadius="left",
    )
    addPitch2Button = addButton(
        editor,
        os.path.join(ADDON_ROOT_PATH, "icons", "add_pitch_2.svg"),
        "addPitch2",
        lambda e: selection(e, addPitch2),
        "Add continuous pitch",
        disables="always",
        borderRadius="none",
    )
    addPitch3Button = addButton(
        editor,
        os.path.join(ADDON_ROOT_PATH, "icons", "add_pitch_3.svg"),
        "addPitch3",
        lambda e: selection(e, addPitch3),
        "Add closing pitch",
        disables="always",
        borderRadius="none",
    )
    clearPitchButton = addButton(
        editor,
        os.path.join(ADDON_ROOT_PATH, "icons", "add_pitch_4.svg"),
        "clearPitch",
        lambda e: selection(e, clearPitch),
        "Clear pitch",
        disables="always",
        borderRadius="right",
    )

    return buttons + [
        addPitch1Button,
        addPitch2Button,
        addPitch3Button,
        clearPitchButton
    ]


def addPitch1(editor: Editor, selection: Selection):
    if selection.selectedText == None:
        return

    if config.useSpansOverTags:
        selection.modify(
            f'<span class="{config.openingPitchClassname}">{selection.selectedText}</span>')
    else:
        selection.modify(f'<pop>{selection.selectedText}</pop>')


def addPitch2(editor: Editor, selection: Selection):
    if selection.selectedText == None:
        return

    if config.useSpansOverTags:
        selection.modify(
            f'<span class="{config.continuousPitchClassname}">{selection.selectedText}</span>')
    else:
        selection.modify(f'<pco>{selection.selectedText}</pco>')


def addPitch3(editor: Editor, selection: Selection):
    if selection.selectedText == None:
        return

    if config.useSpansOverTags:
        selection.modify(
            f'<span class="{config.closingPitchClassname}">{selection.selectedText}</span>')
    else:
        selection.modify(f'<pcl>{selection.selectedText}</pcl>')


def _subr(
    pattern: Union[str, re.Pattern[str]],
    repl: Union[str, Callable[[re.Match[str]], str]],
    string: str,
):
    a = string
    b = ""
    while a != b:
        b = a
        a = re.sub(pattern, repl, b)
    return a


def clearPitch(editor: Editor, selection: Selection):
    if selection.text == None:
        return

    if editor.currentField is None:
        return

    patterns = [
        r"<span class=\"(?:"
        + re.escape(config.openingPitchClassname)
        + "|" + re.escape(config.continuousPitchClassname)
        + "|" + re.escape(config.closingPitchClassname)
        + r")\">(.*?)<\/span>",
        r"<pop>(.*?)<\/pop>",
        r"<pco>(.*?)<\/pco>",
        r"<pcl>(.*?)<\/pcl>",
    ]

    s = selection.text
    for p in patterns:
        s = _subr(p, lambda x: x[1], s)
    selection.modify(s, True)


def _editorDidInit(editor: Editor):
    global _editor, _editorInjectedStyles
    _editor = weakref.ref(editor)
    _editorInjectedStyles = False


def _setEditorInjectedStyles(success: bool):
    global _editorInjectedStyles
    _editorInjectedStyles = success


def _editorDidFocusField(note: Note, currentField: int):
    global _editorInjectedStyles
    if _editorInjectedStyles:
        return

    assert _editor is not None
    editor = _editor()
    if editor is None:
        return

    enhanceAllAnkiEditables(
        editor,
        _getPitchAccentStylesheet(),
        "pitchAccentStyle",
        _setEditorInjectedStyles)


def _editorDidLoadNote(editor: Editor):
    # WARNING: doesn't ensure that `aqt.editor.Editor` is fully loaded, i.e.
    # has `.fields` container

    global _editorInjectedStyles
    if _editorInjectedStyles:
        return

    enhanceAllAnkiEditables(
        editor,
        _getPitchAccentStylesheet(),
        "pitchAccentStyle",
        _setEditorInjectedStyles)


def initHooks():
    addHook("setupEditorButtons", setupEditorButtons)

    # solution for versions prior to 23.12.1
    # (before `aqt.gui_hooks.editor_state_did_change` was added)
    gui_hooks.editor_did_init.append(_editorDidInit)
    gui_hooks.editor_did_focus_field.append(_editorDidFocusField)
    gui_hooks.editor_did_load_note.append(_editorDidLoadNote)
