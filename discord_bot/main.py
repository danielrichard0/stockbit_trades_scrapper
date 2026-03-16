
import os 
import uvicorn
from api import app

token = os.getenv('DISCORD_KEY')
#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode= 'w')

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000 )

#bot.run(token, log_handler=handler, log_level=logging.DEBUG)