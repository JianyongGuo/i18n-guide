# I18N Checker 介绍






|  分类   | 规则描述  | 分级标准  |   
|  ----  | ----  |  ----  |
| I18N 展示格式  | 用户看到的时间、货币展示格式适配各国本地化风格  |   P1    |   
| I18N 禁用函数  | 可能会造成时间、货币等数值错误的类型，主要包含几大类：<br/>  - Date and Time <br/>  - Encoding <br/>  - String Operation <br/>  - Sort and Compare <br/>  - Formating         |   P0    |   
| I18N 硬编码类  | 某些参数、文案硬编码，无法横向扩展到其他国家         |   P1    |   
| 118N 资源引用  | 某些页面、html、jpg等直接引用，需要改造成i18n形式         |  P2      |   
| 自定义类   | 各公司、各业务自定义的规则，比如禁用某些函数、组件、参数错误等         |   -    |   




# I18N 禁用函数
[进度表](https://cooper.didichuxing.com/docs/sheet/2199863708862)


## 时间类

【时区相关】
- 修改默认时区
- 获取默认时区
- 获取某个Date对象的时区名称
- 获取某个时间的utcoffset



【时间戳格式化】
- 时间戳 —》字符串，不带时区的，类似 time.Format("yyyy-MM-dd", nowtime)
- 时间戳 —》字符串，带时区的，类似 time.Format("yyyy-MM-dd", "Asia/Shanghai", nowtime)
- 字符串 -》时间戳，不带时区的，类似 time.Parse()
- 字符串 -》时间戳，带时区的，类似 time.ParseInLocation()
- 使用什么pattern可以把时间戳分别转换为 "2022-11-29 17:27:39"， "2022/11/29 17:27:46"


【日期格式化】
- Date对象 —》字符串，不带时区的，类似 Date.Format("yyyy-MM-dd", nowtime)
- Date对象 —》字符串，带时区的，类似 Date.Format("yyyy-MM-dd", "Asia/Shanghai")
- 字符串 -》Date对象，不带时区的，类似 ParseTimeToDate("2022-11-29 17:19:30")
- 字符串 -》Date对象，带时区的，类似 ParseTimeToDate("Asia/Shanghai", "2022-11-29 17:19:21")
- 使用什么pattern可以把Date对象分别转换为 "2022-11-29 17:27:39"， "2022/11/29 17:27:46"
- 不能使用printf类函数拼接字符串， 类似fmt.Sprintf("%v-%v-%v %v:%v:%v", year, month, day, hour, mintue, second)
- 不能用字符串加号拼接时间，类似 time_format = year + "-" + month + "-" + day + " " + hour + ":" + mintue + ":" + second



【时间运算】
- 计算两个时间间隔多久，类似time.Since、time.Until、time.Duation
- 如何计算7天后时间，类似 AddDate(0, 0, 7)
- 自己用时间戳计算7天后，类似 newtime = now + 86400 * 7


【日期和时间戳】
- Date对象 转换为时间戳，类似 Date().ToUnix()
- 时间戳转换为日期对象， 类似new Date(timestamp)
- 带时区的转换方式，类似Date().InLocation("Asia/Shanghai").ToUnix()


【日历相关】
- 计算某个时间戳是周几
- 计算当前时间是几号
- 获取周一
- 获取某月1号
- 判断是不是周末、周中



## 货币类
- 货币格式化函数，类似 money_format(locale, money)


## 语言类
- 修改默认语言配置
- 获取默认语言配置
- 国家硬编码， if "BR"... if "CN"... 

