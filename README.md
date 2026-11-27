# News Image — 26 November 2026

An editorial poster summarising six front-page stories of the day in a dark-navy, six-card layout. `render.py` draws the whole picture from scratch with Python and Pillow (no image assets); `main.ts` copies the finished PNG into the bounty's output directory.

![make.fun bounty](https://make.fun/badge/news-image-20261126.svg)
![make.fun rank](https://make.fun/badge/news-image-20261126/mohere747-ui/makefun-news-image/rank.svg)
![make.fun reward](https://make.fun/badge/news-image-20261126/mohere747-ui/makefun-news-image/reward.svg)

Bounty: https://make.fun/bounty/news-image-20261126

## Run

Render the poster (writes `entry.png`, 1024x1024):

```sh
python3 render.py
```

Copy the poster to the grader output directory:

```sh
npx tsx main.ts
```

`bun main.ts` works too. Set `MAKEFUN_OUTPUT_DIR` to override the default `/output`.
