# The Proof is Trivial Parse

Here you can find a script to parse questions from the tsr thread [The Proof is Trivial](https://www.thestudentroom.co.uk/showthread.php?t=2313384). Also contains an example pdf with the first 500 questions.

## Requirements

Requires python3 and pandoc.

## Usage

```
$ questions2latex [name of output latex file] [question number to start at] [question number to end at]
```

### Example

```
# Will write questions 5 to 25 (inclusive) to questions.tex
$ questions2latex questions.tex 5 25
```
