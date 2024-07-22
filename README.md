# CS50 Finance Stocks


## Overview
This repository contains my solution to the Harvard CS50 Finance project. This project is part of the CS50x course, where I built a web application using Flask that allows users to manage their stock portfolio.


## Note
The project skeleton, including `layout.html` and `helpers.py`, was provided by the CS50x course. I have implemented the features and functionality of my version of the web application. Stock data is retrieved using the IEX Cloud API.


## Project Structure
The project consists of the following main files and directories:
- `application.py`: The main application file that contains all the routes and logic for handling user requests.
- `helpers.py`: Contains helper functions used throughout the application.
- `templates/`: Directory containing all the HTML templates used to render the web pages.
- `static/`: Directory containing static files such as CSS and JavaScript.


## Code Explanation

1. **application.py**
This file contains the main logic for the application, including:
- User Authentication: Routes for registering, logging in, and logging out users.
- Stock Operations: Routes for quoting, buying, and selling stocks.
- Portfolio Management: Routes for viewing the current portfolio, transaction history, and watchlist.

2. **helpers.py**
This file includes helper functions such as:
- lookup(): Looks up current stock prices using the API.
- usd(): Formats numbers as USD currency.

3. **templates/**
This directory contains HTML templates for the different pages of the application:

4. **static**
- layout.html: Base template used by other templates.
- register.html: Template for the registration page.
- login.html: Template for the login page.
- quote.html: Template for the stock quote page.
- buy.html: Template for the stock buy page.
- sell.html: Template for the stock sell page.
- index.html: Template for the portfolio overview page.
- history.html: Template for the transaction history page.
- watchlist.html: Template for watchlist page.
  
5. **static/**
This directory contains static files such as:
- styles.css: Custom CSS for styling the web application.

  
## Features
- **User Registration**: Users can register for an account.
- **User Authentication**: Users can log in and log out securely.
- **Stock Quoting**: Users can look up current stock prices.
- **Buying Stocks**: Users can buy stocks, and the purchase will be recorded in their portfolio.
- **Selling Stocks**: Users can sell stocks they own.
- **Transaction History**: Users can view their transaction history.
- **Portfolio Overview**: Users can view their current portfolio, including the stocks they own, the number of shares, the current price, and the total value.
- **Watchlist**: Users can keep track of and monitor stocks they wish to purchase.


## Installation
To run this project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/cs50-finance.git
   cd cs50-finance
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
3. Set up the environment variables:
   ```bash
    export FLASK_APP=application.py
  (This command sets the FLASK_APP environment variable to application.py, indicating to Flask that this is the main file to run.)
    
    ```bash
    export FLASK_ENV=development 
    
  (This command sets the FLASK_ENV environment variable to development, enabling development mode, which provides helpful error messages and other development features.)

    ```bash
    export API_KEY=your_api_key_here 
  (This command sets the API_KEY environment variable to your IEX Cloud API key. This key is required for the application to fetch real-time stock data from the IEX Cloud API. Make sure to replace your_api_key_here with your actual IEX Cloud API key.)
4. Run the application
  ```bash
  flask run





