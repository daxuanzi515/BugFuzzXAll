import argparse
import glob
import os
import re
import shutil
import subprocess


def natural_sort_key(s):
    _nsre = re.compile(r"([0-9]+)")
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]
            
def compile_and_run(file_map, output_folder):
    """
    Compile and run Java files using `javac` and `java` with JaCoCo.
    Generate coverage reports for each file.
    """
    agent_path = "/home/cxx/fuzz4all/jacoco-0.8.12/lib/jacocoagent.jar"
    coverage_folder = os.path.join(output_folder, "coverage")
    os.makedirs(coverage_folder, exist_ok=True)

    log_records = []  # 用于记录日志

    for temp_file, original_file in file_map.items():
        class_name = os.path.splitext(os.path.basename(temp_file))[0]
        class_folder = os.path.join(output_folder, "classes")
        os.makedirs(class_folder, exist_ok=True)

        # Compile Java file
        try:
            compile_cmd = ["/home/cxx/fuzz4all/javac/bin/javac", "-d", class_folder, temp_file]
            subprocess.run(compile_cmd, check=True, text=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.replace(temp_file, original_file)
            log_records.append(f"Compilation failed for {original_file}:\n{error_message}")
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
            subprocess.run(run_cmd, check=True, text=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            log_records.append(f"Execution failed for {original_file}:\n{e.stderr}")
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
    for log in sorted(log_records):
        print(log)



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

       
def determine_file_name(index, code, temp_folder):
    """
    Determine the file name for a Java source code based on the public class name.
    Handles cases with duplicate class names or missing public class.
    """
    # Match public class name
    public_class_match = re.search(r"\s*public\s+class\s+([^\s\{]+)", code)
    
    if public_class_match:
        class_name = public_class_match.group(1)
    else:
        # Fallback to temp file naming
        class_name = f"TempClass_{index}"

    # Ensure unique file name in the temp folder
    temp_file_path = os.path.join(temp_folder, f"{class_name}.java")
    unique_file_path = temp_file_path
    counter = 1

    while os.path.exists(unique_file_path):
        unique_file_path = os.path.join(temp_folder, f"{class_name}_{counter}.java")
        counter += 1

    return unique_file_path

        
def coverage_loop(args):
    """
    Main loop for coverage analysis, processing `.fuzz` files in intervals.
    """
    files = glob.glob(os.path.join(args.folder, "*.fuzz"))
    files = sorted(files, key=natural_sort_key)  # Ensure natural sorting order

    combined_exec_file = os.path.join(args.folder, "combined/java-comb.exec")
    combined_folder = os.path.join(args.folder, "combined")
    os.makedirs(combined_folder, exist_ok=True)
    end_num = args.clip if args.clip else len(files)  # Process all files if no clip specified
    files = files[:end_num]

    for i in range(0, len(files), args.interval):
        temp_folder = os.path.join(args.folder, f"temp_interval_{i}")
        coverage_folder = os.path.join(args.folder, f"coverage_interval_{i}")
        os.makedirs(temp_folder, exist_ok=True)
        os.makedirs(coverage_folder, exist_ok=True)

        file_map = {}  # Map temp Java files to original .fuzz files

        # Process files in the current interval
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
        compile_and_run(file_map, coverage_folder)

        # Combine only the current interval's .exec files
        current_exec_files = glob.glob(os.path.join(coverage_folder, "*.exec"))
        interval_exec_file = os.path.join(combined_folder, f"interval_{i}.exec")
        combine_reports(current_exec_files, interval_exec_file)

        # Clean up temporary files
        shutil.rmtree(temp_folder, ignore_errors=True)
        shutil.rmtree(coverage_folder, ignore_errors=True)

    # After all intervals, combine all interval .exec files
    all_interval_exec_files = glob.glob(os.path.join(combined_folder, "interval_*.exec"))
    combine_reports(all_interval_exec_files, combined_exec_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, required=True, help="Input folder containing .fuzz files")
    parser.add_argument("--interval", type=int, required=True, help="Number of files to process per batch")
    parser.add_argument("--clip", type=int, required=True, default=1, help="End of your clip")
    args = parser.parse_args()
    coverage_loop(args)


if __name__ == "__main__":
    main()
