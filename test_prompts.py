import json
import uuid
import requests
import time
import os
from openai import OpenAI
from prompts import prompts
import httpx

# API参数
TEXT_API_URL_SUBMIT = "http://120.241.200.233/submit_task"
TEXT_API_URL_RESULT = "http://120.241.200.233/get_result"
TEXT_API_APPID = "10117"

# 请在此处填写邮件中获取的队伍ID作为appsecret
APPSECRET = "028faef5e5602a047fd4230863002c08"

# 请在此处填写您的DeepSeek API密钥
DEEPSEEK_API_KEY = "sk-5365b696440a4efbadc3e04c12002435"

def submit_text_detection(text):
    """提交文本检测任务"""
    request_uuid = str(uuid.uuid4())
    params = {
        "appid": TEXT_API_APPID,
        "appsecret": APPSECRET,
        "uuid": request_uuid,
        "text": text
    }
    
    try:
        response = requests.post(TEXT_API_URL_SUBMIT, json=params)
        result = response.json()
        
        # 修改判断逻辑，接受'submitted'状态
        if result.get("status") in ["success", "submitted"]:
            print(f"提交成功，UUID: {request_uuid}")
            print(f"剩余配额: {result.get('quota_remaining')}")
            # 返回API响应中的UUID，如果不存在则使用本地生成的UUID
            return result.get("uuid", request_uuid)
        else:
            print(f"提交失败: {result}")
            return None
    except Exception as e:
        print(f"提交出错: {e}")
        return None

def get_detection_result(request_uuid):
    """获取检测任务结果"""
    params = {
        "appid": TEXT_API_APPID,
        "appsecret": APPSECRET,
        "uuid": request_uuid
    }
    
    for _ in range(10):  # 最多尝试10次
        try:
            # 使用GET请求而不是POST
            response = requests.get(
                TEXT_API_URL_RESULT, 
                params=params  # 使用params参数而不是json参数
            )
            result = response.json()
            
            if result.get("status") == "completed":
                confidence = result.get("result", {}).get("confidence", 0)
                print(f"检测完成，AI置信度: {confidence}")
                return confidence
            elif result.get("status") == "waiting":
                print("结果尚未准备好，等待5秒...")
                time.sleep(5)
            else:
                print(f"获取结果失败: {result}")
                return None
        except Exception as e:
            print(f"获取结果出错: {e}")
            return None
    
    print("检测超时")
    return None

def save_prompt_result(prompt, response, model, user_id, filename):
    """保存提示词和响应到JSON文件"""
    data = {
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的学术论文写作助手，帮助用户创作高质量的学术内容，请你模仿人类写作。"
            },
            {
                "role": "user",
                "content": prompt
            },
            {
                "role": "assistant",
                "content": response
            }
        ],
        "model": model,
        "user": user_id
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已保存到文件: {filename}")

def generate_with_deepseek(prompt):
    """使用DeepSeek API生成内容"""
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY, 
        base_url="https://api.deepseek.com",
        http_client=httpx.Client()
    )
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # 使用DeepSeek-V3模型
            messages=[
                {"role": "system", "content": "你是一个专业的学术论文写作助手，帮助用户创作高质量的学术内容。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"生成内容出错: {e}")
        return None

def test_prompt(prompt_index, model_name="deepseek-chat", user_id="your_team_id"):
    """测试特定提示词，并将结果保存到文件"""
    prompt = prompts[prompt_index]
    print(f"\n测试提示词 #{prompt_index + 1}")
    print("="*50)
    
    # 使用DeepSeek生成内容
    print("正在生成内容...")
    response = generate_with_deepseek(prompt)
    
    if not response:
        print("生成内容失败")
        return None
    
    print(f"生成内容长度: {len(response)} 字符")
    
    # 保存提示词和响应
    os.makedirs("submissions", exist_ok=True)
    filename = f"submissions/submit_{prompt_index + 1}.json"
    save_prompt_result(prompt, response, model_name, user_id, filename)
    
    # 提交检测
    print("提交检测中...")
    request_uuid = submit_text_detection(response)
    if request_uuid:
        confidence = get_detection_result(request_uuid)
        
        # 添加None值检查
        if confidence is not None:
            result = "绕过成功" if confidence < 0.5 else "绕过失败"
            print(f"检测结果 - AI置信度: {confidence}")
            print(f"检测结果 - {result}")
            
            # 记录测试结果
            with open("test_results.txt", "a", encoding="utf-8") as f:
                f.write(f"提示词 #{prompt_index + 1} - 置信度: {confidence} - {result}\n")
            
            return confidence
        else:
            print("未能获取有效的检测结果")
            return None
    return None

def test_all_prompts(start_index=0, end_index=None):
    """测试所有提示词"""
    if end_index is None:
        end_index = len(prompts)
    
    results = []
    
    for i in range(start_index, end_index):
        result = test_prompt(i)
        results.append({"index": i, "confidence": result, "success": result < 0.5 if result is not None else False})
        time.sleep(5)  # 避免API请求过于频繁
    
    # 打印总结
    success_count = sum(1 for r in results if r["success"])
    print("\n测试总结")
    print("="*50)
    print(f"测试提示词数量: {len(results)}")
    print(f"成功绕过数量: {success_count}")
    print(f"成功率: {success_count/len(results)*100:.2f}%")
    
    # 保存总结结果
    with open("test_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "total": len(results),
            "success": success_count,
            "success_rate": success_count/len(results),
            "results": results
        }, f, indent=2)
    
    return results

if __name__ == "__main__":
    # 创建测试结果文件
    with open("test_results.txt", "w", encoding="utf-8") as f:
        f.write("AI检测绕过测试结果\n")
        f.write("="*50 + "\n")
    
    # 可以选择测试单个提示词或者多个提示词
    # test_prompt(0)  # 测试第一个提示词
    
    # 测试所有提示词
    test_all_prompts()
    
    # 也可以指定范围测试部分提示词
    # test_all_prompts(0, 5)  # 测试前5个提示词 