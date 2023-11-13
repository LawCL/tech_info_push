import pandas as pd
import xlsxwriter
import logging
import random
from time import sleep
from selenium import webdriver
import requests
from bs4 import BeautifulSoup

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# 配置日志
logging.basicConfig(filename='bug.log',
                    filemode='w',
                    datefmt='%a %d %b %Y %H:%M:%S',
                    format='%(asctime)s %(filename)s %(levelname)s:%(message)s',
                    level=logging.INFO)

try:
    #laptop資料重整
    df = pd.read_excel("DELL_NB.xlsx",index_col=0)
    df = df.T
    df.reset_index(drop = True, inplace = True)
    
    my_header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}
    
    #Dell_NB 資料檢驗/補充
    DNB = 0
    for DNB in range(len(df["Brand"])):        
        if len(str(df["Ports & Slots"][DNB])) < 20:
            print(DNB)
            delay = random.uniform(0.5, 5.0)
            sleep(delay)
            url_dell = df["Web Link"][DNB] + "#techspecs_section"
            option = webdriver.ChromeOptions()
            option.add_argument("headless")
            dell_dock = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=option)
            dell_dock.get(url_dell)
            sleep(2)
            dell_dock.execute_script("document.body.style.zoom='50%'")
            sleep(2)
            dell_dock.execute_script("window.scrollTo(0, document.body.scrollHeight*0.5);")
            sleep(2)
            soup = BeautifulSoup(dell_dock.page_source,"html.parser")
            dell_dock.quit()
            one_data = soup.select("ul.cf-hero-bts-list > li")
            Ports_Slots=""
            for one in one_data:
                two_data = one.select("p")
                if "Power Supply" in two_data[0].text:
                    Power_Supply = two_data[0].text.strip()
                if "Ports" in two_data[0].text or "Slots" in two_data[0].text or "PORTS" in two_data[0].text:
                    two_data = one.select(" p > a")
                    Ports_Slots = two_data[0]["data-description"]
                    Ports_Slots = Ports_Slots.replace("<br>","\n")
                    Ports_Slots = Ports_Slots.replace("<ul>","")
                    Ports_Slots = Ports_Slots.replace("</ul>","")
                    Ports_Slots = Ports_Slots.replace("<li>"," ")
                    Ports_Slots = Ports_Slots.replace("</li>","\n")
                    Ports_Slots = Ports_Slots.replace("<span>"," ")
                    Ports_Slots = Ports_Slots.replace("</span>","")
            No_select_data = soup.select("li.mb-2")
            for no_data in No_select_data:
                No_select_title = no_data.select("div")
                No_select_Data = no_data.select("p")
                if "Ports" in No_select_title[0].text or "Slots" in No_select_title[0].text or "PORTS" in No_select_title[0].text:
                    Ports_Slots = Ports_Slots + "\n" + No_select_Data[0].text
            df["Ports & Slots"][DNB] = Ports_Slots
           
    df = df.T
    
    #載入其他公司資料進行合併
    
    df_1 = pd.read_excel("HP_NB.xlsx",index_col="Unnamed: 0")
    df_2 = pd.read_excel("Lenovo_NB.xlsx",index_col="Unnamed: 0")
    df_1 = df_1.T
    df_2 = df_2.T
    df_1.reset_index(drop = True, inplace = True)
    df_2.reset_index(drop = True, inplace = True)
    
    
    re_load = 0
    # 檢查Lenovo_NB的缺值(HWD/Weight)並補齊
    for re_load in range(len(df_2)):
        if str(df_2['Ports & Slots'][re_load]) != "Web No Data":
            if str(df_2['Depth(mm)'][re_load]) == "nan":
                print(re_load)
                delay = random.uniform(1.0, 5.0)
                sleep(delay)
                data_url = df_2['Web Link'][re_load] 
                Lenovo_NB_data = requests.get(data_url + "#features", headers=my_header)
                if Lenovo_NB_data.status_code==200:
                    L_NB_soup = BeautifulSoup(Lenovo_NB_data.text,'html.parser')
                    #商品詳細網址            
                    NB_deta_url = L_NB_soup.select("div.system_specs_top > a")
                delay = random.uniform(0.5, 5.0)
                sleep(delay)
                option = webdriver.ChromeOptions()
                option.add_argument("headless")
                Lenovo_NB_data_deta = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=option)
                Lenovo_NB_data_deta.get("https://www.lenovo.com" + NB_deta_url[0]['href']+"#features")
                Lenovo_NB_data_deta.execute_script("document.body.style.zoom='50%'")
                
                L_NB_deta_soup = BeautifulSoup(Lenovo_NB_data_deta.page_source,'html.parser')
                NB_deta_n = L_NB_deta_soup.select("tr.item")
                j = 0
                H=[]
                W=[]
                for j in range(len(NB_deta_n)):
                    NB_deta_Name = NB_deta_n[j].select("th")
                    NB_deta_d = NB_deta_n[j].select("p")
                    k = 0
                    D = []
                    for k in range(len(NB_deta_d)):
                        D.append(NB_deta_d[k].text)
                    D = "\n".join(D)
                    if "Dimensions" in NB_deta_Name[0].text:
                        Dim = D.split("/")
                        D_cut = 0
                        for D_cut in range(len(Dim)):
                            if len(Dim[D_cut].split("mm")) > 2:
                                Dim_1 = Dim[D_cut].split("mm")
                                if len(Dim_1[2]) < 2:
                                    Dim_1 = Dim[D_cut].split("x")
                                    H = Dim_1[0].split(":")[-1].split("-")[-1].split("at")[-1].split("~")[-1].split("covers")[-1].split("chassis")[-1].split("as")[-1].split("–")[-1].split("aluminum")[-1].split("mm")[0].strip()
                                    W = Dim_1[1].split("mm")[0].strip()
                                    De = Dim_1[2].split("as")[-1].split("-")[-1].split("–")[-1].split("~")[-1].split("mm")[0].strip()
                                else:
                                    H = Dim_1[0].split("x")[-1].split(":")[-1].split("-")[-1].split("at")[-1].split("~")[-1].split("covers")[-1].split("chassis")[-1].split("as")[-1].split("–")[-1].split("aluminum")[-1].split("mm")[0].strip()
                                    W = Dim_1[1].split("x")[-1].split("mm")[0].strip()
                                    De = Dim_1[2].split("x")[-1].split("as")[-1].split("-")[-1].split("–")[-1].split("~")[-1].split("mm")[0].strip()
                                if "W x D x H" in NB_deta_Name[0].text:
                                    df_2['Height(mm)'][re_load] = De
                                    df_2['Width(mm)'][re_load] = H
                                    df_2['Depth(mm)'][re_load] = W
                                else:
                                    df_2['Height(mm)'][re_load] = H
                                    df_2['Width(mm)'][re_load] = W
                                    df_2['Depth(mm)'][re_load] = De
                            elif "mm" in Dim[D_cut] and "inches" in Dim[D_cut]:
                                Dim = D.split("(")
                                hwd = 0
                                for hwd in range(len(Dim)):
                                    if "mm" in Dim[hwd]:
                                        H = Dim[hwd].split(":")[-1].split("x")[0].strip()
                                        W = Dim[hwd].split(":")[-1].split("x")[1].strip()
                                        De = Dim[hwd].split(":")[-1].split("x")[2].split("as")[-1].strip()
                                    if "W x D x H" in NB_deta_Name[0].text:
                                        df_2['Height(mm)'][re_load] = De
                                        df_2['Width(mm)'][re_load] = H
                                        df_2['Depth(mm)'][re_load] = W
                                    else:
                                        df_2['Height(mm)'][re_load] = H
                                        df_2['Width(mm)'][re_load] = W
                                        df_2['Depth(mm)'][re_load] = De
                            elif "mm" in Dim[D_cut] and (len(Dim[D_cut].split("mm")[0]) > len(Dim[D_cut].split("mm")[1])):
                                H = Dim[D_cut].split("(mm")[0].split("x")[0].strip()
                                W = Dim[D_cut].split("(mm")[0].split("x")[1].strip()
                                De = Dim[D_cut].split("(mm")[0].split("x")[2].strip()
                                if "W x D x H" in NB_deta_Name[0].text:
                                    df_2['Height(mm)'][re_load] = De
                                    df_2['Width(mm)'][re_load] = H
                                    df_2['Depth(mm)'][re_load] = W
                                else:
                                    df_2['Height(mm)'][re_load] = H
                                    df_2['Width(mm)'][re_load] = W
                                    df_2['Depth(mm)'][re_load] = De  
                    elif "Weight" in NB_deta_Name[0].text:
                        W_cut = D.split("at")[-1].split("from")[-1].split("than")[-1].split("Starting")[-1].split("g")
                        if len(W_cut) > 1:
                            if str(W_cut[0])[-1] == "K" or str(W_cut[0])[-1] == "k":
                                # 
                                if "<" in W_cut[0]: 
                                    Wei = W_cut[0].split("K")[0].split("k")[0].split("/")[-1].split("(")[-1].split("<")[-1]
                                    Wei = float(Wei)
                                    symbol = "<"
                                elif "Up" in W_cut[0]:
                                    Wei = W_cut[0].split("K")[0].split("k")[0].split("/")[-1].split("(")[-1].split("to")[-1]
                                    Wei = float(Wei)
                                    symbol = ">"
                                else:
                                    Wei = W_cut[0].split("K")[0].split("k")[0].split("/")[-1].split("(")[-1].split("<")[-1]
                                    Wei = float(Wei)
                            else:
                                if "<" in W_cut[0]: 
                                    Wei = W_cut[0].split("/")[-1].split("(")[-1].split("<")[-1]
                                    Wei = round(float(Wei)/1000,2)
                                    symbol = "<"
                                else:
                                    Wei = W_cut[0].split("/")[-1].split("(")[-1].split("<")[-1]
                                    Wei = round(float(Wei)/1000,2)
                        else:
                            Wei = ""
                        df_2['Weight(kg)'][re_load] = Wei                
    df_1 = df_1.T   
    df_2 = df_2.T
    df = df.merge(df_1,how = "outer", left_index=True, right_index=True)
    df = df.merge(df_2,how = "outer", left_index=True, right_index=True)
    
    #desktop資料重整
    df1 = pd.read_excel("DELL_DT.xlsx",index_col=0)
    df1 = df1.T
    df1.reset_index(drop = True, inplace = True)
    df1 = df1.T
    #載入其他公司資料進行合併
    df1_1 = pd.read_excel("HP_DT.xlsx",index_col="Unnamed: 0")    
    df1_2 = pd.read_excel("Lenovo_DT.xlsx",index_col="Unnamed: 0")
    df1_1 = df1_1.T
    df1_2 = df1_2.T
    df1_1.reset_index(drop = True, inplace = True)
    df1_2.reset_index(drop = True, inplace = True)
    
    
    # 檢查Lenovo_DT的缺值(HWD/Weight)並補齊
    re_load = 0
    
    for re_load in range(len(df1_2)):
        if str(df1_2['Ports & Slots'][re_load])!= "Web No Data":
            if str(df1_2['Depth(mm)'][re_load]) == "nan":
                print(re_load)
                delay = random.uniform(1.0, 5.0)
                sleep(delay)
                data_url = df1_2['Web Link'][re_load] 
                Lenovo_NB_data = requests.get(data_url + "#features", headers=my_header)
                if Lenovo_NB_data.status_code==200:
                    L_NB_soup = BeautifulSoup(Lenovo_NB_data.text,'html.parser')
                    #商品詳細網址            
                    NB_deta_url = L_NB_soup.select("div.system_specs_top > a")
                delay = random.uniform(0.5, 5.0)
                sleep(delay)
                option = webdriver.ChromeOptions()
                option.add_argument("headless")
                Lenovo_NB_data_deta = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=option)
                Lenovo_NB_data_deta.get("https://www.lenovo.com" + NB_deta_url[0]['href']+"#features")
                Lenovo_NB_data_deta.execute_script("document.body.style.zoom='50%'")
                
                L_NB_deta_soup = BeautifulSoup(Lenovo_NB_data_deta.page_source,'html.parser')
                NB_deta_n = L_NB_deta_soup.select("tr.item")
                j = 0
                H=[]
                W=[]
                for j in range(len(NB_deta_n)):
                    NB_deta_Name = NB_deta_n[j].select("th")
                    NB_deta_d = NB_deta_n[j].select("p")
                    k = 0
                    D = []
                    for k in range(len(NB_deta_d)):
                        D.append(NB_deta_d[k].text)
                    D = "\n".join(D)
                    if "Dimensions" in NB_deta_Name[0].text:
                        Dim = D.split("/")
                        D_cut = 0
                        for D_cut in range(len(Dim)):
                            if len(Dim[D_cut].split("mm")) > 2:
                                Dim_1 = Dim[D_cut].split("mm")
                                if len(Dim_1[2]) < 2:
                                    Dim_1 = Dim[D_cut].split("x")
                                    H = Dim_1[0].split(":")[-1].split("-")[-1].split("at")[-1].split("~")[-1].split("covers")[-1].split("chassis")[-1].split("as")[-1].split("–")[-1].split("aluminum")[-1].split("mm")[0].strip()
                                    W = Dim_1[1].split("mm")[0].strip()
                                    De = Dim_1[2].split("as")[-1].split("-")[-1].split("–")[-1].split("~")[-1].split("mm")[0].strip()
                                else:
                                    H = Dim_1[0].split("x")[-1].split(":")[-1].split("-")[-1].split("at")[-1].split("~")[-1].split("covers")[-1].split("chassis")[-1].split("as")[-1].split("–")[-1].split("aluminum")[-1].split("mm")[0].strip()
                                    W = Dim_1[1].split("x")[-1].split("mm")[0].strip()
                                    De = Dim_1[2].split("x")[-1].split("as")[-1].split("-")[-1].split("–")[-1].split("~")[-1].split("mm")[0].strip()
                                if "W x D x H" in NB_deta_Name[0].text:
                                    df1_2['Height(mm)'][re_load] = De
                                    df1_2['Width(mm)'][re_load] = H
                                    df1_2['Depth(mm)'][re_load] = W
                                else:
                                    df1_2['Height(mm)'][re_load] = H
                                    df1_2['Width(mm)'][re_load] = W
                                    df1_2['Depth(mm)'][re_load] = De
                            elif "mm" in Dim[D_cut] and "inches" in Dim[D_cut]:
                                Dim = D.split("(")
                                hwd = 0
                                for hwd in range(len(Dim)):
                                    if "mm" in Dim[hwd]:
                                        H = Dim[hwd].split(":")[-1].split("x")[0].strip()
                                        W = Dim[hwd].split(":")[-1].split("x")[1].strip()
                                        De = Dim[hwd].split(":")[-1].split("x")[2].split("as")[-1].strip()
                                    if "W x D x H" in NB_deta_Name[0].text:
                                        df1_2['Height(mm)'][re_load] = De
                                        df1_2['Width(mm)'][re_load] = H
                                        df1_2['Depth(mm)'][re_load] = W
                                    else:
                                        df1_2['Height(mm)'][re_load] = H
                                        df1_2['Width(mm)'][re_load] = W
                                        df1_2['Depth(mm)'][re_load] = De
                            elif "mm" in Dim[D_cut] and (len(Dim[D_cut].split("mm")[0]) > len(Dim[D_cut].split("mm")[1])):
                                H = Dim[D_cut].split("(mm")[0].split("x")[0].strip()
                                W = Dim[D_cut].split("(mm")[0].split("x")[1].strip()
                                De = Dim[D_cut].split("(mm")[0].split("x")[2].strip()
                                if "W x D x H" in NB_deta_Name[0].text:
                                    df1_2['Height(mm)'][re_load] = De
                                    df1_2['Width(mm)'][re_load] = H
                                    df1_2['Depth(mm)'][re_load] = W
                                else:
                                    df1_2['Height(mm)'][re_load] = H
                                    df1_2['Width(mm)'][re_load] = W
                                    df1_2['Depth(mm)'][re_load] = De  
                    elif "Weight" in NB_deta_Name[0].text:
                        W_cut = D.split("at")[-1].split("from")[-1].split("than")[-1].split("Starting")[-1].split("g")
                        if len(W_cut) > 1:
                            if str(W_cut[0])[-1] == "K" or str(W_cut[0])[-1] == "k":
                                # 
                                if "<" in W_cut[0]: 
                                    Wei = W_cut[0].split("K")[0].split("k")[0].split("/")[-1].split("(")[-1].split("<")[-1]
                                    Wei = float(Wei)
                                    symbol = "<"
                                elif "Up" in W_cut[0]:
                                    Wei = W_cut[0].split("K")[0].split("k")[0].split("/")[-1].split("(")[-1].split("to")[-1]
                                    Wei = float(Wei)
                                    symbol = ">"
                                else:
                                    Wei = W_cut[0].split("K")[0].split("k")[0].split("/")[-1].split("(")[-1].split("<")[-1].split("From")[-1]
                                    Wei = float(Wei)
                            else:
                                if "<" in W_cut[0]: 
                                    Wei = W_cut[0].split("/")[-1].split("(")[-1].split("<")[-1]
                                    Wei = round(float(Wei)/1000,2)
                                    symbol = "<"
                                else:
                                    Wei = W_cut[0].split("/")[-1].split("(")[-1].split("<")[-1]
                                    Wei = round(float(Wei)/1000,2)
                        else:
                            Wei = ""
                        df1_2['Weight(kg)'][re_load] = Wei
    
    # 檢查HP_DT
    re_load = 0
    for re_load in range(len(df1_1)):
        if str(df1_1['Ports & Slots'][re_load]) != "Web No Data":
            if str(df1_1['Processor'][re_load]) == "Nan" and str(df1_1['Graphics Card'][re_load]) == "Nan" and str(df1_1['Memory'][re_load]) == "Nan":
                print(re_load)
                Processor = "Nan"
                GC = "Nan"
                Memory = "Nan"
                data_url = df1_1['Web Link'][re_load]
                option = webdriver.ChromeOptions()
                option.add_argument("headless")
                HP_DT_data = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=option)
                HP_DT_data.get(data_url)
                sleep(2)
                L_DT_soup = BeautifulSoup(HP_DT_data.page_source,'html.parser')
                L_DT_data_n = L_DT_soup.select("li.Typography-module_root__eQwd4.Typography-module_bodyS__DBLtm.Typography-module_responsive__iddT7")
                L_DT_data_n_date = L_DT_data_n[1].text
                L_DT_data_n_date = L_DT_data_n_date.split("+")
                df1_1['Processor'][re_load] = L_DT_data_n_date[0]
                df1_1['Graphics Card'][re_load] = L_DT_data_n_date[1]
                df1_1['Memory'][re_load] = L_DT_data_n_date[2]
                       
            if str(df1_1['Official Price'][re_load]) == "Nan":
                print(re_load)
                Price = "Nan"
                data_url = df1_1['Web Link'][re_load]
                option = webdriver.ChromeOptions()
                option.add_argument("headless")
                HP_DT_data = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=option)
                HP_DT_data.get(data_url)
                sleep(2)
                L_DT_soup = BeautifulSoup(HP_DT_data.page_source,'html.parser')
                L_DT_data_n = L_DT_soup.select("div.Typography-module_root__eQwd4.Typography-module_boldL__LZR-5.PriceBlock-module_hasActiveDeal__W4zIr.Typography-module_responsive__iddT7")
                if len(L_DT_data_n) <1:
                    L_DT_data_n = L_DT_soup.select("div.Typography-module_root__eQwd4.Typography-module_boldL__LZR-5.Typography-module_responsive__iddT7")
                HP_DT_data.quit()
                if len(L_DT_data_n) >0:           
                    Price = L_DT_data_n[0].text
                    Price = Price.replace("$","")
                df1_1['Official Price'][re_load] = Price
            if str(df1_1['Height(mm)'][re_load]) == "nan" or str(df1_1['Processor'][re_load]) == "Nan" or str(df1_1['Graphics Card'][re_load]) == "Nan":
                print(re_load)
                data_url = df1_1['Web Link'][re_load]
                option = webdriver.ChromeOptions()
                option.add_argument("headless")
                HP_DT_data = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=option)
                HP_DT_data.get(data_url)
                sleep(2)
                L_DT_soup = BeautifulSoup(HP_DT_data.page_source,'html.parser')
                L_DT_data_n = L_DT_soup.select("div.Spec-module_spec__71K6S > div.Spec-module_innerLeft__Z13zG > p")
                L_DT_data_d_ack = L_DT_soup.select("div.Spec-module_spec__71K6S > div.Spec-module_innerRight__4TTuE")
                L_DT_specs = L_DT_soup.select("div.Container-module_root__luUPH.Container-module_container__jSUGk > div.Footnotes-module_item__LOUR3 > div")
                HP_DT_data.quit()
                specs_data = []
                W,D,H,Weight_kg = "No_Data","No_Data","No_Data","No_Data"
                if len(L_DT_specs) > 0:
                    L_DT_specs_list = L_DT_specs[-1].select("span")        
                    if len(L_DT_specs_list) >0:
                        for specs in L_DT_specs_list:
                            specs_data.append(specs.text)
                j=0            
                for j in range(len(L_DT_data_n)):
                    L_DT_data_d = L_DT_data_d_ack[j].select("div.Spec-module_valueWrapper__DTxWC > p.Typography-module_root__eQwd4.Typography-module_bodyM__XNddq.Spec-module_value__9FkNI.Typography-module_responsive__iddT7 > span")
                    #抓取特徵內容
                    N_D = L_DT_data_d[0].text
                    if "[" in N_D and "]" in N_D:
                        N_Dnum = N_D.split("[")[-1].split("]")[0]
                        num = 0
                        for num in range(len(N_Dnum.split(','))):
                            sp_num = 0
                            for sp_num in range(len(specs_data)):
                                if N_Dnum.split(',')[num] in specs_data[sp_num]:
                                    N_D = N_D.replace(N_Dnum.split(',')[num], specs_data[sp_num].split("]")[-1])             
                    if L_DT_data_n[j].text =="Dimensions (W X D X H)":
                        Dim = (N_D).split("x")
                        W = round(float(Dim[0].strip())*25.4,2)
                        D = round(float(Dim[1].strip())*25.4,2)
                        H = round(float(Dim[2].split("in")[0].strip())*25.4,2)
                    elif L_DT_data_n[j].text =="Weight":
                        Weight_kg = round(float(N_D.split("lb")[0].strip())*0.4536,2)            
                df1_1['Height(mm)'][re_load] = H
                df1_1['Depth(mm)'][re_load] = D
                df1_1['Width(mm)'][re_load] = W
                df1_1['Weight(kg)'][re_load] = Weight_kg
    
    df1_1 = df1_1.T
    df1_2 = df1_2.T
    df1 = df1.merge(df1_1,how = "outer", left_index=True, right_index=True)
    df1 = df1.merge(df1_2,how = "outer", left_index=True, right_index=True)    
    
    #docking資料重整
    df2 = pd.read_excel("DELL_Dock.xlsx",index_col="Unnamed: 0")
    
    #載入其他公司資料進行合併
    df2_1 = pd.read_excel("HP_Dock.xlsx",index_col="Unnamed: 0")
    df2_2 = pd.read_excel("Lenovo_docking.xlsx",index_col="Unnamed: 0")
    df2 = df2.merge(df2_1,how = "outer", left_index=True, right_index=True)
    df2 = df2.merge(df2_2,how = "outer", left_index=True, right_index=True)
       
    #分別對合併完的資料特徵進行重新排序
    df = df.T
      
    #排序
    df = df[["Type","Brand","Model Name","Official Price","Ports & Slots","Camera","Display","Primary Battery","Processor","Graphics Card","Hard Drive","Memory","Operating System","Audio and Speakers","Height(mm)","Width(mm)","Depth(mm)","Weight(kg)","WWAN","NFC","FPR_model","FPR",'Power Supply',"Web Link"]]
    
    df1 = df1.T      
    #排序
    df1 = df1[["Type","Brand","Model Name","Official Price","Ports & Slots","Display","Processor","Graphics Card","Hard Drive","Memory","Operating System","Audio and Speakers","Height(mm)","Width(mm)","Depth(mm)","Weight(kg)",'Power Supply',"Web Link"]]
    
    df2 = df2.T
    df2 = df2[["Type","Brand","Model Name","Official Price","Ports & Slots","Power Supply","Weight(kg)","Web Link"]]
    
    df = df.T.fillna('NA')
    df1 = df1.T.fillna('NA')
    df2 = df2.T.fillna('NA')
        
    # #儲存資料
    writer = pd.ExcelWriter('data(new)/Data_products_total.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='laptop', index=True,header = False)
    df1.to_excel(writer, sheet_name='desktop', index=True,header = False)
    df2.to_excel(writer, sheet_name='docking', index=True,header = False)
    writer.save()
  
except Exception as bug:
    # 捕获并记录错误日志
    logging.error(f"An error occurred: {str(bug)}", exc_info=True)
