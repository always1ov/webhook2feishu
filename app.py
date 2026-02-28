from fastapi import FastAPI, Request
import requests
import json
import os  # 新增：导入os模块读取环境变量

app = FastAPI()

# 从环境变量读取飞书Webhook地址（没有则报错）
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")
if not FEISHU_WEBHOOK_URL:
    raise ValueError("请设置 FEISHU_WEBHOOK_URL 环境变量！")

@app.post("/webhook")
async def catch_all_webhook(request: Request):
    try:
        # 接收任意格式的请求体
        body = await request.body()
        body_str = body.decode("utf-8", errors="replace")

        # 构造飞书文本消息（原样转发）
        feishu_msg = {
            "msg_type": "text",
            "content": {
                "text": f"收到 Webhook 消息：\n{body_str}"
            }
        }

        # 转发到飞书
        requests.post(
            FEISHU_WEBHOOK_URL,
            json=feishu_msg,
            timeout=5
        )

        return {"status": "ok", "message": "已转发到飞书"}

    except Exception as e:
        return {"status": "error", "detail": str(e)}
