
import urllib
import time

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import  datetime, timedelta


def GetInstitutionForeignTradingInfoFromNaver(dfref, stockCode,dateRecent, datePast ):
    """
    Naver Finance에서 기관,외국인 매매 Crawing 하는 함수

    네이버증권 외국인ㆍ기관 순매매 거래량 크롤링 ( https://ldgeao99.wordpress.com/2017/04/23/%EB%84%A4%EC%9D%B4%EB%B2%84%EC%A6%9D%EA%B6%8C-%EC%99%B8%EA%B5%AD%EC%9D%B8%E3%86%8D%EA%B8%B0%EA%B4%80-%EC%88%9C%EB%A7%A4%EB%A7%A4-%EA%B1%B0%EB%9E%98%EB%9F%89-%ED%81%AC%EB%A1%A4%EB%A7%81/ )
    날짜: 2019.02.21 기관순매매: -128,361 외인순매매: -76,141 외인보유 주식수: 999,456 외인 보유율: 4.08%
    날짜: 2019.02.20 기관순매매: 0 외인순매매: +1,808 외인보유 주식수: 1,075,597 외인 보유율: 4.39%
    날짜: 2019.02.19 기관순매매: 0 외인순매매: +12,894 외인보유 주식수: 1,073,789 외인 보유율: 4.38%
    날짜: 2019.02.18 기관순매매: 0 외인순매매: +1,103 외인보유 주식수: 1,060,895 외인 보유율: 4.33%
    날짜: 2019.02.15 기관순매매: 0 외인순매매: -158,529 외인보유 주식수: 1,059,792 외인 보유율: 4.33%
    ...

    """
    # stockCode = '065450' # 065450 빅텍

    trendOfInvestorUrl = 'http://finance.naver.com/item/frgn.nhn?code=' + stockCode
    trendOfInvestorHtml = urlopen(trendOfInvestorUrl)
    trendOfInvestorSource = BeautifulSoup(trendOfInvestorHtml.read(), "html.parser")

    trendOfInvestorPageNavigation = trendOfInvestorSource.find_all("table", align="center")
    trendOfInvestorMaxPageSection = trendOfInvestorPageNavigation[0].find_all("td", class_="pgRR")
    trendOfInvestorMaxPageNum = int(trendOfInvestorMaxPageSection[0].a.get('href')[-3:])

    col = ["date", "institutionPureDealing", "foreignerPureDealing", "ownedVolumeByForeigner", "ownedRateByForeigner"]
    df = pd.DataFrame(columns=col)
    done = False
    for page in range(1, trendOfInvestorMaxPageNum + 1):
        url = 'http://finance.naver.com/item/frgn.nhn?code=' + stockCode + '&page=' + str(page)
        html = urlopen(url)
        source = BeautifulSoup(html.read(), "html.parser")
        dataSection = source.find("table", summary="외국인 기관 순매매 거래량에 관한표이며 날짜별로 정보를 제공합니다.")
        dayDataList = dataSection.find_all("tr")

        # day: 날짜
        # institutionPureDealing: 기관순매매
        # foreignerPureDealing: 외인순매매
        # ownedVolumeByForeigner: 외인보유 주식수
        # ownedRateByForeigner : 외인 보유율

        for i in range(3, len(dayDataList)):

            if(len(dayDataList[i].find_all("td", class_="tc")) != 0 and len(dayDataList[i].find_all("td", class_="num")) != 0):
                day = dayDataList[i].find_all("td", class_="tc")[0].text
                institutionPureDealing = dayDataList[i].find_all("td", class_="num")[4].text
                foreignerPureDealing = dayDataList[i].find_all("td", class_="num")[5].text
                ownedVolumeByForeigner = dayDataList[i].find_all("td", class_="num")[6].text
                ownedRateByForeigner = dayDataList[i].find_all("td", class_="num")[7].text

                day = datetime.strptime(day, "%Y.%m.%d")
                institutionPureDealing = int(institutionPureDealing.replace(",", ""))
                foreignerPureDealing = int(foreignerPureDealing.replace(",", ""))
                ownedVolumeByForeigner = int(ownedVolumeByForeigner.replace(",", ""))
                ownedRateByForeigner = float(ownedRateByForeigner.replace("%", "")) / 100.
                ownedRateByForeigner = round(ownedRateByForeigner, 6)

                if (day > dateRecent ) :
                    continue
                elif ( day < datePast ):
                    done = True
                    break

                listtemp = [day, institutionPureDealing, foreignerPureDealing, ownedVolumeByForeigner, ownedRateByForeigner ]
                print(listtemp)
                df = df.append(dict(zip(col, listtemp)), ignore_index=True)
        if (done == True):
            break

    df = df.set_index("date")

    dfres = pd.concat([dfref, df], axis=1)
    print(dfres)

    return dfres








def GetStockTradingInfoFromNaver(stockCode,dateRecent, datePast ):
    """
    날짜: 2019.02.28 종가: 3,100 시가: 2,485 고가: 3,130 저가: 2,475 거래량: 17,255,128
    날짜: 2019.02.27 종가: 2,475 시가: 2,440 고가: 2,485 저가: 2,435 거래량: 201,703
    날짜: 2019.02.26 종가: 2,440 시가: 2,450 고가: 2,490 저가: 2,435 거래량: 267,439
    날짜: 2019.02.25 종가: 2,450 시가: 2,475 고가: 2,490 저가: 2,435 거래량: 225,572
    날짜: 2019.02.22 종가: 2,485 시가: 2,465 고가: 2,495 저가: 2,445 거래량: 344,336
    날짜: 2019.02.21 종가: 2,465 시가: 2,520 고가: 2,535 저가: 2,450 거래량: 557,773
    ...

    return : DataFrame

    """

    #stockCode = '065450'  # 065450 빅텍
    col = ["date", "open", "close", "high", "low", "volume"]

    df = pd.DataFrame(columns=col)
    dayPriceUrl = 'http://finance.naver.com/item/sise_day.nhn?code=' + stockCode
    dayPriceHtml = urlopen(dayPriceUrl)
    dayPriceSource = BeautifulSoup(dayPriceHtml.read(), "html.parser")

    dayPricePageNavigation = dayPriceSource.find_all("table", align="center")
    dayPriceMaxPageSection = dayPricePageNavigation[0].find_all("td", class_="pgRR")
    dayPriceMaxPageNum = int(dayPriceMaxPageSection[0].a.get('href')[-3:])

    done = False
    for page in range(1, dayPriceMaxPageNum + 1):
        url = 'http://finance.naver.com/item/sise_day.nhn?code=' + stockCode + '&page=' + str(page)
        html = urlopen(url)
        source = BeautifulSoup(html.read(), "html.parser")
        srlists = source.find_all("tr")
        isCheckNone = None

        # day: 날짜
        # closingPrice: 종가
        # variation: 전일대비
        # openingPrice: 시가
        # highestPrice: 고가
        # lowestPrice: 저가
        # volume: 거래량

        for i in range(1, len(srlists) - 1):
            if (srlists[i].span != isCheckNone):
                day = srlists[i].find_all("td", align="center")[0].text
                closingPrice = srlists[i].find_all("td", class_="num")[0].text
                openingPrice = srlists[i].find_all("td", class_="num")[2].text
                highestPrice = srlists[i].find_all("td", class_="num")[3].text
                lowestPrice = srlists[i].find_all("td", class_="num")[4].text
                volume = srlists[i].find_all("td", class_="num")[5].text

                day = datetime.strptime(day, "%Y.%m.%d")
                closingPrice = int(closingPrice.replace(",", ""))
                openingPrice = int(openingPrice.replace(",", ""))
                highestPrice = int(highestPrice.replace(",", ""))
                lowestPrice = int(lowestPrice.replace(",", ""))
                volume = int(volume.replace(",", ""))

                if (day > dateRecent ) :
                    continue
                elif ( day < datePast ):
                    done = True
                    break

                listtemp = [day, openingPrice, closingPrice, highestPrice, lowestPrice, volume]
                print(listtemp)
                df = df.append(dict(zip(col, listtemp)), ignore_index=True)

        if( done == True):
            break

    df = df.set_index("date")

    return df

def ExchangeDaily_USDKRW(dateRecent, datePast ):
    """
    원달러 환율표에서 매매기준율 을 가져오기
    url = https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW
    :return:
    """

    col = ["date", "usdkrw"]

    df = pd.DataFrame(columns=col)
    dayExchangeUrl = 'https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW'
    dayExchangePageSection = dayExchangeUrl + '&page='

    # 먼저 시작 일자를 찾는다.
    pageindex = 1
    done = False
    while(1):
        UrlPage = dayExchangePageSection + str(pageindex)
        dayExchangeSource = BeautifulSoup(urlopen(UrlPage), "html.parser")
        listtr = dayExchangeSource.find("tbody").find_all("tr")

        for tr in listtr :
            listtd = tr.find_all("td")
            day = listtd[0].text
            price = listtd[1].text


            day = datetime.strptime(day, "%Y.%m.%d")
            price = float(price.replace(",", ""))

            if (day > dateRecent):
                continue
            elif (day < datePast):
                done = True
                break

            listtemp = [day, price]
            # print(listtemp)
            df = df.append(dict(zip(col, listtemp)), ignore_index=True)

        if done == True :
            break;

        pageindex = pageindex + 1

    return df

def OilDaily_DU(dateRecent, datePast ):
    """
    두바이유 매매기준율 을 가져오기
    url = https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=OIL_DU&fdtc=2
    :return:
    """

    col = ["date", "oil_du"]

    df = pd.DataFrame(columns=col)
    dayExchangeUrl = 'https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=OIL_DU&fdtc=2'
    dayExchangePageSection = dayExchangeUrl + '&page='

    # 먼저 시작 일자를 찾는다.
    pageindex = 1
    done = False
    while(1):
        UrlPage = dayExchangePageSection + str(pageindex)
        dayExchangeSource = BeautifulSoup(urlopen(UrlPage), "html.parser")
        listtr = dayExchangeSource.find("tbody").find_all("tr")

        for tr in listtr :
            listtd = tr.find_all("td")
            day = listtd[0].text.strip()
            price = listtd[1].text.strip()


            day = datetime.strptime(day, "%Y.%m.%d")
            price = float(price.replace(",", ""))

            if (day > dateRecent):
                continue
            elif (day < datePast):
                done = True
                break

            listtemp = [day, price]
            # print(listtemp)
            df = df.append(dict(zip(col, listtemp)), ignore_index=True)

        if done == True :
            break;

        pageindex = pageindex + 1

    return df



if __name__ == "__main__" :
    dateRecent = datetime.strptime("2019-02-28", "%Y-%m-%d" )
    dateDelta = timedelta(days=365 * 3)
    datePast = dateRecent - dateDelta
    # df = GetStockTradingInfoFromNaver('065450',dateRecent, datePast )
    #
    # dfres = GetInstitutionForeignTradingInfoFromNaver(df, '065450',dateRecent, datePast )
    # # dfres.to_hdf("sample.h5", "df")
    # dfres.to_csv("sample.csv")
    #
    # # df = pd.read_hdf("sample.h5", "df")
    # # df.to_csv("sample.csv")

    # df = ExchangeDaily_USDKRW(dateRecent, datePast)
    # df.to_csv("Exchange_usdkrw.csv")

    df = OilDaily_DU(dateRecent, datePast)
    df.to_csv("oil_du.csv")