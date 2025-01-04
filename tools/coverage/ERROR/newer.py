import re
import pandas as pd
from list import output_dict

out = output_dict["c"]["c_std"]
with open(out, 'r', encoding='utf-8') as f:
    log_content = f.read()
# Initialize a dictionary to store error types and their counts across all logs
error_type_summary = {
    'Syntax Error': 0,
    'Fatal Error': 0,
    'Warning': 0
}

# Define the error patterns
syntax_error_pattern = r'错误：([^：]+)'
fatal_error_pattern = r'致命错误：([^：]+)'
warning_pattern = r'警告：([^：]+)'
note_pattern = r'附注：([^：]+)'


file_error_summary = []
# Split the log content by each file's validation
log_entries = log_content.split("[TRACE] Validating")

# Iterate through each log entry and count the errors
# for entry in log_entries:
#     # Count occurrences of each error type in the current log entry
#     error_type_summary['Syntax Error'] += len(re.findall(syntax_error_pattern, entry))
#     error_type_summary['Fatal Error'] += len(re.findall(fatal_error_pattern, entry))
#     error_type_summary['Warning'] += len(re.findall(warning_pattern, entry))

for entry in log_entries:
    # Skip empty entries
    if not entry.strip():
        continue
    
    # Extract the file name from the log entry (assumes the file name appears after "Validating")
    file_name_match = re.search(r'\/([^\/]+\.fuzz)', entry)
    if file_name_match:
        file_name = file_name_match.group(1)
    else:
        continue
    
    # Count occurrences of each error type in the current log entry
    syntax_error_count = len(re.findall(syntax_error_pattern, entry))
    fatal_error_count = len(re.findall(fatal_error_pattern, entry))
    warning_count = len(re.findall(warning_pattern, entry))
    note_count = len(re.findall(note_pattern, entry))

    description = re.findall(syntax_error_pattern,entry) + re.findall(fatal_error_pattern,entry) + re.findall(warning_pattern,entry) + re.findall(note_pattern,entry)
    description = ' '.join(description)
    
    # Store the result for the current file
    file_error_summary.append({
        'File Name': file_name,
        'Syntax Error Count': syntax_error_count,
        'Fatal Error Count': fatal_error_count,
        # 'Warning Count': warning_count,
        # 'Note Count': note_count,
        # 'Description': description
    })



# Convert the summary into a DataFrame
# summary_df = pd.DataFrame(list(error_type_summary.items()), columns=["Error Type", "Count"])
file_error_summary_df = pd.DataFrame(file_error_summary)

# Save the summary to a CSV file
# summary_output_file = 'error_type_summary.csv'
# summary_df.to_csv(summary_output_file, index=False)

summary_output_file = f'{out}/error_type_summary.csv'
file_error_summary_df.to_csv(summary_output_file, index=False)

print("Error type summary has been saved to:", summary_output_file)
