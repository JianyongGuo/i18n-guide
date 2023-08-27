# 为全球化技术一起做贡献，让出海更简单

欢迎为本项目贡献内容，建议在为项目作出贡献时，阅读以下指南。

### I. Commit Mesage 编写指引

为便于索引，Commit Message应包括三个部分：Header（必需），Body（可选）和 Footer（可选）。

```html
<type>(<scope>): <subject>
// 空一行
<body>
// 空一行
<footer>
```

**Header 部分**只有一行，包括三个字段：type（必需）、scope（可选）和subject（必需）。

> type 用于说明 commit 的类别，可使用下面3个标识：<br/>
> 
> - add: 添加新规范语言或条目<br/>
> - fix: 修订内容<br/>
> - chore: 非指南文档本身或相关辅助工具的变动<br/>
> 
> scope 用于指定 commit 影响的范围，包括对应的语言及其条目编号；如：go/1.1.1。
> 
> subject是 commit 目的的简短描述。

**Body 部分**是对本次 commit 的详细描述。

**Footer 部分**关闭 Issue。如果当前 commit 针对某个issue，可以在 Footer 部分关闭这个 issue 。

一个完整的示例如下：

```html
fix(go/1.1.1): 修订条目内容
 
- 修正代码示例缩进问题
 
Close #1
```

### II. CASE 编写指引

为便于理解与管理，提交问题或建议时，参考以下格式：

```
<标题> 块：以CASE: 开头
<reason> 块：解释为什么会错用，会造成什么影响，以三个反斜杠包裹

<bad>  块： 展示bad代码和good代码示例，以三个反斜杠包裹
<good>

<checker_rule> 块：用于自动提取checker规则，内容是yaml格式，以三个反斜杠包裹，示例如下：
checker_rule:
  # 命中哪些敏感关键词
  reg: .*Format*
  # 给用户提示什么信息，指导用户修正代码
  alert_msg: '不能自定义时间格式'
  # 问题的分级，取值 0: Fatal类致命错误；1：比较严重，但不致命，比如体验类；2：影响较小，某些场景会造成影响的
  level: 1
  # 排除哪些关键词, 同一行内如果包含这些关键词的任何一个，扫描报告就不会包含此问题
  exclude: (log|test|nolint|mysql)
```

<br>

**一个完整的CASE示例如下**：

CASE: 不能使用Sprintf拼接 时间格式

```
// reason: 不同国家，时间展示规则不同:
CN(中国): 2019-12-31 01:59:59
BR(巴西): 31/12/2019 01:59:59
```

```
// bad: 使用 Sprint + %v或者%s拼接，期望得到 2022-11-24 17:03:44
now_time, _ := fmt.Sprintf("%v-%v-%v %v:%v:%v", year, month, day, hour, mintue, second)

// good: 
timezone, _ := time.LoadLocation("America/Tijuana")
now_time:= time.Now().In(timezone).Format("2006-01-02 15:04:05")
```

```yaml
checker_rule:
  reg: .*"%v-%v-%v %v:%v:%v.*
  alert_msg: '不能自定义时间格式, 慎用:time.Format(2006-01-02 15:04:05) --> 推荐:请用Elvish的datetimeutil.FormatBy**系列方法'
  level: 1
  exclude: (log|test|nolint|no_lint|no-lint)
```










