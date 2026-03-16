from fastapi import APIRouter 
from discord_bot.dc_bot import  bot
import discord
from dotenv import load_dotenv
import os

load_dotenv()
img_url = os.getenv('STOCK_IMG_URL')

router = APIRouter(
    prefix = '/alert', 
    tags= ["alert"], 
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def rt_alert(code: str,tick_time: str, price: float, shares: int, type: int ):    
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.name == 'running-trade-detector':
                if type == 1:
                    status = 'BUY'
                    color = discord.Colour.green()
                else:
                    status = 'SELL'    
                    color = discord.Colour.red()
                    
                value = round((price * shares), 2)  

                embed = discord.Embed(
                    color=color,
                    title=f"[{status}][{code}]",
                    description=f"""
                        - TICK TIME \t: {tick_time} \n- PRICE     \t\t: {price:,}\n- LOT     \t\t\t: {round(shares/100)}\n- VALUE\t\t\t: Rp. {value:,}
                    """
                )               

                construct_url = img_url+code+'.png'
                print(construct_url)
                
                #embed.set_image(url=construct_url)
                embed.set_thumbnail(url=construct_url)
               # await channel.send(f'PRICE ALERT!, [{code}][{tick_time}| HARGA : {price:,} | LOT : {shares/100}] | {status} | TOTAL NILAI : RP. {value:,} ')
                await channel.send(embed=embed)