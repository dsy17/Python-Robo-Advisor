import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import datetime
from sklearn.metrics import mean_squared_error
import math

# parameters
look_back = 10000  # number of days to look back in data
today = datetime.datetime.today().date()
month = today - datetime.timedelta(days=look_back)  # retrieve look_back days worth of data


# retrieves LSTM model from files, or creates new model if none exists
def create_model(x):
    try:
        training_model = load_model("data/LSTM_models/lstm_model.h5")
    except OSError:
        training_model = Sequential()
        training_model.add(LSTM(64, input_shape=(1, x)))
        training_model.add(Dense(64, activation="relu"))
        training_model.add(Dense(128, activation="relu"))
        training_model.add(Dense(1024, activation="relu"))
        training_model.add(Dense(1))

        training_model.compile(optimizer="Adam", loss='mse')

        training_model.save(f"data/LSTM_models/lstm_model.h5")

    return training_model


# gets historical data with yfinance
def get_data(sym):
    data = yf.download(tickers=sym, start=month, end=today)
    x = data.drop(['Adj Close'], axis=1).values
    y = data['Adj Close'].values

    return data, x, y


# splits and scales datasets for training and testing
def get_train_test(x, y):
    scaler = MinMaxScaler(feature_range=(0, 1))

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=False)

    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    x_train = np.reshape(x_train, (x_train.shape[0], 1, x_train.shape[1]))
    x_test = np.reshape(x_test, (x_test.shape[0], 1, x_test.shape[1]))

    return x_train, x_test, y_train, y_test, x.shape[1]


# gets rmse value of model predictions
def get_rmse(y_ts, pr):
    rmse = math.sqrt(mean_squared_error(y_ts, pr))

    return rmse


# generates accuracy graph, plots x_test against predictions
def accuracy_graph(x_train, x_test, predict, data):
    valid = data.iloc[len(x_train):, :]
    valid['Predictions'] = predict

    plt.style.use("bmh")
    plt.figure(figsize=(16, 8))
    plt.plot(valid[['Adj Close', 'Predictions']])
    plt.legend(['Adj Close', 'Predictions'])
    plt.title(f"Predictions and Actual Closing Price over the last {len(x_test)} days")
    plt.show()


# passes results of prediction to tradingStrategy.py
def pass_results(sym):
    data, x, y = get_data(sym)
    x_train, x_test, y_train, y_test, x_shape = get_train_test(x, y)
    model = create_model(x_shape)
    model.fit(x_train, y_train, batch_size=100, epochs=20)

    predict = model.predict(x_test[-1:])
    predict = predict[0].astype(float)
    current = []
    for a in range(5, 0, -1):
        y_get = y_test[-a].astype(float)
        current.append(float(y_get))

    return current, predict


if __name__ == "__main__":
    symbol = "TSLA"
    data, x, y = get_data(symbol)
    x_train, x_test, y_train, y_test, x_shape = get_train_test(x, y)
    model = create_model(x_shape)
    model.fit(x_train, y_train, batch_size=60, epochs=20)

    predict = model.predict(x_test)

    print(get_rmse(y_test, predict))
    accuracy_graph(x_train, x_test, predict, data)
