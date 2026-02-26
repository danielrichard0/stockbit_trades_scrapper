from playwright.sync_api import sync_playwright
from playwright_recaptcha import recaptchav3
from protobuf_decoder.protobuf_decoder import Parser
import ast
import json
from datetime import datetime
import requests

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        data_retrieve = []
        trigger_val = 100000000
        api_url = 'http://127.0.0.1:5000/rt-alert'

        def on_websocket(ws):
            print("🧠 WebSocket opened:", ws.url)

            ws.on("framereceived", lambda frame: handle_frame(ws.url, frame))
            #ws.on("framesent", lambda frame: handle_sent(ws.url, frame))

        # harus memfilter websocket hanya yang running trade saja
        def handle_frame(url, frame)->bool:
            if not url == 'wss://wss-jkt.trading.stockbit.com/ws':
                return False           
                        
            payload_hex = frame.hex() 
            try:
                payload_data = Parser().parse(payload_hex).to_dict()
            except Exception as e:
                print(f"ada error saat parsing data payload : {e}")
                return False

            # filter hanya dari running trade
            if payload_data['results'][0]['field'] != 8:
                return False     
            
            payload_data = payload_data['results'][0]['data']['results']
            for stock in payload_data:
                
                data = stock['data']['results']

                param = {}
                
                param['code'] = data[1]['data'] 
                param['tick_time'] = str(datetime.fromtimestamp(data[0]['data']['results'][0]['data'])) # array 1 waktu + id
                param['price'] = data[2]['data']['value']
                param['shares'] = data[3]['data']['value']
                param['type'] = data[4]['data']
                total_val = param['price'] * param['shares']
               # undef3 = data[7]['data']['results'][1]['data']['value']

                # lebih dari 1 milyar
                if total_val > trigger_val:
                    requests.get(url=api_url, params=param)

                    
                    # with open('output2.json', 'w') as json_file:
                    #     json.dump(data_retrieve, json_file, indent=4)                    


            return True
            # data_retrieve.append(payload_data)
            # with open('output.json', 'w') as json_file:
            #     json.dump(data_retrieve, json_file, indent=4)

            # return


            # # wss://ws3.stockbit.com/primus/507/_bx8ya7s/websocket
            # print(json.dumps(data, indent=2)[:1000])

        # belum kepakai
        def handle_sent(url, frame):
            pass 

        page.goto("https://stockbit.com/login")
        with recaptchav3.SyncSolver(page) as solver:            
            token = solver.solve_recaptcha(timeout=60)  

        page.on("websocket", on_websocket)
        page.pause()

      
        

run()