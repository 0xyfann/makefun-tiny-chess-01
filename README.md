[![make.fun](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/0xyfann/makefun-tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/0xyfann/makefun-tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

# tiny-chess-01 engine

`main.py` is the whole engine, in ordinary Python 3 source. It uses only the standard library and communicates with the game environment using JSON over `urllib.request`.

    MAKEFUN_ENV_URL=http://... python3 -P -s main.py

## Engine

Iterative alpha-beta negamax uses a 150,000-node budget per move with principal-variation search, null-move pruning and late-move reductions. The last completed iteration supplies the move. Captures and promotions come first (MVV-LVA), then the transposition-table move. Bounded quiescence searches captures, quiet promotions and all check evasions. Search is deterministic and clock-free.

The board uses an immutable 10×12 mailbox. Castling rights and the en passant target follow the squares. `moves` yields `(x, y, promo)`, where `x` and `y` are the origin and destination squares. `push` creates the new position, and `checked` filters moves that expose the moving side's king. White is side 0 and Black is side 1. `caps` enables tactical generation, `tt` remembers ordering moves by position and side, and `PST` holds precomputed piece-square scores.

Evaluation keeps material, the bishop pair, knight and bishop centralization, pawn advancement and its endgame bonus, endgame king centralization, and rook activity on the seventh rank; it penalizes an advanced king. The 4,096-byte budget excludes open and semi-open rook files, pawn-file bonuses, castled-king preference, transposition scores and bounds, and in-search repetition scoring. The game environment handles draws. The engine has no mobility or passed-pawn detection.

## Local verification

Python 3.12.3 and independent move validation with python-chess 1.11.2.

| Perft position | Depth | Nodes |
| --- | ---: | ---: |
| Start | 3 | 8,902 |
| Kiwipete | 2 | 2,039 |
| En passant test position | 3 | 2,812 |
| Kings and rooks with KQkq rights | 1 | 26 |

All six perft fixtures and 1,500 randomized python-chess differential positions passed. The HTTP mock accepted 12 legal moves with no errors; the engine exited with code 0 and averaged 3.50 seconds per move, with a maximum of 4.37 seconds.

Against `dbf5bc7`, it drew both games by threefold repetition (one as White, one as Black): 100 and 55 plies. The match score was 1–1, with no losses. Official practice Elo is unverified.

Bounty: https://make.fun/bounty/tiny-chess-01

Referral: https://make.fun/r/p1x954ca
