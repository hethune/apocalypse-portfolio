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
    df = shuffle("score_v1_appreciation", df)
    score = list(df.sort_values(by="score_v1_appreciation", ascending=False)["score_v1_appreciation"][:limit])
    price = [int(i) for i in list(df.sort_values(by="score_v1_appreciation", ascending=False)["list_price"][:limit])]
  elif mode == 2:
    df = shuffle("score_v2_balance", df)
    score = list(df.sort_values(by="score_v2_balance", ascending=False)["score_v2_balance"][:limit])
    price = [int(i) for i in list(df.sort_values(by="score_v2_balance", ascending=False)["list_price"][:limit])]
  elif mode == 3:
    df = shuffle("score_v3_return", df)
    score = list(df.sort_values(by="score_v3_return", ascending=False)["score_v3_return"][:limit])
    price = [int(i) for i in list(df.sort_values(by="score_v3_return", ascending=False)["list_price"][:limit])]

  matrix = np.zeros((limit + 1, budget + 1))

  result = knapsack(limit, budget, price, score, matrix)
  n, c, arr, sack = limit, budget, matrix, []
  tmp = []
  while (n > 0 and c > 0):

    if (c - price[n - 1] >= 0 and arr[n][c] == arr[n - 1][c - price[n - 1]] + score[n - 1]):
      c -= price[n - 1]
      tmp.append(n - 1)
    n -= 1

  for item in tmp:
    if mode == 1:
      sack.append(df[df["score_v1_appreciation"] == score[item]]["id"].values[0])
    elif mode == 2:
      sack.append(df[df["score_v2_balance"] == score[item]]["id"].values[0])
    elif mode == 3:
      sack.append(df[df["score_v3_return"] == score[item]]["id"].values[0])

  return sack

def shuffle(frame, database):

    test = database.sort_values(frame, ascending = False)
    it = list(item for item in test[frame][:40])
    index_db = np.array(list(test[test[frame] == item].index.values[0] for item in it))
    index = np.random.choice(range(5, 40), 25, replace = False)

    return pd.concat([test.loc[index_db[:5]], test.loc[index_db[index]]])


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
