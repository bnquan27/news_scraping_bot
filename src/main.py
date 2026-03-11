from google.genai import types
import os
from dotenv import load_dotenv
from google import genai
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests_html import HTMLSession

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
result_schema = {
    "name": "string",
    "publishers": "string",
    "time": "string",
    "authors": "string",
    "tags": "array",
}


def has_aria_label_and_href(tag):
    return tag.has_attr("aria-label") and tag.has_attr("href")


def main():
    url = "https://news.google.com"
    session = HTMLSession()
    reqs = session.get(url)
    reqs.html.render(sleep=2)
    soup = BeautifulSoup(reqs.html.html, "html.parser")
    session.close()

    all_articles = []
    for link in soup.find_all(has_aria_label_and_href):
        title = link.get("aria-label")
        tmp = title.split(" - ", 4)
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
    with open("articles.json", "r") as fp:
        json_cont = fp.read()
    prompt = (
        "Set tag for my news info json file from their title and context. Don't change any existing info. Remember to add indent in the output at each key = tag"
        + "Here are the json file content: "
        + json_cont
    )
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_json_schema=result_schema, response_mime_type="application/json"
        ),
    )
    json_output = response.text
    with open("articles.json", "w") as fp:
        fp.write(json_output)


if __name__ == "__main__":
    main()
