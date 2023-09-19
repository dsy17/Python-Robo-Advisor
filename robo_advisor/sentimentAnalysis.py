from pytz import timezone
from textblob import TextBlob
import newsScraper
import datetime

tz = timezone('US/Eastern')


# returns polarity of given articles
def sentiment_analysis(articles):
    result = []
    for a in articles:
        article_sentiment = TextBlob(a)
        article_polarity = article_sentiment.sentiment.polarity
        article_subjectivity = article_sentiment.sentiment.subjectivity

        overall_polarity = article_polarity * article_subjectivity

        result.append(overall_polarity)

    return result


# returns sentiment average from all given polarities
def sentiment_avg(sent):
    return sum(sent) / len(sent)


# prints polarity
def sentiment_analysis_print(result):
    for a in result:
        if a > 0:
            print("Positive: " + str(a))
        else:
            print("Negative: " + str(a))


# determines ratio of positive to negative polarity values
def sentiment_ratio(result):
    pos_ratio, neg_ratio = 0, 0
    for a in result:
        if a > 0 or a == "Positive":
            pos_ratio += 1
        else:
            neg_ratio += 1

    return [pos_ratio, neg_ratio]


# pass results to tradingStrategy.py
def pass_to_ts(sym):
    get_keyword = read_keywords(sym)
    get_articles = newsScraper.pass_to_sentiment(get_keyword)
    sent_analysis = sentiment_analysis(get_articles)
    avg_sentiment = sentiment_avg(sent_analysis)
    write_to_file(avg_sentiment, sym)

    return avg_sentiment


# reads sentiment file, checks if updates are required
def read_sentiment(sym):
    sentiment_file = open(f"data/sentiment/sentiment_data_{sym}.txt", "r")
    date = str(datetime.datetime.now(tz).date())

    read_file = sentiment_file.read().splitlines()

    if (len(read_file) == 0) or (read_file[0] != date):
        sentiment_file.close()
        return 0

    sentiment_file.close()
    return read_file


# writes updated sentiment values to file
def write_to_file(sentiment, sym):
    sentiment_file = open(f"data/sentiment/sentiment_data_{sym}.txt", "w")
    date = str(datetime.datetime.now(tz).date())

    new_data = [date, sentiment, sym]

    for a in new_data:
        sentiment_file.write(str(a) + "\n")

    sentiment_file.close()


# reads keywords from preset keywords file
def read_keywords(sym):
    keywords = open(f"data/sentiment/keywords.txt", "r")

    get_keywords = keywords.read().splitlines()
    for word in get_keywords:
        w = word.split(", ")
        if sym == w[0]:
            return w[1]


if __name__ == "__main__":
    symbol = "NDAQ"
    keyword = read_keywords(symbol)

    sent_update = read_sentiment(symbol)
    if sent_update == 0:
        getArticles = newsScraper.pass_to_sentiment(keyword)
        s = sentiment_analysis(getArticles)
        s_avg = sentiment_avg(s)
        write_to_file(s_avg, symbol)
    else:
        s_avg = sent_update[1]

    print(f"Sentiment analysis average: {s_avg}")
