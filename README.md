[![make.fun](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/0xyfann/makefun-tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/0xyfann/makefun-tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

# tiny-chess-01 engine

A deterministic Python 3 chess engine using 0x88 legal move generation, iterative alpha-beta negamax, capture quiescence, material and compact positional evaluation. Search uses a 12,000-node budget, a transposition table with bound-aware cutoffs and move ordering, and a penalty for returning to observed game positions. Castling, en passant, all promotion choices, and a bishop pair bonus are supported. Killer moves were removed to meet the byte limit. It communicates only with `MAKEFUN_ENV_URL` and uses no model calls or wall-clock search.

Run with the competition environment:

    MAKEFUN_ENV_URL=http://... python3 main.py

`main.py` is self-contained and remains below the 4 KiB engine limit. Local grading requires Docker because the kit runs Python 3.13 inside the bot container.

Local verification of this revision:

| Position | Depth | Nodes | Expected |
| --- | ---: | ---: | ---: |
| Start position | 3 | 8,902 | 8,902 |
| Kiwipete | 2 | 2,039 | 2,039 |
| En passant perft position | 3 | 2,812 | 2,812 |
| Kings and rooks with KQkq rights | 1 | 26 | 26 |

Kiwipete has 48 legal moves including `e1g1` and `e1c1`. Both black castling moves were also checked. In the explicit en passant fixture, `e5d6` is legal and removes the black pawn on d5. Every perft edge checks that undo restores the board, castling rights, and en passant target.

An HTTP mock using `/game` and `/move` ran the actual process for 12 legal plies without a crash (exit 0). Times including HTTP overhead: mean 0.643 s, range 0.497–0.765 s. Moves: `b1c3 b8c6 e2e4 e7e5 f1d3 f8d6 g1f3 g8e7 a2a4 a7a5 g2g4 h7h5`. Mock legality uses this engine's generator, as allowed by the brief. These are local runtime measurements, not container grading results.

Additional checks cover quiescence stand-pat, TT lower bounds versus fresh full-window search, exact TT hits, distinct keys for castling/en passant state, and the repetition penalty. Temporary test scripts and results live outside the entry snapshot in `/tmp`.

Bounty: https://make.fun/bounty/tiny-chess-01

Referral: https://make.fun/r/p1x954ca
