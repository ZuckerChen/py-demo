# 1. 构造MIMEMultipart对象做为根容器
# 2. 构造MIMEText对象做为邮件显示内容并附加到根容器
# 3. 构造MIMEBase对象做为文件附件内容并附加到根容器
# 　　a. 读入文件内容并格式化
# 　　b. 设置附件头
# 4. 设置根容器属性
# 5. 得到格式化后的完整文本
# 6. 用smtp发送邮件
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import json
import smtplib

def send(subject=None,sender=None, receiver=None, cc=None, filename=None,newfilename=None):
    # sender = 'chenzhang@nonobank.com'
    # receiver = 'chenzhang@nonobank.com,chenzhang@nonobank.com'
    # file_name = '/Users/chenchang/Documents/线上修复数据记录/script/tranNo'
    # receiver = str.split(receiver, ",")

    smtpserver = 'mail.nonobank.com'
    username = 'chenzhang'
    password = 'mzjf2017.'

    currDate = time.strftime("%Y-%m-%d", time.localtime())
    print("主题：" + subject)
    print("附件名：" + newfilename)
    print("发件人：" + ', '.join(sender))
    print("收件人：" + ', '.join(receiver))
    print("抄送人：" + ', '.join(cc))

    # 多个部分
    msg = MIMEMultipart()
    msg['From'] = Header(', '.join(sender), 'utf-8')
    msg['To'] = Header(', '.join(receiver), 'utf-8')
    msg['Cc'] = Header(', '.join(cc), 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    # 文字部分
    msg.attach(MIMEText('你好', 'plain', 'utf-8'))  # 中文需参数‘utf-8’，单字节字符不需要

    # 附件部分
    part = MIMEApplication(open(filename, 'rb').read())
    part["Content-Type"] = 'application/octet-stream'
    part["Content-Disposition"] = 'attachment; filename="%s"' % newfilename
    msg.attach(part)

    smtp = smtplib.SMTP(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver + cc, msg.as_string())
    smtp.quit()