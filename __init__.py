from . import editor
from . import webview


def main():
    editor.initHooks()
    webview.initHooks()


main()
