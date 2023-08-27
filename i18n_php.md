[[_TOC_]]

# 1. I18N敏感函数


## 1.1 时间类

### CASE: 时间格式化/时间戳转时间字符串，需要指定时区

```
// reason
所有时区、时间操作都必须明确指定timezone，不应该一直使用一个默认时区
```

```
// bad: 使用默认时区,可能是错误的时间
$sTime = date('Y-m-d H:i:s', $iStartTime);

// good: (for 其他公司), 使用请求参数中的时区
$timezone = $request->getUserTimezone();

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 
$sDateTime = DatetimeUtil::formatByCityID("pt-BR", 1573421371, 55000007, DatetimeUtil::DATE_STYLE_YYMMDD,
            DatetimeUtil::TIME_STYLE_HHMM);
```


### CASE: 时间反解析/时间字符串转换为时间戳，需要指定时区
```
// bad: 使用默认时区,可能是错误的时间
$iTime = strtotime("2022-01-01 00:00:00")

// good: (for 其他公司), 使用请求参数中的时区,并使用intl扩展IntlDateFormatter类
$sTimezone = $request->getUserTimezone();
$formatter = new \IntlDateFormatter($sLocale,
            \IntlDateFormatter::MEDIUM,
            \IntlDateFormatter::MEDIUM,
            $sTimezone,
            \IntlDateFormatter::GREGORIAN,
            "yyyy-MM-dd HH:mm:ss");
$iTimestamp = $formatter->parse("2022-01-01 00:00:00");

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 
$iTimestamp = DatetimeUtil::getTsByPatternAndCityID("es-MX", "2019-11-10 15:29:31", 52110100,
            "yyyy-MM-dd HH:mm:ss");
```

### CASE: 时间计算/计算未来过去时间，涉及天级别的时间，不要自己加减时间戳
```
// reason
由于夏令时的缘故, 1天 != 24小时, 1天 != 86400秒
有可能是23小时, 也有可能是25小时
全球所有国家一般都是在 00:00 到03:00:00切换令时
```

```
// bad: 
$seven_days_later = time() + 3600 * 60 * 7;

// good: (for 其他公司), 使用intl插件里面的IntlCalendar类实现
https://www.php.net/manual/zh/intlcalendar.add.php
$cal = \IntlCalendar::createInstance($sTimezone);
//设置时间
$cal->setTime($iTime * 1000.00);
$cal->add(\IntlCalendar::FIELD_DAY_OF_MONTH, 7);

```

### CASE: 时间运算/ 定时任务的幂等性
```
// reason
由于夏令时的缘故, 1天 != 24小时, 1天 != 86400秒
```

```
// bad: 有可能有2个 01:30, 需要业务自己处理 可重入性(幂等性)
if ($now_time == "01:30:00") {
    start_task();
}

// bad: 有可能没有 01:30, 需要业务自己回放数据, 补录数据
if ($now_time == "01:30:00") {
    start_task();
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




### CASE: 日历相关/获取时间对应的年、月、日、周等日历信息


```
// good:（for 其他公司），使用intl扩展的IntlCalendar类
$cal = \IntlCalendar::createInstance($sTimezone);
$cal->setTime($iTime * 1000.00); 
$dayOfMonth = $cal->get(\IntlCalendar::FIELD_DAY_OF_MONTH);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 用city_id和时间戳即可获取 
$result = CalendarUtil::getCalendarFromTimestampAndCityID($cityID, $iTime);
$month = $result["month"];
$dayOfMonth = $result["dayOfMonth"];
$dayOfWeek = $result["dayOfWeek"];                    

```

### CASE: 时区相关/ 哪些国家有夏令时
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


### CASE: 时区相关/ 不能指定某个特定的时区
```
// reason
不应该hardcode指定某个特定时区, 应该使用用户请求中的时区
```

```
// bad
date_default_timezone_set("Asia/Shanghai");

// good: (for 其他公司), 使用请求参数中的时区
$timezone = $request->getUserTimezone();

```

```yaml
checker_rule:
  reg: date_default_timezone_set\(
  alert_msg: '不应该hardcode指定某个特定时区; 推荐:应该使用用户请求中的时区'
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
$summer = new DateTimeImmutable('2008-06-21', new DateTimeZone('America/New_York'));
echo $summer->getOffset() . "\n";

// good: (for 其他公司), 任何时候不要使用utc_offset进行操作,可以使用timezone
$fmt = datefmt_create(
    'de-DE',
    IntlDateFormatter::FULL,
    IntlDateFormatter::FULL,
    'America/Los_Angeles',
    IntlDateFormatter::GREGORIAN,
    'MM/dd/yyyy'
);
echo datefmt_format($fmt, 0);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注 utc_offset, 用city_id处理 
 $sDateTime = DatetimeUtil::formatByCityID("pt-BR", 1573421371, 55000007, DatetimeUtil::DATE_STYLE_YYMMDD,
            DatetimeUtil::TIME_STYLE_HHMM);
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
date_default_timezone_set("CST");

// good: 使用完整的时区名称
$timezone = "Asia/Shanghai";
```

```yaml
checker_rule:
  reg: date_default_timezone_set.*"(CST|MST|PST|EDT|CDT)"
  alert_msg: ''
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时区相关/ 不建议使用UTC+8, GMT+8等格式的时区
```
// reason
一个国家的时区可能会变化, 夏令时本质就是从 GMT-7切换到GMT-6
```

```
// bad
$timezone = "GMT-8";

// good: 使用完整的时区名称
$timezone = "Asia/Shanghai";
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
$timezone =  $timezone_map[$country];

// good: 使用用户所在地的时区, 而不是国家的时区
$timezone = $reuest->getUserTimezone(); 

// 引申
非精确的需求场景,可以使用国家首都时区,业务自己判断因此带来的时间误差 
```


# 2.I18N展示格式

## 2.1 时间类

### CASE: 时间展示/时间戳转为时间字符串：不能自定义时间格式
```
// reason: 不同国家，时间展示格式不同:
CN(中国): 2019-12-31 01:59:59
BR(巴西): 31/12/2019 01:59:59
CO(哥伦比亚): 31/12/2019, 01:59:59 am
AU(澳大利亚): 31/12/2019, 1:59:59 am
EG(埃及): 2019/11/11، 10:11 ص
```

```
// bad: 使用 - (减号) 分割，如 2006-01-02 15:04:05
$sTime = date('Y-m-d H:i:s', $iStartTime);

// bad: 使用 / (斜杠) 分割，如 2006/01/02 15:04:05
$sTime = date('Y/m/d H:i:s', $iStartTime);

// good for 滴滴: 用Elvish SDK解决，elvish自动选择该国最佳风格 (***)
$sDateTime = DatetimeUtil::formatByCityID("pt-BR", 1573421371, 55000007, DatetimeUtil::DATE_STYLE_YYMMDD,
            DatetimeUtil::TIME_STYLE_HHMM);


// good for 其他公司: 自己维护map<locale, 时间风格>, 或者if-else，具体风格也需要参考CLDR国际标准
$locale = "pt-BR";
$pattern = self::getGatternByLocale($locale);
$fmt = datefmt_create(
    $locale$locale,
    IntlDateFormatter::FULL,
    IntlDateFormatter::FULL,
    'America/Los_Angeles',
    IntlDateFormatter::GREGORIAN,
    $pattern
);
echo datefmt_format($fmt, $timestamp);

```

```yaml
checker_rule:
  reg: \bdate.*'Y-m-d H:i:s'
  alert_msg: '不能自定义时间格式, 慎用:date('Y-m-d H:i:s')系列 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint|DatetimeUtil::)
```


### CASE: 时间展示/不能自己拼接时间格式
```
// reason: 不同国家，时间展示规则不同:
CN(中国): 2019-12-31 01:59:59
BR(巴西): 31/12/2019 01:59:59
CO(哥伦比亚): 31/12/2019, 01:59:59 am
AU(澳大利亚): 31/12/2019, 1:59:59 am
```

```
// bad: 使用 string 加号操作符拼接
$now_time = $year . "-" . $month . "-" . $day . " " . $hour . ":" . $mintue . ":" . $second

// good for 滴滴: 用Elvish SDK解决
$sDateTime = DatetimeUtil::formatByCityID("pt-BR", 1573421371, 55000007, DatetimeUtil::DATE_STYLE_YYMMDD,
            DatetimeUtil::TIME_STYLE_HHMM);

// good: for 其他公司, 使用 intl扩展的IntlDateFormatter::format函数，参考：https://www.php.net/manual/zh/intldateformatter.format.php
$fmt = datefmt_create(
    'de-DE',
    IntlDateFormatter::FULL,
    IntlDateFormatter::FULL,
    'America/Los_Angeles',
    IntlDateFormatter::GREGORIAN,
    'MM/dd/yyyy'
);
echo datefmt_format($fmt, 0);
```

### CASE: 倒计时/倒计时格式化，比如 1min 5s

// reason: 不同国家，倒计时展示格式不同:
en-AU: 1 min 5 s
ja-JP: 1分5秒
pt-BR: 1 min e 5 s
```

```
// bad: 写死倒计时格式
$duration = $mintue . "min " . $second . "s";

// good for 其他公司: 根据locale决定倒计时格式

// good for 滴滴: 用Elvish SDK解决
$sDurationDisplay = DatetimeUtil::formatDuration($startTimestamp, $endTimestamp);

```

