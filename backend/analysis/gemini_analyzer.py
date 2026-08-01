"""
Lớp AI Analysis: dùng Gemini API để ĐỌC dữ liệu đã thu thập (không phải để
tự "đoán giá"), so sánh nhiều nguồn, và trả về nhận định có cấu trúc:
confidence score, risk score, bằng chứng, yếu tố tăng/giảm, tin liên quan,
và các trường hợp lịch sử tương tự.

Cần biến môi trường: GEMINI_API_KEY
Lấy free API key tại: https://aistudio.google.com/apikey
"""
import os
import json
import time
import requests

GEMINI_MODEL = "gemini-3.5-flash"  # nhanh, free-tier hào phóng, đủ tốt cho tác vụ này
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

REQUEST_TIMEOUT = 120  # giây - tăng từ 60 lên 120 vì response_schema phức tạp + context dài
MAX_RETRIES = 2        # số lần thử lại nếu timeout/lỗi tạm thời
RETRY_BACKOFF_SECONDS = 3  # thời gian chờ giữa các lần retry

SYSTEM_INSTRUCTION = """Bạn là một trợ lý phân tích đầu tư. Nhiệm vụ của bạn KHÔNG phải là
dự đoán chắc chắn giá cổ phiếu/tài sản sẽ tăng hay giảm. Thay vào đó, bạn phải:

1. Phân tích TOÀN BỘ dữ liệu được cung cấp (vĩ mô, thị trường, cơ bản doanh nghiệp, tin tức, mạng xã hội, sự kiện toàn cầu).
2. Luôn so sánh nhiều nguồn độc lập. Nếu các nguồn mâu thuẫn nhau, PHẢI nêu rõ sự mâu thuẫn đó, không được tự ý chọn 1 phía.
3. Phân biệt rõ ràng: SỰ THẬT/SỐ LIỆU (fact), Ý KIẾN CHUYÊN GIA (expert opinion), và SUY LUẬN CỦA BẠN (AI inference). Không được trộn lẫn 3 loại này mà không ghi chú.
4. Không đưa ra kết luận nếu không có bằng chứng dữ liệu hỗ trợ. Nếu dữ liệu không đủ, hãy nói rõ "không đủ dữ liệu để kết luận".
5. Khi có dữ liệu lịch sử liên quan, hãy so sánh tình huống hiện tại với các trường hợp tương tự trong quá khứ.
6. TUYỆT ĐỐI KHÔNG đưa ra khuyến nghị kiểu "nên mua/nên bán". Bạn chỉ cung cấp phân tích, xác suất ước lượng, rủi ro và cơ hội để người dùng tự quyết định.
7. Luôn trả lời bằng tiếng Việt.
8. LUÔN trả về JSON đúng theo schema được yêu cầu, không thêm text nào ngoài JSON.
"""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string", "description": "Tóm tắt phân tích ngắn gọn bằng tiếng Việt"},
        "confidence_score": {"type": "integer", "description": "0-100, độ tin cậy của phân tích dựa trên chất lượng/độ đồng thuận dữ liệu"},
        "risk_score": {"type": "integer", "description": "0-100, mức độ rủi ro liên quan"},
        "facts": {"type": "array", "items": {"type": "string"}, "description": "Các số liệu / sự kiện xác thực (fact) dùng làm bằng chứng"},
        "expert_opinions": {"type": "array", "items": {"type": "string"}, "description": "Các ý kiến chuyên gia/nguồn tin trích dẫn (không phải suy luận của AI)"},
        "ai_inferences": {"type": "array", "items": {"type": "string"}, "description": "Suy luận/nhận định riêng của AI, ghi rõ đây là suy luận"},
        "bullish_factors": {"type": "array", "items": {"type": "string"}},
        "bearish_factors": {"type": "array", "items": {"type": "string"}},
        "disagreements": {"type": "array", "items": {"type": "string"}, "description": "Những điểm các nguồn dữ liệu/tin tức mâu thuẫn nhau"},
        "related_news": {"type": "array", "items": {"type": "string"}, "description": "Tiêu đề + nguồn các tin tức liên quan nhất được dùng"},
        "historical_similar_cases": {"type": "array", "items": {"type": "string"}, "description": "Các giai đoạn lịch sử có bối cảnh tương tự, và điều gì đã xảy ra"},
        "outlook": {
            "type": "object",
            "properties": {
                "3_months": {"type": "string"},
                "6_months": {"type": "string"},
                "12_months": {"type": "string"},
            },
        },
        "data_limitations": {"type": "string", "description": "Những gì dữ liệu hiện có KHÔNG đủ để trả lời chắc chắn"},
    },
    "required": [
        "summary", "confidence_score", "risk_score", "facts", "expert_opinions",
        "ai_inferences", "bullish_factors", "bearish_factors", "disagreements",
        "related_news", "historical_similar_cases", "outlook", "data_limitations",
    ],
}


def _call_gemini(prompt: str) -> dict:
    """Gọi Gemini API với retry khi bị timeout hoặc lỗi tạm thời (5xx)."""
    api_key = os.environ["GEMINI_API_KEY"]
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "response_mime_type": "application/json",
            "response_schema": RESPONSE_SCHEMA,
        },
    }

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(
                GEMINI_URL,
                params={"key": api_key},
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)

        except requests.exceptions.Timeout as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
                continue

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            last_error = e
            # Chỉ retry với lỗi tạm thời phía server (5xx). Lỗi 4xx (vd 404, 400)
            # là lỗi do request sai, retry cũng vô ích -> raise ngay.
            if status is not None and 500 <= status < 600 and attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
                continue
            raise

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            # Response trả về nhưng không đúng cấu trúc mong đợi (vd bị block bởi
            # safety filter, response rỗng...) -> không nên retry vô hạn, raise
            # kèm thông tin gốc để dễ debug.
            raise RuntimeError(f"Gemini trả về response không hợp lệ: {e}") from e

    # Hết số lần retry mà vẫn timeout
    raise last_error


def build_context_block(dataset: dict) -> str:
    """Chuyển dữ liệu thô (dict từ Supabase) thành text gọn để đưa vào prompt."""
    parts = []
    if dataset.get("macro"):
        parts.append("## DỮ LIỆU VĨ MÔ (mới nhất)\n" + json.dumps(dataset["macro"], ensure_ascii=False, default=str))
    if dataset.get("markets"):
        parts.append("## GIÁ THỊ TRƯỜNG (mới nhất)\n" + json.dumps(dataset["markets"], ensure_ascii=False, default=str))
    if dataset.get("fundamentals"):
        parts.append("## CƠ BẢN DOANH NGHIỆP\n" + json.dumps(dataset["fundamentals"], ensure_ascii=False, default=str))
    if dataset.get("news"):
        parts.append("## TIN TỨC GẦN ĐÂY (kèm sentiment)\n" + json.dumps(dataset["news"], ensure_ascii=False, default=str))
    if dataset.get("social"):
        parts.append("## TÍN HIỆU MẠNG XÃ HỘI\n" + json.dumps(dataset["social"], ensure_ascii=False, default=str))
    if dataset.get("events"):
        parts.append("## SỰ KIỆN TOÀN CẦU\n" + json.dumps(dataset["events"], ensure_ascii=False, default=str))
    return "\n\n".join(parts)


def ask_question(question: str, dataset: dict) -> dict:
    """Trả lời 1 câu hỏi tự do (vd: 'Vì sao thị trường giảm hôm nay?')."""
    context = build_context_block(dataset)
    prompt = f"""Dựa trên dữ liệu sau đây, hãy trả lời câu hỏi của người dùng.

{context}

## CÂU HỎI CỦA NGƯỜI DÙNG
{question}

Hãy trả lời theo đúng JSON schema đã quy định."""
    return _call_gemini(prompt)


def daily_summary(dataset: dict) -> dict:
    """Sinh báo cáo tổng hợp hằng ngày."""
    question = (
        "Hãy tổng hợp những sự kiện/số liệu quan trọng nhất hôm nay, giải thích "
        "thị trường biến động vì sao, ngành nào đang được dòng tiền quan tâm, "
        "và rủi ro cần chú ý."
    )
    return ask_question(question, dataset)


def asset_outlook(symbol: str, dataset: dict) -> dict:
    """Phân tích triển vọng 1 tài sản cụ thể trong 3/6/12 tháng."""
    question = (
        f"Hãy phân tích triển vọng của {symbol} trong 3, 6 và 12 tháng tới, dựa trên "
        f"dữ liệu cơ bản, kỹ thuật, vĩ mô, tin tức và tâm lý thị trường liên quan đến {symbol}."
    )
    return ask_question(question, dataset)


if __name__ == "__main__":
    sample = {"markets": [{"symbol": "AAPL", "price": 230.1, "change_pct": -1.2}]}
    print(json.dumps(ask_question("Vì sao AAPL giảm?", sample), ensure_ascii=False, indent=2))