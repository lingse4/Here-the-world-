import mysql.connector
from mysql.connector import Error

def get_arknights_data():
    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host='localhost',
            database='lingse',
            user='root',
            password='1078813860abc.'
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # 查询数据
            cursor.execute("SELECT * FROM arknights LIMIT 10;")
            records = cursor.fetchall()

            insert_sql = "INSERT INTO arknights (name, rarity, profession) VALUES (%s, %s, %s)"
            data = ("斯卡蒂", "6★", "近卫")  # 替换为实际数据
            cursor.execute(insert_sql, data)
            connection.commit()  # 提交事务
            print("新增成功，影响行数:", cursor.rowcount)
    
            # 删除数据示例
            delete_sql = "DELETE FROM arknights WHERE name = %s"
            data = ("斯卡蒂",)  # 替换为实际条件
            cursor.execute(delete_sql, data)
            connection.commit()  # 提交事务
            print("删除成功，影响行数:", cursor.rowcount)

            print("查询结果：")
            for row in records:
                print(f"ID: {row['id']}, 角色名: {row['name']}, 类型: {row['type']}")

    except Error as e:
        print(f"数据库错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    get_arknights_data()
