#!/usr/bin/env python3
import sys
import re


def remove_preformat(text):
    text = text.replace("\\begin{verbatim}\nINLINE", r"\(")
    text = text.replace("INLINE\n\\end{verbatim}", r"\)")
    text = re.sub("(\n)+\\\\\(", r" \(", text)
    text = re.sub("\\\\\)(\n)+", r"\) ", text)

    text = text.replace(r"\begin{verbatim}", r"\[")
    text = text.replace(r"\end{verbatim}", r"\]")
    return text


def add_linebreaks(text):
    text = re.sub(
        r"(\\textbf{[^{]*?Problem.*?})", r"\subsection{\g<1>}",
        text, flags=re.IGNORECASE | re.DOTALL
    )
    text = re.sub(
        r"Posted", r"\\newline Posted",
        text, flags=re.IGNORECASE
    )
    return text


def correct_bad_text(text):
    text = re.sub(r"&lt;", r"<", text)
    text = re.sub(r"&gt;", r">", text)
    text = text.replace(r"\\[2\baselineskip]", r"")
    return text


def remove_extraneous_text(text):
    # Remove extra text from first post
    text = re.sub(
        r"(\\end{enumerate})([^{}]+?)((\\subsection{\\textbf{)?Problem [0-9]+)",
        sub_call_back, text, flags=re.DOTALL | re.IGNORECASE
    )
    # General case
    text = re.sub(
        r"(\\emph{.*?Posted by.*?})(.+?)((\\subsection{\\textbf{)?Problem [0-9]+)",
        sub_call_back, text, flags=re.DOTALL | re.IGNORECASE
    )
    return text


def sub_call_back(match):
    problem_text = match.group(2)
    if (is_parenthicalley_closed(problem_text)):
        return match.group(1) + match.group(3)
    else:
        return match.group(1) + problem_text + match.group(3)


def is_parenthicalley_closed(string, open_char="{", close_char="}"):
    count = 0
    for char in string:
        if (char == open_char):
            count += 1
        elif (char == close_char):
            count -= 1
        if (count < 0):  # Can't close bracket not opened
            return False
    return count == 0


def main():
    with open(sys.argv[1], "r+") as f:
        text = f.read()
        text = remove_preformat(text)
        text = correct_bad_text(text)
        text = add_linebreaks(text)
        text = remove_extraneous_text(text)
    with open(sys.argv[1], "w") as f:
        f.write(text)


if __name__ == "__main__":
    main()
