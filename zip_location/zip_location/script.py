import pandas as pd
import re

def read_zip(file_name):
   # read zipcode data 
   name =["code","zip5","zip7","yomi1","yomi2","yomi3","name1","name2","name3","other1","other2","other3","other4","other5","reason"]
   zipcode = pd.read_csv(file_name, names=name, encoding='cp932')
   
   zipcode = zipcode[ ["zip7","yomi3","name1","name2","name3"] ]
   # extract section
   pat1 = r"（.+）$"
   pattern1 = re.compile(pat1)
   zipcode["大字"] = zipcode["name3"].replace(pattern1, '', regex=True)
   
   # Extract section number 
   pat1 = r"(\d+-\d+ﾁﾖｳﾒ)"
   pattern1 = re.compile(pat1)
   zipcode["丁目"] = zipcode["yomi3"].str.extract(pattern1)
   
   return zipcode

def read_df(file_name):
   df = pd.read_csv(file_name, encoding='cp932')
   #  Remove the section number  
   pat2 = r"[一二三四五六七八九十壱弐参拾百千万萬億兆〇]+丁目$"
   pattern2 = re.compile(pat2)
   df["大字"] = df["大字町丁目名"].replace(pattern2, '', regex=True)
   #丁目の番号は大字町丁目コードの下３桁
   df["丁目"] = df["大字町丁目コード"] % 100
   return df

def compute_lat_lng(zipcode,df):
   # Compute the latitude and longitude for each zipcode using the government database (named df)
   count =0
   lat_column, lng_column = [ ],[ ]
   for row in zipcode.itertuples():
       try:
           cyoume = row.丁目.split("-")
           #print(cyoume)
           start, finish = int(cyoume[0]), int(cyoume[1][:-4]) #start cyoume and finish cyoume 
       except:
           start, finish = 0, 0
       extract = df[ (df["都道府県名"] == row.name1) & (df["市区町村名"]==row.name2) & (df["大字"]==row.大字)]
       if len(extract)==0:
           extract = df[ (df["都道府県名"] == row.name1) & (df["市区町村名"]==row.name2) & (df["大字"]=="大字"+row.大字)]
           
       #print( count, len(extract), start, finish )
       lat_list, lng_list = [ ],[ ]
       if len(extract)>0: #compute the median point 
           for row2 in extract.itertuples():
               if start<finish: #cyoume has a range
                   if start<=row2.丁目 and row2.丁目 <=finish:
                       lat_list.append(row2.緯度)
                       lng_list.append(row2.経度)
               else:
                   lat_list.append(row2.緯度)
                   lng_list.append(row2.経度)
           lat_column.append( sum(lat_list)/len(lat_list) )
           lng_column.append( sum(lng_list)/len(lng_list) )
       else:
           #no coreesponding row in df
           lat_column.append(0.)
           lng_column.append(0.)
       count+=1
   zipcode["latitude"] = pd.Series(lat_column)
   zipcode["longitude"] = pd.Series(lng_column)
   return zipcode

def main():
    print('test')
    print(read_zip('./KEN_ALL.CSV'))
