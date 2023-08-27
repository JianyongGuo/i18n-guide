```
1. I18N 最佳实践
提供I18N出海技术的最佳实践，聚焦领域知识的准确性和落地可行性。


2. I18N 敏感函数
    2.1. 时间类
        CASE: 时区相关/ FixedZone(), 不能一直用默认时区
        CASE: 时区相关/ LoadLocation(), 不能指定某个特定的时区
        CASE: 时区相关/ Format(), 时间转换时未指定时区
        CASE: 时区相关/ Zone(), 不建议获取并操作utc_offset
        CASE: 时区相关/ LoadLocation(), timezone应该使用完整格式,不能使用简写
        CASE: 时区相关/ LoadLocation(), 不能使用UTC+8、GMT+8 等格式的时区
        CASE: 时区相关/ LoadLocation(), 不能按国家粒度进行时间计算,必须按时区粒度
        CASE: 时区相关/ LoadLocation(), 自定义时区数据路径
        CASE: 时间转换/ Date.Unix(), Date转时间戳 必须保证时区数据库是最新版本
        CASE: 时间转换/ Format(), 时间戳格式化时应该指定timezone或者city_id
        CASE: 时间转换/ Format(), 必须保证时区数据库是最新版本
        CASE: 时间转换/ Day(), 时间戳和Date转换时,必须指定时区
        CASE: 时间转换/ Date(), time.Date对象应该带时区参数
        CASE: 时间反转/ Parse(), 时间字符串转时间戳时, 应该指定timezone或者city_id
        CASE: 时间运算/ AddDate(), 1天 != 24小时
        CASE: 时间运算/ AddDate(), 定时任务的幂等性
        CASE: 时间运算/ AddDate(), 未来时间不能用86400方式计算
        CASE: 时间运算/ AddDate(), 不能用86400, 判断是否是一天的开始
        CASE: 时间运算/ AddDate(), 关于未来时间、过去时间需注意
        CASE: 时间运算/ Sub(), 计算两个时间的间隔多久
        CASE: 日历相关/ Date(), 获取一天的开始时间
        CASE: 日历相关/ Date(), 获取一天的结束时间
        CASE: 日历相关/ Date(), 获取一周的开始时间戳
        CASE: 日历相关/ Date(), 判断是否属于同一天

3. I18N展示格式
    3.1 时间类
        CASE: 时间展示风格/ 不能使用 Sprintf 拼接 时间格式
        CASE: 时间展示风格/ 不能用 string 加号拼接 时间格式
        CASE: 时间展示风格/ Format时使用的Pattern错误
        CASE: 时间展示风格/ 时间Pattern不能写死成 "2006-01-02 15:04:05"
        CASE: 时间展示风格/ 不应该定制时间格式
        CASE: 时间段相关/ 时间段风格

```
