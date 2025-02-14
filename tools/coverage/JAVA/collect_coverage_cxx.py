import argparse
import glob
import os
import re
import shutil
import subprocess


def natural_sort_key(s):
    _nsre = re.compile(r"([0-9]+)")
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]


def get_input_type_from_scanner(code):
    """
    从 Java 程序的源代码中推测输入类型。
    """
    # 匹配 Scanner 使用的输入方法
    if re.search(r"new\s+Scanner\(\s*\"[^\"]*\"\s*\)", code):  # 直接传入字符串
        return "string_input"
    if re.search(r"nextInt\(\)", code):
        return "int"
    elif re.search(r"nextDouble\(\)", code):
        return "double"
    elif re.search(r"nextLine\(\)", code):
        return "string"
    elif re.search(r"nextLong\(\)", code):
        return "long"
    elif re.search(r"nextBoolean\(\)", code):
        return "boolean"

    return "unknown"  # 如果无法确定输入类型，返回 "unknown"

def simulate_input_for_type(input_type):
    """
    根据输入类型返回模拟输入。
    """
    if input_type == "int":
        return "42\n"  # 假设程序需要一个整数输入
    elif input_type == "double":
        return "3.14\n"  # 假设程序需要一个浮点数输入
    elif input_type == "string":
        return "hello world\n"  # 假设程序需要一个字符串输入
    elif input_type == "long":
        return "1234567890\n"  # 假设程序需要一个长整型输入
    elif input_type == "boolean":
        return "true\n"  # 假设程序需要一个布尔型输入
    elif input_type == "string_input":
        print("Please enter input for string_input")
        return "Hello Indian\nworld\n"
    else:
        return ""  # 如果无法确定输入类型，返回空输入



def compile_and_run(file_map, output_folder):
    """
    Compile and run Java files using `javac` and `java` with JaCoCo.
    Generate coverage reports for each file.
    """
    agent_path = "/home/cxx/fuzz4all/jacoco-0.8.12/lib/jacocoagent.jar"
    coverage_folder = os.path.join(output_folder, "coverage")
    os.makedirs(coverage_folder, exist_ok=True)

    log_records = []  # 用于记录日志
    # ind = 0
    for temp_file, original_file in file_map.items():
        # print(f"index: {ind}")
        # ind += 1
        class_name = os.path.splitext(os.path.basename(temp_file))[0]
        # print(f"temp_file: {temp_file}")
        # /home/cxx/fuzz4all/outputs/java_std/temp/14/HelloIndian.java
        # print(f"ClassName: {class_name}")
        index = os.path.basename(os.path.dirname(temp_file))
        class_folder = os.path.join(output_folder, f"classes/{index}")
        coverage_folder = os.path.join(output_folder, f"coverage/{index}")
        os.makedirs(class_folder, exist_ok=True)
        os.makedirs(coverage_folder, exist_ok=True)

        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                code = f.read()
                input_type = get_input_type_from_scanner(code)
                simulated_input = simulate_input_for_type(input_type)  # 模拟输入
        except Exception as e:
            log_records.append(f"Error reading {temp_file}: {str(e)}")
            continue

        # Compile Java file
        try:
            compile_cmd = ["/home/cxx/fuzz4all/javac/bin/javac", "-d", class_folder, temp_file]
            subprocess.run(compile_cmd, check=True, text=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.replace(temp_file, original_file)
            log_records.append(f"Compilation failed for {original_file}:\n{error_message}")
            continue
        if not os.path.exists(class_folder):
            log_records.append(f"Class file for {original_file} was not generated. Skipping execution.")
            continue

        # Run Java file with JaCoCo agent
        exec_file = os.path.join(coverage_folder, f"{class_name}.exec")
        try:
            run_cmd = [
                "/home/cxx/fuzz4all/javac/bin/java",
                f"-javaagent:{agent_path}=destfile={exec_file}",
                "-cp",
                class_folder,
                class_name,
            ]
            # print(f"STDIN: {simulated_input}")
            result = subprocess.run(run_cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            input=simulated_input, timeout=10)

            # print(f"STDOUT: {result.stdout}")
            # print(f"STDERR: {result.stderr}")


        except subprocess.CalledProcessError as e:
            log_records.append(f"Execution failed for {original_file}:\n{e.stderr}")
            continue
        except subprocess.TimeoutExpired as e:
            # 捕获 TimeoutExpired 异常，不使用 e.stderr
            log_records.append(f"Execution timed out for {original_file}. Command was: {e.cmd}")
            continue

        # Generate JaCoCo HTML report
        report_folder = os.path.join(coverage_folder, f"{class_name}-report")
        os.makedirs(report_folder, exist_ok=True)
        try:
            report_cmd = [
                "/home/cxx/fuzz4all/javac/bin/java",
                "-jar",
                "/home/cxx/fuzz4all/jacoco-0.8.12/lib/jacococli.jar",
                "report",
                exec_file,
                "--classfiles",
                class_folder,
                "--sourcefiles",
                os.path.dirname(temp_file),
                "--html",
                report_folder,
            ]
            subprocess.run(report_cmd, check=True, text=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            log_records.append(f"Report generation failed for {original_file}:\n{e.stderr}")

    # 按顺序输出日志
    # for log in sorted(log_records):
    #     print(log)

    return log_records



def combine_reports(exec_files, combined_exec_file):
    """
    Combine multiple JaCoCo `.exec` files into a single `.exec` file.
    """
    cli_path = "/home/cxx/fuzz4all/jacoco-0.8.12/lib/jacococli.jar"
    try:
        combine_cmd = ["/home/cxx/fuzz4all/javac/bin/java", "-jar", cli_path, "merge"] + exec_files + [
            "--destfile",
            combined_exec_file,
        ]
        subprocess.run(combine_cmd, check=True, text=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Combining reports failed:\n{e.stderr}")


def determine_file_name(index,code, folder):
    """
    Determine the file name for a Java source code based on the public class name.
    """
    public_class_match = re.search(r"\s*public(\s)+class(\s)+([^\s\{]+)", code)

    # Ensure the folder exists
    folder_path = f"{folder}/{index}"
    os.makedirs(folder_path, exist_ok=True)
    if public_class_match is None:
        # No public class found, return default file name
        return os.path.join(folder_path, "temp.java")

    # Public class is found, return a file name based on the public class name
    return os.path.join(folder_path, f"{public_class_match[3]}.java")


def coverage_loop(args):
    """
    Main loop for coverage analysis, processing `.fuzz` files in intervals.
    """
    files = glob.glob(os.path.join(args.folder, "*.fuzz"))
    files = sorted(files, key=natural_sort_key)  # Ensure natural sorting order

    combined_exec_file = os.path.join(args.folder, "combined/java-comb.exec")
    combined_folder = os.path.join(args.folder, "combined")
    os.makedirs(combined_folder, exist_ok=True)
    log_file = os.path.join(args.folder, "cxx_log.txt")
    logs = []
    files = files[: args.clip]

    for i in range(0, len(files), args.interval):
        temp_folder = os.path.join(args.folder, "temp")
        os.makedirs(temp_folder, exist_ok=True)

        file_map = {}  # Map temp Java files to original .fuzz files

        for j in range(i, min(i + args.interval, len(files))):
            try:
                with open(files[j], "r", encoding="utf-8") as f:
                    code = f.read()
                    temp_file = determine_file_name(j, code, temp_folder)
                    with open(temp_file, "w", encoding="utf-8") as temp_file_handle:
                        temp_file_handle.write(code)
                    file_map[temp_file] = files[j]  # Map temp file to original .fuzz file
            except Exception as e:
                print(f"Error processing {files[j]}:\n{e}")

        # Pass file_map to compile_and_run
        log = compile_and_run(file_map, args.folder)
        logs.extend(log)

        # Combine coverage reports
        exec_files = glob.glob(os.path.join(args.folder, "coverage/*/*.exec"))
        combine_reports(exec_files, combined_exec_file)

        # Clean up temporary files
        # shutil.rmtree(temp_folder, ignore_errors=True)
    with open(log_file, "w", encoding="utf-8") as f:
        for log in logs:
            f.write(log + "\n")
    print(f"Coverage analysis completed. Logs saved to {log_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, required=True, help="Input folder containing .fuzz files")
    parser.add_argument("--interval", type=int, required=True, help="Number of files to process per batch")
    parser.add_argument("--clip", type=int, required=True, default=100, help="End of your clip")
    args = parser.parse_args()
    coverage_loop(args)


if __name__ == "__main__":
    main()
