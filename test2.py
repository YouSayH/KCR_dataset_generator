from google import genai
from google.genai import types
import pathlib
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("エラー: .env ファイルに GEMINI_API_KEY が設定されていません。")


client = genai.Client(api_key=api_key)
client = genai.Client()

# Retrieve and encode the PDF byte
filepath = pathlib.Path('file.pdf')

prompt = """
このPDFから読み取れる文字を、そのまま書き出してください。
"""
response = client.models.generate_content(
  model="gemini-2.5-flash-lite",
  contents=[
      types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type='application/pdf',
      ),
      prompt])
print(response.text)