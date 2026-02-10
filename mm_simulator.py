# defining basic parameters
T = 10000               # number of time steps
true_vol = 0.2          # volatility - how the reality actually moves
process_var = 0.05      # belief uncertainty growth
obs_noise = 1.0         # the trade noise
k_spread = 1.5          # spread vs sigma
gamma = 0.1             # inventory pressure
k_flow = 1.0            # execution sensitivity

import numpy as np
def logistic(x):
    return 1/(1 + np.exp(-x))

def makeQuotes(mu, sigma, inventory):
    center = mu - gamma*inventory
    half_spread = k_spread*sigma
    return center-half_spread, center+half_spread

def sampleOrder(p_true, bid, ask):
    d_ask = p_true - ask
    d_bid = bid - p_true

    prob_buy = logistic(k_flow*d_ask)
    prob_sell = logistic(k_flow*d_bid)

    buy = np.random.rand() < prob_buy
    sell = np.random.rand() < prob_sell

    if buy and sell:
        buy = np.random.rand() < 0.5
        sell = not buy

    if buy: return 'buy'
    elif sell: return 'sell'
    else: return None

def updateBelief(mu, sigma, trade_price):
    alpha = sigma**2/(sigma**2 + obs_noise)
    mu = mu + alpha*(trade_price - mu)
    sigma = (1 - alpha)*sigma
    return mu, sigma

# initialising values
p_true = 100
mu = 100
sigma = 2
inventory = 0
cash = 0

pnl_history = []
inv_history = []

# loop
for t in range(T):
    # nature moves
    p_true += np.random.normal(0, true_vol)

    # expanding uncertainty
    sigma = np.sqrt(sigma**2 + process_var)

    # making quotes
    bid, ask = makeQuotes(mu, sigma, inventory)

    # sample order
    event = sampleOrder(p_true, bid, ask)

    # updating portfolio
    if event == 'buy':
        inventory -= 1
        cash += ask
        mu, sigma = updateBelief(mu, sigma, ask)
    elif event == 'sell':
        inventory += 1
        cash -= bid
        mu, sigma = updateBelief(mu, sigma, bid)
    
    # mark to market
    pnl = cash + inventory*p_true
    pnl_history.append(pnl)
    inv_history.append(inventory)

# plotting the results
import matplotlib.pyplot as plt
plt.plot(pnl_history)
plt.title('PnL')
plt.show()

plt.plot(inv_history)
plt.title('Inventory')
plt.show()