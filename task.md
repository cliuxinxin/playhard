https://sjpl.bibliocommons.com/v2/events

针对这个网站我们需要下载到这个网页
然后解析到文件
然后要保存这个网页

我想做一个系统，这个系统有几个核心功能，下载网页，解析网页，数据规整落库
1. 下载网页
1.1 定期调度下载网页
1.2 不同的网页有不同的下载策略，每个网页的翻页机制不一样
1.3 知道自己应该下载到那里就更新完毕
1.4 下载失败需要重试和报警机制
2. 解析网页
2.1 不同的网页有不同的解析策略
2.2 解析的调度，下载完成以后解析最新的数据
2.3 解析失败需要重试和报警机制
3. 数据落库
3.1 落库的调度，解析完成以后落库
3.2 不同的网页有不同的落库策略
3.3 落库失败需要重试和报警机制
4. 先用这个网页来做一个demo
4.1 并且可以扩展到其他的网页

这是取得这个网页的json数据curl：
curl 'https://gateway.bibliocommons.com/v2/libraries/sjpl/events/search?page=2&limit=20&locale=en-US' \
  -H 'accept: application/json' \
  -H 'accept-language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7' \
  -b 'EVENT=app01b; NERF_SRV=nerf17; SRV=app36; _ga=GA1.1.184796718.1749706354; _ga_G99DMMNG39=GS2.1.s1749800401$o3$g0$t1749800401$j60$l0$h0; _ga_F5QPDQX1BM=GS2.1.s1749800401$o3$g0$t1749800401$j60$l0$h0' \
  -H 'dnt: 1' \
  -H 'origin: https://sjpl.bibliocommons.com' \
  -H 'priority: u=1, i' \
  -H 'referer: https://sjpl.bibliocommons.com/' \
  -H 'sec-ch-ua: "Chromium";v="137", "Not/A)Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'