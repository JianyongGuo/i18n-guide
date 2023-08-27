[[_TOC_]]

<a id="1"></a>

# 1. I18N 敏感函数

<a id="1.1"></a>

## 1.1. 时间类
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

### CASE: 时区相关/ 出海全球化软件建议使用ICU4J
```
// reason
出海全球化软件时间类建议使用ICU4J，不使用java原生的时间类来处理
```

### CASE: 时区相关/ 不能一直使用默认时区
```
// reason
所有时区、时间操作都必须明确指定timezone，不应该一直使用一个默认时区
```

```
// bad
Calendar calendar = new GregorianCalendar();
Calendar calendar = Calendar.getInstance();
TimeZone timeZone = TimeZone.getDefault();
LocalDate now = LocalDate.now();
LocalDateTime now = LocalDateTime.now();


// good: (for 其他公司), 根据场景显式指定需要的时区和locale
Calendar calendar = new GregorianCalendar(request.getUserTimeZone(), request.getUserLocale());
Calendar calendar = Calendar.getInstance(request.getUserTimeZone(), request.getUserLocale());

TimeZone timeZone = TimeZone.getTimeZone(request.getUserTimeZone());
LocalDate now = LocalDate.now(ZoneId.of(request.getUserTimeZone()));
LocalDateTime now = LocalDateTime.now(ZoneId.of(request.getUserTimeZone()));

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: GregorianCalendar\(\)|Calendar.getInstance\(\)
  alert_msg: '不应该一直使用一个默认时区, 推荐:使用用户请求参数中的时区'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时区相关/ 不能修改默认时区
```
// reason
修改默认时区再使用，在多线程场景下可能存在问题。
```

```
// bad
TimeZone.setDefault(request.getUserTimeZone());
TimeZone timeZone = TimeZone.getDefault();


// good: (for 其他公司), 根据场景显式指定需要的时区
TimeZone timeZone = TimeZone.getTimeZone(request.getUserTimeZone());


// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: TimeZone.setDefault|TimeZone.getDefault\(\)
  alert_msg: '修改默认时区再使用，在多线程场景下可能存在问题。推荐:使用用户请求参数中的时区'
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
TimeZone timeZone = TimeZone.getTimeZone("Asia/Shanghai");
ZoneId zoneId = ZoneId.of("America/Los_Angeles");


// good: (for 其他公司), 使用请求参数中的时区
TimeZone timeZone = TimeZone.getTimeZone(request.getUserTimeZone());
ZoneId zoneId = ZoneId.of(request.getUserTimeZone());

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: TimeZone.getTimeZone\(\"\\s+\"\)|ZoneId.of\(\"\\s+\")
  alert_msg: '不应该hardcode指定某个特定时区; 推荐:应该使用用户请求中的时区'
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
TimeZone timeZone = TimeZone.getTimeZone("CST");


// good: (for 其他公司), 使用请求参数中的时区
TimeZone timeZone = TimeZone.getTimeZone(request.getUserTimeZone());


// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: TimeZone.getTimeZone\(\"\\s+\"\)
  alert_msg: ''
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时区相关/ 不能使用UTC+8, GMT+8等格式的时区
```
// reason
一个国家的时区可能会变化, 夏令时本质就是从 GMT-7切换到GMT-6
```

```
// bad
TimeZone timeZone = TimeZone.getTimeZone("GMT-8");


// good: (for 其他公司), 使用完整的时区名称
TimeZone timeZone = TimeZone.getTimeZone(request.getUserTimeZone());


// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: TimeZone.getTimeZone\(\"\\s+\"\)
  alert_msg: ''
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint|GMT+8|UTC)
```

### CASE: 时间戳格式化/ Format时 必须保证时区数据库是最新版本

### CASE: 时间运算/ 1天 != 24小时
```
// reason
由于夏令时的缘故, 1天 != 24小时, 1天 != 86400秒
有可能是23小时, 也有可能是25小时
全球所有国家一般都是在 00:00:00 到03:00:00切换令时
```

```
// bad
long sevenDaysLater = System.currentTimeMillis() + 7 * 24 * 60 * 60 * 1000 


// good: (for 其他公司), 使用完整的时区名称
LocalDateTime now = LocalDateTime.now(ZoneId.of(request.getUserTimeZone()));
LocalDateTime localDateTime = now.plusDays(7);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

### CASE: 时间运算/ 定时任务的幂等性
```
// reason
由于夏令时的缘故, 1天 != 24小时, 1天 != 86400秒

```

```
// bad: 有可能有2个 01:30:00, 需要业务自己处理 可重入性(幂等性)
if (nowTime.equals("01:30:00")) {
    startTask();
}

// bad: 有可能没有 01:30:00, 需要业务自己回放数据, 补录数据
if (nowTime.equals("01:30:00")) {
    startTask();
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
  reg: ''
  alert_msg: '定时任务尽量避开0点到3点, 高精度业务需要自己保证幂等性和补偿机制'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

<a id="2"></a>

# 2. I18N 展示格式

<a id="2.1"></a>

## 2.1. 时间类

### CASE: 时间展示风格/时间Pattern不能写死
```
// reason: 不同国家时间格式不同, 比如:
CN(中国): 2019-12-31 01:59:59
BR(巴西): 31/12/2019 01:59:59
CO(哥伦比亚): 31/12/2019, 01:59:59 am
AU(澳大利亚): 31/12/2019, 1:59:59 am
EG(埃及): 2019/11/11، 10:11
```

```
// bad：所有国家使用同一个pattern
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yy HH:mm");


// good: (for 其他公司) 自己维护map{"CN":"yyyy-MM-dd", "CA":"dd-MM-yyyy", "JP":"yyyy/MM/dd"}, 具体风格参考CLDR标准

DateTimeFormatter formatter = DateTimeFormatter.ofPattern(map.get(country));

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: ((?i)[0-9]\s*(am|pm)\b)|(D,\s*dd?\s*M\s*yy?)|(dd\.MM\.yyyy)|(dd/MM/yy(yy\s*HH:mm)?)|(dddd\s*dd)|(hh:mm\s*(dd\s*MM\s*yyyy)?)|(M/dd/yy)|(mm-dd-yyyy)|(MMM(M)?\s*d(,|d)\s*yyyy)|(yyyy:MM:dd)
  alert_msg: '时间Pattern不能写死'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ LocalDate日期转换未指定locale
```
// reason
使用没有设置locale的格式化器，可能会存在默认locale问题。
```

```
// bad: 使用没有设置locale的格式化器，可能会存在默认locale问题。
DateFormatter dateFormatter = DateFormatter.ofLocalizedDate(dateStyle);
LocalDate localDate = LocalDate.now();
String str = localDate.format(dateFormatter);

LocalDate localDate = LocalDate.parse(text, dateTimeFormatter);

// good: (for 其他公司), 通过withLocale函数给格式化器实例设置locale
DateFormatter dateFormatter = DateFormatter.ofLocalizedDate(dateStyle);
dateFormatter = dateFormatter.withLocale(request.getUserLocale());
LocalDate localDate = LocalDate.now(ZoneId.of(request.getUserTimeZone()));
String str = localDate.format(dateFormatter);

LocalDate localDate = LocalDate.parse(text, dateFormatter);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: format|LocalDate.parse
  alert_msg: '要确保使用正确的格式化器，请在创建格式化器时传入locale设置，或在现有格式化器上调用withLocale，传入locale设置'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ LocalDateTime日期时间转换未指定locale
```
// reason
使用没有设置locale的格式化器，可能会存在默认locale问题。
```

```
// bad: 使用没有设置locale的格式化器，可能会存在默认locale问题。
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedDateTime(dateStyle);
LocalDateTime localDateTime = LocalDateTime.now()
String str = localDateTime.format(dateTimeFormatter);

LocalDateTime localDateTime = LocalDateTime.parse(text, dateTimeFormatter);

// good: (for 其他公司), 通过withLocale函数给格式化器设置locale信息
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedDateTime(dateStyle);
dateTimeFormatter = dateTimeFormatter.withLocale(request.getUserLocale());
LocalDateTime localDateTime = LocalDateTime.now(ZoneId.of(request.getUserTimeZone()))
String str = localDateTime.format(dateTimeFormatter);

LocalDateTime localDateTime = LocalDateTime.parse(text, dateTimeFormatter);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: format|LocalDateTime.parse
  alert_msg: '要确保使用正确的格式化器，请在创建格式化器时传入locale设置，或在现有格式化器上调用withLocale函数，传入locale设置'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ LocalTime时间转换未指定locale
```
// reason
使用没有设置locale的格式化器，可能会存在默认locale问题。
```

```
// bad: 使用没有设置locale的格式化器，可能会存在默认locale问题。
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedTime(dateStyle);
LocalTime localTime = LocalTime.now();
String str = localTime.format(dateTimeFormatter);

LocalTime localTime = LocalTime.parse(text, dateTimeFormatter);

// good: (for 其他公司), 通过withLocale函数给格式化器设置locale信息
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedTime(dateStyle);
dateTimeFormatter = dateTimeFormatter.withLocale(request.getUserLocale());
LocalTime localTime = LocalTime.now(ZoneId.of(request.getUserTimeZone()));
String str = localTime.format(dateTimeFormatter);

LocalTime localTime = LocalTime.parse(text, dateTimeFormatter);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: format|LocalTime.parse
  alert_msg: '要确保使用正确的格式化器，请在创建格式化器时传入locale设置，或在现有格式化器上调用withLocale函数，传入locale设置'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ MonthDay日期转换未指定locale
```
// reason
使用没有设置locale的格式化器，可能会存在默认locale问题。
```

```
// bad: 使用没有设置locale的格式化器，可能会存在默认locale问题。
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
MonthDay monthDay = MonthDay.now();
String str = monthDay.format(dateTimeFormatter);

MonthDay monthDay = MonthDay.parse(text, dateTimeFormatter);

// good: (for 其他公司), 通过withLocale函数给格式化器设置locale信息
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
dateTimeFormatter = dateTimeFormatter.withLocale(request.getUserLocale());
MonthDay monthDay = MonthDay.now(ZoneId.of(request.getUserTimeZone()));
String str = monthDay.format(dateTimeFormatter);

MonthDay monthDay = MonthDay.parse(text, dateTimeFormatter);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: format|MonthDay.parse
  alert_msg: '要确保使用正确的格式化器，请在创建格式化器时传入locale设置，或在现有格式化器上调用withLocale函数，传入locale设置'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ OffsetDateTime日期转换未指定locale
```
// reason
使用没有设置locale的格式化器，可能会存在默认locale问题。
```

```
// bad: 使用没有设置locale的格式化器，可能会存在默认locale问题。
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
OffsetDateTime offsetDateTime = OffsetDateTime.now();
String str = offsetDateTime.format(dateTimeFormatter);

OffsetDateTime offsetDateTime = OffsetDateTime.parse(text, dateTimeFormatter);

// good: (for 其他公司), 通过withLocale函数给格式化器设置locale信息
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
dateTimeFormatter = dateTimeFormatter.withLocale(request.getUserLocale());
OffsetDateTime offsetDateTime = OffsetDateTime.now(ZoneId.of(request.getUserTimeZone()));
String str = offsetDateTime.format(dateTimeFormatter);

OffsetDateTime offsetDateTime = OffsetDateTime.parse(text, dateTimeFormatter);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: format|OffsetDateTime.parse
  alert_msg: '要确保使用正确的格式化器，请在创建格式化器时传入locale设置，或在现有格式化器上调用withLocale函数，传入locale设置'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ OffsetTime日期转换未指定locale
```
// reason
使用没有设置locale的格式化器，可能会存在默认locale问题。
```

```
// bad: 使用没有设置locale的格式化器，可能会存在默认locale问题。
OffsetTime offsetTime = OffsetTime.now();
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
String str = offsetTime.format(dateTimeFormatter);

OffsetTime offsetTime = OffsetTime.parse(text, dateTimeFormatter);

// good: (for 其他公司), 通过withLocale函数给格式化器设置locale信息
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
OffsetTime offsetTime = OffsetTime.now(ZoneId.of(request.getUserTimeZone()));
dateTimeFormatter = dateTimeFormatter.withLocale(request.getUserLocale());
String str = offsetTime.format(dateTimeFormatter);

OffsetTime offsetTime = OffsetTime.parse(text, dateTimeFormatter);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: format|OffsetTime.parse
  alert_msg: '要确保使用正确的格式化器，请在创建格式化器时传入locale设置，或在现有格式化器上调用withLocale函数，传入locale设置'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ 获取DateFormat实例未指定locale
```
// reason
无locale参数函数会导致使用默认locale，要确保正确的日期/时间格式，请使用需要Locale参数的函数。
```

```
// bad: 使用无Locale参数的函数，会使用默认locale
DateFormat dateFormatter = DateFormat.getDateInstance(DateFormat.DEFAULT);
DateFormat dateFormatter = DateFormat.getDateInstance();

DateFormat dateFormatter = DateFormat.getDateTimeInstance(DateFormat.DEFAULT, DateFormat.DEFAULT);
DateFormat dateFormatter = DateFormat.getDateTimeInstance();

DateFormat dateFormatter = DateFormat.getInstance();

DateFormat dateFormatter = DateFormat.getTimeInstance(DateFormat.DEFAULT);
DateFormat dateFormatter = DateFormat.getTimeInstance();


// good: (for 其他公司), 根据场景显式指定需要的Locale参数
Locale locale = request.getUserLocale();
DateFormat dateFormatter = DateFormat.getDateInstance(DateFormat.DEFAULT, locale);
DateFormat dateFormatter = DateFormat.getDateTimeInstance(DateFormat.DEFAULT, DateFormat.DEFAULT, locale);
DateFormat dateFormatter = DateFormat.getDateTimeInstance(DateFormat.DEFAULT, DateFormat.DEFAULT, locale);
DateFormat dateFormatter = DateFormat.getTimeInstance(DateFormat.DEFAULT, locale);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: DateFormat.getDateInstance\(\)|DateFormat.getDateTimeInstance\(\)|DateFormat.getInstance\(\)|DateFormat.getTimeInstance\(\)
  alert_msg: '不应该使用无locale参数的函数获取实例, 推荐:使用用户请求参数中的locale信息来获取DateFormat实例'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```
### CASE: 时间展示风格/ 获取DateFormatSymbols实例未指定locale
```
// reason
无参构造函数会导致使用默认locale，要确保正确的日期/时间格式，请使用需要Locale参数的函数。
```

```
// bad: 使用无参函数，会使用默认locale
DateFormatSymbols symbols = new DateFormatSymbols();

// good: (for 其他公司), 根据场景显式指定需要的locale
DateFormatSymbols symbols = new DateFormatSymbols(getUserLocale());

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 
```

```yaml
checker_rule:
  reg: DateFormatSymbols\(\)
  alert_msg: '不应该使用无locale参数的函数获取实例, 推荐:使用用户请求参数中的locale信息来获取DateFormatSymbols实例'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ 获取DateTimeFormatter实例未指定locale
```
// reason
无locale参数函数会导致使用默认locale，要确保正确的日期/时间格式，请使用包含Locale参数的函数创建格式化器，或者对现有格式化器调用withLocale函数进行处理。
```

```
// bad: 使用无参函数，会使用默认locale
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedDate(dateStyle);

DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedDateTime(timeStyle);
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedDateTime(dateStyle, timeStyle);

DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedTime(timeStyle);

DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);

// good: (for 其他公司), 根据场景显式指定需要的时区和locale
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedDate(dateStyle);

DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedDateTime(dateTimeStyle);
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedDateTime(dateStyle, timeStyle);

DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofLocalizedTime(timeStyle);

dateTimeFormatter = dateTimeFormatter.withLocale(request.getUserLocale());

DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern, request.getUserLocale())

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: DateTimeFormatter.ofLocalizedDate|DateTimeFormatter.ofLocalizedDateTime|DateTimeFormatter.ofLocalizedTime|DateTimeFormatter.ofPattern
  alert_msg: '对格式化器调用withLocale函数进行处理或者使用包含Locale参数的函数构造格式化器'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```


### CASE: 时间展示风格/ SimpleDateFormat实例没有locale信息
```
// reason
SimpleDateFormat对用户输入模式的依赖使其无法生成根据用户的语言环境格式化的日期字符串。如果生成的日期字符串是要显示给用户的，则应使用DateFormat类。
```

```
// bad: SimpleDateFormat无法生成根据用户的语言环境格式化的日期字符串。
SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
String dateString = formatter.format(new Date());

// good: (for 其他公司), 使用DateFormat
DateFormat df = DateFormat.getDateInstance(DateFormat.SHORT, request.getUserLocale());
String dateString = formatter.format(new Date());

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: SimpleDateFormat
  alert_msg: '应使用DateFormat类，并在获取实例时传入locale设置'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ YearMonth日期转换未指定locale
```
// reason
使用没有设置locale的格式化器，可能会存在默认locale问题。
```

```
// bad: 使用没有设置locale的格式化器，可能会存在默认locale问题。
YearMonth yearMonth = YearMonth.now();
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
String str = yearMonth.format(dateTimeFormatter);

YearMonth yearMonth = YearMonth.parse(text, dateTimeFormatter);

// good: (for 其他公司), 通过withLocale函数给格式化器设置locale信息
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
YearMonth yearMonth = YearMonth.now(ZoneId.of(request.getUserTimeZone()));
dateTimeFormatter = dateTimeFormatter.withLocale(request.getUserLocale());
String str = yearMonth.format(dateTimeFormatter);

YearMonth yearMonth = YearMonth.parse(text, dateTimeFormatter);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: format|YearMonth.parse
  alert_msg: '要确保使用正确的格式化器，请在创建格式化器时传入locale设置，或在现有格式化器上调用withLocale函数，传入locale设置'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ ZonedDateTime日期转换未指定locale
```
// reason
使用没有设置locale的格式化器，可能会存在默认locale问题。
```

```
// bad: 使用没有设置locale的格式化器，可能会存在默认locale问题。
ZonedDateTime zonedDateTime = ZonedDateTime.now();
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
String str = zonedDateTime.format(dateTimeFormatter);

ZonedDateTime zonedDateTime = ZonedDateTime.parse(text, dateTimeFormatter);

// good: (for 其他公司), 通过withLocale函数给格式化器设置locale信息
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(pattern);
ZonedDateTime zonedDateTime = ZonedDateTime.now(ZoneId.of(request.getUserTimeZone()));
dateTimeFormatter = dateTimeFormatter.withLocale(request.getUserLocale());
String str = zonedDateTime.format(dateTimeFormatter);

ZonedDateTime zonedDateTime = ZonedDateTime.parse(text, dateTimeFormatter);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: format|ZonedDateTime.parse
  alert_msg: '要确保使用正确的格式化器，请在创建格式化器时传入locale设置，或在现有格式化器上调用withLocale函数，传入locale设置'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ 自定义时间展示样式
```
// reason
自定义的展示样式和locale的可能样式不一样
```

```
// bad
String date = String.format("%s-%s-%s", localDate.getYear(), localDate.getMonthValue(), localDate.getDayOfMonth());

// good: (for 其他公司), 从用户请求中获取locale信息
DateFormat df = DateFormat.getDateInstance(DateFormat.MEDIUM, Locale.CHINA);
String dt = df.format(date);

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: \"%s-%s-%s\"
  alert_msg: '自定义的展示样式和locale的样式可能不一样'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```

### CASE: 时间展示风格/ 获取TimeZone相关信息未指定locale
```
// reason
默认时区/硬编码时区可能不准确，需要根据具体场景设置，然后使用。
```

```
// bad: 使用默认的时区/硬编码时区可能不准确
TimeZone timeZone = TimeZone.getDefault();
String name = timeZone.getDisplayName();

// good: (for 其他公司), 指定locale信息
TimeZone timeZone = TimeZone.getTimeZone(request.getUserTimeZone());
String name = timeZone.getDisplayName(request.getUserLocale());


// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: getDisplayName
  alert_msg: '获取TimeZone相关信息未指定locale'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```


### CASE: 时间展示风格/ 确认ZoneId相关信息获取的locale
```
// reason
getDisplayName函数需要指定locale信息，请确保locale是正确的。
```

```
// bad: 指定的locale可能不正确
ZoneId zoneId = ZoneId.of("America/Los_Angeles");
String name = zoneId.getDisplayName(TextStyle.FULL, Locale.getDefault());

// good: (for 其他公司), 从用户请求中获取locale信息
ZoneId zoneId = ZoneId.of(request.getUserTimeZone());
String name = zoneId.getDisplayName(TextStyle.FULL, request.getUserLocale());

// good: (for 滴滴), 用Elvish SDK解决, 业务不需要关注timezone, 大部分场景用city_id处理即可 

```

```yaml
checker_rule:
  reg: getDisplayName
  alert_msg: 'getDisplayName函数需要指定locale信息，请确保locale是正确的'
  level: P1
  exclude: (log|test|nolint|no_lint|no-lint)
```


