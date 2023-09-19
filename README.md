# Python Robo-Advisor for Stock Market Prediction

### About this project:
The goal of this project was to build a robust robo-advisor that reacts accordingly to the volatile nature of stock markets to successfully generate profit. It does this by compiling data from multiple sources to produce an informed decision on what stocks to trade with, when to trade them and how long for. The user may decide on the assets they wish to trade with, their budget and their stop loss. The robo-advisor is designed to automatically handle the opening/closing and monitoring of trades when the user activates it.

## APIs/Resources:
- TensorFlow (https://github.com/tensorflow/tensorflow)
- scikit-learn
- Alpaca Trading API
- NewsAPI
- SQLite
- YFinance (created by Ran Aroussi https://github.com/ranaroussi/yfinance)

## User Interface:

The user input system is a core part of this application as it enables users to remain in control of their trades and finances, rather than granting complete control to the robo-advisor. The user can register their own account where they can connect to Alpaca with their personal API keys and tailor their experience.

  <img height="400" alt="Screenshot 2023-04-28 at 06 28 24" src="https://github.com/dsy17/Python-Robo-Advisor/assets/127321145/45fbc1ea-96e3-4f9c-ab2a-8bf2982f4b1f">
  <img height="400" alt="Screenshot 2023-04-20 at 20 54 28" src="https://github.com/dsy17/Python-Robo-Advisor/assets/127321145/8637a844-f978-494d-9c4a-bf505d9ce7d7">
<p/>

## Database features:
I enhanced the user interface feature with a local database that holds all user data, including API keys for connecting the user to Alpaca API, and their variable configurations that can be changed at any time with the GUIs shown previously. This feature allows multiple users to use this robo-advisor. The database is operated by SQLite3, a library included in Python’s standard libraries.

## Usage of LSTM:

To predict future stock prices for informed trading, I used the LSTM (short for Long Short Term Memory) neural network feature provided by the TensorFlow Keras API. The reason why I chose to use an LSTM model for this project is because of how well it handles large datasets. Since a company could have historical financial data that contains decades worth of information, I needed a model that could process a dataset of this size.

### Performance:
The lowest root-mean-square error (RMSE) recorded was 9.8729.
<p align="center">
<img width="700" alt="LSTM_accuracygraph" src="https://github.com/dsy17/python-robo-advisor/assets/127321145/ebb3f1f5-1e91-435d-80a4-48e2704d8f4c">
<p/>

## Application Structure:
The structure and relationships between every component of the robo-advisor.
<p align="center">
<img width="700" alt="LSTM_accuracygraph" src="https://github.com/dsy17/python-robo-advisor/assets/127321145/dfcf4530-a8ab-4772-acd8-8d4ac6d190ad">
<p/>

Trading Strategy System:

Receives and processes input from social media sources and gathers historical stock data, analyses the input for overall sentiment and stock price forecasting (respectively) and passes to Trading Strategy to determine whether opening a trade (either long or short) will be likely to yield profit or not. If the decision to open a trade has been approved, it sends the information trade type and overall confidence of decision to Main.

User Interface System:

Handles login and input from the user. When the user opens the application, they will first interact with the Login module. If user has an existing login, they will be granted access to User Input with a successful login attempt. If they do not have an existing login, they can register for a new account. Their information is stored in a local database, and their passwords will be encrypted to protect them if unauthorised access to the database’s contents occur. When users want to change information such as what assets to watch, their maximum budget and stop loss percentage, they will do so in User Input and their changes will be saved to the database.

Main Module System:

This is where the connection with Alpaca will be established and the results from User Input system and the Trading Strategy system will be collected to open/close trades.
