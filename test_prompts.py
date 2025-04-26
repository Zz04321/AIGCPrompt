import json
import uuid
import requests
import time
import os
import anthropic
from prompts import prompts

# API参数
TEXT_API_URL_SUBMIT = "http://120.241.200.233/submit_task"
TEXT_API_URL_RESULT = "http://120.241.200.233/get_result"
TEXT_API_APPID = "10117"

# 请在此处填写邮件中获取的队伍ID作为appsecret
APPSECRET = "在此填写队伍ID"

# 请在此处填写您的Anthropic API密钥
ANTHROPIC_API_KEY = "在此填写您的Anthropic API密钥"

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
        
        if result.get("status") == "success":
            print(f"提交成功，UUID: {request_uuid}")
            print(f"剩余配额: {result.get('quota_remaining')}")
            return request_uuid
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
            response = requests.post(TEXT_API_URL_RESULT, json=params)
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
                "content": "你是一个专业的学术论文写作助手，帮助用户创作高质量的学术内容。"
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

def generate_with_claude(prompt):
    """使用Claude API生成内容"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    try:
        message = client.messages.create(
            model="claude-3-7-sonnet-20240307",
            max_tokens=4000,
            system="你是一个专业的学术论文写作助手，帮助用户创作高质量的学术内容。",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"生成内容出错: {e}")
        return None

def test_prompt(prompt_index, model_name="claude-3-7-sonnet-20240307", user_id="your_team_id"):
    """测试特定提示词，并将结果保存到文件"""
    prompt = prompts[prompt_index]
    print(f"\n测试提示词 #{prompt_index + 1}")
    print("="*50)
    
    # 使用Claude生成内容
    print("正在生成内容...")
    response = generate_with_claude(prompt)
    
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
        result = "绕过成功" if confidence < 0.5 else "绕过失败"
        print(f"检测结果 - AI置信度: {confidence}")
        print(f"检测结果 - {result}")
        
        # 记录测试结果
        with open("test_results.txt", "a", encoding="utf-8") as f:
            f.write(f"提示词 #{prompt_index + 1} - 置信度: {confidence} - {result}\n")
        
        return confidence
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