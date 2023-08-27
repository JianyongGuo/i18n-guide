```
1. I18N 最佳实践
	常见问题/ 哪些国家有夏令时
	环境工具/ 全球时间转换
	环境工具/ I18N问题建议使用ICU4J解决



2. I18N 敏感函数
2.1 时间类
	CASE: 时区相关/ 不能一直使用默认时区
	CASE: 时区相关/ 不能修改默认时区
	CASE: 时区相关/ 不能指定某个特定的时区
	CASE: 时区相关/ timezone应该使用完整格式,不能使用简写
	CASE: 时区相关/ 不能使用UTC+8, GMT+8等格式的时区
	CASE: 时间戳格式化/ Format时 必须保证时区数据库是最新版本
	CASE: 时间戳格式化/ Format时 必须指定时区
	CASE: 时间运算/ 1天 != 24小时
	CASE: 时间运算/ 定时任务的幂等性




3. I18N 展示格式
3.1 时间类
	CASE: 时间展示风格/ 时间Pattern不能写死
	CASE: 时间展示风格/ LocalDate日期转换未指定locale
	CASE: 时间展示风格/ LocalDateTime日期时间转换未指定locale
	CASE: 时间展示风格/ LocalTime时间转换未指定locale
	CASE: 时间展示风格/ MonthDay日期转换未指定locale
	CASE: 时间展示风格/ OffsetDateTime日期转换未指定locale
	CASE: 时间展示风格/ OffsetTime日期转换未指定locale
	CASE: 时间展示风格/ 获取DateFormat实例未指定locale
	CASE: 时间展示风格/ 获取DateFormatSymbols实例未指定locale
	CASE: 时间展示风格/ SimpleDateFormat实例没有locale信息
	CASE: 时间展示风格/ YearMonth日期转换未指定locale
	CASE: 时间展示风格/ ZonedDateTime日期转换未指定locale
	CASE: 时间展示风格/ 自定义时间展示样式
	CASE: 时间展示风格/ 获取TimeZone相关信息未指定locale
	CASE: 时间展示风格/ 确认ZoneId相关信息获取的locale
```

