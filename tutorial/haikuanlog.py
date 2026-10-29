# import pandas as pd
# import datetime
#
# balance = 421721.29
# monthly_payment = 1984.86
# annual_rate = 0.026
# monthly_rate = annual_rate / 12
# start_date = datetime.date(2026, 10, 11)
#
# data = []
# current_date = start_date
#
# while balance > 0:
#     # 计算当月利息和本金
#     interest = round(balance * monthly_rate, 2)
#     principal = round(monthly_payment - interest, 2)
#
#     # 处理最后一期不足月供的情况
#     if balance < principal:
#         principal = balance
#         monthly_payment_final = principal + interest
#     else:
#         monthly_payment_final = monthly_payment
#
#     balance = round(balance - principal, 2)
#
#     # 日期推后一个月
#     if current_date.month == 12:
#         current_date = datetime.date(current_date.year + 1, 1, 11)
#     else:
#         current_date = datetime.date(current_date.year, current_date.month + 1, 11)
#
#     data.append([current_date.strftime('%Y-%m-%d'), monthly_payment_final, principal, interest, 0.00, balance])
#
#     if balance <= 0:
#         break
#
# df = pd.DataFrame(data, columns=['还款日期', '还款总金额', '还款本金', '还款利息', '罚息', '贷款余额'])
# df.to_excel('公积金完整还款计划.xlsx', index=False)
# print("完整还款计划已生成！预计结清日期：", data[-1][0])


import pandas as pd
import datetime

balance = 421721.29
monthly_principal = round(421721.29 / 285, 2)
rate = 0.026 / 12
date = datetime.date(2026, 10, 11)

data = []
for i in range(285):
    interest = round(balance * rate, 2)
    if i == 284:  # 最后一期结清
        principal = balance
        total = round(principal + interest, 2)
    else:
        principal = monthly_principal
        total = round(principal + interest, 2)

    balance = round(balance - principal, 2)

    if date.month == 12:
        date = datetime.date(date.year + 1, 1, 11)
    else:
        date = datetime.date(date.year, date.month + 1, 11)

    data.append([date.strftime('%Y-%m-%d'), total, principal, interest, 0.00, balance])

df = pd.DataFrame(data, columns=['还款日期', '还款总金额', '还款本金', '还款利息', '罚息', '贷款余额'])
df.to_excel('公积金等额本金完整还款计划.xlsx', index=False)
print("文件生成成功！")