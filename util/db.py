import pymysql

db = pymysql.connect(
    host='db-pay-max-monitor.prod.com',
    port=3327,
    user='payment_monitor',
    password='F+bl+qB0rVUTx3qGQ==',
    charset='utf8')

cursor = db.cursor()
sql=""
cursor.execute(sql)
data = cursor.fetchall()
cursor.close();