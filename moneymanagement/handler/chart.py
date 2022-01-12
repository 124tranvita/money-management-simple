from datetime import datetime
from moneymanagement.models import Expenditure

# Tính tổng các khoản chi theo ngày
def expense_sum_by_date(user_id: int, date: datetime) -> int:
  expenses = Expenditure.query.filter_by(user_id=user_id, date=date).all()
  # Tính tổng các khoản chi trong ngày
  sum_amount = 0
  for expense in expenses:
    sum_amount += expense.amount

  return sum_amount

# Tính % các khoản chi trong ngày trên tổng ngân sách
def month_report_in_percent(sum_by_date: dict) -> dict:
  '''
  Hàm trả về 1 dictionary gồm {key: [value, percent]}
  Trong đó:
  1. key = ngày
  2. value = tổng các khoản chi trong ngày
  3. percent = phần trăm khoản chi trong ngày trên tổng khoản chi trong tháng
  Chú ý: Nếu tổng khoản chi trong tháng = 0, thì sẽ gán phần trăm của tất cả các khoảng chi trong ngày = 0,
  để tránh trường hợp chia 0 khi tính %, sẽ dẫn đến lỗi "devide by zero)
  '''
  # Tạo 1 dict chứa key = ngày và value = % (khoản chi của ngày trên tổng tất cả các khoản chi)
  report_in_percent = {}
  # Tính tổng các khoản chi đến ngày hiện tại
  sum_expense = sum(sum_by_date.values())
  # Tính % các khoản chi
  for key, value in sum_by_date.items():
    # Kiểm tra nếu tổng các khoản chi của người dùng = 0 thì sẽ gán phần trăm = 0 cho tất cả các ngày
    if sum_expense == 0:
      report_in_percent[key] = [value, 0]
    else:
      percent = (value / sum_expense) * 100
      report_in_percent[key] = [value, round(percent, 2)]
  
  return report_in_percent

def month_report(user_id: int) -> dict:
  '''
  1. Khởi tạo biến "current_day" để chưa ngày tháng năm hiện tại.
  2. Sử dụng hàm replace(day=1) để lấy ngày đầu tháng từ "current_day" và gán vào biến "first_day_of_month"
  3. Chuyển "current_day" và "first_day_of_month" thành giá trị int để đưa vào hàm range() phục vụ chi việc loop.
  '''
  # Khởi tạo biến "current_day"
  current_day = datetime.today().date()
  # Khởi tạo biến "first_day_of_month" từ "current_day"
  # first_day_of_month = current_day.replace(day=1)
  # Danh sách các khoản chi theo ngày
  report = {}
  # Tạo vòng lặp for để tính tổng các khoản chi từ đầu tháng (1) tới ngày hiện tại của tháng (current_day)
  for day in range(1, int(current_day.strftime('%d')) + 1):
    report[day] = expense_sum_by_date(user_id, current_day.replace(day=day))

  return report