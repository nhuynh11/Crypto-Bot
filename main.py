import os
import discord
from discord.ext import commands
import requests
import json
import pandas as pd
import numpy as np
import plotly.express as px
# import plotly.graph_objects as go

FIGURE_1 = "images/fig1.png"

bot = commands.Bot(command_prefix = "!", help_command=None)
# get current price
def get_simple_price_usd(coin):
  params = {}
  params["ids"] = coin
  params["vs_currencies"] = "usd"
  response = requests.get("https://api.coingecko.com/api/v3/simple/price", params=params)
  json_data = json.loads(response.text)
  return json_data[coin]['usd']

# functions for price, marketcap, and volume dfs
def get_price_df_day(coin, days):
  params = {}
  params["vs_currency"] = "usd"
  params["days"] = days
  url = 'https://api.coingecko.com/api/v3/coins/{0}/market_chart'.format(coin)
  response = requests.get(url,params=params)
  json_data = json.loads(response.text)
  df = pd.DataFrame(json_data["prices"], columns=['time','price'])
  df['time'] = np.asarray(df['time'], dtype='datetime64[ns]')
  return df

def get_volume_df_day(coin, days):
  params = {}
  params["vs_currency"] = "usd"
  params["days"] = days
  url = 'https://api.coingecko.com/api/v3/coins/{0}/market_chart'.format(coin)
  response = requests.get(url,params=params)
  json_data = json.loads(response.text)
  df = pd.DataFrame(json_data["total_volumes"], columns=['time','volume'])
  df['time'] = np.asarray(df['time'], dtype='datetime64[ns]')
  return df

def get_summary(coin):
  params = {}
  params["localization"] = "false"
  params["tickers"] = "false"
  params["community_data"] = "false"
  params["developer_data"] = "false"
  params["sparkline"] = "false"
  url = 'https://api.coingecko.com/api/v3/coins/{0}'.format(coin)
  response = requests.get(url,params=params)
  json_data = json.loads(response.text)
  return json_data

def save_graph(fig):
  if not os.path.exists("images"):
    os.mkdir("images")
  fig.write_image(FIGURE_1)

def create_price_graph(coin, days):
  df = get_price_df_day(coin, days)
  # print(df)
  fig = px.line(df, x='time', y='price')
  save_graph(fig)

def create_volume_graph(coin, days):
  df = get_volume_df_day(coin, days)
  # print(df)
  fig = px.line(df, x='time', y='volume')
  save_graph(fig)

# when the bot is initialized
@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

# when the bot recieves a message return the usd price for the crypto asset
# seems like on_message doesn't play well with commands
@bot.command()
async def summary(ctx, coin):
  summary_data = get_summary(coin)
  create_price_graph(coin, 1)
  embed = discord.Embed(
    title = ' '.join((str(summary_data["market_data"]["market_cap_rank"]), summary_data["name"], summary_data["symbol"].upper())),
    url= summary_data["links"]["homepage"][0],
    color = discord.Color.blue()
  )
  embed.add_field(name = "Price", value = str('${:,.2f}'.format(summary_data["market_data"]["current_price"]["usd"])), inline = True)
  embed.add_field(name = "Market Cap", value = str('${:,.2f}'.format(summary_data["market_data"]["market_cap"]["usd"])), inline = True)
  embed.add_field(name = "24 Hour High", value = str('${:,.2f}'.format(summary_data["market_data"]["high_24h"]["usd"])), inline = True)
  embed.add_field(name = "24 Hour Low", value = str('${:,.2f}'.format(summary_data["market_data"]["low_24h"]["usd"])), inline = True)
  embed.add_field(name = "Max Supply", value = str(summary_data["market_data"]["max_supply"]), inline = True)
  embed.add_field(name = "Circulating Supply", value = str(summary_data["market_data"]["circulating_supply"]), inline = True)
  file = discord.File(FIGURE_1, filename="image.png")
  embed.set_image(url="attachment://image.png")
  await ctx.send(file=file, embed=embed)

@bot.command()
async def price(ctx, coin):
  await ctx.send(get_simple_price_usd(coin))

@bot.command()
async def graph(ctx, coin, days):
  create_price_graph(coin, days)
  embed = discord.Embed(
    title = coin.upper(),
    description = 'Price Chart Over {}'.format(days) +' days.',
    color = discord.Color.blue()
  )
  file = discord.File(FIGURE_1, filename="image.png")
  embed.set_image(url="attachment://image.png")
  await ctx.send(file=file, embed=embed)

@bot.command()
async def graph_volume(ctx, coin, days):
  create_volume_graph(coin, days)
  embed = discord.Embed(
    title = coin.upper(),
    description = 'Volume Chart Over {}'.format(days) +' days.',
    color = discord.Color.blue()
  )
  file = discord.File(FIGURE_1, filename="image.png")
  embed.set_image(url="attachment://image.png")
  await ctx.send(file=file, embed=embed)

@bot.command()
async def test(ctx):
  print('test')

bot.run(os.environ['TOKEN'])

#TODO: help command
#TODO: overall summary
#TODO: timeframe
#TODO: error handling
#TODO: graph styling
#TODOMaybe: candlestick
#remember: pip install -U kaleido