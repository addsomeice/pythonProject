# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

import csv

def count_column_value(filename, column_index, target_value):
    count = 0

    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > column_index and row[column_index] == target_value:
                count += 1

    return count
def count_matching_rows(filename, column_index, target_value, other_column_index, keyword):
    count = 0

    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # 读取标题行
        for row in reader:
            if len(row) > column_index and len(row) > other_column_index:
                if row[column_index] == target_value and keyword in row[other_column_index]:
                    count += 1

    return count

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    # 示例用法
    filename = 'amazon-reviews.csv'  # 替换为你的CSV文件路径
    column_index = 1  # 列索引，假设要统计第一列
    target_value = 'Parma'  # 目标值

    result = count_column_value(filename, column_index, target_value)
    print(f"在列 {column_index + 1} 中值为 '{target_value}' 的数量为: {result}")


    other_column_index = 3  # 另一列索引，假设要检查第二列
    keyword = 'great'  # 要检查的关键词

    result = count_matching_rows(filename, column_index, target_value, other_column_index, keyword)
    print(f"满足条件的行数为: {result}")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
