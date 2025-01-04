import os
import re
import pandas as pd
from list import output_dict

# 获取日志文件路径
out = output_dict["python"]["qiskit_switch"]
directory_path = os.path.dirname(out)

# 打开并读取日志内容
with open(out, 'r', encoding='utf-8') as f:
    log_content = f.read()

# 定义错误模式
error_patterns = {
    'AttributeError': r"AttributeError: (.*?)(?=\n)",
    'TypeError': r"TypeError: (.*?)(?=\n)",
    'NameError': r"NameError: (.*?)(?=\n)",
    'CircuitError': r"CircuitError: (.*?)(?=\n)",
    'ImportError': r"ImportError: (.*?)(?=\n)",
    'ModuleNotFoundError': r"ModuleNotFoundError: (.*?)(?=\n)",
    'MissingOptionalLibraryError': r"MissingOptionalLibraryError: (.*?)(?=\n)",
    'IndexError': r"IndexError: (.*?)(?=\n)"
}

# 初始化错误类型统计字典
error_type_summary = {key: 0 for key in error_patterns.keys()}

# 存储每个文件的错误统计
file_error_summary = []

# 将日志按 "[TRACE] Validating" 分割
log_entries = log_content.split("[TRACE] Validating")

# 处理每个日志条目
for entry in log_entries:
    # 跳过空条目
    if not entry.strip():
        continue
    
    # 提取文件名，假设文件名出现在 "Validating" 后面
    file_name_match = re.search(r'\/([^\/]+\.fuzz)', entry)
    if file_name_match:
        file_name = file_name_match.group(1)
    else:
        continue
    
    # 初始化当前文件的错误计数
    file_error_count = {key: 0 for key in error_patterns.keys()}
    
    # 统计各类错误的出现次数
    for error_type, pattern in error_patterns.items():
        error_count = len(re.findall(pattern, entry))
        file_error_count[error_type] = error_count
        error_type_summary[error_type] += error_count
    
    # 将当前文件的错误统计结果添加到文件统计列表中
    file_error_summary.append({'File Name': file_name, **file_error_count})

# 将文件错误统计转换为DataFrame
file_error_summary_df = pd.DataFrame(file_error_summary)

# 添加总统计行
summary_row = pd.DataFrame([{'File Name': 'Total', **error_type_summary}])
file_error_summary_df = pd.concat([file_error_summary_df, summary_row], ignore_index=True)

# 输出统计结果到CSV文件
summary_output_file = f'{directory_path}/error_summary.csv'
file_error_summary_df.to_csv(summary_output_file, index=False)

print("Error type summary has been saved to:", summary_output_file)
