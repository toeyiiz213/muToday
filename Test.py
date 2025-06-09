# from databricks.sql import connect
# print("Start")
# try:
#     print("Start Connect")
#     acc = "dapie20a5689668815dc5b6f60ff21dcf233"
#     connection = connect(
#         server_hostname="886789292378781.1.gcp.databricks.com",  # ลบ https:// ออก
#         http_path="/sql/1.0/warehouses/9a6582c8c1fe8f71",
#         access_token=acc
#     )
#     print("After Connect")
#     cursor = connection.cursor()
#     cursor.execute("SELECT 1")
#     query_result = cursor.fetchall()
#     print("After Query")
#     print(query_result)

#     cursor.close()
#     connection.close()

# except Exception as e:
#     print('failed:', e)
from jaydebeapi import jaydebeapi
import os

# กำหนดค่าเชื่อมต่อ
JDBC_HOST = "databricks://886789292378781.1.gcp.databricks.com"
HTTP_PATH = "/sql/1.0/warehouses/9a6582c8c1fe8f71"
TOKEN = "dapie20a5689668815dc5b6f60ff21dcf233"
JDBC_PORT = 443

# สร้าง JDBC URL สำหรับ Databricks
jdbc_url = (
    f"jdbc:databricks://886789292378781.1.gcp.databricks.com:443/default;transportMode=http;ssl=1;AuthMech=3;httpPath=/sql/1.0/warehouses/9a6582c8c1fe8f71;"
)

# Path ไปยัง Databricks JDBC .jar driver
driver_path = "/Users/wisithempornwisarn/Downloads/DatabricksJDBC-2.7.3.1010/DatabricksJDBC42.jar"

# สร้างการเชื่อมต่อ
conn = jaydebeapi.connect(
    "com.databricks.client.jdbc.Driver",  # JDBC driver class name
    jdbc_url,
    ["token", TOKEN],
    driver_path
)

# สร้าง cursor เพื่อรัน SQL
cursor = conn.cursor()
cursor.execute("SELECT 1")

# ดึงข้อมูล
rows = cursor.fetchall()
for row in rows:
    print(row)

# ปิดการเชื่อมต่อ
cursor.close()
conn.close()

