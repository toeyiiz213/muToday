from databricks.sql import connect
print("Start")
try:
    print("Start Connect")
    acc = "dapie20a5689668815dc5b6f60ff21dcf233"
    connection = connect(
        server_hostname="886789292378781.1.gcp.databricks.com",  # ลบ https:// ออก
        http_path="/sql/1.0/warehouses/9a6582c8c1fe8f71",
        access_token=acc
    )
    print("After Connect")
    cursor = connection.cursor()
    cursor.execute("SELECT current_date()")
    query_result = cursor.fetchall()
    print("After Query")
    print(query_result)

    cursor.close()
    connection.close()

except Exception as e:
    print('failed:', e)