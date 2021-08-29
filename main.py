import os
import discord
from discord.ext import commands
import requests
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
from keep_alive import keep_alive

FIGURE_1 = "images/fig1.png"

bot = commands.Bot(command_prefix = "!")

# when the bot is initialized
@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send('Please provide all required arguments.')
  else:
    await ctx.send('Error processing request. Check server log for details.')

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
  df['time'] = [datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S') for ts in df['time']]
  return df

def get_volume_df_day(coin, days):
  params = {}
  params["vs_currency"] = "usd"
  params["days"] = days
  url = 'https://api.coingecko.com/api/v3/coins/{0}/market_chart'.format(coin)
  response = requests.get(url,params=params)
  json_data = json.loads(response.text)
  df = pd.DataFrame(json_data["total_volumes"], columns=['time','volume'])
  df['time'] = [datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S') for ts in df['time']]
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
  fig = px.line(df, x='time', y='price')
  save_graph(fig)

def create_volume_graph(coin, days):
  df = get_volume_df_day(coin, days)
  fig = px.line(df, x='time', y='volume')
  save_graph(fig)

# when the bot recieves a message return the usd price for the crypto asset
# seems like on_message doesn't play well with commands
@bot.command(brief='Returns a market summary.', description='Type the command with 1 argument <coin_name> to get the market summary details of the specified coin. Ex: !summary bitcoin')
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

@bot.command(brief='Returns the current price.', description='Type the command with 1 argument <coin_name> to get the current price. Ex: !price bitcoin')
async def price(ctx, coin):
  await ctx.send('${:,.2f}'.format(get_simple_price_usd(coin)))

@bot.command(brief='Returns a price graph.', description='Type the command with 2 arguments <coin_name> and <days> to get a price graph over the specified amount of days. Ex: !graph bitcoin 1')
async def graph(ctx, coin, days):
  create_price_graph(coin, days)
  embed = discord.Embed(
    title = coin.upper(),
    description = 'Price chart over {}'.format(days) +' day(s).',
    color = discord.Color.blue()
  )
  file = discord.File(FIGURE_1, filename="image.png")
  embed.set_image(url="attachment://image.png")
  await ctx.send(file=file, embed=embed)

@bot.command(brief='Returns a volume graph.', description='Type the command with 2 arguments <coin_name> and <days> to get a volume graph over the specified amount of days. Ex: !graph_volume bitcoin 1')
async def graph_volume(ctx, coin, days):
  create_volume_graph(coin, days)
  embed = discord.Embed(
    title = coin.upper(),
    description = 'Volume chart over {}'.format(days) +' day(s).',
    color = discord.Color.blue()
  )
  file = discord.File(FIGURE_1, filename="image.png")
  embed.set_image(url="attachment://image.png")
  await ctx.send(file=file, embed=embed)

# error handling for price command
# @price.error
# async def price_error(ctx, error):
#   if isinstance(error, commands.MissingRequiredArgument):
#     await ctx.send('Please provide all required arguments.')
#   else:
#     await ctx.send('Error processing request. Check server log for details.')

bot.run(os.environ['TOKEN'])

#TODO: error handling
#TODO: graph styling
#TODOMaybe: candlestick