# make.fun — news-image (26 November 2026)

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/mohere747-ui/makefun-news-image/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard)
[![reward](https://make.fun/badge/news-image-20261126/mohere747-ui/makefun-news-image/reward.svg)](https://make.fun/bounty/news-image-20261126)

A broadsheet-style world news poster summarising 38 stories from 26 November 2026.
The 1600×1200 image is drawn entirely with Python and Pillow: masthead, deck,
metric strip, region band with a UTC timeline, three illustrated hero cards,
eight smaller illustrated cards, a world map with numbered pins, and a
three-column story index. Headlines are auto-fitted so nothing clips, and the
script verifies that no text is clipped or overlapping before saving `entry.png`.

Contested claims are attributed (`Iran claims`, `Ukraine said`, `officials say`)
and speculation is not presented as fact.

## Requirements

- Python 3
- Pillow (`pip install Pillow`)
- DejaVu fonts (bundled with most Linux distributions)

## Run

```sh
cd ~/workspace/makefun/news-image
python3 render.py
```

This writes `entry.png` in the same directory and prints the image size, byte
count and verification result.
