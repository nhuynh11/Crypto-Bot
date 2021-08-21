import os
import discord
from discord.ext import commands
import requests
import json
import pandas as pd
import plotly.express as px
# import plotly.graph_objects as go

FIGURE_1 = "images/fig1.png"

bot = commands.Bot(command_prefix = "!", help_command=None)

def get_simple_price_usd(coin):
  params = {}
  params["ids"] = coin
  params["vs_currencies"] = "usd"
  response = requests.get("https://api.coingecko.com/api/v3/simple/price", params=params)
  json_data = json.loads(response.text)
  return json_data[coin]['usd']

def message_from_bot(message):
  # check if the message is from the bot
  return True if message.author == bot.user else False

# functions for price, marketcap, and volume dfs
def get_price_df_day(coin):
  params = {}
  params["vs_currency"] = "usd"
  params["days"] = "1"
  url = 'https://api.coingecko.com/api/v3/coins/{0}/market_chart'.format(coin)
  response = requests.get(url,params=params)
  json_data = json.loads(response.text)
  df = pd.DataFrame(json_data["prices"], columns=['time','price'])
  return df

def save_image(fig):
  if not os.path.exists("images"):
    os.mkdir("images")
  fig.write_image(FIGURE_1)

# when the bot is initialized
@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

# when the bot recieves a message return the usd price for the crypto asset
# seems like on_message doesn't play well with commands
@bot.command()
async def summary(ctx, coin):
  df = get_price_df_day(coin)
  # print(df)
  fig = px.line(df, x='time', y='price')
  save_image(fig)
  # TODO: get price of coin from last data point, so we don't have to make api call 2 times
  embed = discord.Embed(
    title = coin.upper(),
    description = '$' + str(get_simple_price_usd(coin)),
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