from fastapi import FastAPI, Request
import requests
import json
import os

app = FastAPI()

# 【必配】从环境变量读取飞书Webhook地址
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")
if not FEISHU_WEBHOOK_URL:
    raise ValueError("ERROR: 未配置 FEISHU_WEBHOOK_URL 环境变量！")

# 【自定义端口】从环境变量读取端口，默认8080（可任意改）
APP_PORT = int(os.getenv("APP_PORT", 8080))

def parse_apprise_webhook(body_str: str) -> str:
    """
    解析 Apprise 发送的标准 JSON Webhook 格式
    Apprise 格式示例：
    {
        "type": "notification",
        "title": "通知标题",
        "body": "通知正文内容",
        "tag": "可选标签"
    }
    """
    try:
        # 尝试解析JSON
        data = json.loads(body_str)
        # 提取关键字段，适配Apprise格式
        title = data.get("title", "无标题")
        body = data.get("body", "无内容")
        notify_type = data.get("type", "unknown")
        tag = data.get("tag", "无标签")
        
        # 构造易读的飞书消息
        formatted_msg = f"""【Apprise 通知】
📌 类型：{notify_type}
🏷️ 标签：{tag}
📝 标题：{title}
💬 内容：{body}"""
        return formatted_msg
    except json.JSONDecodeError:
        # 如果不是JSON格式，返回原始内容（兼容旧格式）
        return f"【非Apprise格式消息】\n{body_str}"

@app.post("/webhook")
async def receive_and_forward_webhook(request: Request):
    """接收任意POST请求（适配Apprise格式），转发到飞书"""
    try:
        raw_body = await request.body()
        body_str = raw_body.decode("utf-8", errors="replace")

        # 解析Apprise格式，生成友好的消息内容
        message_content = parse_apprise_webhook(body_str)

        feishu_message = {
            "msg_type": "text",
            "content": {
                "text": message_content
            }
        }

        response = requests.post(
            FEISHU_WEBHOOK_URL,
            json=feishu_message,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        return {
            "status": "success",
            "message": "转发成功",
            "feishu_response": response.json()
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}

# 健康检查（显示当前端口）
@app.get("/health")
async def health_check():
    return {"status": "ok", "port": APP_PORT, "service": "webhook2feishu"}

# 启动入口（用环境变量端口）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=APP_PORT)
