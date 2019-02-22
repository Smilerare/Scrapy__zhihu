import requests
from lxml import etree
import pymysql

conn = pymysql.connect(host="localhost",port=3306,user='root',passwd="645270052", db="mysql", charset="utf8")
cursor = conn.cursor()

#爬取西刺的免费ip代理存入mysql
def crawl_ips():
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"}
    for i in range(1,10):
        r = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        r.encoding = r.apparent_encoding
        html = etree.HTML(r.text)
        all_item = html.xpath('//tr[@class="odd"] | //tr[@class=""]')
        ip_list = []
        for item in all_item:
            ip = item.xpath('./td[2]/text()')[0]
            port = item.xpath('./td[3]/text()')[0]
            type = item.xpath('./td[6]/text()')[0]
            speed_str = item.xpath('./td[7]/div/@title')[0]
            speed = speed_str.split('秒')[0]
            ip_list.append((ip, port, type, speed))
        for ip_info in ip_list:
            is_exsit = cursor.execute('select ip from proxy where ip="%s"'%ip_info[0])#判断ip是否已经存在
            if not is_exsit:
                cursor.execute(
                    "insert proxy(ip, port, type, speed) VALUES('{0}', '{1}',' {2}', '{3}')".format(
                        ip_info[0], ip_info[1], ip_info[2],ip_info[3]
                    )
                )
                conn.commit()

class GetIP(object):
     #从数据库中删除无效的ip
    def delete_ip(self, ip):
            delete_sql = "delete from proxy where ip='{0}'".format(ip)
            cursor.execute(delete_sql)
            conn.commit()
            return True

    #判断ip是否可用
    def judge_ip(self, ip, port):
            http_url = "http://www.baidu.com"
            proxy_url = "http://{0}:{1}".format(ip, port)
            try:
                proxy_dict = {
                    "http":proxy_url,
                }
                response = requests.get(http_url, proxies=proxy_dict)
            except Exception as e:
                print ("invalid ip and port")
                self.delete_ip(ip)
                return False
            else:
                code = response.status_code
                if code >= 200 and code < 300:
                    print ("effective ip")
                    return True
                else:
                    print  ("invalid ip and port")
                    self.delete_ip(ip)
                    return False

    #从数据库中随机获取一个可用的ip
    def get_random_ip(self):
        random_sql = "SELECT ip, port FROM proxy ORDER BY RAND() LIMIT 1"
        result = cursor.execute(random_sql)
        for ip_info in result.fetchone():
            ip = ip_info[0]
            port = ip_info[1]
            judge_re = self.judge_ip(ip, port)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()
print (crawl_ips())
if __name__ == "__main__":
    get_ip = GetIP()
    get_ip.get_random_ip()