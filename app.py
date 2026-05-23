
"""
AI学习助手 - 个性化学习资源生成系统
基于DeepSeek大模型，模拟"多智能体"架构
3个智能体：画像师、规划师、资源师
"""

import json
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# ============================================
# 配置区 -- 把这里改成你自己的API Key
# ============================================
DEEPSEEK_API_KEY = "sk-3dce7c32972b48be939495ffaec8a981"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


def call_deepseek(system_prompt, user_message):
    """
    调用DeepSeek API的通用函数
    system_prompt: 告诉AI它是什么角色
    user_message: 用户的问题/需求
    返回: AI生成的文本内容
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=120)
    result = response.json()

    if "error" in result:
        raise Exception(f"API错误: {result['error']}")

    return result["choices"][0]["message"]["content"]


# ============================================
# 智能体1：画像师 —— 分析学生的学习画像
# ============================================
def agent_profiler(topic, level):
    """分析学生的学习基础、目标、风格，生成学习画像"""
    system_prompt = """
你是一位专业的教育评估师，擅长分析学生的学习状况。
请根据学生想学的主题和自述水平，生成一份学习画像。

输出格式（用Markdown，结构清晰）：

## 学习画像

### 1. 当前知识基础评估
- 根据学生的自述水平，推断他/她已经掌握的前置知识
- 指出学习中可能遇到的主要困难

### 2. 学习目标拆解
- 把这个主题拆成3-5个子目标
- 每个子目标用一句话描述

### 3. 推荐学习风格
- 根据主题特点，推荐1-2种学习方式（如：动手实践、阅读文档、看视频、做项目等）
- 说明为什么推荐这种方式

### 4. 预估学习周期
- 根据主题难度，给出一个合理的学习周期估算
"""
    user_message = f"学生想学：{topic}\n学生的自述水平：{level}"
    return call_deepseek(system_prompt, user_message)


# ============================================
# 智能体2：规划师 —— 生成4周学习路线图
# ============================================
def agent_planner(topic, level):
    """根据主题和水平，生成一份4周学习路线图"""
    system_prompt = """
你是一位资深的学习规划师，擅长为学习者制定科学合理的学习计划。
请生成一份4周（每周5天）的学习路线图。

要求：
1. 每周有一个明确的主题
2. 每天有具体的学习任务（1-2小时）
3. 难度循序渐进
4. 包含理论学习和动手练习的搭配

输出格式（使用Markdown表格）：

## 四周学习路线图

### 第1周：XXX（主题名）
| 天数 | 学习内容 | 练习任务 | 预计时间 |
|------|---------|---------|---------|
| 周一 | ... | ... | ... |
| 周二 | ... | ... | ... |
...（周一到周五，共4周）

### 学习建议
- 给出3条实用的学习建议
"""
    user_message = f"学生想学：{topic}\n学生的水平：{level}\n请制定4周（每周5天）的学习计划。"
    return call_deepseek(system_prompt, user_message)


# ============================================
# 智能体3：资源师 —— 生成教程 + 练习题 + 思维导图
# ============================================
def agent_creator(topic, level):
    """生成学习教程文档、练习题和思维导图结构"""
    system_prompt = f"""
你是一位优秀的教育内容创作者，擅长编写通俗易懂的学习教程。
请根据学生想学的主题，生成以下三个部分的内容。

输出格式：

---

## 学习教程

写一份入门级教程（适合{level}水平的学习者），包含：
1. 核心概念讲解（用通俗的语言，配合生活化的类比）
2. 关键知识点（用列表列出，每个知识点加简短解释）
3. 一个完整的入门示例（代码/操作步骤/案例分析，根据主题类型决定）
4. 常见误区提醒（3个左右）

---

## 练习题

出3-5道练习题（由易到难），每道题包含：
- 题目描述
- 参考答案或解题思路

---

## 思维导图结构

用缩进文本的方式展示思维导图结构（三级节点即可），让学生一眼看清知识脉络。
格式示例：
中心主题
├── 子主题1
│   ├── 知识点1.1
│   └── 知识点1.2
├── 子主题2
│   ├── 知识点2.1
│   └── 知识点2.2
"""
    user_message = f"学生想学：{topic}\n学生的当前水平：{level}"
    return call_deepseek(system_prompt, user_message)


# ============================================
# 主路由：接收前端请求，调用3个智能体
# ============================================
@app.route("/generate", methods=["POST"])
def generate():
    """
    接收前端的请求，依次调用3个智能体，汇总结果返回
    """
    try:
        data = request.get_json()
        topic = data.get("topic", "").strip()
        level = data.get("level", "零基础")

        if not topic:
            return jsonify({"error": "请输入你想学的主题"}), 400

        print(f"[收到请求] 主题: {topic}, 水平: {level}")

        # 依次调用3个智能体（注意：每个API调用需要几秒到十几秒）
        print("[智能体1] 画像师工作中...")
        profile = agent_profiler(topic, level)

        print("[智能体2] 规划师工作中...")
        roadmap = agent_planner(topic, level)

        print("[智能体3] 资源师工作中...")
        content = agent_creator(topic, level)

        print("[完成] 所有智能体工作完毕")

        # 汇总结果返回前端
        return jsonify({
            "topic": topic,
            "profile": profile,
            "roadmap": roadmap,
            "content": content
        })

    except Exception as e:
        print(f"[错误] {str(e)}")
        return jsonify({"error": f"生成失败：{str(e)}"}), 500


# ============================================
# 首页 —— 默认打开登录页
# ============================================
@app.route("/")
def index():
    return send_from_directory(".", "login.html")

@app.route("/login.html")
def login_page():
    return send_from_directory(".", "login.html")

@app.route("/index_main.html")
def main_page():
    return send_from_directory(".", "index_main.html")


# ============================================
# 启动服务器
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("   AI学习助手 启动成功！")
    print("   请在浏览器打开：http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
