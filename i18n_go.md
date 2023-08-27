[[_TOC_]]

<a id="1"></a>

# 1. I18N 敏感函数

<a id="1.1"></a>

## 1.1. 时间类

### CASE: 时区相关/ 业务测试需覆盖到夏令时国家

```
// 有夏令时的 (举例几个)
美国
墨西哥 (2023年后取消了)
智利
澳大利亚
...

// 没有夏令时的 (举例几个)
中国: Asia/Shanghai
格林尼治: UTC
...
```

### CASE: 时区相关/不能一直用默认时区

```
// reason
所有时区、时间操作都必须明确指定timezone，不应该一直使用一个默认时区
```

```
// bad: 指定北京时区,无法扩展到其他国家
beijing_timezone := time.FixedZone("Beijing Time", 3600 * 8)

// good: (for 其他公司), 使用请求参数中的时区
timezone, _ := time.LoadLocation(request.UserTimeZone)

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 
now_time, _ := datetimeutil.FormatByCityId(local, city_id, timestamp, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")
```

```yaml
checker_rule:
  reg: .*time.FixedZone\(.*
  alert_msg: '不应该一直使用一个默认时区, 推荐:使用用户请求参数中的时区'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时区相关/ 不能指定某个特定的时区

```
// reason
不应该hardcode指定某个特定时区, 应该使用用户请求中的时区
```

```
// bad
location, err := time.LoadLocation("Asia/Shanghai")

// good: (for 其他公司), 使用请求参数中的时区
timezone, _ := time.LoadLocation(request.UserTimeZone)
```

```yaml
checker_rule:
  reg: time.LoadLocation\(".*"
  alert_msg: '不应该hardcode指定某个特定时区; 推荐:应该使用用户请求中的时区'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时区相关/ 时间转换时未指定时区

```
// reason
未指定时区就使用默认时区, 可能会出现错误,应该明确指定使用的时区
```

```
// bad
time.Now().Format("2006-01-02 15:04:05")

// good: (for 其他公司), 明确指定timezone
time.Now().In(timezone).Format("2006-01-02 15:04:05")

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 用city_id处理
datetimeutil.FormatByCityId(local, city_id, timestamp, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")
```

```yaml
checker_rule:
  reg: time.Unix((?!\.In\().)*Format\(
  alert_msg: '未明确指定时区,使用的是UTC时区,可能会出错; 推荐: 明确指定timezone'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时区相关/ 不建议获取并操作utc_offset

```
// reason
一个地区的utc_offset是会变化的,比如夏令时本质就是把该地区的utc_offset从 GMT-7 切换到 GMT-6
```

```
// bad
name, offset := time.Now().Zone()

// good: (for 其他公司), 任何时候不要使用utc_offset进行操作,可以使用timezone
time.Now().In(timezone).Format("2006-01-02 15:04:05")

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注 utc_offset, 用city_id处理 
datetimeutil.FormatByCityId(local, city_id, timestamp, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")
```

```yaml
checker_rule:
  reg: time\.(Now|Unix).*.Zone\(\)
  alert_msg: ''
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时区相关/ timezone应该使用完整格式,不能使用简写

```
// reason
简写方式会出现冲突, 比如 CST 不同机器上表示的不一样
 - CST中原标准时间，Chungyuan Standard Time
 - CST澳洲中部时间，Central Standard Time (Australia)
 - CST北美中部时区，Central Standard Time (North America)
 - CST古巴标准时间，Cuba Standard Time
```

```
// bad
time.LoadLocation("CST")

// good: 使用完整的时区名称
time.LoadLocation("Asia/Shanghai")
```

```yaml
checker_rule:
  reg: time.*Location.*"(CST|MST|PST|EDT|CDT)"
  alert_msg: ''
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时区相关/ 不能使用UTC+8, GMT+8等格式的时区

```
// reason
一个国家的时区可能会变化, 夏令时本质就是从 GMT-7切换到GMT-6
UTC和GMT+8这两个除外
```

```
// bad
time.LoadLocation("GMT-8")

// good: 使用完整的时区名称
time.LoadLocation("Asia/Shanghai")
```

```yaml
checker_rule:
  reg: .*"(GMT|UTC)(-|\+)\d+".*
  alert_msg: ''
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时区相关/ 不能按国家粒度进行时间计算,必须按时区粒度

```
// reason
一个国家可能有多个时区
中国是单时区国家,但是诸如巴西,澳大利亚等都是多时区国家
举个例子, 西部城市可能是06:00, 东部城市是07:00
```

```
// bad
time.LoadLocation(timezone_map[country])

// good: 使用用户所在地的时区, 而不是国家的时区
time.LoadLocation(request.UserTimeZone)

// 引申
非精确的需求场景,可以使用国家首都时区,业务自己判断因此带来的时间误差
```

```yaml
checker_rule:
  reg: time.LoadLocation\([^(),]*country[^(),]*\)
  alert_msg: ''
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

---

### CASE: 时间转换/ Date转时间戳 必须保证时区数据库是最新版本

```
// reason
时区数据库如果不是最新, 得到的时间戳是错误的
```

```
// bad: 时区数据是旧的, 没有更新时
time.Date(2022, 10, 1, 23,59, 59, 0, timezone).Unix()

// 旧的时区版本 (最新版本 >= 2022g)
Shell Command: head -n 1 /usr/share/zoneinfo/tzdata.zi
version 2016b

// good: 确保/usr/share/zoneinfo是最新的, 更新方式参考...
time.Date(2022, 10, 1, 23,59, 59, 0, timezone).Unix()

// 新的时区版本
Shell Command: head -n 1 /usr/share/zoneinfo/tzdata.zi
version 2022g 
(可能随时更新, 最新数据发布到: https://www.iana.org/time-zones)
```


### CASE: 时间转换/ 时间戳格式化时应该指定timezone或者city_id

```
// reason
不指定timezone时, 得到的时间是UTC时间, 而不是实际local time
假如墨西哥本地是 01:00:00, 如果不指定时区,可能得到 07:00:00, 会发生严重问题
```

```
// bad
time.Now().Format("2006-01-02 15:04:05")

// good: (for 其他公司), 明确指定timezone
time.Now().In(timezone).Format("2006-01-02 15:04:05")

// good: (for 滴滴), 用Elvish SDK解决, 无需timezone, 只需city_id
datetimeutil.FormatByCityId(local, city_id, timestamp, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")
```

```yaml
checker_rule:
  reg: time.Unix((?!\.In\().)*Format\(
  alert_msg: '时间格式化时应该指定timezone或者city_id'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```



### CASE: 时间转换/ Format时 必须保证时区数据库是最新版本

```
// reason
时区数据库如果不是最新, 得到的时间是错误的
```

```
// bad: 时区数据是旧的, 没有更新时
time.Now().In(loc).Format("2006-01-02 15:04:05")
Shell Command: head -n 1 /usr/share/zoneinfo/tzdata.zi
version 2016b

// good: 确保/usr/share/zoneinfo是最新的, 更新方式参考...
time.Date(2022, 10, 1, 23,59, 59, 0, timezone).Unix()
Shell Command: head -n 1 /usr/share/zoneinfo/tzdata.zi
version 2022g 
(可能随时更新, 最新数据发布到: https://www.iana.org/time-zones)
```

### CASE: 时间转换/ time.Date对象应该带时区参数

```
// reason
不带时区, 得到的时间戳和格式化时间都是错误的
```

```
// bad
time.Date(2022, 10, 1, 23,59, 59, 0, nil)

// good: (for 其他公司), 维护各国时间pattern, 比如 map<country, 时间pattern>
timezone, _ := time.LoadLocation("America/Chihuahua")
time.Date(2022, 10, 1, 23,59, 59, 0, timezone)

// good: (for 滴滴), 用Elvish SDK解决, 不使用Date对象, 直接用时间戳转换
datetimeutil.FormatByCityId(local, city_id, timestamp, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")
```

```yaml
checker_rule:
  reg: time.*\.Format\(("2006/01/02 15:04:05"|"02/01/2006 15:04:05"|"15:04:05 2006-01-02"|"15:04:05 2006/01/02"|"01-02-2006 15:04:05"|"01/02/2006 15:04:05"|"1-2-2006 15:04:05"|"2-1-2006 15:04:05")
  alert_msg: 'time.Date对象应该带时区参数'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```




### CASE: 时间反转/ 时间字符串转时间戳时, 应该指定timezone或者city_id

```
// reason
不指定timezone时, 得到的时间是UTC时间, 而不是实际local time
假如墨西哥本地是 01:00:00, 如果不指定时区,可能得到 07:00:00, 会发生严重问题
```

```
// bad
timestamp := time.Parse("2006-01-02 15:04:05", "2022-12-04 18:12:42")

// good: (for 其他公司), 明确指定timezone
timestamp := time.ParseInLocation("2006-01-02 15:04:05", "2022-12-04 18:12:42", timezone)

// good: (for 滴滴), 用Elvish SDK解决, 无需timezone, 只需city_id
timestamp := datetimeutil.GetTimeStampByCityId(local, city_id, time_string)
```

```yaml
checker_rule:
  reg: time.Parse\([^(),]*,[^(),]*\)
  alert_msg: '时间字符串转时间戳时, 应该指定timezone或者city_id'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```


### CASE: 时间运算/ 1天 != 24小时

```
// reason
由于夏令时的缘故, 1天 != 24小时, 1天 != 86400秒
有可能是23小时, 也有可能是25小时
全球所有国家一般都是在 00:00 到03:00:00切换令时
```

```
// bad: 
seven_days_later := time.Now().Unix() + 3600 * 60 * 7

// good: (for 其他公司), 使用time.Date包, 但前提也是确保时区数据是最新的
time.Now().AddDate(0, 0, 7).Unix()
```

### CASE: 时间运算/ 定时任务的幂等性

```
// reason
由于夏令时的缘故, 1天 != 24小时, 1天 != 86400秒
```

```
// bad: 有可能有2个 01:30, 需要业务自己处理 可重入性(幂等性)
if (now_time == "01:30:00") {
    go start_task()
}

// bad: 有可能没有 01:30, 需要业务自己回放数据, 补录数据
if (now_time == "01:30:00") {
    go start_task()
}

// good: 低要求的业务
一般夏令时在 00:00 到03:00 之间
可以把定时任务设置在本地时间的3点以后, 可一定程度避免问题, 但是也不是绝对的

// good: 高要求的业务, 比如金融等
1. 必须保证定时任务的幂等性, 也就是允许任务重复执行
2. 必须有机制检查任务是否执行, 没有执行的话, 可以在当天 06:00 补偿执行
```

```yaml
checker_rule:
  reg: time[^ ]* *== *("0[1,2]:[0-5]\d:\d\d"|"0[1,2]:[0-5]\d")
  alert_msg: '定时任务尽量避开0点到3点, 高精度业务需要自己保证幂等性和补偿机制'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间运算/ 未来时间不能用86400方式计算

```
// reason
由于夏令时的缘故, 1天 != 24小时, 1天 != 86400秒
```

```
// bad: 未来时间, 1天 != 86400秒
seven_days_later := time.Now().Unix() + 86400 * 7

// bad: 过去时间
seven_days_later := time.Now().Unix() - 3600 * 60 * 7

// good: (for 其他公司), 使用time.Date包, 但前提也是确保时区数据是最新的
time.Now().AddDate(0, 0, 7).Unix()

// good: (for 滴滴), 用Elvish SDK解决
datetimeutil.AddDate(city_id, timestamp, years, months, days)
datetimeutil.AddDateAndSetHour(cityId, timestamp, add_years, add_months, add_days, set_hour, set_mintue, set_second)
```

```yaml
checker_rule:
  reg: (=|return).*(time|date).*(\+|\-).*\b86400\b *\*
  alert_msg: '未来时间不能用86400方式计算'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间运算/ 不能用86400, 判断是否是一天的开始

```
// reason
由于夏令时的缘故, 1天 != 24小时, 1天 != 86400秒
```

```
// bad: 1天 != 86400秒
is_day_begin := time.Now()/86400.0

// good: (for 其他公司), 使用time.Date包, 但前提也是确保时区数据是最新的
if time.Now().Hour() == 0 && time.Now().Minute() == 0 && time.Now().Second() == 0 {
    println("是一天的开始")
}
```

```yaml
checker_rule:
  reg: time.(Now|Unix).*/ *(86400|SECOND[A-Z_]*DAY|DAY[A-Z_]*SECOND)
  alert_msg: '不能用86400, 判断是否是一天的开始'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间运算/ 计算两个时间的间隔多久

```
// reason
02:00 和 01:00 相差可能是 0秒, 而不是3600秒
```

```
// bad:
time_interval := (hour1 - hour2) * 3600 

// good: (for 其他公司), 使用time.Date包, 但前提也是确保时区数据是最新的
time1.Sub(time2)
```

```yaml
checker_rule:
  reg: \([^ ]*hour[^ ]* *- *[^ ]*hour[^ ]* *\) *\* *(3600|SECOND[A-Z_]*HOUR|HOUR[A-Z_]*SECOND)
  alert_msg: '不能用小时直接相减计算时间差'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间运算/ 关于未来时间、过去时间需注意

```
// reason
未来时间、过去时间有多个细分的需求场景，业务需要明确自己想要什么
```

```
// good: 未来时间需求场景, Elvish提供了完整的功能集合

// 场景1： N天后的，当前时刻
// 比如现在是1号2:00，求7天后的2:00
Elvish.datetimeutil. AddDate(cityId int64, timestamp int64, years int64, months int64, days int64) (toTimestamp int64, err error)

// 场景2：N天后的，指定时刻
比如现在是1号2:00，求7天后的23点（也就是8号23点）
Elvish.datetimeutil. AddDateAndSetHour(cityId int64, timestamp int64, add_years, add_months, add_days, 
                                                            set_hour, set_mintue, set_second int64) (toTimestamp int64, err error)

// 场景3：同一天的，某个时间
比如给定时间戳1644219835，求当天的3:00:00
Elvish.datetimeutil. SomeTimeInSameDay(cityId int64, timestamp int64, hour, mintue, second int64) (toTimestamp int64, err error)

// 场景4：某个时刻，此后的8小时
Elvish.datetimeutil. AddSeconds(timestamp int64, seconds int64) (toTimestamp int64, err error)

// 场景5：两个时间，相差多久
Elvish.datetimeutil. TimeDiff(cityId int64, from string, to string, pattern string) (seconds int64, err error)
```



### CASE: 时间转换/ 时间戳和Date转换时,必须指定时区

```
// reason
```

```
// bad:
date := time.Now().Date()
day := time.Now().Day()
hour := time.Now().Hour()
mintue := time.Now().Mintue()
second := time.Now().Second()
week_day := time.Now().Weekday()
iso_week := time.Now().ISOWeek()

// good: 必须指定时区
date := time.Now().In(timezone).Date()
day := time.Now().In(timezone).Day()
hour := time.Now().In(timezone).Hour()
mintue := time.Now().In(timezone).Mintue()
second := time.Now().In(timezone).Second()
week_day := time.Now().In(timezone).Weekday()
iso_week := time.Now().In(timezone).ISOWeek()
```

```yaml
checker_rule:
  reg: time.(Now|Unix)\([^()]*\)\.(Date|Day|Hour|Mintue|Second|Weekday|ISOWeek)\(\)
  alert_msg: '时间戳和Date转换时,必须指定时区'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```



### CASE: 日历相关/ 获取一天的开始时间
```
// reason
获取一天开始、一周开始、一月开始，都需要指定用户请求的timezone，否则得到的日期可能是错的
```

```
// bad: currentTime.Day() 没有指定时区
currentTime := time.Now()
dayStart := time.Date(currentTime.Year(), currentTime.Month(), currentTime.Day(), 0, 0, 0, 0, currentTime.Location()).Unix()

// good: for 其他公司
loc, err := time.LoadLocation(userTimezone)
currentTime := time.Now().In(loc)
dayStart := time.Date(currentTime.Year(), currentTime.Month(), currentTime.Day(), 0, 0, 0, 0, loc).Unix()

// good: for 滴滴，使用Elvish提供的calendar接口
dayStart := calendarutil.DayStartTime(cityId int64, timestamp int64)
```

```yaml
checker_rule:
  reg_up3: time\.(Now|Unix)((?!\.In\().)*
  reg: time\.Date\(((?!\.In\().)*\.Year\(\),((?!\.In\().)*\.Month.*((?!\.In\().)*\.Day.*0.*0.*0.*0.*
  reg_down3: 
  alert_msg: 'time.Day() Year() Month() 等函数需要指定时区 time.In(location).Day()'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```


### CASE: 日历相关/ 获取一天的结束时间
```
// reason
获取一天开始、一周开始、一月开始，都需要指定用户请求的timezone，否则得到的日期可能是错的
```

```
// bad: currentTime.Day() 没有指定时区
currentTime := time.Now()
dayStart := time.Date(currentTime.Year(), currentTime.Month(), currentTime.Day(), 23, 59, 59, 0, currentTime.Location()).Unix()

// good: for 其他公司
currentTime := time.Now()
dayStart := time.Date(currentTime.In(userTimezone).Year(), currentTime.In(userTimezone).Month(), currentTime.In(userTimezone).Day(), 0, 0, 0, 0, userTimezone).Unix()

// good: for 滴滴，使用Elvish提供的calendar接口
dayStart := calendarutil.DayStartTime(cityId int64, timestamp int64)
```

```yaml
checker_rule:
  reg_up3: time\.(Now|Unix)((?!\.In\().)*
  reg: time\.Date\(((?!\.In\().)*\.Year\(\),((?!\.In\().)*\.Month.*((?!\.In\().)*\.Day.*23.*59.*59.*0.*
  reg_down3: 
  alert_msg: 'time.Day() Year() Month() 等函数需要指定时区 time.In(location).Day()'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```




### CASE: 日历相关/ 获取一周的开始时间戳

```
// reason
获取一天开始、一周开始、一月开始，都需要指定用户请求的timezone，否则得到的日期可能是错的
```

```
// bad: time.Now() 需要指定时区
now := time.Now()
offset := int(time.Monday - now.Weekday())
if offset > 0 {
    offset = -6
}
weekStartDate := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Local).AddDate(0, 0, offset).Unix()

// good: for 其他公司，使用time.Now().In(loc)
loc, err := time.LoadLocation(user.Timezone)
if err != nil {
    return nil, err
}
now := time.Now().In(loc)
offset := int(time.Monday - now.Weekday())
if offset > 0 {
    offset = -6
}
weekStart := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Local).AddDate(0, 0, offset).Unix()

// good: for 滴滴，使用Elvish calendar库
Elvish.calendarutil. WeekStartTime(cityId int64, timestamp int64) 
```

```yaml
checker_rule:
  reg_up3: time\.(Now|Unix)((?!\.In\().)*
  reg: offset.*=.*time.Monday *- *.*Weekday
  alert_msg: '获取一天开始、一周开始、一月开始，都需要指定用户请求的timezone，否则得到的日期可能是错的'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```


### CASE: 日历相关/ 判断是否属于同一天
```
// reason
不能对 86400取模进行判断
```

```
// bad:  不能对 86400取模进行判断，1天 ！=86400秒
day1 := timestamp_1 % 86400
day2 := timestamp_2 % 86400
if day1 == day2 {
     println("属于同一天")  
}

// good: 转换成time.Date 然后判断
day1 := time.Unix(timestamp_1, 0).In(loc)
day2 := time.Unix(timestamp_2, 0).In(loc)
if day1.Day() == day2.Day() {
     println("属于同一天")  
}
```

```yaml
checker_rule:
  reg: time.*% *(86400|SECOND[A-Z_]*DAY|DAY[A-Z_]*SECOND)
  alert_msg: '不能对86400取模判断是哪一天，因为有的国家1天 != 86400秒'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```



# 2. I18N展示格式

<a id="2.1"></a>

## 2.1 时间类

### CASE: 时间展示风格/ 不能使用 Sprintf 拼接 时间格式

```
// reason: 不同国家，时间展示规则不同:
CN(中国): 2019-12-31 01:59:59
BR(巴西): 31/12/2019 01:59:59
CO(哥伦比亚): 31/12/2019, 01:59:59 am
AU(澳大利亚): 31/12/2019, 1:59:59 am
EG(埃及): 2019/11/11، 10:11 ص
```

```
// bad: 使用 Sprint + %v或者%s拼接，期望得到 2022-11-24 17:03:44
now_time, _ := fmt.Sprintf("%v-%v-%v %v:%v:%v", year, month, day, hour, mintue, second)

// good: (for 滴滴), 用Elvish SDK解决
接口：now_time, _ := datetimeutil.FormatByCityId(local, city_id, timestamp, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")
例子: now_time, _ := datetimeutil.FormatByCityId("zh-CN", 500000001, 1899999999, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")

// good: (for 其他公司), 使用 time.In(timezone).Format()
timezone, _ := time.LoadLocation("America/Tijuana")
now_time:= time.Now().In(timezone).Format("2006-01-02 15:04:05")
```

```yaml
checker_rule:
  reg: .*"%v-%v-%v %v:%v:%v.*
  alert_msg: "不能自定义时间格式, 慎用:time.Format(2006-01-02 15:04:05) --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

<br/>

### CASE: 时间展示风格/ 不能用 string 加号拼接 时间格式

```
// reason: 不同国家，时间展示规则不同:
CN(中国): 2019-12-31 01:59:59
BR(巴西): 31/12/2019 01:59:59
CO(哥伦比亚): 31/12/2019, 01:59:59 am
AU(澳大利亚): 31/12/2019, 1:59:59 am
```

```
// bad: 使用 string 加号操作符拼接
now_time := year + "-" + month + "-" + day + " " + hour + ":" + mintue + ":" + second

// good: (for 滴滴), 用Elvish SDK解决
now_time, _ := datetimeutil.FormatByCityId(local, city_id, timestamp, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")

// good: (for 其他公司), 使用 time.In(timezone).Format()
timezone, _ := time.LoadLocation("America/Tijuana")
now_time:= time.Now().In(timezone).Format("2006-01-02 15:04:05")
```

```yaml
checker_rule:
  reg: year *\+ *"-" *\+ *month *\+ *"-" *\+ *day *\+ *" " *\+ *hour *\+ *":" *\+ *mintue *\+ *":" *\+ *second
  alert_msg: "不能自己拼接时间格式"
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ Format时使用的Pattern错误

```
// reason
golang不是使用yyyy-MM-dd等 skeleton,而是使用固定的一个时间 "2006-01-02 15:04:05"
```

```
// bad
time.Now().In(loc).Format("yyyy-MM-dd HH:mm:ss")

// good: 使用 "2006-01-02 15:04:05" 格式化
time.Now().In(loc).Format("2006-01-02 15:04:05")
```

```yaml
checker_rule:
  reg: time.*\.Format\(.*"(\d\d\d\d.{1}\d\d.{1}\d\d \d\d:\d\d:\d\d(?<!2006-01-02 15:04:05))"
  alert_msg: '时间pattern错误,应该使用 "2006-01-02 15:04:05"'
  level: P0
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ 时间Pattern不能写死成 "2006-01-02 15:04:05"

```
// reason: 不同国家时间格式不同, 比如:
CN(中国): 2019-12-31 01:59:59
BR(巴西): 31/12/2019 01:59:59
CO(哥伦比亚): 31/12/2019, 01:59:59 am
AU(澳大利亚): 31/12/2019, 1:59:59 am
EG(埃及): 2019/11/11، 10:11
```

```
// bad: 所有国家使用同一个pattern, "2006-01-02 15:04:05"
now_time:= time.Now().In(timezone).Format("2006-01-02 15:04:05")

// good: (for 其他公司) 自己维护map<country, 时间风格>, 具体风格参考CLDR标准
if country == "CN" {
    time.Now().Format("2006-01-02 15:04:05")
}
if country == "BR" {
    time.Now().Format("02/01/2006 15:04:05")
}
if country == "AU" {
    time.Now().Format("02/01/2006 15:04:05 PM")
}

// good: (for 滴滴) 用Elvish SDK解决，elvish自动选择该国最佳风格 (***)
now_time, _ := datetimeutil.FormatByCityId(local, city_id, timestamp, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")
```

### CASE: 时间展示风格/ 不应该定制时间格式

```
// reason
```

```
// bad
time.Now().In(loc).Format("2006/01/02 15:04:05")

// good: (for 其他公司), 维护各国时间pattern, 比如 map<country, 时间pattern>
pattern = time_pattern_map[country]
time.Now().In(loc).Format(pattern)


// good: (for 滴滴), 用Elvish SDK解决, 无需维护pattern, 只需cityid
datetimeutil.FormatByCityId(local, city_id, timestamp, datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, "")
```

```yaml
checker_rule:
  reg: time.*\.Format\(("2006/01/02 15:04:05"|"02/01/2006 15:04:05"|"15:04:05 2006-01-02"|"15:04:05 2006/01/02"|"01-02-2006 15:04:05"|"01/02/2006 15:04:05"|"1-2-2006 15:04:05"|"2-1-2006 15:04:05")
  alert_msg: '不应该定制时间格式, 需要根据CLDR来决定各国时间展示格式'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```


### CASE: 时间段相关/ 时间段风格
```
// reason
时间段间隔时长不同，展示风格不同，需要业务注意
比如间隔秒级、分钟级、小时级、半天级、天级、月级、年级
```

```
// bad: 把两个时间format后结果直接拼接起来, 在手机端的展示效果不是最佳的
time1 := time.Unix(timestamp_1, 0).In(loc).Format("2006-01-02 15:04:05")
time2 := time.Unix(timestamp_2, 0).In(loc).Format("2006-01-02 15:04:05")
time_interval := fmt.Sprintf("%s - %s", time1, time2)

// good: 最佳的时间段展示风格如下 
// 间隔2分钟
s, _ := datetimeutil.IntervalFormat("pt_BR", 52090100, IYYYYMMDDHHMM, 1223228723, 1223228723 + 60*2)
输出结果:
s = 05/10/2008, 12:45 – 12:47

// 间隔2小时
s, _ := datetimeutil.IntervalFormat("pt_BR", 52090100, IYYYYMMDDHHMM, 1223228723, 1223228723 + 3600*2)
输出结果:
s = 05/10/2008, 12:45 – 14:47

// 间隔2天
s, _ := datetimeutil.IntervalFormat("pt_BR", 52090100, IYYYYMMDDHHMM, 1223228723, 1223228723 + 86400*2)
输出结果:
s = 05/10/2008, 12:45 – 07/10/2008, 12:45

// 间隔2月
s, _ := datetimeutil.IntervalFormat("pt_BR", 52090100, IYYYYMMDDHHMM, 1223228723, 1223228723 + 86400*32)
输出结果:
s = 05/10/2008, 12:45 – 06/11/2008, 11:45

// 间隔2年
s, _ := datetimeutil.IntervalFormat("pt_BR", 52090100, IYYYYMMDDHHMM, 1223228723, 1223228723 + 86400*380)
输出结果:
s = 05/10/2008, 12:45 – 20/10/2009, 12:45

// good: for 滴滴, Elvish组件根据时间自动选择最佳风格
Elvish.datetimeutil.IntervalFormat(locale string, cityId int64, intervalStyle IntervaStyle, start int64, end int64)
```

```yaml
checker_rule:
  reg: Sprintf\("%s - %s", *time[^ ]* *time[^ ]*\)
  alert_msg: '时间段格式化需要注意最佳风格'
  level: P2
  exclude: (log|test|nolint|no_lint|no-lint)
```













