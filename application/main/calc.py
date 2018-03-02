import numpy as np
import pandas as pd


def calc_portfolio(mode, budget, limit, properties):
  df = pd.DataFrame(list(
    {
      "id": x.id,
      "list_price": x.list_price,
      "score_v1_appreciation": x.score_v1_appreciation,
      "score_v2_balance": x.score_v2_balance,
      "score_v3_return": x.score_v3_return,
    } for x in properties))

  if mode == 1:
    score = list(df.sort_values(by="score_v1_appreciation", ascending=False)["score_v1_appreciation"][:limit])
    price = [int(i) for i in list(df.sort_values(by="score_v1_appreciation", ascending=False)["list_price"][:limit])]
  elif mode == 2:
    score = list(df.sort_values(by="score_v2_balance", ascending=False)["score_v2_balance"][:limit])
    price = [int(i) for i in list(df.sort_values(by="score_v2_balance", ascending=False)["list_price"][:limit])]
  elif mode == 3:
    score = list(df.sort_values(by="score_v3_return", ascending=False)["score_v3_return"][:limit])
    price = [int(i) for i in list(df.sort_values(by="score_v3_return", ascending=False)["list_price"][:limit])]

  matrix = np.zeros((limit + 1, budget + 1))

  result = knapsack(limit, budget, price, score, matrix)
  n, c, arr, sack = limit, budget, matrix, []

  while (n > 0 and c > 0):

    if (c - price[n - 1] >= 0 and arr[n][c] == arr[n - 1][c - price[n - 1]] + score[n - 1]):
      sack.append(int(df.loc[n - 1]["id"]))
      c -= price[n - 1]
    n -= 1

  return sack
  # print(score)
  # print(price)
  # print("item picked:", sack)


def knapsack(items, budget, price, score, matrix):
  result = 0

  if matrix[items][budget] != 0:
    return matrix[items][budget]

  if items == 0 or budget == 0:
    result = 0

  elif price[items - 1] > budget:
    result = knapsack(items - 1, budget, price, score, matrix)

  else:
    result = max(knapsack(items - 1, budget, price, score, matrix),
                 score[items - 1] + knapsack(items - 1, budget - price[items - 1], price, score, matrix))

  matrix[items][budget] = result

  return result
