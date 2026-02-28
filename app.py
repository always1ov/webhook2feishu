from fastapi import FastAPI, Request
import requests
import json
import os

app = FastAPI()

# 从环境变量读取飞书Webhook地址，未配置则启动报错
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")
if not FEISHU_WEBHOOK_URL:
    raise ValueError("ERROR: 未配置 FEISHU_WEBHOOK_URL 环境变量！")

@app.post("/webhook")
async def receive_and_forward_webhook(request: Request):
    """接收任意POST请求，原样转发到飞书机器人"""
    try:
        # 读取原始请求体（兼容任意格式）
        raw_body = await request.body()
        body_str = raw_body.decode("utf-8", errors="replace")

        # 构造飞书文本消息格式
        feishu_message = {
            "msg_type": "text",
            "content": {
                "text": f"【Webhook转发】\n收到消息内容：\n{body_str}"
            }
        }

        # 转发到飞书机器人
        response = requests.post(
            FEISHU_WEBHOOK_URL,
            json=feishu_message,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # 捕获HTTP请求错误

        return {
            "status": "success",
            "message": "消息已成功转发到飞书",
            "feishu_response": response.json()
        }

    except requests.exceptions.RequestException as e:
        return {"status": "error", "detail": f"转发到飞书失败：{str(e)}"}
    except Exception as e:
        return {"status": "error", "detail": f"处理请求失败：{str(e)}"}

# 健康检查接口（可选，用于验证服务是否正常）
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "webhook2feishu", "version": "1.0"}
