#!/usr/bin/env python


def calculate_lastest_low_high(double low, double high, _data):
    cdef double mean, c_min, c_max
    x, y, last_price, pred = _data
    y.append(high - (high * 0.025))
    mean = sum(y) / len(y)
    c_min, c_max = (min(y) + mean) / 2, max(y)
    low = c_min - ((c_min - low) * 0.025)
    high = c_max + ((high - c_max) * 0.025)
    return low, high


def calculate_prices(double last_price, double low_profit, double max_profit, double low, double high):
    cdef double c_mean, c_min, c_min_max, c_max, diff
    c_mean = (low + high) / 2
    c_min = low + (low * low_profit)  # Preço mínimo 1% acima do mínimo
    c_min_max = c_min + (c_min * low_profit)
    c_max = c_min_max + (c_min_max * max_profit)  # Preço mínimo de venda 1% do máximo do mínimo
    # A bump in price... last keep going with it... raise the value to buy and sell
    # if last_price > c_max:
    #     diff = 1 - (c_max / last_price)
    #     c_min = c_min + (c_min * (diff - (diff * 0.05)))
    #     c_min_max = c_min_max + (c_min_max * (diff - (diff * 0.05)))
    #     c_max = c_max + (c_max * (diff - (diff * 0.05)))
    return float('{0:.4f}'.format(c_min)), \
           float('{0:.4f}'.format(c_min_max)), \
           float('{0:.4f}'.format(c_max)), \
           float('{0:.4f}'.format(c_mean))
