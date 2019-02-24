
import urllib
import time

from urllib.request import urlopen
from bs4 import BeautifulSoup

def GetApparatusForeignTradingInfoFromNaver(stockCode ):
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
                print("날짜: " + day, end=" ")
                print("기관순매매: " + institutionPureDealing, end=" ")
                print("외인순매매: " + foreignerPureDealing, end=" ")
                print("외인보유 주식수: " + ownedVolumeByForeigner, end=" ")
                print("외인 보유율: " + ownedRateByForeigner)


def GetStockTradingInfoFromNaver(stockCode):
    """
    네이버증권 일별시세 크롤링 방법 ( https://ldgeao99.wordpress.com/2017/04/17/%EB%84%A4%EC%9D%B4%EB%B2%84%EC%A6%9D%EA%B6%8C-%EC%A3%BC%EA%B0%80%EB%8D%B0%EC%9D%B4%ED%84%B0-%ED%81%AC%EB%A1%A4%EB%A7%81-%EB%B0%A9%EB%B2%95/ )
    날짜: 2019.02.21 기관순매매: -128,361 외인순매매: -76,141 외인보유 주식수: 999,456 외인 보유율: 4.08%
    날짜: 2019.02.20 기관순매매: 0 외인순매매: +1,808 외인보유 주식수: 1,075,597 외인 보유율: 4.39%
    날짜: 2019.02.19 기관순매매: 0 외인순매매: +12,894 외인보유 주식수: 1,073,789 외인 보유율: 4.38%
    날짜: 2019.02.18 기관순매매: 0 외인순매매: +1,103 외인보유 주식수: 1,060,895 외인 보유율: 4.33%
    날짜: 2019.02.15 기관순매매: 0 외인순매매: -158,529 외인보유 주식수: 1,059,792 외인 보유율: 4.33%
    ...

    """

    #stockCode = '065450'  # 065450 빅텍

    dayPriceUrl = 'http://finance.naver.com/item/sise_day.nhn?code=' + stockCode
    dayPriceHtml = urlopen(dayPriceUrl)
    dayPriceSource = BeautifulSoup(dayPriceHtml.read(), "html.parser")

    dayPricePageNavigation = dayPriceSource.find_all("table", align="center")
    dayPriceMaxPageSection = dayPricePageNavigation[0].find_all("td", class_="pgRR")
    dayPriceMaxPageNum = int(dayPriceMaxPageSection[0].a.get('href')[-3:])

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

                # srCompareWithYesterday = srlists[i].find("img")
                # if (srCompareWithYesterday != None):
                #     incOrdec = srCompareWithYesterday.get("src")
                #     tagspan = srCompareWithYesterday.find("span")
                #     absoluteVariation = tagspan.text
                #     absoluteVariation = (srCompareWithYesterday.find("span").get_text()).strip()  # 부호가 포함되지 않은 전일비
                #
                #     if (incOrdec == "http://imgstock.naver.com/images/images4/ico_down.gif"):
                #         variation = '-' + absoluteVariation
                #     elif (
                #             incOrdec == "http://imgstock.naver.com/images/images4/ico_up.gif" or incOrdec == "http://imgstock.naver.com/images/images4/ico_up02.gif"):
                #         variation = '+' + absoluteVariation
                # else:
                #     variation = '0'

                openingPrice = srlists[i].find_all("td", class_="num")[2].text
                highestPrice = srlists[i].find_all("td", class_="num")[3].text
                lowestPrice = srlists[i].find_all("td", class_="num")[4].text
                volume = srlists[i].find_all("td", class_="num")[5].text

                print("날짜: " + day, end=" ")
                print("종가: " + closingPrice, end=" ")
                # print("전일비: " + variation, end=" ")
                print("시가: " + openingPrice, end=" ")
                print("고가: " + highestPrice, end=" ")
                print("저가: " + lowestPrice, end=" ")
                print("거래량: " + volume)


if __name__ == "__main__" :
    #GetApparatusForeignTradingInfoFromNaver('065450')
    GetStockTradingInfoFromNaver('065450')