import repo
from datetime import date
from collections import defaultdict

    # series : [
    #     { name: 'DB', data: [{ x: 'BBCA', y: 80 }, { x: 'TLKM', y: -30 }, { x: 'GOTO', y: 50 }, { x: 'AMRT', y: 50 }] },
    #     { name: 'CS', data: [{ x: 'BBCA', y: -20 }, { x: 'TLKM', y: 60 }, { x: 'GOTO', y: -10 }] },
    #     { name: 'ML', data: [{ x: 'BBCA', y: 40 }, { x: 'TLKM', y: 20 }, { x: 'GOTO', y: -70 }] },
    #     { name: 'CT', data: [{ x: 'BBCA', y: 40 }, { x: 'TLKM', y: 20 }, { x: 'GOTO', y: -70 }] },
    #     { name: 'ZZ', data: [{ x: 'BBCA', y: 40 }, { x: 'TLKM', y: 20 }, { x: 'GOTO', y: -70 }] },
    #     { name: 'XX', data: [{ x: 'BBCA', y: 40 }, { x: 'TLKM', y: 20 }, { x: 'GOTO', y: -70 }] },
    #     { name: 'DD', data: [{ x: 'BBCA', y: 40 }, { x: 'TLKM', y: 20 }, { x: 'GOTO', y: -70 }] },
    #     { name: 'L4', data: [{ x: 'BBCA', y: 40 }, { x: 'TLKM', y: 20 }, { x: 'GOTO', y: -70 }] },
    #     { name: '14', data: [{ x: 'BBCA', y: 40 }, { x: 'TLKM', y: 20 }, { x: 'GOTO', y: -70 }] },
    #     { name: '33', data: [{ x: 'BBCA', y: 40 }, { x: 'TLKM', y: 20 }, { x: 'GOTO', y: -70 }] },
    #     { name: '22', data: [{ x: 'BBCA', y: 40 }, { x: 'TLKM', y: 20 }, { x: 'GOTO', y: -70 }] },
    # ],

def _parse_data(data: list)->list:
    parsed_data = {}
    for item in data:
        if item[0] not in parsed_data:
            parsed_data[item[0]] = []   
        parsed_data[item[0]].append({'x': item[1], 'y': item[4]})   
        # if item[0]=='AK':
        #     print('AK : ', item)

    parsed_data2 = []
    for k, v in parsed_data.items():
        parsed_data2.append({'name': k, 'data': v })
        # if k=='AK' :
        #     print('data:', v)

    return parsed_data2        

def get_broker_summary(param: dict)->list:
    broksum = repo.get_broker_summary(param['first_date'], param['second_date'], param['broker_codes'], param['stocks'])
    
    # data is parsed so it can match the apexChart format (It used the format above on the frontend with x and y)
    return _parse_data(broksum)

def get_broker_summary_screened(param: dict)->list:
    offset = (param['page'] - 1) * param['limit']
    total_limit = repo.get_total_broker_on_activity(param['first_date'], param['second_date'])

    broksum = repo.get_top_broker_summary(param['first_date'], param['second_date'], param['limit'], offset )
    parse = _parse_data(broksum)
        
    return {
        'data': parse,
        'total_limit': total_limit[0][0],
        'page': param['page'],
        'limit': param['limit']
    }

def get_all_stocks():
    return repo.get_all_stocks()

def get_all_brokers():
    return repo.get_all_brokers()
