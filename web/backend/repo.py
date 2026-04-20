from connect import connectDB
from datetime import date

def get_broker_summary(first_date: date, second_date: date, broker_codes: list[str], stocks: list[str])->list:
    conn, cursor = connectDB()
    # generate '?' placeholders
    broker_placeholder = ", ".join(["?"] * len(broker_codes))
    stock_placeholder = ", ".join(["?"] * len(stocks))

    query = f"""
        select broker_code, stock_symbol, sum(buy_val), sum(sell_val), sum(buy_val) - sum(sell_val) as net, sum(buy_lot), sum(sell_lot),
            sum(buy_avg), sum(sell_avg) from (
        select broker_code, stock_symbol, value as buy_val, 0 as sell_val,total_lot as buy_lot, 0 as sell_lot, 
            price_average as buy_avg, 0 as sell_avg  from broker_summary 
            where broker_code in ({broker_placeholder})
            and stock_symbol in ({stock_placeholder}) 
            and date_start between ? and ?
            and time_range = 'D'
            and action = 'B'
        union 
        select broker_code, stock_symbol, 0 as buy_val, value as sell_val,0 as buy_lot, total_lot as sell_lot, 
            0 as buy_avg, price_average  as sell_avg  from broker_summary 
            where broker_code in ({broker_placeholder})
            and stock_symbol in ({stock_placeholder}) 
            and date_start between ? and ? 
            and time_range = 'D'
            and action = 'S'	
        ) x
        group by broker_code, stock_symbol    
    """
    cursor.execute(query, [*broker_codes, *stocks, first_date, second_date, *broker_codes, *stocks, first_date, second_date])
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    return result

def get_top_broker_summary(first_date: date, second_date: date, limit: int, offset:int )->list:
    conn, cursor = connectDB()

    query="""
        with top_brokers as (
            SELECT broker_code
                FROM broker_summary
                WHERE date_start BETWEEN %(first_date)s AND %(second_date)s
                AND time_range = 'D'
                GROUP BY broker_code
                ORDER BY SUM(value) DESC
            LIMIT %(limit)s OFFSET %(offset)s
        ),
        top_stock_from_above_brokers as (
            SELECT stock_symbol 
                FROM broker_summary
                WHERE date_start BETWEEN %(first_date)s AND %(second_date)s
                AND time_range = 'D'
                GROUP BY stock_symbol 
                ORDER BY SUM(value) DESC
            LIMIT %(limit)s OFFSET %(offset)s
        )

        select broker_code, stock_symbol, sum(buy_val) ,sum(sell_val), sum(buy_val) - sum(sell_val) as net, sum(buy_lot), sum(sell_lot),
            sum(buy_avg), sum(sell_avg) from (
        select broker_code, stock_symbol, value as buy_val, 0 as sell_val,total_lot as buy_lot, 0 as sell_lot, 
            price_average as buy_avg, 0 as sell_avg  from broker_summary 
            where broker_code in (select * from top_brokers)
            and stock_symbol in (select * from top_stock_from_above_brokers)
            and date_start between %(first_date)s and %(second_date)s 
            and time_range = 'D'
            and action = 'B'
        union 
        select broker_code, stock_symbol, 0 as buy_val, value as sell_val,0 as buy_lot, total_lot as sell_lot, 
            0 as buy_avg, price_average  as sell_avg  from broker_summary 
            where broker_code in (select * from top_brokers)
            and stock_symbol in (select * from top_stock_from_above_brokers)
            and date_start between %(first_date)s and %(second_date)s 
            and time_range = 'D'
            and action = 'S'	
        ) x
        group by broker_code, stock_symbol
        order by broker_code, stock_symbol
    """

    cursor.execute(query, {"first_date": first_date, "second_date": second_date, "limit": limit, "offset": offset})
    result = cursor.fetchall()
    cursor.close()
    conn.close()    
    return result

def get_total_broker_on_activity(first_date: date, second_date: date):
    conn, cursor = connectDB()
    query = """
    SELECT count(distinct(broker_code)) 
		FROM broker_summary
		WHERE date_start BETWEEN ? AND ?
		  AND time_range = 'D'
    """
    cursor.execute(query, [first_date, second_date])
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_all_stocks():
    conn, cursor = connectDB()
    query = """
    SELECT stock_symbol, stock_name FROM stock_symbols
    """
    cursor.execute(query, )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_all_brokers():
    conn, cursor = connectDB()
    query = """
    select broker_code, broker_name from brokers 
    """
    cursor.execute(query, )
    result = cursor.fetchall()
    cursor.close()
    conn.close()   
    return result

# if __name__ == '__main__':
#     a = get_total_broker_on_activity(date(2026,4,1), date(2026,4,4))
#     print(a)