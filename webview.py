from typing import Optional

from aqt import gui_hooks
from aqt.browser.previewer import BrowserPreviewer
from aqt.clayout import CardLayout
from aqt.reviewer import Reviewer
from aqt.webview import WebContent

from .globals import config


def _getPitchAccentStylesheet() -> str:
    return f"""
<style type="text/css">
  pop,
  span.{config.openingPitchClassname} {{
    position: relative;
  }}
  
  pop::before,
  span.{config.openingPitchClassname}::before {{
    content: "";
    position: absolute;
    background-color: black;
    filter: invert(1);
    mix-blend-mode: difference;
    width: 0.5px;
    height: 4px;
  }}

  pop::after,
  span.{config.openingPitchClassname}::after {{
    content: "";
    position: absolute;
    background-color: black;
    filter: invert(1);
    mix-blend-mode: difference;
    transform: translate(-100%, 0);
    width: 100%;
    height: 0.5px;
  }}

  pco,
  span.{config.continuousPitchClassname} {{
    position: relative;
  }}
  
  pco::before,
  span.{config.continuousPitchClassname}::before {{
    content: "";
    position: absolute;
    background-color: black;
    filter: invert(1);
    mix-blend-mode: difference;
    width: 100%;
    height: 0.5px;
  }}

  pcl,
  span.{config.closingPitchClassname} {{
    position: relative;
  }}
  
  pcl::before, span.{config.closingPitchClassname}::before {{
    content: "";
    position: absolute;
    background-color: black;
    filter: invert(1);
    mix-blend-mode: difference;
    width: 100%;
    height: 0.5px;
  }}

  pcl::after,
  span.{config.closingPitchClassname}::after {{
    content: "";
    position: absolute;
    background-color: black;
    filter: invert(1);
    mix-blend-mode: difference;
    width: 0.5px;
    height: 4px;
  }}
</style>
    """


def _webviewWillSetContent(webcontent: WebContent, context: Optional[object]):
    if (not isinstance(context, Reviewer) and
        not isinstance(context, CardLayout) and
            not isinstance(context, BrowserPreviewer)):
        return
    webcontent.head += _getPitchAccentStylesheet()


def initHooks():
    gui_hooks.webview_will_set_content.append(_webviewWillSetContent)
