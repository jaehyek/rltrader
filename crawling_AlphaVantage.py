"""
여기의 함수들은
 https://www.alphavantage.co/documentation/ 을 활용하는
 python module "https://github.com/RomelTorres/alpha_vantage"을 사용한다.
 API key is: V5IARGY5XNYWW2Z0

 dow jons 지수 얻기
 https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=DJI&outputsize=full&apikey=V5IARGY5XNYWW2Z0
"""

from alpha_vantage.timeseries import TimeSeries
from datetime import  datetime, timedelta, date
from pprint import pprint

def IndiceDaily_DJI(dateRecent, datePast):
    ts = TimeSeries(key='V5IARGY5XNYWW2Z0', output_format='pandas')
    data, meta_data = ts.get_daily(symbol="DJI",outputsize='full' )

    data = data['4. close']             # close만 선택 -> series가 나온다.
    data = data[::-1]                   # 최근 item이 첫 번째 요소로 나오게 역순.
    data = data.to_frame('close')       # seriese -> dataframe으로 만들면서, 이름을 close로 할당.
                                        # date이 index으로 되어 있다.
    data = data.reset_index()           # date이 column 이름으로 나오게 한다.
    data = data[(data['date'] >= datePast.strftime("%Y-%m-%d")) & (data['date'] <= dateRecent.strftime("%Y-%m-%d"))]
    data = data.reset_index()

    return data



if __name__ == "__main__":
    dateRecent = datetime.strptime("2019-02-28", "%Y-%m-%d")
    dateDelta = timedelta(days=365 * 3)
    datePast = dateRecent - dateDelta

    df = IndiceDaily_DJI(dateRecent, datePast)
    df.to_csv("Ind_DJI.csv")        # Permission denied 이 나오면, dos command에서 실행한다.