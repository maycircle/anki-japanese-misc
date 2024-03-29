# anki-japanese-misc
> *Developed under Anki version 2.1.66 (Aug 20, 2023)*

Features
1. [Pitch accents](#pitch-accents)

---

## Pitch Accents
Text can be formatted using special buttons in "Add" and "Browse" windows, similar
to notation from [Kanshudo](https://www.kanshudo.com),
「NHK日本語発音アクセント新辞典」 [(Amazon link)](https://www.amazon.co.jp/NHK日本語発音アクセント新辞典/dp/4140113456/)　or
「新明解日本語アクセント辞典 第２版」 [(Amazon link)](https://www.amazon.co.jp/NHK日本語発音アクセント新辞典/dp/4140113456/),
in a way like this:

![using kana じかん、てんき、ひとり、あいて or with furigana 時間、天気、一人、相手（相手）.](extra/pitch_accents_preview.png)
<!-- - using kana じ<span class="p1">かん</span>、<span class="p3">て</span>んき、ひ<span class="p2">と</span>り、あ<span class="p3">いて</span> or with furigana <ruby>時 <rp>(</rp><rt>じ</rt><rp>)</rp> 間<rp>(</rp><rt><span class="p1">かん</span></rt><rp>)</rp></ruby>、<ruby>天 <rp>(</rp><rt><span class="p3">て</span>ん</rt><rp>)</rp> 気<rp>(</rp><rt>き</rt><rp>)</rp></ruby>、<ruby>一人 <rp>(</rp><rt>ひ<span class="p2">と</span>り</rt><rp>)</rp></ruby>、<ruby>相 <rp>(</rp><rt>あ<span class="p2">い</span></rt><rp>)</rp> 手<rp>(</rp><rt><span class="p3">て</span></rt><rp>)</rp></ruby>（<ruby>相手 <rp>(</rp><rt>あ<span class="p3">いて</span></rt><rp>)</rp></ruby>）.
-->
| Config property | Default value | Meaning |
| --- | --- | --- |
| `openingPitchClassname` | `p1` | "Add opening pitch" button will insert `<span class="p1"></span>` |
| `continuousPitchClassname` | `p2` | "Add continuous pitch" button will insert `<span class="p2"></span>` |
| `closingPitchClassname` | `p3` | "Add closing pitch" button will insert `span class="p3"></span>` |
| `useSpansOverTags` | `false` | Described buttons will insert `span` instead of default `pop`, `pco`, `pcl` |

You can override styles for each of three pitch accent buttons. Table below
shows the code of original styles that are used in the addon.

<table>
  <thead>
    <tr>
      <th>Opening pitch accent</th>
      <th>Continuous pitch accent</th>
      <th>Closing pitch accent</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top">
        <pre align="left">
pop,
span.p1 {
  position: relative;
}<br>
pop::before,
span.p1::before {
  content: "";
  position: absolute;
  background-color: black;
  filter: invert(1);
  mix-blend-mode: difference;
  width: 0.5px;
  height: 4px;
}<br>
pop::after,
span.p1::after {
  content: "";
  position: absolute;
  background-color: black;
  filter: invert(1);
  mix-blend-mode: difference;
  transform: translate(-100%, 0);
  width: 100%;
  height: 0.5px;
}
</pre>
      </td>
      <td valign="top">
        <pre align="left">
pco,
span.p2 {
  position: relative;
}<br>
pco::before,
span.p2::before {
  content: "";
  position: absolute;
  background-color: black;
  filter: invert(1);
  mix-blend-mode: difference;
  width: 100%;
  height: 0.5px;
}
</pre>
      </td>
      <td valign="top">
        <pre align="left">
pcl,
span.p3 {
  position: relative;
}<br>
pcl::before,
span.p3::before {
  content: "";
  position: absolute;
  background-color: black;
  filter: invert(1);
  mix-blend-mode: difference;
  width: 100%;
  height: 0.5px;
}<br>
pcl::after,
span.p3::after {
  content: "";
  position: absolute;
  background-color: black;
  filter: invert(1);
  mix-blend-mode: difference;
  width: 0.5px;
  height: 4px;
}
</pre>
      </td>
    </tr>
  </tbody>
</table>
