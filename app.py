from flask import Flask
from flask import render_template
from flask import request
import csv
from collections import Counter
import json
from urllib.parse import unquote

app = Flask(__name__)

@app.route("/")
def index():
    message = "Congratulations, it's a web app!"
    return render_template(
        'welcome.html',
        message=message,
    )
@app.route("/words")
def index():
    message = "Congratulations, it's a web app!"
    return render_template(
        'welcome.html',
        message=message,
    )
@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    print(username)
    password= request.args.get('password')
    print(password)
    return username
    # You will see the username and password in the terminal logs

#city_name 参数用于指定要检索的城市名称，默认为 None，表示检索所有城市。
#include_header 参数用于指定是否包含 CSV 文件的标题行，默认为 False，表示不包含标题行。
#exact_match 参数用于指定是否执行精确匹配，默认为 False，表示执行部分匹配
def fetch_data(city_name = None, include_header = False, exact_match = False):
    with open("us-cities.csv") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        row_id = -1
        wanted_data = []
        #在迭代每一行时，它检查当前行是否满足条件，即是否是所需的行。
        # 如果满足条件，它将该行添加到 wanted_data 列表中，并返回最终的 wanted_data 列表。
        for row in csvreader:
            row_id += 1
            if row_id == 0 and not include_header:
                continue
            line = []
            col_id = -1
            is_wanted_row = False
            if city_name is None:
                is_wanted_row = True
            for raw_col in row:
                col_id += 1
                col = raw_col.replace('"', '')
                line.append( col )
                if col_id == 0 and city_name is not None:
                    if not exact_match and city_name.lower() in col.lower():
                        is_wanted_row = True
                    elif exact_match and city_name.lower() == col.lower():
                        is_wanted_row = True
            if is_wanted_row:
                if row_id > 0:
                    line.insert(0, "{}".format(row_id))
                else:
                    line.insert(0, "")
                wanted_data.append(line)
    return wanted_data

@app.route('/data', methods=['GET'])
def query():
    city_name = request.args.get('city_name')
    #如果 city_name 不为 None，则移除双引号。
    if city_name is not None:
        city_name = city_name.replace('"', '')
    wanted_data = fetch_data(city_name = city_name, include_header = True)
    table_content = ""
    #遍历 wanted_data 列表，将每一行的数据转换为 HTML 表格的行。
    for row in wanted_data:
        line_str = ""
        for col in row:
            line_str += "<td>" + col + "</td>"
        table_content += "<tr>" + line_str + "</tr>"
        #构建一个 HTML 页面，其中包含一个表格，并将表格内容设置为之前生成的 table_content。返回构建的 HTML 页面作为响应。
    page = "<html><title>Tutorial of CSE6332 - Part2</title><body>"
    page += "<table>" + table_content + "</table>"
    page += "</body></html>"
    return page
#此函数用于追加或更新城市数据到名为 "us-cities.csv" 的 CSV 文件
def append_or_update_data(req):
    city_name = req['city_name']
    lat = req['lat']
    lng = req['lng']
    country = req['country']
    state = req['state']
    population = req['population']
    #如果 city_name 为 None，则返回 False 表示输入无效。

    if city_name is None:
        return False
    # 构建一个包含城市数据的输入行(input_line)，使用双引号将每个字段括起来并用逗号分隔。
    input_line = '"{}","{}","{}","{}","{}","{}"'.format(
        city_name, lat, lng, country, state, population,
    )
    #调用 fetch_data() 函数，传递 city_name 参数进行精确匹配，以获取具有相同城市名称的现有记录。
    existing_records = fetch_data(city_name = city_name, exact_match=True)
    #如果没有现有记录，表示该城市是新的，将输入行追加到 CSV 文件的末尾。
    if len(existing_records) == 0:
        with open('us-cities.csv', 'a') as f:
            f.write(input_line)
            f.close()
    #如果存在现有记录，则需要更新数据。首先获取所有记录，包括标题行。然后遍历所有记录，根据城市名称匹配判断是否需要更新数据
    else:
        all_records = fetch_data(include_header=True)
        lines = []
        for row in all_records:
            line_to_write = ""
            #如果城市名称不匹配，将该行写入 lines 列表中。
            if row[1].lower() != city_name.lower():
                line_to_write = ",".join(['"{}"'.format(col) for col in row[1:]])
            #如果城市名称匹配，将输入行写入 lines 列表中，以实现更新。
            else:
                line_to_write = input_line
            #最后，将 lines 列表中的内容写入 CSV 文件，覆盖原有数据。
            lines.append(line_to_write + "\n")
        with open('us-cities.csv', 'w') as f:
            f.writelines(lines)
            f.close()
    return True

@app.route('/data', methods=['PUT'])
def append_or_update():
    req = request.json
    if append_or_update_data(req):
        return "done"
    else:
        return "invalid input"

def delete_data(city_name):
    #调用 fetch_data() 函数，使用精确匹配的方式获取具有相同城市名称的现有记录。
    existing_records = fetch_data(city_name = city_name, exact_match=True)
    if len(existing_records) > 0:
        all_records = fetch_data(include_header=True)
        lines = []
        #获取所有记录，包括标题行。然后遍历所有记录，将不匹配城市名称的行写入 lines 列表中。
        for row in all_records:
            if row[1].lower() != city_name.lower():
                line_to_write = ",".join(['"{}"'.format(col) for col in row[1:]])
                lines.append(line_to_write + "\n")
        #打开 CSV 文件，并将 lines 列表中的内容写入文件，覆盖原有数据。
        #使用 truncate() 方法将文件截断为当前写入内容的长度，以确保删除了原有数据后的文件内容正确。
        with open('us-cities.csv', 'w') as f:
            f.writelines(lines)
            f.truncate()
            f.close()
        return True
    return False

@app.route('/data', methods=['DELETE'])
def delete():
    city_name = request.args.get('city_name')
    if city_name is not None:
        city_name = city_name.replace('"', '')
    else:
        return "invalid input"

    if delete_data(city_name):
        return "done"
    else:
        return "city does not exist"


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

@app.route('/popular', methods=['GET'])
def getPopularity():
    city_name = request.args.get('city_name')
    limitNum=request.args.get('limitNum')
    word=request.args.get("word");
    filename = 'amazon-reviews.csv'  # 替换为你的CSV文件路径
    cityfile='us-cities.csv'
    column_index = 1  # 列索引，假设要统计第一列

    other_column_index = 3  # 另一列索引，假设要检查第二列
    keyword = word  # 要检查的关键词
    wanted_data=[];
    if (city_name !=None and city_name!=""):
        target_value = city_name  # 目标值
        result = count_matching_rows(filename, column_index, target_value, other_column_index, keyword)
        citypop={'city_name':city_name,'popularity':result}
        wanted_data.append(citypop);
    else:
        with open(cityfile, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳过第一行标题行
            index = 0
            for row in reader:
                if len(row) > index:
                    value = row[index]
                    res=count_matching_rows(filename, column_index, value, other_column_index, keyword)
                    citypop = {'city_name': value, 'popularity': res}
                    wanted_data.append(citypop);
    sorted_cities = sorted(wanted_data, key=lambda city: city['popularity'], reverse=True)
    if limitNum!="" and int(limitNum) != 0 and int(limitNum)<len(wanted_data):
        sliceData=[]
        for i in range(0,int(limitNum)):
            sliceData.append(sorted_cities[i])
        sorted_cities=sliceData
    return sorted_cities
import re

@app.route('/popular_words', methods=['GET'])
def get_popular_words():
    city = unquote(request.args.get('city', ''))
    limit = int(request.args.get('limit', 20))
    print(city)
    print(limit)
    file_path = 'amazon-reviews.csv' # 替换为您的 CSV 文件路径
    reviews_column = 'review' # 替换为评论所在的列名称
    if city!=None and city!="":
        word_counts = Counter()
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['city'].lower() == city.lower():
                    review = row[reviews_column]
                    words = re.findall(r'\b\w+\b', review.lower())
                    word_counts.update(set(words))  # 使用 set 去重，只计算每个单词在一条评论中的出现次数

        top_words = word_counts.most_common(limit)
        print(top_words)
        result = [{ 'term': word, 'popularity': count} for word, count in top_words]
        print(result)
        return render_template('result.html', data=result, city=city)
    else:
        wantedata=[]
        cityfile = 'us-cities.csv'
        with open(cityfile, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳过第一行标题行
            index = 0
            for row in reader:
                if len(row) > index:
                    city = row[index]
                    word_counts = Counter()
                    with open(file_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if row['city'].lower() == city.lower():
                                review = row[reviews_column]
                                words = re.findall(r'\b\w+\b', review.lower())
                                word_counts.update(set(words))  # 使用 set 去重，只计算每个单词在一条评论中的出现次数
                    top_words = word_counts.most_common(limit)
                    print(top_words)
                    result = [{'term': word, 'popularity': count} for word, count in top_words]
                    wantedata.append(result)
        return wantedata

    # return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)