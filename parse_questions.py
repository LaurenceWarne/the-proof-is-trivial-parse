#!/usr/bin/env python3

import sys
import re
import urllib.parse as urlparse

import requests
from lxml import html, etree


def get_links(page="https://www.thestudentroom.co.uk/showthread.php?t=2313384"):
    content = requests.get(page).content
    tree = html.fromstring(content)
    links = []
    for link_tag in tree.xpath("//a"):
        if (link_tag.text is not None and "problem" in link_tag.text.lower()):
            links.append(link_tag.attrib["href"])
    return links


def get_posts(start=2, up_to=10):
    page = 1
    current_problem = start
    timeout = 0
    while current_problem <= up_to:
        url = "https://www.thestudentroom.co.uk/showthread.php?t=2313384&page={p}".format(p=page)
        content = requests.get(url).content
        tree = html.fromstring(content)
        found_post, *page_posts = tree.xpath(".//div[contains(@class,'post ')]") + tree.xpath(".//div[contains(@class, 'lastPost ')]")
        # Skip OP
        if (page == 1):
            _, _, found_post, *page_posts = page_posts
        while page_posts:
            problem_in_post = "problem {n}".format(n=current_problem) in \
                str(html.tostring(found_post)).lower()
            # internet hates me
            problem_in_post = problem_in_post or re.search(
                "problem " + "[^<]*?".join(str(current_problem)) + "<",
                str(html.tostring(found_post)).lower()
            )
            if (problem_in_post):
                yield found_post  # We'll filter out dups later
                current_problem += 1
                timeout = 0
                break
            else:
                found_post, *page_posts = page_posts
        else:
            #print("Jumping to page:" + str(page))
            page += 1
            timeout += 1
            if (timeout == 5 and current_problem != start):
                current_problem += 1
                page -= timeout
                timeout = 0


def get_post_content_from_url(post_url):
    content = requests.get(post_url).content
    tree = html.fromstring(content)
    parsed_link = urlparse.urlparse(post_url)
    # Post ids appear to be of the form 'post<post-number>'
    post_id = "post" + urlparse.parse_qs(parsed_link.query)['p'][0]
    # The following functions return lists, but we only want the first element
    post, *_ = tree.xpath("//div[@id='{post_id}']".format(post_id=post_id))
    return get_post_content(post)


def get_post_content(post):
    author = [a for a in post.xpath(".//a") if is_user_link(a)][0].text
    post_content, *_ = post.xpath(".//div[@class='post-content']")
    signature = etree.Element("i")
    signature.text = "Posted by " + author
    post_content.append(signature)
    return post_content


def is_user_link(link):
    has_attr = "class" in link.attrib
    return has_attr and "username" in link.attrib["class"]


def process_post_latex(post):
    # Remove latex images
    latex_links = post.findall(".//a")
    for link in latex_links:
        if (link.attrib["href"] == "javascript:void(0)"):
            # Get latex code from alt attribute
            latex = link.findall(".//img")[0].attrib["alt"]
            # We'll come back to this hack later
            latex_wrapper_tag = etree.Element("pre")
            latex_wrapper_tag.text = latex
            is_inline = len(latex) < 24
            if (is_inline):
                latex_wrapper_tag.text = "INLINE" + latex + "INLINE"
            latex_wrapper_tag.tail = link.tail
            link.getparent().replace(link, latex_wrapper_tag)
    return post


def trim_post_content(post):
    # Remove quotes
    for element in post.findall(".//div[@class='quote_block_container']"):
        element.getparent().remove(element)
    # Remove images which will mess up the pdf
    for image in post.findall(".//img"):
        image.getparent().remove(image)
    return post


def write_elements(_file, *elements):
    root = etree.Element("html")
    root.append(get_document_intro())
    for element in elements:
        root.append(element)
    tree = etree.ElementTree(root)
    tree.write(_file)


def get_document_intro():
    intro_div = etree.Element("div")
    title = etree.Element("h1")
    title.text = "The Proof is Trivial!"
    intro_text = etree.Element("p")
    intro_text.text="Problems collected from the tsr thread: https://www.thestudentroom.co.uk/showthread.php?t=2313384 Key:"
    key = etree.Element("ol")
    key_p1 = etree.Element("li")
    key_p1.text = " * = requires only A-level knowledge"
    key_p2 = etree.Element("li")
    key_p2.text = " ** = may require a little extra (induction, L'hôpital's etc.)"
    key_p3 = etree.Element("li")
    key_p3.text = "*** = requires undergraduate knowledge."
    key.extend([key_p1, key_p2, key_p3])
    intro_div.extend([title, intro_text, key])
    return intro_div


def main2():
    links = get_links()
    start, end = int(sys.argv[2]), int(sys.argv[3])
    links_range = links[start - 1:end]
    posts = []
    for index, link in enumerate(
            sorted(set(links_range), key=links_range.index
            ), start):
        print("Fetching question: " + str(index))
        post = process_post_latex(get_post_content_from_url(link))
        post = trim_post_content(post)
        posts.append(post)
    print(
        "Done, skipped " + str(len(links_range) - len(set(links_range))) +
        " questions in same post."
    )
    write_elements(sys.argv[1], *posts)


def main():
    start, end = int(sys.argv[2]), int(sys.argv[3])
    start = 2 if start == 1 else start
    posts = []
    for index, post in enumerate(get_posts(start, end), start):
        post = process_post_latex(get_post_content(post))
        post = trim_post_content(post)
        if (html.tostring(post) not in map(html.tostring, posts)):
            print("Found Problem: " + str(index))
            posts.append(post)
    print("Writing problems to html...")
    write_elements(sys.argv[1], *posts)


if __name__ == "__main__":
    main()
