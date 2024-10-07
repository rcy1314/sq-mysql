import sqlite3
import mysql.connector

# SQLite 数据库连接信息
sqlite_db_path = 'memos_prod.db'  # 修改为你的 SQLite 文件路径
sqlite_conn = sqlite3.connect(sqlite_db_path)
sqlite_cursor = sqlite_conn.cursor()

# MySQL 数据库连接信息
mysql_conn = mysql.connector.connect(
    host='127.0.0.1',   # 修改为你自己的服务端地址
    port=3306,  # MySQL 默认端口是整数类型，不能加引号
    user='test',   #数据库用户名
    password='123456',   #数据库密码
    database='test'      #数据库名
)
mysql_cursor = mysql_conn.cursor()

# 获取 SQLite 数据库中的所有表名
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

# 遍历 SQLite 中的每个表
for table in tables:
    table_name = table[0]
    
    # 获取表结构
    sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
    columns = sqlite_cursor.fetchall()

    # 构建 MySQL 创建表的 SQL 语句
    create_table_sql = f'CREATE TABLE IF NOT EXISTS `{table_name}` ('
    for column in columns:
        column_name = column[1]
        column_type = column[2].upper()  # SQLite 类型与 MySQL 类型的映射

        # 简单的类型映射，可以根据需要扩展
        if column_type == "TEXT":
            column_type = "VARCHAR(255)"
        elif column_type == "INTEGER":
            column_type = "INT"
        elif column_type == "REAL":
            column_type = "DOUBLE"
        elif column_type == "BLOB":
            column_type = "BLOB"
        
        create_table_sql += f'`{column_name}` {column_type}, '
    
    create_table_sql = create_table_sql.rstrip(", ") + ");"
    
    # 执行创建表的 SQL 语句
    try:
        print(f"正在创建表: {table_name}")
        mysql_cursor.execute(create_table_sql)
    except mysql.connector.Error as e:
        print(f"创建表 {table_name} 时发生错误: {e}")
        continue

    # 将数据导入 MySQL 表
    sqlite_cursor.execute(f'SELECT * FROM "{table_name}";')
    rows = sqlite_cursor.fetchall()
    
    # 打印行数进行调试
    print(f"表 {table_name} 包含 {len(rows)} 行数据.")
    
    for row in rows:
        # 处理空值（None）转为 MySQL 兼容的 NULL
        row = [None if value is None else value for value in row]
        placeholders = ', '.join(['%s'] * len(row))
        insert_sql = f'INSERT INTO `{table_name}` VALUES ({placeholders});'
        
        try:
            print(f"正在插入数据到 {table_name}: {row}")
            mysql_cursor.execute(insert_sql, row)  # 使用参数化查询
        except mysql.connector.Error as e:
            print(f"插入数据到 {table_name} 时发生错误: {e}")
            continue

    # 每次插入表数据后提交事务
    mysql_conn.commit()

# 提交所有事务并关闭连接
mysql_conn.commit()
sqlite_conn.close()
mysql_conn.close()

print("SQLite 数据库已成功导入到 MySQL。")
