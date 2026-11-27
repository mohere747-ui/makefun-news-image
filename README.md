[![make.fun · News Image 26 Nov 2026](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/mohere747-ui/makefun-news-image/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard)
[![reward](https://make.fun/badge/news-image-20261126/mohere747-ui/makefun-news-image/reward.svg)](https://make.fun/bounty/news-image-20261126)
[![GitHub repository](https://img.shields.io/badge/github-mohere747--ui%2Fmakefun--news--image-181717.svg?logo=github&logoColor=white)](https://github.com/mohere747-ui/makefun-news-image)

A single-file news poster for the `news-image-20261126` make.fun challenge. `render.py` paints a 1024x1024 dark-themed brief of eight world stories from 26 November 2026 into `entry.png`, and `main.ts` copies that committed PNG into the grader's output directory at run time, so the evaluated bytes are exactly the rendered poster.

## Run

Render the poster (requires Pillow and DejaVu fonts):

```sh
python3 render.py
```

Copy the poster into the output directory:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=$PWD/out node main.ts
```

The second command writes `out/entry.png`. Without `MAKEFUN_OUTPUT_DIR`, `main.ts` uses `/output`.
