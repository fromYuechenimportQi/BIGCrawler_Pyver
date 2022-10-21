from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from lxml import etree
import os
import sys
import time
import requests
import json
from .gsa import make_directory
from tqdm import tqdm
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
}
url = "https://ngdc.cncb.ac.cn/gwh/api/browse"
BASE_PATH = make_directory("gwh")
PAGE_PATH = os.path.join(BASE_PATH, "gwh_accession_nums")


def gwh_accession():
    os.mkdir(PAGE_PATH)
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }
    url = "https://ngdc.cncb.ac.cn/gwh/api/browse"
    start = [i for i in range(0, 12701, 100)]
    draw = [i for i in range(1, 129)]
    summary = []
    with tqdm(total=len(start), desc="Crawling gwh accession") as pbar:
        for ind in range(len(start)):
            data = {"draw": 1, "columns": [{"data": "scientificName", "name": "scientificName", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "commonNames", "name": "commonNames", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "group", "name": "group", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "source", "name": "source", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "accession", "name": "accession", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "genomeRepresentation", "name": "genomeRepresentation", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "assemblyLevel", "name": "assemblyLevel", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "genomeSize", "name": "genomeSize", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {
                "data": "chrCount", "name": "chrCount", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "gcContent", "name": "gcContent", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "releaseDate", "name": "releaseDate", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "dna", "name": "dna", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "gff", "name": "gff", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "rna", "name": "rna", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "cds", "name": "cds", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}, {"data": "protein", "name": "protein", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}], "order": [{"column": 0, "dir": "asc"}], "start": 2, "length": 100, "search": {"value": "", "regex": False}}
            data["draw"] = draw[ind]
            data["start"] = start[ind]
            json_str = json.dumps(data)
            try:
                r = requests.post(url, headers=headers,
                                  data=json_str, timeout=180)
            except Exception as e:
                with open(os.path.join(PAGE_PATH, "errLog.txt"), "a") as f:
                    f.write("%s\n%s\n" % (e, json_str))
                continue
            json_dict = json.loads(r.text)
            file_name = "gwh_accession" + "_" + str(draw[ind]) + ".txt"
            file_name = os.path.join(PAGE_PATH, file_name)
            with open(file_name, "w") as result_file:
                for sub_dic in json_dict["data"]:
                    need_info = sub_dic["primaryId"]
                    summary.append(need_info)
                    result_file.write("%s\n" % (need_info))
            pbar.update(1)

    with open(os.path.join(PAGE_PATH, "gwh_accession_summary.txt"), "w") as f:
        for i in summary:
            f.write("%s\n" % (i))


def get_accesion_from_txt():

    with open(os.path.join(PAGE_PATH, "gwh_accession_summary.txt"), "r") as f:
        acc = f.read().split("\n")
    return acc


def main():
    errlog_path = os.path.join(BASE_PATH, "errLog.txt")
    gwh_result_path = os.path.join(BASE_PATH, "gwh_result.txt")
    # url_lst = ['https://ngdc.cncb.ac.cn/gwh/Assembly/14585/show', 'https://ngdc.cncb.ac.cn/gwh/Assembly/11806/show', 'https://ngdc.cncb.ac.cn/gwh/Assembly/12283/show', 'https://ngdc.cncb.ac.cn/gwh/Assembly/486/show']
    need_info = ['Accession No.', 'Scientific Name', 'Bioproject', 'Biosample',
                 'Released Date', 'Assembly Level', 'Genome Representation', 'Download']
    download_type = ["DNA", "GFF", "RNA", "Protein"]
    gwh_accession()
    acc = get_accesion_from_txt()
    with tqdm(total=len(acc), desc="Get infomations into resultfile") as pbar:
        for acc in acc:
            # for i in url_lst:
            download_dict = {}
            infos = {}
            url = "https://ngdc.cncb.ac.cn/gwh/Assembly/%s/show" % (acc)
            # url = i
            try:
                r = requests.get(url)
            except Exception as e:
                with open("./errorLogUrl.txt", "a") as f:
                    f.write("%s\n%s\n" % (url, e))
                    continue
            soup = BeautifulSoup(r.text, "html.parser")
            dt = soup.find_all("dt")
            dd = soup.find_all("dd")
            btn = soup.select("a.btn")

            for ind in range(len(btn)):
                value = btn[ind]["href"]
                key = btn[ind].text.strip()
                download_dict[key] = value
            # print(download_dict)
            for type in download_type:
                if type not in download_dict:
                    download_dict[type] = "NA"
            # print(download_dict)
            if len(dt) == len(dt):
                for ind in range(len(dt)):
                    key = dt[ind].text.strip()
                    # print(key)
                    if key.startswith("Accession No") or key.startswith("Scientific Name") or key.startswith("Bioproject") or key.startswith("Biosample") or key.startswith("Released Date") or key.startswith("Assembly Level") or key.startswith("Genome Representation"):
                        value = dd[ind].text.replace(
                            "\n", "").replace("\r", "").strip()
                        infos[key] = value
                    else:
                        continue
            else:
                with open("erroLog.txt", "a") as f:
                    f.write("%s\n%s\n" % (url, "dt == dd => False"))
                continue
            infos["Download"] = download_dict

            for need in need_info:
                if need not in infos:
                    with open(errlog_path, "a") as f:
                        f.write("%s\n%s\n" % (url, "KeyError"))
                    break

            else:
                if infos["Genome Representation"].startswith("Partial"):
                    temp_str = infos["Genome Representation"]
                    infos["Genome Representation"] = temp_str[0:temp_str.find(
                        " ")+1] + temp_str[temp_str.find(" ")+1:].replace(" ", "")
                if infos["Assembly Level"].startswith("Draft"):
                    temp_str = infos["Assembly Level"]
                    infos["Assembly Level"] = temp_str[0:temp_str.find(
                        "t")+2] + temp_str[temp_str.find("g"):]
                with open(gwh_result_path, "a") as f:
                    for need in need_info:
                        if need == "Download":
                            f.write("%s\t%s\t%s\t%s\n" % (
                                infos[need]["DNA"], infos[need]["GFF"], infos[need]["RNA"], infos[need]["Protein"]))
                        else:
                            f.write("%s\t" % (infos[need]))
            pbar.update(1)


if __name__ == "__main__":
    main()
