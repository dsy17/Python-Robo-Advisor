import datetime
from newsapi import NewsApiClient
from newspaper import Article, ArticleException

api_key = "d7fdd614973a4651b2a941fb5ecbcf20"
newsapi = NewsApiClient(api_key=api_key)

max_articles = 100

# get local time for today and the week before (to scrape articles from the past week to now)
today = datetime.datetime.today().date()
week = (today - datetime.timedelta(days=2))


# downloads and summarises articles from list of given URLs
def read_article(articles):
    print("Processing articles...")
    article_summary = []
    if len(articles) > max_articles:
        articles = articles[:max_articles]
    for a in articles:
        try:
            article = Article(a)
            article.download()
            article.parse()
            article.nlp()
            article_summary.append(article.summary)
        except ArticleException:
            print("Could not download article")

    return article_summary


# scrape articles to retrieve URL
def scrape(get_keywords, get_week, get_today):
    articles = []
    for words in get_keywords:
        scrape_articles = newsapi.get_everything(q=words,
                                                 from_param=get_week,
                                                 to=get_today,
                                                 language='en',
                                                 sort_by='relevancy',
                                                 page=2)

        for a in scrape_articles["articles"]:
            articles.append(a["url"])

    # print(articles)
    return articles


# pass results to sentimentAnalysis.py
def pass_to_sentiment(sym):
    read_articles = scrape([sym], week, today)
    summary = read_article(read_articles)

    return summary
