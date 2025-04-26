注意
图像、文本接口，都采用了离线推理的方式，需要先提交任务，然后查看结果（注意结果只能取一次，请注意保存）。由于是异步响应，因此在提交之后可能无法立刻得到返回结果。此外API的提交上限为每天2000次，调用所需要使用的appsecret为各队伍在邮件中得到的队伍ID。
图像
接口地址："http://221.181.81.213"
appid： 7000110

提交任务
接口地址：http://221.181.81.213/submit_task
请求参数
参数名	描述
appid	str, 应用id
appsecret	str, 应用密钥
uuid	str, 36位随机字符，用于标识请求
imageBase64	str, 待检测文本
uuid可使用python中的str(uuid.uuid4())快速获（需要导入uuid库）。
响应字段
字段名	描述
status	str, 结果状态
uuid	str, 用户提交的uuid
quota_remaining	int, 当日用户可用访问次数
若提交成功，返回结果示例：
 
获取任务结果
接口地址：http://221.181.81.213/get_result
请求参数
参数名	描述
appid	str, 应用id
appsecret	str, 应用密钥
uuid	str, 36位随机字符，用于标识请求
响应字段
字段名	描述
status	str, 结果状态
result	dict
    status	str, 模型推理状态
    uuid	str, 用户提交的任务uuid
    confidence	float, AI置信度
    message	str, 一般为空，模型推理错误时为错误原因
error	str, 一般为空，接口错误时为原因
示例代码（curl）
1.	提交检测任务
 

2.	获取任务结果
 

文本
提交检测任务
接口地址：http://120.241.200.233/submit_task
appid： 10117
请求参数
参数名	描述
appid	str, 应用id
appsecret	str, 应用密钥（队伍ID，区别大小写）
uuid	str, 36位随机字符，用于标识请求
text	str, 待检测文本

响应字段
字段名	描述
status	str, 结果状态
uuid	str, 用户提交的uuid
quota_remaining	int, 当日用户可用访问次数

获取任务结果
接口地址：http://120.241.200.233/get_result
请求参数
参数名	描述
appid	str, 应用id
appsecret	str, 应用密钥
uuid	str, 36位随机字符，用于标识请求
响应字段

字段名	描述
status	str, 结果状态 可能的值['completed','waiting']
result	dict
    status	str, 模型推理状态
    uuid	str, 用户提交的任务uuid
    confidence	float, AI置信度
    message	str, 一般为空，模型推理错误时为错误原因
error	str, 一般为空，接口错误时为原因

示例代码（curl）
1.	提交检测任务
请求
 
响应
 
2.	获取任务结果
请求
 
响应