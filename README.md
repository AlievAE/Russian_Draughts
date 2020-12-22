# Russian Draughts
This repository contains checker visualization python library: 
## Quick Start Ubuntu 
      Install following tools, if you don't have them already: 
      $ sudo pip install numpy 
      $ sudo pip install pygame 
## Game start 
      $ python<your version> gui.py 
## Game process 
      Use your mouse or touchpad to make moves 
      Rightclick square to change its status (empty -> W soldier -> W king -> B soldier -> B king)
      CTRL+S to save current position 
      CTRL+D to load last saved game 
      CTRL+R to set a clear board 
      CTRL+X to change move order 
      SPACE for AI to make single move 
      CTRL+T for AI to play against itself and time it's performance 
## AI 
      AI uses an alpha-beta pruning algorithm to optimize move selection pattern. 
      Timed performance can be found in moveTime.txt
