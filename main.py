import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def has_aria_label_and_href(tag):
    return tag.has_attr("aria-label") and tag.has_attr("href")


def main():
    url = "https://news.google.com"
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, "html.parser")

    all_articles = []
    for link in soup.find_all(has_aria_label_and_href):
        title = link.get("aria-label")
        tmp = title.split(" - ", 4)  # TO-DO right split and max split
        if len(tmp) == 4:
            name, publishers, time, authors = tmp[0], tmp[1], tmp[2], tmp[3]
            article_link = link.get("href")
            article_link = urljoin(
                url, article_link
            )  # Convert relative URLs to absolute URLs
            article = {
                "name": name,
                "publishers": publishers,
                "time": time,
                "authors": authors,
                "link": article_link,
            }
            all_articles.append(article)
    with open("articles.json", "w") as fp:
        json.dump(all_articles, fp, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
