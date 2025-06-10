from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from google.genai import types
from fastapi.responses import StreamingResponse
import difflib
import httpx
import jaydebeapi
import os
from dotenv import load_dotenv
import random
from datetime import datetime

load_dotenv()
app = FastAPI(
    title="Dream Predict",
    description="ทำนายฝัน Gemini",
    version="1.0"
)

JDBC_HOST = os.getenv('JDBC_HOST',"")
HTTP_PATH = os.getenv('HTTP_PATH',"")
TOKEN = os.getenv('TOKEN',"")
JDBC_PORT = os.getenv('JDBC_PORT',"")

def get_connection():
    jdbc_url = (
        f"jdbc:databricks://{JDBC_HOST}:{JDBC_PORT}/"
        f"default;transportMode=http;ssl=1;httpPath={HTTP_PATH};AuthMech=3;PWD={TOKEN};UID=token"
    )
    # driver_path = "/Users/wisithempornwisarn/PycharmProjects/muToday/DatabricksJDBC42-2.6.34.1058 2/DatabricksJDBC42.jar"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(current_dir, 'DatabricksJDBC42-2.6.34.1058 2/DatabricksJDBC42.jar')

    conn = jaydebeapi.connect(
        "com.databricks.client.jdbc.Driver",  # JDBC driver class name
        jdbc_url,
        ["token", TOKEN],
        driver_path
    )
    
    return conn

def event_stream(response):
    result = ''
    for chunk in response:
        if chunk.text:
            result+=chunk.text
            # yield f"{chunk.text}"
    return result

# uvicorn main:app --reload

class DreamRequest(BaseModel):
    dream: str

SIMILARITY_THRESHOLD = 0.4  # ปรับได้ตามความต้องการ (0-1)

def is_similar(a: str, b: str) -> bool:
    return difflib.SequenceMatcher(None, a, b).ratio() >= SIMILARITY_THRESHOLD

def insertLog(dreamText,result,resultDigits):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = """
            INSERT INTO main.mutoday.log_conversation (input, output, Number, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?)
            """
    resultDigits_str = ",".join(resultDigits)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (dreamText, result, resultDigits_str, now, now))
    cursor.close()
    conn.close()
    

@app.post("/dreamPredict", summary="แปลงความฝันด้วยโหาราศาสตร์จีนและไทย", tags=["MuToday"])
async def dream_predict(request: DreamRequest):


    client = genai.Client(api_key="AIzaSyCNKZqGKhFA9QsIEpl8pMT582TAkAHSB7M")
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=f"""ช่วยแก้ไขคำภาษาไทยในถูกต้อง {request.dream} แล้วแสดงแค่ข้อความที่ถูกปรับใหม่เท่านั้น"""
        ),
        contents = ["คุณคือผู้ช่วยที่เชี่ยวชาญในการแก้คำผิดในภาษาไทย"]
        # ["กรุณาเรียบเรียงข้อมูลข้างต้นให้อ่านง่ายและน่าสนใจสำหรับผู้อ่านทั่วไป"]
    )

    dreamText = event_stream(response)

    # return dreamText
    one_digit       = [str(random.randint(0, 9)) for _ in range(3)]
    two_digits      = [str(random.randint(10, 99)) for _ in range(3)]
    three_digits    = [str(random.randint(100, 999)) for _ in range(3)]
    resultDigits    = one_digit + two_digits + three_digits
    
    
    promptText = f"""
            คุณคือนักเขียนที่มีความสามารถในการปรับข้อความให้น่าอ่าน เป็นกันเอง และสื่อสารอย่างเข้าใจง่าย
            กรุณานำข้อมูลเกี่ยวกับความฝันด้านล่างนี้มาช่วยเรียบเรียงใหม่ให้อ่านแล้วดูเป็นธรรมชาติ เหมาะกับการเผยแพร่ต่อสาธารณะ เช่น บทความ หรือโพสต์บนโซเชียลมีเดีย

            - หลีกเลี่ยงการใช้ภาษาที่ยากหรือเป็นทางการเกินไป
            - ช่่วยตีความเกี่ยวความฝันตามโหราศาสตร์
            - แสดงเลขนำโชคตามนี้ 1 หลัก ตามนี้ {one_digit}
            - แสดงเลขนำโชคตามนี้ 2 หลัก ตามนี้ {two_digits}
            - แสดงเลขนำโชคตามนี้ 3 หลัก ตามนี้ {three_digits}
            - ให้แสดงเลขนำโชคที่บรรทัดสุดท้ายเท่านั้น
            - เน้นการสื่อสารที่เป็นเชิงบวก อบอุ่น และน่าเชื่อถือ
            - แต่ละหัวข้อความฝันควรถูกแยกเป็นรายการ (เช่น "ฝันเห็นงูบินได้" → งู, บิน)
            - ให้ทำนายโดยแยกหัวข้อตามรายการของแต่ละหัวข้อที่ถูกแยก
    

            ข้อมูลความฝันที่ได้รับอยู่ด้านล่าง:
            {dreamText}

    """
    
    
    client = genai.Client(api_key="AIzaSyCNKZqGKhFA9QsIEpl8pMT582TAkAHSB7M")
    responsePrompt = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=promptText
        ),
        contents = [""]
    )
    
    geminiText = event_stream(responsePrompt)
    
    insertLog(dreamText,geminiText,resultDigits)
    
    return geminiText
    