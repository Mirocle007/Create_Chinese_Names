说明：
1. mySpider.py为本人写的一个爬虫类，其他新的爬虫类继承后可以重用里面的一些方法
	1. 包括随机获取代理（调用了自己写的MyProxy类），随机获取UserAgent（调用了自己写的MyUserAgent）
	2. 方法包括：
		获取网页，解析网页，写入网页等基本操作
2. myproxy.py为本人写的一个自动获取代理IP的爬虫文件，能够检测有无proxy.txt（包括了代理IP的文件），如果没有，则爬取最新的代理IP，并用于爬虫类
3. myUserAgent.py为从useragent自动获取一个随机的useragent
 