import os
import json
import shutil
import zipfile

def analyze_results():
    """分析测试结果并输出统计信息"""
    if not os.path.exists("test_summary.json"):
        print("未找到测试结果摘要文件")
        return None
    
    with open("test_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
    
    print("测试结果分析")
    print("=" * 50)
    print(f"总测试数量: {summary['total']}")
    print(f"成功绕过数量: {summary['success']}")
    print(f"成功率: {summary['success_rate']*100:.2f}%")
    
    # 按照成功率对提示词进行排序
    successful_prompts = [r for r in summary["results"] if r["success"]]
    successful_prompts.sort(key=lambda x: x["confidence"])
    
    print("\n成功绕过的提示词 (按置信度从低到高排序):")
    for i, p in enumerate(successful_prompts):
        print(f"{i+1}. 提示词 #{p['index']+1} - 置信度: {p['confidence']}")
    
    return summary

def create_final_submission(team_id, selected_indices=None):
    """
    创建最终提交文件
    
    Args:
        team_id: 队伍ID
        selected_indices: 选择的提示词索引列表 (从0开始)，如果为None则使用所有成功绕过的提示词
    """
    if not os.path.exists("submissions"):
        print("未找到submissions目录")
        return
    
    # 创建提交目录
    os.makedirs(f"final_submission_{team_id}", exist_ok=True)
    submission_files = []
    
    if selected_indices is None:
        # 如果没有指定，使用所有成功绕过的提示词
        summary = analyze_results()
        if not summary:
            return
        
        successful_prompts = [r["index"] for r in summary["results"] if r["success"]]
        
        # 如果成功的提示词少于20个，也可以选择一些接近成功的提示词
        if len(successful_prompts) < 20:
            unsuccessful_prompts = [r["index"] for r in summary["results"] if not r["success"]]
            unsuccessful_prompts.sort(key=lambda i: next(r["confidence"] for r in summary["results"] if r["index"] == i))
            selected_indices = successful_prompts + unsuccessful_prompts[:20-len(successful_prompts)]
        else:
            # 如果超过20个成功的提示词，选择置信度最低的20个
            successful_prompts.sort(key=lambda i: next(r["confidence"] for r in summary["results"] if r["index"] == i))
            selected_indices = successful_prompts[:20]
    
    # 复制选定的提交文件到最终提交目录
    for i, idx in enumerate(selected_indices):
        source_file = f"submissions/submit_{idx+1}.json"
        if os.path.exists(source_file):
            target_file = f"final_submission_{team_id}/submit_{i+1}.json"
            
            # 读取文件内容并更新用户ID
            with open(source_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 更新用户ID
            data["user"] = team_id
            
            # 保存到目标文件
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            submission_files.append(target_file)
            print(f"已添加 submit_{i+1}.json 到最终提交")
    
    # 创建ZIP文件
    with zipfile.ZipFile(f"{team_id}.zip", "w") as zipf:
        for file in submission_files:
            zipf.write(file, os.path.basename(file))
    
    print(f"\n已创建最终提交文件: {team_id}.zip")
    print(f"包含 {len(submission_files)} 个提交文件")

def create_wp(team_id, filename="write_up.md"):
    """创建Write-up文档"""
    wp_content = f"""# AIGC 论文检测绕过赛道 - Write-up

## 队伍ID: {team_id}

## 题目介绍

本次比赛要求参赛者设计提示词，目标是利用提示词工程生成能够绕过朱雀AI检测的学术论文样本。
成功的标准是AI检测率低于50%。提交的内容应当符合学术论文领域的常识，长度在500-10万字之间，
且仅支持中文和英文。

## 解题思路

### 1. 问题分析

AIGC检测系统通常基于以下特征检测AI生成内容：
- 语言模式的一致性和规律性
- 词汇使用的均匀性和可预测性
- 句式结构的重复和有限变化
- 缺乏个人风格和独特表达
- 内容的完美性和缺少人类自然错误

因此，我们的绕过策略需要打破这些特征，使生成内容更接近人类写作特点。

### 2. 核心策略

我们采用了以下核心策略来设计提示词：

#### 2.1 模拟人类写作特点
- 引入思维跳跃和自然转折
- 添加个人见解和主观表达
- 模拟学术写作中的批判性思考过程
- 融入多样化的表达方式和句式结构

#### 2.2 打破AI生成模式
- 要求使用多种不同的表达方式表达相同意思
- 在严谨的学术语言中融入个人色彩
- 引入少量细微的语法或拼写不规范之处
- 模拟从其他语言翻译的特点

#### 2.3 增加内容真实感
- 要求模拟真实研究者/团队的写作风格
- 引入田野调查、案例分析等具体研究元素
- 融入学术辩论和多视角分析
- 在不同学科领域使用专业术语和概念

### 3. 技术实现

我们设计了20个提示词，每个提示词针对不同学科领域和写作风格，目的是创造多样化的绕过样本。
提示词设计充分考虑了学术论文的特点，同时融入了上述核心策略。

## 提示词设计思路

我们的提示词设计遵循以下几个原则：

### 1. 多样性原则

20个提示词覆盖了多个学科领域，包括：
- 自然科学（量子计算、纳米材料等）
- 社会科学（人类学、社会学、政治经济学等）
- 人文学科（文学理论、语言学等）
- 交叉学科研究（数字人文、认知心理学与计算机科学等）

这种多样性确保了生成内容在词汇、结构和风格上的差异性，降低了被检测的风险。

### 2. 风格多元化原则

我们设计的提示词要求以不同的学术风格进行写作：
- 学术辩论式风格
- 田野调查风格
- 批判理论风格
- 实验研究风格
- 历史叙述风格
- 翻译风格
等等

这种风格多元化进一步增加了生成内容的多样性，破解AI检测系统对风格一致性的识别。

### 3. 技术复杂度原则

为了增加技术复杂度，我们在提示词中设计了多种技术手段：
- 复杂句式变换
- 引入小语种词汇
- 模拟研究团队讨论
- 多层次分析
- 比较研究框架
- 科学反思
- 案例分析

这些技术手段确保了生成内容具有复杂的结构和深度，更接近人类学者的真实写作。

### 4. 个性化原则

为了打破AI生成内容的模板化特征，我们特别设计了以下要求：
- 引入个人研究经历或观察
- 加入研究者的反思性内容
- 表现思考过程中的自然停顿和转折
- 使用第一人称表述
- 展现研究者对学术问题的个人见解

这些个性化元素有效地模拟了人类学者的主观表达，增强了内容的真实感。

## 总结与反思

通过精心设计的提示词，我们成功实现了生成能绕过AI检测的学术内容。我们的方法核心在于理解AI检测系统的工作原理，并有针对性地设计出能打破这些检测模式的提示词策略。

在实践中，我们发现以下几点是成功绕过检测的关键：
1. 融入人类写作的不完美性和主观性
2. 增加内容的多样性和复杂度
3. 模拟学术论文特有的思考模式和表达方式

这种方法不仅有效绕过了AI检测，同时保持了生成内容的学术价值和可读性，符合比赛要求的高质量标准。

"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(wp_content)
    
    print(f"已创建Write-up文档: {filename}")

if __name__ == "__main__":
    # 分析测试结果
    summary = analyze_results()
    
    # 输入队伍ID
    team_id = input("请输入您的队伍ID: ")
    
    # 创建最终提交文件
    create_final_submission(team_id)
    
    # 创建Write-up文档
    create_wp(team_id) 