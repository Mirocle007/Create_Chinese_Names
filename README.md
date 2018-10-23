# Create_Chinese_Names
one Chinese name generator using RNN
说明：
1. crawl data文件夹用于爬取网络上的名字，主要是基于base_crawl_class，使用的文件为：name_spider.py
2. create_Chinese_names.py为训练模型的主文件
3. use_the_model.py文件演示了如何使用训练好的模型参数
4. utils.py是过程中用到的一些小函数
5. name.txt为爬取到的名字库
6. parameters为训练1500000次网络后得到的参数
