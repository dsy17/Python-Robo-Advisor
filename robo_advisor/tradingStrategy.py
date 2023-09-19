import sentimentAnalysis
import historicalData

# parameters
threshold = 5
upper_sentiment = 0.3
lower_sentiment = 0.1


# main trading strategy function - determines whether a trade should be opened or not based on results from
# sentimentAnalysis and historicalData
def check_params(sym):
    long = False
    trade = False
    is_sentiment = sentimentAnalysis.read_sentiment(sym)
    if is_sentiment == 0:
        sentiment = float(sentimentAnalysis.pass_to_ts(sym))
    else:
        sentiment = float(is_sentiment[1])

    current, predict = historicalData.pass_results(sym)
    percentage = ((current[0] - current[-1]) / current[0]) * 100

    confidence = (percentage * 0.5) + (sentiment * 0.5)
    print(confidence)
    if confidence > 1:
        confidence = 1
    elif confidence < -1:
        confidence = -1

    if (percentage >= threshold) and (predict > current[-1]):
        long = True
        if upper_sentiment <= sentiment <= 1:
            trade = True
            return trade, long, confidence
    elif (abs(percentage) >= threshold) and (predict < current[-1]):
        if -1 <= sentiment <= lower_sentiment:
            trade = True
            return trade, long, confidence

    print(f"Predicted next day closing price: ${predict[0]}\nPercentage increase/decrease for {sym} over 5 days: "
          f"{percentage}%\nSentiment analysis for {sym}: {sentiment}")

    return trade, long, confidence
