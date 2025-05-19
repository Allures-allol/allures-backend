import pyodbc

try:
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS01;"
        "DATABASE=ReviewDb;"
        "Trusted_Connection=yes;"
    )
    conn = pyodbc.connect(conn_str)
    print("✅ Успешно подключено к MSSQL (Windows Auth)")
    conn.close()
except Exception as e:
    print("❌ Ошибка соединения:")
    print(e)
