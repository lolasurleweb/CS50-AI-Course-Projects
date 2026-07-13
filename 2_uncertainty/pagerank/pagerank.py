import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transition_probs = {}

    if corpus[page]:
        # assigning baseline random-jump probability to every page
        for corp in corpus:
            transition_probs[corp] = (1 - damping_factor) / len(corpus)

        # adding link-following probability to each linked page
        for link in corpus[page]:
            transition_probs[link] += damping_factor / len(corpus[page])

    else:
        # page has no outgoing links, so assing equal probability to all pages
        for corp in corpus:
            transition_probs[corp] = 1 / len(corpus)

    return transition_probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # keeps track of how many times you visited each page
    counts = {
        page: 0
        for page in corpus
    }

    # first sample is randomly chosen
    current_page = random.choice(list(corpus.keys()))

    for _ in range(n):
        counts[current_page] += 1

        # choose next sample randomly based on the transition model of given page
        transition_probs = transition_model(corpus, current_page, damping_factor)

        current_page = random.choices(
            population=list(transition_probs.keys()),
            weights=list(transition_probs.values()),
            k=1
        )[0]   # always returns a list, so need to extract the element (["html.1"] -> "html.1")

    pagerank = {
        page: count / n
        for page, count in counts.items()
    }

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # initialize pagerank values to equal probability for each page
    pagerank = {
        page: 1 / len(corpus)
        for page in corpus
    }

    while True:
        new_pagerank = {}

        for target_page in corpus:  # this is the page we want to calculate the pagerank for
            pr = 0
            for source_page in corpus:  # iterate over every page in the dictionary
                links = corpus[source_page]

                if links:
                    if target_page in links:  # check whether it links to our target page 
                        # probability that we were on page source and chose the link to page target
                        pr += pagerank[source_page] / len(links)   
                else:
                    # if page has no links, link to every page
                    pr += pagerank[source_page] / len(corpus)

            new_pagerank[target_page] = ((1 - damping_factor) / len(corpus)
                                         + damping_factor * pr)  # formula specified in task

        # check whether every page changed by at most 0.001
        converged = all(
            abs(new_pagerank[page] - pagerank[page]) <= 0.001
            for page in corpus
        )

        pagerank = new_pagerank

        if converged:
            break

    return pagerank


if __name__ == "__main__":
    main()
