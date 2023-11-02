import math
import os
import re
from datetime import datetime
from typing import Union
import chardet
import requests

from baiduspider.util import convert_time


class BaseSpider(object):
    def __init__(self) -> None:
        """所有爬虫的基类

        此类包括了常用的util和自定义方法，继承自`object`。
        """
        super().__init__()
        self.spider_name = "BaseSpider"
        self.headers = {}

    def _format(self, string: str) -> str:
        """去除字符串中不必要的成分并返回

        Args:
            string (str): 要整理的字符串

        Returns:
            str: 处理后的字符串
        """
        text_to_replace = ("\xa0", "\u2002""\u3000")
        string = string.strip()
        for text in text_to_replace:
            string = string.replace(text, "")
        return string

    def _remove_html(self, string: str) -> str:
        """从字符串中去除HTML标签

        Args:
            string (str): 要处理的字符串

        Returns:
            str: 处理完的去除了HTML标签的字符串
        """
        pattern = re.compile(r"<[^*>]+>", re.S)
        removed = pattern.sub("", string)
        return removed

    def _minify(self, html: str) -> str:
        """压缩HTML代码

        Args:
            html (str): 要压缩的代码

        Returns:
            str: 压缩后的HTML代码
        """
        return html.replace("\u00a0", "")

    def _get_response(
        self, url: str, proxies: dict = {}, encoding: str = None
    ) -> str:
        """获取网站响应，并返回源码

        Args:
            url (str): 要获取响应的链接
            proxies (dict): 代理相关设置
            encoding (Union[str, None]): 目标网页编码

        Returns:
            str: 获取到的网站HTML代码
        """
        if 'baijiahao.baidu.com' in url:
            self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
            self.headers['cookie'] = 'BIDUPSID=3150F28F040A5B09D525851D9A76D350; PSTM=1686110160; BAIDUID=E2B64AB1A0A5859312BA02058C1172C4:FG=1; BDUSS=R5SGYyQkNXYk5sN35PZDZMekdxQkhpS1NEaEZCeVpDdnpWYUdwZm5UZC1HOEprSVFBQUFBJCQAAAAAAAAAAAEAAAAViWCOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH6OmmR-jppkem; BDUSS_BFESS=R5SGYyQkNXYk5sN35PZDZMekdxQkhpS1NEaEZCeVpDdnpWYUdwZm5UZC1HOEprSVFBQUFBJCQAAAAAAAAAAAEAAAAViWCOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH6OmmR-jppkem; MCITY=-289%3A; H_WISE_SIDS=234020_216846_213357_214793_110085_244728_254835_261720_262146_236312_265881_266371_267372_265615_256302_267074_259033_268029_259642_268235_269904_267066_256739_270460_270517_264423_270547_271173_263618_269297_271321_271482_270102_271813_256154_271254_234296_234208_272284_267596_272613_260335_267559_273161_273120_273146_273266_273248_273300_273369_273400_273392_271157_273518_272641_271147_273670_272766_264170_270186_272262_273734_273164_274080_273931_274141_273918_273045_273598_272694_274293_274300_272319_274385_272560_274420_274767_274763_274779_274854_274857_274846_270158_273981_275067_267806_267548_273922_275167_274333_275211_275148_272332_274894_269286_275770_273491_275018_275826_275865_275939_275970_276089_269610_276202_276250_274283_274502_276196_276312_276332_276147; H_WISE_SIDS_BFESS=234020_216846_213357_214793_110085_244728_254835_261720_262146_236312_265881_266371_267372_265615_256302_267074_259033_268029_259642_268235_269904_267066_256739_270460_270517_264423_270547_271173_263618_269297_271321_271482_270102_271813_256154_271254_234296_234208_272284_267596_272613_260335_267559_273161_273120_273146_273266_273248_273300_273369_273400_273392_271157_273518_272641_271147_273670_272766_264170_270186_272262_273734_273164_274080_273931_274141_273918_273045_273598_272694_274293_274300_272319_274385_272560_274420_274767_274763_274779_274854_274857_274846_270158_273981_275067_267806_267548_273922_275167_274333_275211_275148_272332_274894_269286_275770_273491_275018_275826_275865_275939_275970_276089_269610_276202_276250_274283_274502_276196_276312_276332_276147; BAIDUID_BFESS=E2B64AB1A0A5859312BA02058C1172C4:FG=1; ZFY=sJKy43X2pHpU6LU:BZz9vM3PewiwRTpcLgM:AQMM662m0:C; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; PSINO=3; delPer=0; BDRCVFR[C0p6oIjvx-c]=I67x6TjHwwYf0; H_PS_PSSID=39396_39420_39592_39524_39497_39565; BA_HECTOR=21812lah0k2l0kah0gahah021ik6hcd1q; ab_sr=1.0.1_NzU3OTUyMDMzYjlmN2VkM2VhOWMzMjM4NDc1NWI1NTE1M2E2OGNkZDJhMDMwYTY3NzQxYjVhODc3NjcyMzJlMDNmZDc1ZjYxZGM0YzI2Mjg0ZDcwODA4YzU5N2E2ZDIxYmJjYjYzODM0MDFjMmVhMWJlZWI4NjE0ZjBmY2U2MGFmOTE5MTRmMDYwOWVmNTU4Yjk4ZTFhMzI0YTdjZDk1Yg=='
        response = requests.get(url, headers=self.headers, proxies=proxies, timeout=10)
        if encoding:
            response.encoding = encoding
            return response.text
        # 如果响应中没有指定编码，使用chardet来检测编码
        # if not response.encoding:
        #     response.encoding = response.apparent_encoding
        # if not response.encoding:
        #     response.encoding = chardet.detect(response.content)["encoding"]
        content = bytes(response.text, response.encoding).decode("utf-8")
        return content

    def _handle_error(self, err: Exception, parent="", cause="") -> None:
        if not err:
            return None
        if int(os.environ.get("DEBUG", 0)):
            raise err
        else:
            print(
                f"\033[33mWARNING: An error occurred while executing function {parent}.{cause}, "
                "which is currently ignored. However, the rest of the parsing process is still being executed normally. "
                "This is most likely an inner parse failure of BaiduSpider. For more details, please set the environment "
                "variable `DEBUG` to `1` to see the error trace and open up a new issue at https://github.com/BaiduSpider/"
                "BaiduSpider/issues/new?assignees=&labels=bug%2C+help+wanted&template=bug_report.md&title=%5BBUG%5D.\033[0m"
            )
            # 错误日志中文输出
            # print(f'\n\033[1;31m警告：在执行函数{parent}.{cause}时发生了一个错误，并且已被忽略。尽管如此，剩余的解析过程仍被正常执行。'
            #     '这很有可能是一个BaiduSpider内部错误。请将环境变量`DEBUG`设为`1`并查看Traceback。'
            #     '请在https://github.com/BaiduSpider/BaiduSpider/issues/new?assignees=&labels=bug%2C+help+wanted&template=bug_report.md'
            #     '&title=%5BBUG%5D%20%E6%AD%A4%E5%A4%84%E5%A1%AB%E5%86%99%E4%BD%A0%E7%9A%84%E6%A0%87%E9%A2%98 提交一个新的issue。\033[31;m')
            return None

    def _convert_time(self, time_str: str, as_list: bool = False) -> Union[datetime, bool]:
        """转换有时间差的汉字表示的时间到`datetime.datetime`形式的时间

        Args:
            time_str (str): 要转换的字符串
            as_list (bool): 是否以列表形式返回

        Returns:
            datetime: 转换后的`datetime.datetime`结果
        """
        return convert_time(time_str, as_list)

    def _reformat_big_num(self, t: str, r: str = "") -> int:
        delta = 1
        if "万" in t:
            delta = 10000
        elif "亿" in t:
            delta = 100000000
        return int(float(t.replace(r, "").replace("万", "").replace("亿", "")) * delta)

    def _calc_pages(self, tot: int, per: int) -> int:
        return 1 if tot / per < 0 else math.ceil(tot / float(per))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Spider {self.spider_name}>"

    def __str__(self) -> str:  # pragma: no cover
        return self.__repr__()
