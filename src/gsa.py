from urllib import response
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from lxml import etree
import os
import sys
import time
import requests
from tqdm import tqdm
def make_directory(dirname):

    cwd = os.getcwd()  
    dir= "\\%s\\"%(dirname) if sys.platform == "win32" or sys.platform == "win64" else "/%s/"%(dirname)
    path= cwd + dir 
    try:
        os.mkdir(path)
    except:
        now = time.ctime()[4:].replace(" ","_").replace(":","-")
        if sys.platform == "win32" or sys.platform == "win64":
            dir = "\\%s_%s\\"%(dirname,now)
        else:
            dir = "/%s_%s/"%(dirname,now)
        path = cwd + dir
        os.mkdir(path)
    return path

def get_CRA_from_GSA():

    print("Get CRA accession number from CRA!")

    accession_numbers = []
    total_page = "" 
    ## Request headers and GSA_URL
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    } 
    GSA_URL = "https://ngdc.cncb.ac.cn/gsa/browse"
    
    ## mkdir to store cra
    path = make_directory("cra_accession_result")
    post = {
        "pageSize":"50",
        "pageNo":"1"
    }
    ## Get pages

    try:
        r = requests.post(GSA_URL,post,timeout=180,headers=headers)
    except Exception as e:
        print(e)
        print("Error: Can not get total pages!! Try again!")
        return -1
    soup = BeautifulSoup(r.text, 'html.parser')
    all_footer_info = soup.select(".total")

    for info in all_footer_info:
        if info.text.lower().startswith("page") and "/" in info.text:
            info = info.text.strip()
            total_page = info[info.find("/")+1:]
            break
    try:
        pages = [i for i in range(1,int(total_page)+1)]
    except Exception as e:
        print("Error: can not get correct page info")
        return -1
    pages = list(map(lambda x:str(x),pages))
    with tqdm(total=len(pages),desc="Crawling CRA") as pbar:
        for page in pages:
            post["pageNo"]  = page
            try:
                r = requests.post(GSA_URL,post,timeout=180)
                soup = BeautifulSoup(r.text, 'html.parser')
            except Exception as e:
                with open(path+"erroLog.txt","a") as f:
                    f.write("%s\n%s\n%s\n"%("get CRA accession wrong!",post,e))
                continue
            
            file_name = path + "cra_page" + page + ".txt"
            # print("----------%s------------"%(page))
            with open(file_name,"w") as f:
                for i in soup.select("td>a"):
                    CRA = ""
                    if i.text.startswith("CRA"):
                        CRA = i.text
                        # print(CRA)
                        accession_numbers.append(CRA)
                        f.write("%s\n"%(CRA))
            pbar.update(1)
    summary_file_name = path + "cra_summary.txt"
    with open(summary_file_name,"w") as summary_file:
        for accesion in accession_numbers:
            summary_file.write("%s\n"%(accesion))

    print("All accession number completed!")

    return summary_file_name




#Get BioProject Release data and FTP, and return a dict
def get_bioP_relD_FTP(soup):  
    infos_needed = soup.findAll("span")
    infos_arr = []
    infos_dic = {}
    
    for i in infos_needed:
        textInfo = i.text
        if textInfo.startswith("BioProject:")  or textInfo.startswith("Release date:") or textInfo.startswith("FTP"):
            infos_arr.append(textInfo)
            
    for index in range(len(infos_arr)):
        str_to_split = ":"
        if infos_arr[index].startswith("FTP"):
            str_to_split = "："
        ind = infos_arr[index].find(str_to_split)
        key = infos_arr[index][:ind].strip()
        value = infos_arr[index][ind+1:].strip()
        if value:
            infos_dic[key] = value
    bioproject = infos_dic["BioProject"].split("/")[0].strip()
    infos_dic["BioProject"] = bioproject
    infos_dic["FTP"] += "/"
    return infos_dic

def get_all_page(soup):
    total_page = 0

    li_content = soup.select("li.total")
    for i in li_content:
        if i.text.startswith("Page") and i.text.find('/') != -1:
            page = i.text[i.text.find('/')+1:].strip()
    
    total_page = int(page)
    
    return total_page

def write_page(path,experiments_dict):
    with open(path+"gsa_result.txt","a") as f:
        for experiments, runs in experiments_dict.items():
            for run in runs:
                for run_info in run:
                    f.write("%s\t"%(run_info))
                for experiment_info in experiments:
                    f.write("%s\t"%(experiment_info))
                f.write("\n")

def get_cra_summary(cra_summary_file):
    ret_list = []
    with open(cra_summary_file,"r") as f:
        all_info = f.read().split('\n')
    ret_list = [i for i in all_info]
    return ret_list

def main(mode="auto",filename=None,acc=[]):
    if mode == "manual":
        if filename:
            with open(filename,"r") as f:
                temp = f.read().strip().split('\n')
            for i in temp:
                if not i.startswith("CRA"):
                    print(f"WARNNING: {i} is not an invalid CRA accession")
                    temp.pop(temp.index(i))
            cra_list = temp
        else:
            for i in acc:
                if not i.startswith("CRA"):
                    print(f"WARNNING: {i} is not an invalid CRA accession")
                    acc.pop(temp.index(i))
            cra_list = acc
    else:
        cra_list = get_cra_summary(get_CRA_from_GSA())
    path = make_directory("gsa_result")
    indx = 0
    with tqdm(total=len(cra_list),desc=f"Crawling {cra_list[indx]} info:") as pbar:
        for cra in cra_list:
            pbar.set_description(f"Crawling {cra_list[indx]} info:")
            #print(indx)
            url = "https://ngdc.cncb.ac.cn/gsa/browse/"
            url += cra
            post = {
                "pageSize":"50",
                "pageNo":"1",
            }
            #print("I am getting all informations of %s"%(cra))
            try:
                r = requests.post(url,post,timeout=180)
            except Exception as e:
                with open(path+"erroLog.txt","a") as f:
                    f.write("%s\t%s\n%s\n"%(cra,post,e))
                continue
            soup = BeautifulSoup(r.text, 'html.parser')
            pages = get_all_page(soup)
            page_list = [i for i in range(1,pages+1)]
            page_list = list(map(lambda x:str(x),page_list))

            other_infos = get_bioP_relD_FTP(soup)
            for current_page in page_list:
                experiments_dict = {}
                post["pageNo"] = current_page
                try:
                    r = requests.post(url,post,timeout=180)
                except Exception as e:
                    with open(path+"erroLog.txt","a") as f:
                        f.write("%s\t%s\n%s\n"%(cra,post,e))
                    continue
                soup = BeautifulSoup(r.text, 'html.parser')
                try:
                    tr_list = soup.find_all("tr")
                    for tr_tmp in tr_list:
                        tr_class = tr_tmp.attrs['class'][0]
                        tr_content = tr_tmp.text
                        if tr_class == 'experiment':
                            # last_exp = tr_tmp.find("a").attrs['href'].split("/")[-1]
                            experiment_list = list(filter(lambda x:x,tr_content.strip().split("\n")))
                            experiment_list.append(other_infos["BioProject"])
                            experiment_list.append(other_infos["Release date"])
                            experiment_tuple = tuple(experiment_list)
                            experiments_dict.setdefault(experiment_tuple, [])
                        elif tr_class == 'runTr':
                            # run_id = tr_tmp.find("a").attrs['href'].split("/")[-1]
                            run_list = list(filter(lambda x:x and not x.startswith('\t'),tr_content.strip().split("\n")))
                            for ind in range(len(run_list)):
                                if run_list[ind].startswith("File:"):
                                    post_fix = run_list[ind].split(":")[1].strip()
                                    run_list[ind] = other_infos["FTP"] + post_fix
                            experiments_dict[experiment_tuple].append(run_list)
                    write_page(path,experiments_dict)
                except Exception as e:
                    with open("erroLog.txt","a") as f:
                        f.write("%s\t%s\n%s\n"%(cra,post,e))
                    continue
            indx += 1
            pbar.update(1)
            
    return experiments_dict


#main()

