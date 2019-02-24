#-*- coding: utf-8 -*-
"""
https://pydata.tistory.com/2 설명에서 주식종목 list을 가져오기를 참조한다.
파일은 \data\상장회사code.csv을 읽어서  상장회사 --> stockcode 로 변환.
"""

import pandas as pd
import numpy as np

def getStockCode(strCompanyname):
    stock_data = pd.read_csv("data/stockcode.csv",encoding='utf-8')
    stock_data = stock_data[['종목코드', '기업명']]
    index = np.where (stock_data['기업명'] == strCompanyname )[0]
    index = index[0]
    code = stock_data.iat[index, 0 ]
    code = '{:0>6}'.format(code)
    return code


if __name__ == "__main__" :
    getStockCode("삼성전자")