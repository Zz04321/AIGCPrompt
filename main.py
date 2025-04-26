import json
import uuid
import requests
import time
import os

# API参数
TEXT_API_URL_SUBMIT = "http://120.241.200.233/submit_task"
TEXT_API_URL_RESULT = "http://120.241.200.233/get_result"
TEXT_API_APPID = "10117"

# 请在此处填写邮件中获取的队伍ID作为appsecret
APPSECRET = "在此填写队伍ID"

def submit_text_detection(text):
    """提交文本检测任务"""
    request_uuid = str(uuid.uuid4())
    params = {
        "appid": TEXT_API_APPID,
        "appsecret": APPSECRET,
        "uuid": request_uuid,
        "text": text
    }
    
    response = requests.post(TEXT_API_URL_SUBMIT, json=params)
    result = response.json()
    
    if result.get("status") == "success":
        print(f"提交成功，UUID: {request_uuid}")
        print(f"剩余配额: {result.get('quota_remaining')}")
        return request_uuid
    else:
        print(f"提交失败: {result}")
        return None

def get_detection_result(request_uuid):
    """获取检测任务结果"""
    params = {
        "appid": TEXT_API_APPID,
        "appsecret": APPSECRET,
        "uuid": request_uuid
    }
    
    for _ in range(10):  # 最多尝试10次
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

def test_prompt(prompt, model_name="claude-3-7-sonnet-latest", user_id="your_team_id"):
    """测试提示词，并将结果保存到文件"""
    # 这里应该是实际调用模型API获取响应
    # 在此示例中，我们只是模拟一个响应
    response = "这里是模型生成的响应文本。在实际使用时，应该替换为真实的模型API调用结果。"
    
    # 保存提示词和响应
    os.makedirs("submissions", exist_ok=True)
    filename = f"submissions/submit_{int(time.time())}.json"
    save_prompt_result(prompt, response, model_name, user_id, filename)
    
    # 提交检测
    request_uuid = submit_text_detection(response)
    if request_uuid:
        confidence = get_detection_result(request_uuid)
        print(f"检测结果 - AI置信度: {confidence}")
        print(f"检测结果 - {'绕过成功' if confidence < 0.5 else '绕过失败'}")
        return confidence
    return None

if __name__ == "__main__":
    # 示例提示词
    example_prompt = """
    请撰写一篇关于人工智能在医疗领域应用的学术论文摘要，重点讨论AI在医学影像分析中的优势和挑战。
    """
    
    test_prompt(example_prompt) 