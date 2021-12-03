import argparse
import csv
import datetime
import os
import urllib.request

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta


def main():
    """
    scraping.py's main
    """
    
    args = Parse()
    print("Get Data...")
    dataList = getData(args)
    print("Create CSV...")
    CreateCSV(args, dataList)

def getData(args):
    """
    Download Data from JMA Website

    Args:
        args (argparse): Commandline Arguments

    Returns:
        dataList (list): List of JMA Data

    Note:
        ・風向
          北基準の方位角を示す。ex. 北：０, 東：90, ...
        ・取得データ一覧
          ["日時", "現地気圧", "海面気圧", "降水量", "平均気温", "最高気温", "最低気温",
           "湿度", "平均風速", "最大風速", "最大風向", "日照時間"]
    """

    startDate = datetime.date(int(args.startDate[:4]), int(args.startDate[4:6]),
                              int(args.startDate[6:8]))
    endDate = datetime.date(int(args.endDate[:4]), int(args.endDate[4:6]),
                            int(args.endDate[6:8]))
    date = startDate
    
    dataList = []
    while True:
        print(date)
        url = "http://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?"\
            "prec_no=44&block_no=47662&year=%d&month=%d&day=01&view="%(date.year, date.month)
        
        html = urllib.request.urlopen(url).read()
        # args[1] = lxml, html.parser, xml, html5lib
        soup = BeautifulSoup(html, "lxml")
        
        tbl = soup.find("table", { "class" : "data2_s" })
        
        # table の中身を取得
        for tr in tbl.findAll('tr'):
            dataLineList = []
            tdList = tr.findAll('td')
            
            if len(tdList) == 0:
                continue

            print(type(float(tdList[0].string)))
            # " )"がついていることがあるので削除
            for i_column in range(15):
                if tdList[i_column].string[-1] == ")":
                    tdList[i_column].string = tdList[i_column].string[:-2]

                    
            dataDate = datetime.date(date.year, date.month, int(tdList[0].string))

            # 北基準に方位を数値化
            if tdList[13].string == "北":
                direction = 0
            elif tdList[13].string == "北北東":
                direction = 22.5
            elif tdList[13].string == "北東":
                direction = 45
            elif tdList[13].string == "東北東":
                direction = 67.5
            elif tdList[13].string == "東":
                direction = 90
            elif tdList[13].string == "東南東":
                direction = 112.5
            elif tdList[13].string == "南東":
                direction = 135
            elif tdList[13].string == "南南東":
                direction = 157.5
            elif tdList[13].string == "南":
                direction = 180
            elif tdList[13].string == "南南西":
                direction = 202.5
            elif tdList[13].string == "南西":
                direction = 225
            elif tdList[13].string == "西南西":
                direction = 247.5
            elif tdList[13].string == "西":
                direction = 270
            elif tdList[13].string == "西北西":
                direction = 292.5
            elif tdList[13].string == "北西":
                direction = 315
            elif tdList[13].string == "北北西":
                direction = 337.5
            else:
                break

            # 行リストに各情報を追加
            dataLineList.append(dataDate)
            dataLineList.append(tdList[1].string)
            dataLineList.append(tdList[2].string)
            dataLineList.append(tdList[3].string)
            dataLineList.append(tdList[6].string)
            dataLineList.append(tdList[7].string)
            dataLineList.append(tdList[8].string)
            dataLineList.append(tdList[9].string)
            dataLineList.append(tdList[11].string)
            dataLineList.append(tdList[12].string)
            dataLineList.append(direction)
            dataLineList.append(tdList[16].string)
        
            dataList.append(dataLineList)
        
        date = date + relativedelta(months=1)
        
        if date >= endDate:
            break

    return dataList



def CreateCSV(args, dataList):
    """
    Output the Acquired Data to CSV File

    Args:
        args (argparse): Commandline Arguments
        dataList (list): List of JMA Data
    """
    
    header = ["日時", "現地気圧", "海面気圧", "降水量", "平均気温", "最高気温", "最低気温",
              "湿度", "平均風速", "最大風速", "最大風向", "日照時間"]
    
    with open(args.csvPath, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(header)
        for data in dataList:
            writer.writerow(data)

    return



def Parse():
    """
    Get Commandline Arguments

    Returns:
        args (argparse): Commandline Arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-sd", "--startDate", type=str, default="20200101")
    parser.add_argument("-ed", "--endDate", type=str, default="20210101")
    parser.add_argument("-cp", "--csvPath", type=str, default="./data.csv")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
