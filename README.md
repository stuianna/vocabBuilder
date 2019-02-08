# vocabBuilder

A simple, annoying, program to help increase vocabulary in a foreign language. The program runs in the background, pops up after a set number of minutes and asks you a series of questions. Once all questions have been answered, the program hides in the background, ready to annoy you later.

![Screen Shot](screenshot.png "Screenshot")

# Installation

So far this has only been tested on Arch Linux using I3WM and Windows 10. Although, I can't see why it wouldn't work on other Linux / Windows distros. The program is boxed using [PyInstaller](https://www.pyinstaller.org/).

Get the binary directly with:

(Linux)
```
wget https://github.com/stuianna/vocabBuilder/releases/download/v0.1.0/vocabBuilder
```

(Windows)
```
wget https://github.com/stuianna/vocabBuilder/releases/download/v0.1.0/vocabBuilder.exe
```

Or clone this directory and run it directly with a Python interpreter (requires Python 3 and PyQt5).

# Usage

The words and translations are stored in a CSV file, like this:

```
one, eins
two, zwei
police, Polizei
three, drei
four, vier
grenadier, Grenadier
```

Assuming you're in the installed directory, the program is then started from the command line / terminal like so:

(Linux)
```
 vocabBuilder words.csv
```

(Windows)
```
 .\vocabBuilder \.words.csv
```

By default, it asks 5 questions every 10 minutes, this can be changed using the options -t and -q:
```
vocabBuilder words.csv -q 10 -t 20
```

