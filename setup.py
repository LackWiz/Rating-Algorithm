from email import header
import os
import csv
def checkFolderPath():
    try:
        f = open('bs_path.txt', 'r')
        bsPath = f.read()
    except FileNotFoundError:
        print('Enter Beat Saber custom songs folder:')
        # TODO: validate path
        #bsPath = askdirectory()
        bsPath = input()
        if bsPath[-1] not in ['\\', '/']:  # Checks if song path is empty
            bsPath += '/'
        f = open('bs_path.txt', 'w')
        f.write(bsPath)
    finally:
        f.close()
    return bsPath

def writeToExcel(folderName,fileName,headerList,dataList):
    excelFileName = os.path.join(f"{folderName}/{fileName} export.csv")
    try:
        x = open(excelFileName, 'w', newline="", encoding='utf8')
    except FileNotFoundError:
        print(f'Making {folderName} Folder')
        os.mkdir(folderName)
        x = open(excelFileName, 'w', newline="")
    finally:
        writer = csv.writer(x)
        writer.writerow(headerList)
        writer.writerows(dataList)
        x.close()

def writeSingleToExcel(folderName,fileName,headerList,data):
    excelFileName = os.path.join(f"{folderName}/{fileName} export.csv")
    try:
        x = open(excelFileName, 'w', newline="", encoding='utf8')
    except FileNotFoundError:
        print(f'Making {folderName} Folder')
        os.mkdir(folderName)
        x = open(excelFileName, 'w', newline="")
    finally:
        writer = csv.writer(x)
        writer.writerow(headerList)
        writer.writerow(data.returnList())
        x.close()
