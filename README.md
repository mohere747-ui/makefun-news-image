[![make.fun challenge](https://img.shields.io/badge/make.fun-news--image--20261126-7C3AED.svg)](https://make.fun/c/news-image-20261126)
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
