from .hooks import editor
from .hooks import webview


def main():
    editor.initHooks()
    webview.initHooks()


main()
