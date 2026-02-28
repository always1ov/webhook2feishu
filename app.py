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

@app.post("/webhook")
async def receive_and_forward_webhook(request: Request):
    """接收任意POST请求，转发到飞书"""
    try:
        raw_body = await request.body()
        body_str = raw_body.decode("utf-8", errors="replace")

        feishu_message = {
            "msg_type": "text",
            "content": {
                "text": f"【Webhook转发】\n收到消息：\n{body_str}"
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
