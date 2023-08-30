#!encoding:utf-8
"""
Usage: 
    example 1: python i18n_checker_python.py  ./
    example 2: python i18n_checker_python.py  /home/user/workspace/some_project
"""

import os
import json
import sys
import re

## 时间规则 golang
i18n_rules = [
  {"rule_type": "i18n", "rule_name": "sample", "level": "error", # 规则名称
    "reg_in_func_no": "",                                        # 函数开头到本行, 没有某个关键词时
    "reg_up3_no": "",                                            # 前3行没有某个关键词
    "reg_up3": "",                                               # 前3行包含什么内容, 并且
    "reg": '''.*FuncChinaRain\d{100}$''',                        # 本行正则表达式, 并且 
    "reg_down3": "",                                             # 后3行包含什么内容
    "reg_down3_no": "",                                          # 后3行没有某个关键词
    "line_to_lower": 0,                                          # 转换为小写,再进行匹配
    "i18n_type": "time",                                         # 规则类别
    "file_type": ".*.go",                                        # 这条规则, 只扫描.go文件
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", # 排除某些关键词
    "alert_msg": "不能怎么怎么样, 推荐怎么怎么样"},              # 提醒风险内容

   
  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''(loc|format|parse|pattern|layout|Layout).*(2006-01-02 15:04:05|2006-01-02).*(location|zone|offset)?''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能自定义时间格式, 慎用:time.Format(2006-01-02 15:04:05) --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"},

  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "warning",
    "reg": '''(time|Now).*(2006-01-02 15:04:05|2006-01-02)''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能自定义时间格式, 慎用:time.Format(2006-01-02 15:04:05) --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"},

  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "warning",
    "reg": '''time.Now\(\).Format\(''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能自定义时间格式, 慎用:time.Format(2006-01-02 15:04:05) --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"},


  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''%v(-|/)%v(-|/)%v %v:%v:%v.*year.*month.*day''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能自定义时间格式 慎用:自己用Sprintf拼接时间格式 --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"},

  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''year *\+ *"-" *\+ *month *\+ *"-" *\+ *day *\+ *" " *\+ *hour *\+ *":" *\+ *mintue *\+ *":" *\+ *second''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能自定义时间格式 慎用:自己用Sprintf拼接时间格式 --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"},



  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''%v:%v:%v %v(-|/)%v(-|/)%v.*year.*month.*day''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能自定义时间格式, 慎用:自己用Sprintf拼接时间格式 --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"},

  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''=.*%v:%v:%v.*hour.*minute.*second''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能自定义时间格式, 慎用:自己用Sprintf拼接时间格式 --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"},

  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''=.*%s(-|/)%s(-|/)%s %s:%s:%s.*year.*month.*day''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能自定义时间格式, 慎用:自己用Sprintf拼接时间格式 --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"},

  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''%d-%02d-%02d %02d:%02d:%02d''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能自定义时间格式, 慎用:自己用Sprintf拼接时间格式 --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法"},

  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''time.*\.Format\(.*"(\d\d\d\d.{1}\d\d.{1}\d\d \d\d:\d\d:\d\d(?<!2006-01-02 15:04:05))"''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "时间pattern错误,应该使用 2006-01-02 15:04:05"},

  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''(format|display|local|Format|Local|style|Style|show).*=.*time\..*\.Format\("2006-01-02 15:04:05"\)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "时间Pattern不能写死成 2006-01-02 15:04:05, 因为各国时间风格不同"},

  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''time.*\.Format\(("2006/01/02 15:04:05"|"02/01/2006 15:04:05"|"15:04:05 2006-01-02"|"15:04:05 2006/01/02"|"01-02-2006 15:04:05"|"01/02/2006 15:04:05"|"1-2-2006 15:04:05"|"2-1-2006 15:04:05")''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不应该定制时间格式, 需要根据CLDR来决定各国时间展示格式, 推荐:使用Elvish处理时间展示"},


  {"rule_type": "i18n", "rule_name": "go 不能自定义时间格式", "level": "error",
    "reg": '''Sprintf\("%s - %s", *time[^ ]* *time[^ ]*\)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "时间段格式化不同时间间隔有不同的展示风格, 请使用Elvish处理时间段展示"},

  {"rule_type": "i18n", "rule_name": "go 时区相关", "level": "error",
    "reg": '''.*time.FixedZone\(.*''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不应该一直使用一个默认时区, 推荐:使用用户请求参数中的时区"},

  {"rule_type": "i18n", "rule_name": "go 时区相关", "level": "error",
    "reg": '''time.LoadLocation\(".*"''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不应该hardcode指定某个特定时区; 推荐:应该使用用户请求中的时区"},

  {"rule_type": "i18n", "rule_name": "go 时区相关", "level": "error",
    "reg": '''time\.(Now|Unix).*.Zone\(\)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不建议直接使用timezone或者utc_offset来进行时间计算, 推荐: 使用Elvish的时间类处理"},

  {"rule_type": "i18n", "rule_name": "go 时区相关", "level": "error",
    "reg": '''time.*Location.*"(CST|MST|PST|EDT|CDT)"''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "timezone应该使用完整格式,不能使用简写, 推荐:使用完整格式的时区比如America/Chihuahua"},

  {"rule_type": "i18n", "rule_name": "go 时区相关", "level": "error",
    "reg": '''.*"(GMT|UTC)(-|\+)\d+".*''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能使用UTC+8、GMT+8 等格式的时区, 推荐:使用完整格式的时区比如America/Chihuahua"},

  {"rule_type": "i18n", "rule_name": "go 时区相关", "level": "error",
    "reg": '''time.LoadLocation\([^(),]*(country|Country)[^(),]*\)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能按国家粒度进行时间计算,必须按时区粒度, 因为一个国家可能有多个时区"},

  {"rule_type": "i18n", "rule_name": "go 时间转换", "level": "error",
    "reg": '''time.Unix((?!\.In\().)*Format\(''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "时间格式化时应该指定timezone或者city_id, 例如:time.Unix().In(loc).Format()"},

  {"rule_type": "i18n", "rule_name": "go 时间转换", "level": "error",
    "reg": '''time.(Now|Unix)\([^()]*\)\.(Date|Day|Hour|Mintue|Second|Weekday|ISOWeek)\(\)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "时间戳和Date转换时,必须指定时区, 例如:time.Unix().In(loc).Hour()"},

  {"rule_type": "i18n", "rule_name": "go 时间转换", "level": "error",
    "reg": '''time.*\.Format\(("2006/01/02 15:04:05"|"02/01/2006 15:04:05"|"15:04:05 2006-01-02"|"15:04:05 2006/01/02"|"01-02-2006 15:04:05"|"01/02/2006 15:04:05"|"1-2-2006 15:04:05"|"2-1-2006 15:04:05")''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "time.Date对象初始化时应该带时区参数, 例如:time.Date(2022, 10, 1, 23,59, 59, 0, timezone)"},


  {"rule_type": "i18n", "rule_name": "go 时间反转", "level": "error",
    "reg": '''time.Parse\([^(),]*,[^(),]*\)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "时间字符串转时间戳时, 应该指定timezone, 或者使用Elvish.GetTimeStampByXXX进行处理"},

  {"rule_type": "i18n", "rule_name": "go 时间反转", "level": "error",
    "reg": '''time.Parse\([^(),]*,[^(),]*\)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "时间字符串转时间戳时, 应该指定timezone, 或者使用Elvish.GetTimeStampByXXX进行处理"},


  {"rule_type": "i18n", "rule_name": "go 时间反转", "level": "warning",
    "reg": '''time[^ ]* *== *("0[1,2]:[0-5]\d:\d\d"|"0[1,2]:[0-5]\d")''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "定时任务尽量避开0点到3点, 高精度业务需要自己保证幂等性和补偿机制"},


  {"rule_type": "i18n", "rule_name": "go 日历相关", "level": "warning",
    "reg": '''(=|return).*time.Now.*\+(.*3600.*24 *\*|.*86400 *\*|.*24.+60.+60 *\*|.*60.+60.+24 *\*) *\d+''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "未来时间不能用86400方式计算, 推荐:使用Elvish提供的未来时间计算函数"},

  {"rule_type": "i18n", "rule_name": "go 日历相关", "level": "warning",
    "reg": '''time.(Now|Unix).*/ *(86400|SECOND[A-Z_]*DAY|DAY[A-Z_]*SECOND)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能用86400, 判断是否是一天的开始, 推荐:使用Elvish的Canlender类处理"},

  {"rule_type": "i18n", "rule_name": "go 日历相关", "level": "warning",
    "reg": '''\([^ ]*hour[^ ]* *- *[^ ]*hour[^ ]* *\) *\* *(3600|SECOND[A-Z_]*HOUR|HOUR[A-Z_]*SECOND)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能用小时直接相减计算时间差, 推荐: 使用Elvish的TimeDiff函数计算时间间隔"},


  {"rule_type": "i18n", "rule_name": "go 日历相关", "level": "warning",
    "reg_up3_no": '''time\.(Now|Unix)((?!\.In\().)*''',
    "reg": '''time\.Date\(((?!\.In\().)*\.Year\(\),((?!\.In\().)*\.Month.*((?!\.In\().)*\.Day.*0.*0.*0.*0.*''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "time.Day() Year() Month() 等函数需要指定时区 time.In(location).Day()"},

  {"rule_type": "i18n", "rule_name": "go 日历相关", "level": "warning",
    "reg_up3_no": '''time\.(Now|Unix)((?!\.In\().)*''',
    "reg": '''time\.Date\(((?!\.In\().)*\.Year\(\),((?!\.In\().)*\.Month.*((?!\.In\().)*\.Day.*23.*59.*59.*0.*''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "获取一天的开始或者结束时间, 请使用Elvish提供的能力"},


  {"rule_type": "i18n", "rule_name": "go 日历相关", "level": "warning",
    "reg_up3_no": '''time\.(Now|Unix)((?!\.In\().)*''',
    "reg": '''offset.*=.*time.Monday *- *.*Weekday''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "获取一天开始、一周开始、一月开始，都需要指定用户请求的timezone 或者:推荐使用Elvish解决"},

  {"rule_type": "i18n", "rule_name": "go 日历相关", "level": "warning",
    "reg": '''time.*% *(86400|SECOND[A-Z_]*DAY|DAY[A-Z_]*SECOND)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|datetimeutil)", "alert_msg": "不能对86400取模判断是哪一天，因为有的国家1天 != 86400秒; 推荐:使用Elvish处理时间日历"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "warning",
    "reg": '''datetimeutil.FormatBy\(''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不推荐用此函数，除非不知道cityid只知道timezone时可用此函数. 推荐: 请业务尽量使用 FormatByCityId"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "error",
    "reg": '''datetimeutil.Format\(''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "使用了禁用函数datetimeutil.Format, 请使用datetimeutil.FormatByCityID"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "error",
    "reg": '''datetimeutil.GetTimeStampByCityId\(''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不推荐用此函数，参数过于复杂，业务可能用错。 推荐: 业务尽量使用 GetTimeStampByPattern"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "error",
    "reg": '''datetimeutil.FormatSimple\(''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不推荐用此函数，此函数是RD自定义时间pattern，并不是local最佳时间风格。推荐: 请业务尽量使用 FormatByCityId"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "error",
    "reg": '''(time.LoadLocation\(|time.ParseInLocation\()''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "使用了禁用函数 time.ParseInLocation, 使用Elvish处理时间,业务不需要自己加载location"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "error",
    "reg": '''(time|Time|Local|local)*(time|Time|Local|local).*\.In\(''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "使用了禁用函数 time.In, 使用Elvish处理时间,如datetimeutil.FormatByCityID"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "error",
    "reg": '''=.*(time|Time|Local|local)\.(Year|Month|Day)\(\)''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|elvish)", "alert_msg": "使用了禁用函数 time.Year|Month|Day(), 使用Elvish处理时间,如datetimeutil.FormatByCityID"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "warning",
    "reg": '''(unix|time|local|Unix|Time|Local).*\.Weekday\(\)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|elvish)", "alert_msg": "使用了禁用函数 time.Weekday(), 使用Elvish处理时间,如calendarutil.Get(.. CAL_DAY_OF_WEEK ..)"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "warning",
    "reg": '''time\.Date\(.*, *loc.*\.AddDate\(''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|elvish)", "alert_msg": "使用了禁用函数 time.Date().Unix(), 使用Elvish进行时间戳->时间字符串的转换, 如datetimeutil.FormatByCityID"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "warning",
    "reg": '''time\.Date\(.*\.Unix\(\)''',
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|elvish)", "alert_msg": "使用了禁用函数 time.Date().Unix(), 使用Elvish进行时间戳->时间字符串的转换, 如datetimeutil.FormatByCityID"},

  {"rule_type": "i18n", "rule_name": "go 不建议的函数", "level": "warning",
    "reg": '''datetimeutil.GetTimeStampByCityId\(''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不推荐用此函数，参数过于复杂，业务可能用错。 推荐: 业务尽量使用 GetTimeStampByPattern"},

  {"rule_type": "i18n", "rule_name": "go 不建议的函数", "level": "warning",
    "reg": '''datetimeutil.FormatSimple\(''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不推荐用此函数，此函数是RD自定义时间pattern，并不是local最佳时间风格。推荐: 请业务尽量使用 FormatByCityId"},


  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "error",
    "reg": '''(=|return ).*format.*\(.*utc.*offset''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "禁止使用utcoffset计算时间, 使用Elvish格式化时间,如datetimeutil.FormatByCityID"},

  {"rule_type": "i18n", "rule_name": "go 禁用函数", "level": "warning",
    "reg": '''(=|return ).*\bformat\(.*(time|zone|Time|Zone|local|Local)''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "禁止使用timezone处理时间,  使用Elvish格式化时间,如datetimeutil.FormatByCityID"},


  {"rule_type": "i18n", "rule_name": "go hardcode 时间", "level": "warning",
    "reg": '''"2\d{3}(-|/)\d{2}(-|/)\d{2}"''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|create_time|update_time|2006-01-02|len)", "alert_msg": "时间变量不能硬编码"},

  {"rule_type": "i18n", "rule_name": "go hardcode 时间", "level": "warning",
    "reg": '''"\d{2}(-|/)\d{2}(-|/)2\d{3}"''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|create_time|update_time|2006-01-02|len)", "alert_msg": "时间变量不能硬编码"},

  {"rule_type": "i18n", "rule_name": "go hardcode 时间", "level": "warning",
    "reg": '''\d{2}:\d{2}:\d{2}''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|create_time|update_time|2006-01-02|len)", "alert_msg": "时间变量不能硬编码"},

  {"rule_type": "i18n", "rule_name": "go hardcode 国家", "level": "error",
    "reg": '''=.*\(.*('|")(AE|AR|AU|BD|BY|BO|BR|CL|CI|CO|CR|DO|DZ|EC|EG|GB|GH|GT|JP|KZ|KE|MA|MX|NG|NL|NZ|PK|PA|PE|PR|RU|SA|TZ|UG|UA|ZA)('|")''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|intlGettext)", "alert_msg": "国家不能硬编码"},

  {"rule_type": "i18n", "rule_name": "go hardcode 国家", "level": "error",
    "reg": '''=.*(time|date).*\(.*\b(BR|MX|CL|AU)\b''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|intlGettext)", "alert_msg": "国家不能硬编码"},

  {"rule_type": "i18n", "rule_name": "go hardcode cityid", "level": "error",
    "reg": '''=.*(datetimeutil|DatetimeUtil::).*\(\d{7,15}.*,.*,''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "cityid不能硬编码"},


  {"rule_type": "i18n", "rule_name": "go 时间加减风险", "level": "error",
    "reg": '''(=|return).{0,64}(time|date).*(\+|\-).{0,64}(day|DAY)''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|sql|select|table)", "alert_msg": "前N天或者后N天不能用时间戳直接加减, 推荐: 用elvish处理未来和过去时间"},


  {"rule_type": "i18n", "rule_name": "go 时间加减风险", "level": "error",
    "reg": '''(=|return).*(time|date).*(\+|\-).* [a-zA-Z_$]*(day|DAY)[a-zA-Z_]* *\* *''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "前N天或者后N天不能用时间戳直接加减, 推荐: 用elvish处理未来和过去时间"},

  {"rule_type": "i18n", "rule_name": "go 时间加减风险", "level": "error",
    "reg": '''date\("Y(-|/| )m(-|/| )d.*\+.*(day"|days"|day'|days')''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "前N天或者后N天不能用时间戳直接加减, 推荐: 用elvish处理未来和过去时间"},


  {"rule_type": "i18n", "rule_name": "go 时间计算风险", "level": "error",
    "reg": '''(=|return).*(time|date).*(\+|\-).*\b86400\b *\*''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "未来时间不能直接用86400秒算, 有的国家一天不是24小时; 推荐: 用elvish提供的方案计算"},

  {"rule_type": "i18n", "rule_name": "go 时间计算风险", "level": "error",
    "reg": '''(=|return).*(time|date).*(\+|\-) *[a-zA-Z_]* *\* *\b86400\b''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "未来时间不能直接用86400秒算, 有的国家一天不是24小时; 推荐: 用elvish提供的方案计算"},


  {"rule_type": "i18n", "rule_name": "go 时间计算风险", "level": "error",
    "reg": '''(day|week|year|month|Month|Year|Day|Week).*=.*(unix|time|stamp|\bts\b|local).*(\+|-) *''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能用时间戳直接做加减法, 有的国家一天不是24小时"},

  {"rule_type": "i18n", "rule_name": "go 时间比较", "level": "error",
    "reg": '''time.*str.*(>|<).*time.*str''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "时间字符串不能比较, 有的国家是时分秒日月年格式, 如果要比较请用自定义时间pattern=yyyy-MM-dd HH:mm:ss"},


  {"rule_type": "i18n", "rule_name": "go 时间截取", "level": "warning",
    "reg": '''(date|day).*=.*time.*\[0 *:10 *\]''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "前10个字符不一定是日期, 有的国家是 时分秒日月年格式"},

  {"rule_type": "i18n", "rule_name": "go 时间截取", "level": "warning",
    "reg": '''(date|day).*=.*time.*\[0 *:10 *\]''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "前10个字符不一定是日期, 有的国家是 时分秒日月年格式"},
  {"rule_type": "i18n", "rule_name": "go 时间截取", "level": "warning",
    "reg": '''(date|day).*=.*time.*\[ *\w *: *\w\]''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能按下标截取时间或者日期, 有的国家是 时分秒日月年格式"},



  {"rule_type": "i18n", "rule_name": "go elvish 使用错误", "level": "warning",
    "reg": '''datetimeutil.[A-Z].*\(.*time.*float''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "elvish参数不能是浮点数"},



  {"rule_type": "i18n", "rule_name": "go elvish 参数错误", "level": "warning",
    "reg": '''datetimeutil.FormatBy.*\(.*,.*,.*,(.*HHMM|.*HHMMSS),.*,.*''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "第4个参数错误, 应该是datetimeutil.HHMM 或者 datetimeutil.HHMMSS"},


  {"rule_type": "i18n", "rule_name": "go elvish 参数错误", "level": "warning",
    "reg": '''datetimeutil.FormatBy.*\(.*,.*,.*,.*,.*M[YMD]*,.*''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "第5个参数错误, 应该是YYYYMMDD或YYMMDD或YYYYMMM或MMMDDEEE或MMMDD"},

  {"rule_type": "i18n", "rule_name": "go elvish 参数错误", "level": "warning",
    "reg": '''datetimeutil.FormatBy.*\(.*,.*,.*,.*M[YMD]*,.*H[MS]*, *".*[-/ :].*"''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": '''4、5参数必须是PATTERN时才能使用第6个自定义参数, 正确用法: (local,city,time,datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, ""), 或者: (local,city,time,datetimeutil.PATTERN, datetimeutil.PATTERN, "yyyy-MM-dd HH:mm:ss")'''},


  {"rule_type": "i18n", "rule_name": "go elvish 参数错误", "level": "warning",
    "reg": '''datetimeutil.FormatBy.*\(.*,.*,.*,.*M[YMD]*,.*, *".*[-/ :].*"''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": '''4、5参数必须是PATTERN时才能使用第6个自定义参数, 正确用法: (local,city,time,datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, ""), 或者: (local,city,time,datetimeutil.PATTERN, datetimeutil.PATTERN, "yyyy-MM-dd HH:mm:ss")'''},

  {"rule_type": "i18n", "rule_name": "go elvish 参数错误", "level": "warning",
    "reg": '''datetimeutil.FormatBy.*\(.*,.*,.*,.*,.*H[MS]*, *".*[-/ :].*"''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": '''4、5参数必须是PATTERN时才能使用第6个自定义参数, 正确用法: (local,city,time,datetimeutil.YYYYMMDD, datetimeutil.HHMMSS, ""), 或者: (local,city,time,datetimeutil.PATTERN, datetimeutil.PATTERN, "yyyy-MM-dd HH:mm:ss")'''},

  {"rule_type": "i18n", "rule_name": "go elvish 赋值错误", "level": "warning",
    "reg": '''(bj_time|beijing).*=.*datetimeutil.Format.*\(''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "elvish结果赋值给了 北京时间变量"},

  {"rule_type": "i18n", "rule_name": "环境配置错误", "level": "warning",
    "reg": '''(time|zone|Zone|local|Local).*"CST"''', 
    "i18n_type": "time",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能使用CST时区, 不同系统CST有歧义, 既表示中国时区又表示美国中部时区"},



] ## end of 时间规则


## 时间规则 php
i18n_rules += [
  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "reg": '''\bdate.*'Y-m-d H:i:s',''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:date('Y-m-d H:i:s')系列 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "error",
    "reg": '''\bdate.*'yyyy-MM-dd hh:mm:ss',''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:date('yyyy-MM-dd hh:mm:ss')系列 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "error",
    "reg": '''\bdate_format\b.*'yyyy-MM-dd hh:mm:ss',''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:date_format('yyyy-MM-dd hh:mm:ss')系列 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "error",
    "reg": '''=.*\$year.'-'.\$month.'-'.\$day.' '.\$hour.':'.\$minute.':'.\$second''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:$year.$month.$day方式自行拼接时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "error",
    "reg": '''=.*\$year.'-'.\$mon(th){0,1}.'-'.\$day.' '.\$hour.':'.\$min(ute){0,1}.':'.\$second''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:$year.$month.$day方式自行拼接时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "error",
    "reg": '''=.*\$year.'/'.\$mon(th){0,1}.'/'.\$day.' '.\$hour.':'.\$min(ute){0,1}.':'.\$second''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:$year.$month.$day方式自行拼接时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "error",
    "reg": '''\$(time_str|local_time|local_date|display).*=.*\$.*\.'-'\.\$.*\.'-'\.\$.*\.' '\.\$.*\.':'\.\$.*\.':'\.\$.*''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:$year.$month.$day方式自行拼接时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "error",
    "reg": '''\$(time_str|local_time|local_date|display).*=.*\$.* \. '-' \. \$.* \. '-' \. \$.* \. ' ' \. \$.* \. ':' \. \$.* \. ':' \. \$.*''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:$year.$month.$day方式自行拼接时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "error",
    "reg": '''=.*sprintf.*%s(-|/)%s(-|/)%s %s:%s:%s.*year.*month.*day''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:用sprintf拼接时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "reg": '''=.*sprintf.*%s(-|/)%s(-|/)%s.*year.*month.*day''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:用sprintf拼接时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "reg": '''local.*time.*=.*sprintf.*%s(-|/)%s(-|/)%s''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:用sprintf拼接时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},


  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "reg": '''(format|display|local|Format|Local|style|Style|show).*=.*conf.*(\$loc|\$LOC)''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:自定义各国的时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "reg": '''('|")(pt|en|es|zh)('|").*('|")(Y-m-d|d-m-Y|Y/m/d|d/m/Y|Y.m.d|d.m.Y|Y m d|d m Y|h:i A|H:i)('|")''',
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:自定义各国的时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},


  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "reg": '''(format|Format).*(time|Time|unix|Unix|Timestamp|timestamp|zone|Zone).*(Y-m-d|d-m-Y|Y/m/d|d/m/Y|Y.m.d|d.m.Y|Y m d|d m Y|h:i A|H:i).*(time|Time|unix|Unix|Timestamp|timestamp|zone|Zone)''',
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:自定义时间格式函数 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},


  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "reg": '''\$.*=.*\$.*\.'-'\.\$.*\.'-'\.\$.*\.' '\.\$.*\.':'\.\$.*\.':'\.\$.*''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:$year.$month.$day方式自行拼接时间格式 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "reg": '''=.*\bdate\(.*('|")Y-m-d('|").*''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|DatetimeUtil::)", "alert_msg": "不能自定义时间格式, 慎用:date('Y-m-d')系列 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},


  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "line_to_lower": 0,
    "reg": '''(format|Format|date|Date).*\(.*(time|stamp|format|zone|unix|pattern).*,.*(time|stamp|zone|unix|pattern)''',
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|strconv|DatetimeUtil::| function |datetimeutil)", "alert_msg": "不能自定义时间格式, 慎用:自定义时间格式函数 --> 推荐:请用Elvish的DatetimeUtil::formatBy** 系列函数"},
 
  {"rule_type": "i18n", "rule_name": "php 不能自定义时间格式", "level": "warning",
    "reg": '''\bDateTime\(.*,.*(time|zone|local|Time|Zone)''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能使用DateTime自定义时间格式, 请使用elvish对应方法, 如DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 禁用函数", "level": "error",
    "reg": '''=.*strtotime\(\$''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|self::strtotime|->strtotime)", "alert_msg": "使用了禁用函数strtotime, 请使用Elvish的 DatetimeUtil::getTsByPattern** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 禁用函数", "level": "error",
    "reg": '''\bdate_default_timezone_set\(''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint|self::strtotime|->strtotime)", "alert_msg": "使用了禁用函数date_default_timezone_set, 业务不应该自己设置时区; Elvish以cityId为主要参数,业务无需关注timezone"},

  {"rule_type": "i18n", "rule_name": "php 禁用函数", "level": "error",
    "reg": '''=.*date_format\(\$''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "使用了禁用函数date_format, 请使用Elvish的 DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php 禁用函数", "level": "error",
    "reg": '''=.*date_format\(\$''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "使用了禁用函数date_format, 请使用Elvish的 DatetimeUtil::formatBy** 系列函数"},

  {"rule_type": "i18n", "rule_name": "php elvish 使用错误", "level": "warning",
    "reg": '''DatetimeUtil::.*\(.*\d*\.\d*''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "elvish参数不能是浮点数"},

  {"rule_type": "i18n", "rule_name": "php elvish 使用错误", "level": "warning",
    "reg": '''DatetimeUtil::.*\(.*float''', 
    "i18n_type": "time",
    "file_type": ".*.php",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "elvish参数不能是浮点数"},

] # end of 时间规则 php


## 时间规则 java
i18n_rules += [
  {"rule_type": "i18n", "rule_name": "java 自定义时间展示", "level": "warning",
    "reg": '''String.format\("%s[-\/]%s[-\/]%s.*Year.*Month.*Day''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能自己拼接时间展示, 推荐使用Elvish的DatetimeUtil类处理时间展示"},

  {"rule_type": "i18n", "rule_name": "java 时区相关", "level": "warning",
    "reg": '''GregorianCalendar\(\)|Calendar.getInstance\(\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不应该一直使用一个默认时区, 推荐:使用用户请求参数中的时区"},

  {"rule_type": "i18n", "rule_name": "java 时区相关", "level": "warning",
    "reg": '''TimeZone.setDefault\(.+\)|TimeZone.getDefault\(\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能使用默认时区。推荐:使用用户请求参数中的时区"},

  {"rule_type": "i18n", "rule_name": "java 时区相关", "level": "warning",
    "reg": '''(timezone|timeZone|TimeZone)\.getDisplayName\(\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "timezone.getDisplayName方法需要指定locale"},




  {"rule_type": "i18n", "rule_name": "java 时区相关", "level": "warning",
    "reg": '''(TimeZone.getTimeZone|ZoneId.of)\("\w*\/\w*"\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不应该hardcode指定某个特定时区; 推荐:应该使用用户请求中的时区"},

  {"rule_type": "i18n", "rule_name": "java 时区相关", "level": "warning",
    "reg": '''(TimeZone|timezone)\("(CST|MST|PST|EDT|CDT)"\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能使用简写的timezone格式, 因为可能存在歧义"},

  {"rule_type": "i18n", "rule_name": "java 时区相关", "level": "warning",
    "reg": '''(timezone|TimeZone).*"(GMT|UTC)(-|\+)\d+".*''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能使用UTC+8, GMT+8等格式的时区"},

  {"rule_type": "i18n", "rule_name": "java 时间运算", "level": "warning",
    "reg": '''currentTimeMillis.*\+(.*3600.*24 *\*|.*86400 *\*|.*24.+60.+60 *\*|.*60.+60.+24 *\*) *\d+''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "1天!=24小时, 不能用86400秒等方式进行时间运算"},

  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg": '''dd[-/]MM[-/]yy(yy)* HH(:mm)*(:ss)*"|"yy(yy)*[-/]MM[-/]dd HH(:mm)*(:ss)*|"MM[-/]dd HH(:mm)*(:ss)*"''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "时间展示Pattern不能写死, 推荐使用Elvish的DatetimeUtil类进行处理"},


  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg_in_func_no": '''.*\.(setTimeZone|withLocale)\(''',
    "reg": '''\.format\(\w*(TimeFormatter|time_formatter)\w*\)''', 
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "Date.format方法前面必须用 withLocale方法设置时区"},

  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg_in_func_no": '''.*\.(setTimeZone|withLocale)\(''',
    "reg": ''' LocalDateTime.parse\(.*,.*(Formatter|formatter) *\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "LocalDateTime.parse方法前面必须用 withLocale方法设置时区"},

  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg_in_func_no": '''.*\.(setTimeZone|withLocale)\(''',
    "reg": ''' LocalTime.parse\(.*,.*(Formatter|formatter) *\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "LocalDateTime.parse方法前面必须用 withLocale方法设置时区"},


  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg_in_func_no": '''.*\.(setTimeZone|withLocale)\(''',
    "reg": ''' MonthDay.parse\(.*,.*(Formatter|formatter) *\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "MonthDay.parse方法前面必须用 withLocale方法设置时区"},


  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg_in_func_no": '''.*\.(setTimeZone|withLocale)\(''',
    "reg": ''' OffsetDateTime.parse\(.*,.*(Formatter|formatter) *\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "OffsetDateTime.parse方法前面必须用 withLocale方法设置时区"},


  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg_in_func_no": '''.*\.(setTimeZone|withLocale)\(''',
    "reg": ''' OffsetTime.parse\(.*,.*(Formatter|formatter) *\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "OffsetTime.parse方法前面必须用 withLocale方法设置时区"},


  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg_in_func_no": '''.*\.(setTimeZone|withLocale)\(''',
    "reg": ''' YearMonth.parse\(.*,.*(Formatter|formatter) *\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "YearMonth.parse方法前面必须用 withLocale方法设置时区"},


  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg_in_func_no": '''.*\.(setTimeZone|withLocale)\(''',
    "reg": ''' ZonedDateTime.parse\(.*,.*(Formatter|formatter) *\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "ZonedDateTime.parse方法前面必须用 withLocale方法设置时区"},


  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg": '''DateFormat.(getDateInstance|getDateTimeInstance|getInstance|getTimeInstance)\((?!.*locale.*)[^)]*\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "getDateInstance等方法必须指定locale参数"},


  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg": '''DateFormat.(getDateInstance|getDateTimeInstance|getInstance|getTimeInstance)\((?!.*locale.*)[^)]*\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "getDateInstance方法必须指定locale参数"},

  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg": '''new SimpleDateFormat\(''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "SimpleDateFormat无法生成本地化的时间格式, 如果日期是显示给用户的，则应使用DateFormat类"},

  {"rule_type": "i18n", "rule_name": "java 时间展示风格", "level": "warning",
    "reg": '''new DateFormatSymbols\(\)''',
    "i18n_type": "time",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "new DateFormatSymbols()需要指定locale参数, 推荐 new DateFormatSymbols(locale)"},

] # end of 时间规则 java


## 货币规则 golang
i18n_rules += [
  {"rule_type": "i18n", "rule_name": "go 拼接货币符号", "level": "warning",
    "reg": '''('|")(CNY|TWD|HKD|USD|BRL|AUD|MXN|COP|JPY|CLP|PEN|CRC|USD|RUB|DOP|ARS|USD|NZD|USD|ZAR|EGP|KZT|GBP|UAH|UGX|NGN|TZS|SAR|HK\$|₡|元|£|MXN\$|円|₦|US\$|TSh|USh|R\$|RD\$|₴|₸|圜|S/|₽)('|")''', 
    "i18n_type": "currency",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock|demo)", "alert_msg": "不能硬编码货币符号"},

  {"rule_type": "i18n", "rule_name": "go 拼接货币符号", "level": "warning",
    "reg": '''('|").*%(s|v) *(CNY|TWD|HKD|USD|BRL|AUD|MXN|COP|JPY|CLP|PEN|CRC|USD|RUB|DOP|ARS|USD|NZD|USD|ZAR|EGP|KZT|GBP|UAH|UGX|NGN|TZS|SAR|HK\$|₡|元|£|MXN\$|円|₦|US\$|TSh|USh|R\$|RD\$|₴|₸|圜|S/|₽)('|")''', 
    "i18n_type": "currency",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock|demo)", "alert_msg": "不能自己拼接货币格式, 推荐: 用elvish的currencyutil类处理货币展示"},

  {"rule_type": "i18n", "rule_name": "go 拼接货币符号", "level": "warning",
    "reg": '''('|")(CNY|TWD|HKD|USD|BRL|AUD|MXN|COP|JPY|CLP|PEN|CRC|USD|RUB|DOP|ARS|USD|NZD|USD|ZAR|EGP|KZT|GBP|UAH|UGX|NGN|TZS|SAR|HK\$|₡|元|£|MXN\$|円|₦|US\$|TSh|USh|R\$|RD\$|₴|₸|圜|S/|₽) *%(s|v).*('|")''',
    "i18n_type": "currency",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock|demo)", "alert_msg": "不能自己拼接货币格式, 推荐: 用elvish的currencyutil类处理货币展示"},


  {"rule_type": "i18n", "rule_name": "go 货币符号硬编码", "level": "error",
    "reg": '''.*=.*"MXN\$" *\+''', 
    "i18n_type": "currency",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能硬编码货币符号"},

  {"rule_type": "i18n", "rule_name": "go 货币符号硬编码", "level": "error",
    "reg": '''(format|display|currency).*(CNY|TWD|HKD|USD|BRL|AUD|MXN|COP|JPY|CLP|PEN|CRC|USD|RUB|DOP|ARS|USD|NZD|USD|ZAR|EGP|KZT|GBP|UAH|UGX|NGN|TZS|SAR|HK\$|₡|元|£|MXN\$|円|₦|US\$|TSh|USh|R\$|RD\$|₴|₸|圜|S/|₽) %.*,''', 
    "i18n_type": "currency",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能硬编码货币符号"},


  {"rule_type": "i18n", "rule_name": "php 货币符号硬编码", "level": "error",
    "reg": '''.*=.*'(CNY|TWD|HKD|USD|BRL|AUD|MXN|COP|JPY|CLP|PEN|CRC|USD|RUB|DOP|ARS|USD|NZD|USD|ZAR|EGP|KZT|GBP|UAH|UGX|NGN|TZS|SAR|HK\$|₡|元|£|MXN\$|円|₦|US\$|TSh|USh|R\$|RD\$|₴|₸|圜|S/|₽) *' *\. *\$''', 
    "i18n_type": "currency",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint)", "alert_msg": "不能硬编码货币符号"},

  {"rule_type": "i18n", "rule_name": "php 货币符号硬编码", "level": "error",
    "reg": '''.*=.*"MXN\$ *" *\. *\$''', 
    "i18n_type": "currency",
    "file_type": ".*.go",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能硬编码货币符号"},


]# end of 货币规则


## 货币规则 java
i18n_rules += [
  {"rule_type": "i18n", "rule_name": "java 自己拼接货币展示格式", "level": "error",
    "reg": '''String.format\("%s *(%s|%f|%.2f)" *,[^(),]*(\$|Currency|Symbol|Huobi)[^,]*,[^,]*(amount|Amount|money|Money|bill|Bill)''', 
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能自定义货币展示格式, 推荐使用Elvish的CurrencyUtil类处理"},


  {"rule_type": "i18n", "rule_name": "java 自己拼接货币展示格式", "level": "error",
    "reg": '''String.format\("[A-Z]{0,3}\$ *(%f|%d|%s|%.2f)" *,[^,]*(amount|Amount|money|Money|bill|Bill)''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能自定义货币展示格式, 推荐使用Elvish的CurrencyUtil类处理"},


  {"rule_type": "i18n", "rule_name": "java 自己拼接货币展示格式", "level": "error",
    "reg": '''.*= *"[A-Z]{0,3}\$" *\+ *(amount|Amount|money|Money|bill|Bill) *;''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能自定义货币展示格式, 推荐使用Elvish的CurrencyUtil类处理"},

  {"rule_type": "i18n", "rule_name": "java 自己拼接货币展示格式", "level": "error",
    "reg": '''.*= *\w+\.append\("[A-Z]{0,3}\$"\)\.append\(\w*(amount|Amount|money|Money|bill|Bill)\w*\)''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能自定义货币展示格式, 推荐使用Elvish的CurrencyUtil类处理"},



  {"rule_type": "i18n", "rule_name": "java 自己拼接货币展示格式", "level": "error",
    "reg": '''.*= *\w+\.append\(\w*(Currency|Symbol|Huobi).*\)\.append\(\w*(amount|Amount|money|Money|bill|Bill)\w*\) *;''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能自定义货币展示格式, 推荐使用Elvish的CurrencyUtil类处理"},


  {"rule_type": "i18n", "rule_name": "java 自己拼接货币展示格式", "level": "error",
    "reg": '''.*= *\w+\.add\(\w*("[A-Z]{0,3}\$"|Currency|Symbol|Huobi).*\)\.add\(\w*(amount|Amount|money|Money|bill|Bill)\w*\) *;''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能自定义货币展示格式, 推荐使用Elvish的CurrencyUtil类处理"},


  {"rule_type": "i18n", "rule_name": "java 硬编码货币符号", "level": "error",
    "reg": '''.*=.*"(CNY|TWD|HKD|USD|BRL|AUD|MXN|COP|JPY|CLP|PEN|CRC|USD|RUB|DOP|ARS|USD|NZD|USD|ZAR|EGP|KZT|GBP|UAH|UGX|NGN|TZS|SAR|HK\$|₡|元|£|MXN\$|円|₦|US\$|TSh|USh|R\$|RD\$|₴|₸|圜|S/|₽) *".*(\+|\.add\(|\.append\(|\.join\()''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能硬编码写死货币符号, 推荐使用Elvish的CurrencyUtil类处理"},

  {"rule_type": "i18n", "rule_name": "java 硬编码", "level": "error",
    "reg": '''\["\w+"\] = "(CNY|TWD|HKD|USD|BRL|AUD|MXN|COP|JPY|CLP|PEN|CRC|USD|RUB|DOP|ARS|USD|NZD|USD|ZAR|EGP|KZT|GBP|UAH|UGX|NGN|TZS|SAR|HK\$|₡|元|£|MXN\$|MX\$|円|₦|US\$|TSh|USh|R\$|RD\$|₴|₸|圜|S/|₽)"''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能硬编码写死货币符号, 推荐使用Elvish的CurrencyUtil类处理"},


  {"rule_type": "i18n", "rule_name": "java 硬编码", "level": "error",
    "reg": '''\w*(format|Format|display|Display|local|Local|show|Show)\w*\([^()]*("en[-_]US"|"en[-_]AU"|"pt[-_]BR"|"es[-_]MX"|"es[-_]419"|"es[-_]CO"|"es[-_]AR"|"en[-_]CL").*,.*\)''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "不能硬编码写死locale, 推荐使用用户请求中的locale"},


  {"rule_type": "i18n", "rule_name": "java 滴分军规", "level": "error",
    "reg": '''\b(int|int32|float|float32)\b *\w*(difen|Difen|DiFen)\w*''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "命名中有difen的，数据类型应该是int64/long，数据库类型应该是bigint"},


  {"rule_type": "i18n", "rule_name": "java 滴分军规", "level": "error",
    "reg": '''if *\w*(amount|money|Amount|Money|Difen|difen|DiFen)\w* *(<|<=|>|>=) *(\d+|MAX\w+LIMIT|MAX\w+QUOTA|MAX\w+AMOUT|MAX\w+MONEY|MIN\w+LIMIT|MIN\w+QUOTA|MIN\w+AMOUT|MIN\w+MONEY)''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "货币限额不应该写死在代码中, 应该按各国汇率进行换算"},

  {"rule_type": "i18n", "rule_name": "java 滴分军规", "level": "error",
    "reg": '''(?!.*(difen|Difen|DiFen).*)String *\w*(format|Format)\w*(Amount|Bill|Money|amout|bill|money)\w*\(.*(amount|Amount|Money|money).*\).*{''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "货币util函数，参数命名必须包含difen关键词, 比如amout_difen 或者 AmoutDiFen"},


  {"rule_type": "i18n", "rule_name": "java 滴分军规", "level": "error",
    "reg": '''(?!.*(difen|Difen|DiFen|Yuan|yuan|YUAN).*).*=.*\w*(format|Format)\w*(Amount|Bill|Money|amout|bill|money)\w*\(.*(amount|Amount|Money|money).*\)''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "调用货币相关函数时， amout参数必须带 difen 标识, 比如amout_difen 或者 AmoutDiFen"},

  {"rule_type": "i18n", "rule_name": "java 滴分军规", "level": "error",
    "reg": '''(?!.*(difen|Difen|DiFen|DIFEN|_fen|_Fen).*).*CurrencyUtil\.\w*Format\w*\(.*$''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "调用货币格式化函数时, 参数名称必须包含difen, 错误:currencyUtil.format(amount), 正确:currencyUtil.format(amountDiFen)"},


  {"rule_type": "i18n", "rule_name": "java 滴分军规", "level": "error",
    "reg": '''\b((?!difen|Difen|DiFen)\w)*(amount|Amount|money|Money)((?!difen|Difen|DiFen)\w)*\b *(\+|-|\+=|-=).*(difen|Difen|DiFen)''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "货币运算时, 滴分变量和元变量 不能运算，错误: amount_1_DiFen + amount_2_Yuan, 正确: amount_1_DiFen + amount_2_DiFen"},


  {"rule_type": "i18n", "rule_name": "java 滴分军规", "level": "error",
    "reg": '''(?=\w*difen\w*)\w*amount\w* *(\+|-|\+=|-=) *(?!.*(difen|Difen|DiFen).*).*(amount|Amount|Money|money).*''',
    "i18n_type": "currency",
    "file_type": ".*.java",
    "exclude": "(log|test|nolint|no_lint|no-lint|mock)", "alert_msg": "货币运算时, 滴分变量和元变量 不能运算，错误: amount_1_DiFen + amount_2_Yuan, 正确: amount_1_DiFen + amount_2_DiFen"},

] # end of 货币 java



for i in i18n_rules:
    # 修正\b 转移字符
    if "\b" in i["reg"]:
        i["reg"] = i["reg"].replace("\b", "\\b")
    if "line_to_lower" not in i:
        i["line_to_lower"] = 0
    for k in i:
        if i[k] == " ":
            i[k] = ""


# 遍历目录， 返回该目录下所有文件
def scan_dir(path):
    file_names = []
    for root, dirs, files in os.walk(path):
        for f in files:
            full_path = os.path.join(root, f)
            file_names.append(full_path)

    return file_names

def need_ignore(f):
    ignore_files = [
        "/.",
        "output/",
        "tools/",
        "mock",
        "Mock",
        ".git/",
        "vendor/",
        "app/Classes/ClientFactory/",
        ".sh",
        "/test_",
        "go.mod",
        "go.sum",
        "Makefile",
        "log/",
        "/test/",
        "logs/",
        "bin/",
        "Test.php",
        "Test.go",
        "_test.go",
        "Test.java",
        "_test.java",
    ]
    only_files = [
        ".go",
        ".php",
        ".java",
        ".cpp",
    ]

    for i in ignore_files:
        if i in f:
            return True

    for i in only_files:
        if f[-1*len(i):] == i:
            return False
    if len(only_files) > 0:
        return True
    return False

def get_key(d, key, default=""):
    try:
        return d[key]
    except:
        return default

class LineParser():
    def __init__(self):
        self.line_no = 0
        self.line = ""
        self.l = ""         # 等号左边内容
        self.llist = []     # 等号左边, 变量列表
        self.r = ""         # 等号右边的内容
        self.filename = ""
        self.funcname = ""
        self.funcline = ""
        self.func_line_no = ""
        self.up3 = []
        self.down3 = []
        self.sign = ""     # 存储到map里的key签名

def near_lines(context, line_no, lines, num):
    from_line = line_no + num
    ret = []
    if num > 0:
        pos = line_no
        while len(ret) < num:
            pos = pos + 1
            if pos >= len(lines):
                break
            if lines[pos].strip() == "":
                continue
            if is_comment(context, lines[pos]):
                continue
            ret.append(lines[pos])

    if num < 0:
        pos = line_no
        while len(ret) < -1 * num:
            pos = pos - 1
            if pos < 0: 
                break
            if lines[pos].strip() == "":
                continue
            if is_comment(context, lines[pos]): 
                continue
            ret.append(lines[pos])
    return ret

def language_type(context):
    if ".go" == context["filename"][-3:]:
        return "go"
    if ".php" == context["filename"][-4:]:
        return "php"
    if ".cpp" == context["filename"][-4:]:
        return "cpp"
    if ".java" == context["filename"][-5:]:
        return "java"
    if ".c" == context["filename"][-2:]:
        return "cpp"
    return "other"


func_start_pattern = {
    "go": [
        r" *func +(.+?)\(",  # (.+?)提取函数名
    ],

    "php": [
        r"^ *(public|private) *(static){0,1} *function *(.+?)\(",
    ],

    "cpp": [
    ],

    "java": [
        r'''^ *(private|public) *(static)* *[\w.]* *(\w+?) *\(.*\) *{ *$''',
        r'''^ *\b\w{3,}\b *\b\w{2,}\b *\(.*\) *{ *$''',
    ],

    "other": [
    ],
}

def is_new_func_start(context, line):
    lang = language_type(context) 
    func_name = ""
    for i in func_start_pattern[lang]:
        match = re.search(i, line)
        if match:
            func_name = match.group() 
            return True, func_name
    return False, func_name


def split_line(line, context):
    lang = language_type(context)
    if lang == "go":
        if ":=" in line:
            return line.split(":=")
        if " = " in line:
            return line.split(" = ")
        if "err = " in line:
            return line.split("err =")
        if "err=" in line:
            return line.split("err=")
        if ",_ = " in line:
            return line.split(",_ = ")
    return []

def ParseOneLine(line, context, var_defines):
    p = LineParser()
    p.line_no = context["line_no"]
    p.line = line 
    p.l = ""
    p.r = ""
    p.llist = []
    p.filename = context["filename"]
    p.funcname = context["funcname"]
    p.funcline = context["funcline"]
    p.func_line_no = context["func_line_no"]
    p.up3 = context["up3"]
    p.down3 = context["down3"]
    p.sign = ""

    try:
        split = split_line(line, context)
        split.append("")
        split.append("")
        p.l = split[0]
        p.r = split[1] 
        p.llist = p.l.split(",")
        for i in range(0, len(p.llist)):
            p.llist[i] = p.llist[i].strip()
            p.llist[i] = p.llist[i].replace("\t", "")

        # 如果有新变量,更新 var_defines 
        for i in p.llist:
            if i in ["err", "_", "errcode", "succ"]:
                continue
            var_defines[i] = p
    except Exception as e:
        print(e)
        pass

    return p


def ParseOneFile(filename):
    fp = open(filename, "r")    
    fp = fp.read()
    lines = fp.split("\n")

    parsed_lines = []
    var_defines = {}
    context = {
        "filename": filename,
        "line_no": 0,
        "up3": [],
        "down3": [],
        "funcname": "",
        "funcline": "",
        "func_line_no": 0,
    }

    for i in range(0, len(lines)):
        context["line_no"] = i + 1
        context["lang"] = language_type(context) 
        context["up3"] = near_lines(context, i, lines, -3) 
        context["down3"] = near_lines(context, i, lines, 4) 

        is_new_func, func_name =  is_new_func_start(context, lines[i])
        if is_new_func:
            context["funcname"] = func_name 
            context["funcline"] = lines[i]
            context["func_line_no"] = i + 1

        p = ParseOneLine(lines[i], context, var_defines)
        parsed_lines.append(p)

    return lines, parsed_lines, var_defines, context

def is_comment(context, text):
     # 如果是注释
    if context["lang"] == "go":
        sl = text.strip()
        if sl[0:2] == "//":
            return True
        if sl[0:2] == "/*":
            return True
        if sl[0] == "*":
            return True

    if context["lang"] == "php":
        sl = text.strip()
        if sl[0:2] == "//":
            return True
        if sl[0:2] == "/*":
            return True
        if sl[0] == "*":
            return True
    if context["lang"] == "java":
        sl = text.strip()
        if sl[0:2] == "//":
            return True
        if sl[0:2] == "/*":
            return True
        if sl[0] == "*":
            return True

def ignore_lines(context, l):
    line = l.line
    if len(line) <= 6:
        return True
    strip_line = line.strip()
    if strip_line == "":
        return True
    if len(strip_line) <= 6:
        return True
    if "}" == strip_line:
        return True
    if "return" == strip_line:
        return True

    # 如果是注释
    if is_comment(context, l.line):
        return True

    # json数据
    if '":{"' in l.line or '": {"' in l.line:
        return True
    return False

def exclude_global(global_exclude, lines, lineparser):
    for i in global_exclude:
        if i == "":
            continue
        # 本行内容有 nolint时
        if i in lineparser.line:
            return True

        # 上面一行有nolint时
        if lineparser.line_no >= 2 and lineparser.line_no < len(lines):
            if i in lines[lineparser.line_no - 2]:
                return True
        # 函数顶部有 nolint时
        if i in lineparser.funcline:
            return True
        # 函数上一行有nolint
        if lineparser.func_line_no >= 2:
            if i in lines[lineparser.func_line_no - 2]:
                return True
        if "beijing" in lineparser.funcline.lower():
            return True
        if "bj_time" in lineparser.funcline.lower():
            return True
        if "bjtime" in lineparser.funcline.lower():
            return True

    return False 

def exclude_special(parsed_line, rule, context):
    if "exclude" not in rule:
        return False
    if rule["exclude"] == "":
        return False
    match = re.search(rule["exclude"], parsed_line.line)
    if match:
        return True
    if "|" in rule["exclude"]:
        exrule = rule["exclude"].split("|")
        for i in exrule:
            if i in parsed_line.line:
                return True
    return False

def exclude_filetype(parsed_line, rule, context):
    try:
        if 'file_type' not in rule:
            return False
        if rule["file_type"] in ["", "*", ".*", "any", "ANY", "all", "ALL"]:
            return False
        match = re.search(rule["file_type"], context['filename'])
        if match:
            return False
        return True
    except:
        return False

def read_rules(conffile):
    # 内置规则
    return i18n_rules

    # 从文件加载规则
    rules = []
    fp = open(conffile, "r")
    fc = fp.read()
    js = json.loads(fc)
    rules += js
    return rules

def process_line_before_match(reg, l):
    # 去掉注释
    if True:
        line_code = l.line.split("//")
        line_code = line_code[0]

    # 转换为小写
    if True:
        if reg["line_to_lower"] == 1:
            line_code = line_code.lower()

    return line_code

def filter_reg_in_func_no(context, reg_rule, this_line, all_lines):
    if get_key(reg_rule, "reg_in_func_no") == "":
        return True
    # 从函数开始行到本行, 进行遍历
    for i in range(this_line.func_line_no, this_line.line_no):
        match = re.search(get_key(reg_rule, "reg_in_func_no"), all_lines[i].line)
        if match:
            return False
    return True

def filter_reg_up3(context, reg_rule, this_line, all_lines):
    if get_key(reg_rule, "reg_up3") == "":
        return True
    for k in this_line.up3:
        match = re.search(get_key(reg_rule, "reg_up3"), k)
        if match:
            return True
    return False

def filter_reg_up3_no(context, reg_rule, this_line, all_lines):
    if get_key(reg_rule, "reg_up3_no") == "":
        return True
    for k in this_line.up3:
        match = re.search(get_key(reg_rule, "reg_up3_no"), k)
        if match:
            return False
    return True

def filter_reg_down3(context, reg_rule, this_line, all_lines):
    if get_key(reg_rule, "reg_down3") == "":
        return True
    for k in this_line.up3:
        match = re.search(get_key(reg_rule, "reg_down3"), k)
        if match:
            return True
    return False

def filter_reg_down3_no(context, reg_rule, this_line, all_lines):
    if get_key(reg_rule, "reg_down3_no") == "":
        return True
    for k in this_line.down3:
        match = re.search(get_key(reg_rule, "reg_down3_no"), k)
        if match:
            return False
    return True



g_scan_count = {"count": 0}

def run_checker(i18n_checker_rules, global_exclude, context, lines, parsed_lines, var_defines):
    detect_result = []
    for l in parsed_lines:
        # 忽略一些空行
        if ignore_lines(context, l):
            continue
        if exclude_global(global_exclude, lines, l):
            continue

        # 遍历所有 checker rules 正则规则
        for reg in i18n_checker_rules:
            # 规则中指定排除一些情况
            if exclude_special(l, reg, context):
                continue
            # 只扫描指定的文件类型, 提升性能
            if exclude_filetype(l, reg, context):
                continue

            line_code = process_line_before_match(reg, l)

            match = re.search(reg["reg"], line_code)
            if match:

                if filter_reg_up3_no(context, reg, l, parsed_lines) == False:
                    print("bbbbbbbbb", 1)
                    continue
                if filter_reg_up3(context, reg, l, parsed_lines) == False:
                    print("bbbbbbbbb", 2)
                    continue
                if filter_reg_down3(context, reg, l, parsed_lines) == False:
                    print("bbbbbbbbb", 3)
                    continue
                if filter_reg_down3_no(context, reg, l, parsed_lines) == False:
                    print("bbbbbbbbb", 4)
                    continue
                if filter_reg_in_func_no(context, reg, l, parsed_lines) == False:
                    continue

            if match:
                msg = {
                    "level": reg["level"],
                    "rule_name": reg["rule_name"],
                    "alert_msg": reg["alert_msg"],
                    "line": l.line,
                    "line_no": l.line_no,
                    "file_name": l.filename,
                    "func_name": l.funcname,
                    "reg_hit":match.group(),
                    "reg": reg["reg"],
                    "code_up_down": [],
                    "i18n_type": reg["i18n_type"],
                }

                msg["code_up_down"].append("%s %s" % (l.func_line_no, l.funcline))
                msg["code_up_down"].append("...")
                for i in range(0, len(l.up3)):
                    msg["code_up_down"].append("%s %s" % (l.line_no - len(l.up3) + i, l.up3[i]))
                # 红色 颜色 白色
                msg["code_up_down"].append("%s \033[41;37m%s\033[0m [** i18n_checker_alert **]" % (l.line_no, l.line))
                msg["code_up_down"].append("    ==> [i18n reason]: \033[35m%s\033[0m" % (msg["alert_msg"]))
                for i in range(0, len(l.down3)):
                    msg["code_up_down"].append("%s %s" % (l.line_no + i + 1, l.down3[i]))

                detect_result.append(msg)
                break
    # 输出结果
    for i in range(0, len(detect_result)):
        g_scan_count["count"] += 1
        r = detect_result[i]
        print("-" * 30)
        print("[- %s -] [%s] [%s]" % (g_scan_count["count"], r["level"], r["alert_msg"]))
        print("文件路径: %s:%s" % (r["file_name"], r["line_no"]))
        print("规则:%s %s" % (r["rule_name"], r["reg"]))
        for k in r["code_up_down"]:
            print("%s" % (k))
        print("\n")

    return detect_result

def check_dir(path):
    file_names = scan_dir(path)
    i18n_checker_rules = read_rules("/Users/guojianyong/ssd/ssd/go/src/icu4g/tools/i18n_checker_rules/i18n_checker_rules.conf")
    i18n_checker_global_exclude = [
        "Logger|log|test|nolint|no_lint|no-lint",
    ]
    global_exclude = []
    print("如何加扫描白名单: 共4种方法, [1]本行加注释nolint, [2]本行上面加注释nolint, [3]本函数行加nolint, [4]本函数上一行加nolint")
    for i in i18n_checker_global_exclude:
        global_exclude += i.split("|") 

    detect_result = []
    for i in file_names:
        try:
            if need_ignore(i):
                continue
            lines, parsed_lines, var_defines, context = ParseOneFile(i)
            tmp_result = run_checker(i18n_checker_rules, global_exclude, context, lines, parsed_lines, var_defines)
            detect_result.extend(tmp_result)
        except Exception as e:
            print(e)
            pass
    
    # 打印报告
    print("扫描总问题数:%d" % (len(detect_result)))
    i18n_type_num = {} #i18n问题域的问题数量
    rule_name_num = {} #具体规则的问题数量
    for i in range(0, len(detect_result)):
      r = detect_result[i]
      i18n_type_num[r["i18n_type"]] = i18n_type_num.get(r["i18n_type"], 0) + 1
      rule_name_num[r["rule_name"]] = rule_name_num.get(r["rule_name"], 0) + 1
    for i18n_type_key in i18n_type_num.keys():
      print("i18n问题域：%s,问题数量:%d" % (i18n_type_key, i18n_type_num[i18n_type_key]))
    for rule_name_key in rule_name_num.keys():
      print("具体问题：%s,问题数量:%d" % (rule_name_key, rule_name_num[rule_name_key]))
    pass


if __name__ == "__main__":

    dir_path = "./"
    dir_path = "./common/util"

    if len(sys.argv) == 1:
        print("Usage: python %s some_dir [-h, --genconf]" % (sys.argv[0]))
        print("example 1: python %s ./" % (sys.argv[0]))
        print("example 2: python %s /home/xiaoju/git/coin" % (sys.argv[0]))
        print("Contact: 郭建勇")
        exit(0)
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--h", "-help", "help", "--help"]:
        print("Usage: python %s some_dir [-h, --genconf]" % (sys.argv[0]))
        print("example 1: python %s ./" % (sys.argv[0]))
        print("example 2: python %s /home/xiaoju/git/coin" % (sys.argv[0]))
        print("Contact: 郭建勇")
        exit(0)

    if len(sys.argv) > 1 and sys.argv[1] in ["--genconf"]:
        # 输出到配置
        for i in range(0, len(i18n_rules)):
            i18n_rules[i]["id"] = i+1 
            i18n_rules[i]["level"] = "warning"

        ss = json.dumps(i18n_rules, ensure_ascii=False, indent=2)
        fp = open("./i18n_checker_rules.conf", "w+")
        fp.write(ss)
        fp.close()
        print("生成配置文件: ./i18n_checker_rules.conf")
        exit(0)

    if len(sys.argv) > 1:
        dir_path = sys.argv[1]
    check_dir(dir_path)

