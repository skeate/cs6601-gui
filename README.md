## isolation GUI

The command line interface seemed a little clunky (no offense), so I thought I'd
try making a GUI for it. It's fairly barebones (first time using pygame), but
it's reasonably functional.

To use:

1. Install pygame (`pip install pygame` for most people)
2. Put `gui.py` in the same directory as the assignment files
3. Run `python gui.py`

This'll open a window with some instructions, which I'll repeat here for your
convenience:

> Press ESC or Ctrl+C to close this window at any time.
>
> Press 1 to start a new game as player 1 against the AI.
> Press 2 to start a new game as player 2 against the AI.
> Press 3 to start a game with two human players.
> Press 4 to watch the AI play against itself.

These controls work even in the middle of a game -- the numbers will terminate
the current game and start a new one.

After starting a game you'll see the grid. Whenever it's a human's turn, legal
moves should be highlighted green (except the first move -- the whole board
would be green).

Once a player wins, they'll get a "W" over their last move.


## Changing the AI player

This is a little clunky. You need to edit `gui.py`, specifically the `new_game`
function. The first line of that function is `AIPlayer = RandomPlayer`. Change
this to `CustomPlayer` (after you `import` it) or whatever else you want. It
should also be clear how to pit two different AIs against each other.

## Slowing down AI vs AI play

One way that works is to _lower_ the number in the line `self.clock.tick(60)`.


## To Do

- Make the method of changing AIs a little nicer
- Enforce timing constraints on AI players
- ???

PRs welcome
