[![make.fun](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/0xyfann/makefun-tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/0xyfann/makefun-tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

# tiny-chess-01 engine

`main.py` is the whole engine, in ordinary Python 3 source. It uses only the standard library and communicates with the game environment using JSON over `urllib.request`.

    MAKEFUN_ENV_URL=http://... python3 -P -s main.py

## Engine

Iterative-deepening alpha-beta with guarded null-move pruning uses a 90,000-node budget per move. It plays the best move from the last completed depth. A remembered move leads the ordering, followed by captures and promotions ranked by piece value. Bounded quiescence searches captures, quiet promotions and check evasions. Move selection is deterministic and clock-free. A branch that returns to the root position with the same side to move is scored as a draw.

The immutable 10×12 mailbox stores castling rights and the en passant target after the board squares. The move generator yields candidate moves, and king attack detection filters out illegal moves. Round 4 fixes a transposition-table bug: lookup, storage and root selection now use `(board, side_to_move)`, preventing a repeated board from supplying the opponent's move.

Evaluation scores material and piece-square placement. While queens remain, it rewards a pawn shield and penalizes a back-rank king whose three shield pawns block its escape when an enemy rook reaches the seventh rank. In queenless positions it rewards king centralization. A cached pawn-structure term rewards passed pawns quadratically as they advance. Passed pawns have no enemy pawn ahead on their file or either neighboring file.

## Local verification

Python 3.12.3. All six CPW perft fixtures passed; `play()` also returned a legal move in each of the eight round-4 regression positions, including both previously failing endgames.

| Perft position | Depth | Nodes |
| --- | ---: | ---: |
| Start | 3 | 8,902 |
| Kiwipete | 2 | 2,039 |
| En passant | 3 | 2,812 |
| Kings and rooks | 1 | 26 |
| Promotion and castling | 3 | 9,467 |
| Black castling | 3 | 62,379 |

The HTTP mock accepted 12/12 legal moves, averaging 2.18 seconds with a 3.62-second maximum (turn delivery to move receipt). The eight regression move sets matched the round-3 generator. Official practice Elo is unverified.

Bounty: https://make.fun/bounty/tiny-chess-01

Referral: https://make.fun/r/p1x954ca
