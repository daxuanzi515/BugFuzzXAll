# README
## Core task
It contains 2 parts: prompts generation and selection; fuzzing examples generation.

The 1st phase uses chatgpt4o to generate prompts from given documents for requirements and then refine them via evaluating scores.
If not given prompt in best_prompt.txt, it will use api to generate prompts.

The 2nd phase uses startcoder model to generate programs via refined prompts. 
Then check these examples using corresponding compilers. 
Evaluate outputs from starcoder via scoring generated tokens function. 
Collect results from compilers to divide categories of bugs.

## Localization
### copy files
You need to copy some compilers in docker.
Load docker:
```bash
docker load < Fuzz4All_Docker_Image.tar.gz # this may take a while.
docker run -it --rm --runtime=nvidia --gpus all fuzz4all/fuzz4all:v3 bash
cd /home/Fuzz4All
```

Get container id:
```bash
docker ps
docker cp id:/home/Fuzz4All/??? /home/cxx/fuzz4all/???
```
### PreDownload
original link: https://huggingface.co/bigcode/starcoder
docker tar: https://zenodo.org/records/10456883

### customize
#### setting
```bash
cd /home/cxx/fuzz4all/Fuzz4All
conda activate fuzz4all
export FUZZING_BATCH_SIZE=1
export FUZZING_MODEL="bigcode/starcoderbase"
export FUZZING_DEVICE="gpu"
export PYTHONPATH=$PYTHONPATH:/home/cxx/fuzz4all
export OPENAI_API_KEY=???
```

#### proxy
if you use, it is necessary.
```bash
env | grep -i proxy
remove socks:
unset all_proxy
unset ALL_PROXY
```

#### launch
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/cpp_demo.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/demo/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/g++
```

HF-MIRROR:
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
export HF_ENDPOINT=https://hf-mirror.com

### EXPERIMENTS
#### C++ g++-13.0.1
#### NEED A TRUE API KEY FOR GPT-4
Mine:
```bash
cd /home/cxx/fuzz4all/Fuzz4All
conda activate fuzz4all
export FUZZING_BATCH_SIZE=1
export FUZZING_MODEL="bigcode/starcoderbase"
export FUZZING_DEVICE="gpu"
export PYTHONPATH=$PYTHONPATH:/home/cxx/fuzz4all
export OPENAI_API_KEY=???
```

Magic cannot work well in openAI like this:
```bash
Error: Connection error.. Retrying...
Error: Connection error.. Retrying...
Error: Connection error.. Retrying...
```
Solution:
Find your openai(1.54) package and edit proxy settings.
My path: `/home/cxx/anaconda3/envs/fuzz4all/lib/python3.10/site-packages/openai/_base_client.py`
```python
self._proxies = {'http': 'http://127.0.0.1:7899', 'https': 'https://127.0.0.1:7899'}
```
and 
```python   
pip install urllib3==1.25.11
```

Pay Attention to your cuda memory, it is easy to overflow.
So I change this code for computation memory <= 23.9GB:
```python
    # it can work but slow
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,  
        llm_int8_threshold=6.0 # 4.0 / 6.0 
    )
    # 加载模型时传递 quantization_config
    self.model = AutoModelForCausalLM.from_pretrained(
        checkpoint,
        quantization_config=quantization_config,
        device_map="auto"
    )
```

##### 1. with auto prompt AND cpp_23.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/cpp_23.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/cpp_23/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/g++
```


##### 2. with auto prompt AND cpp_apply.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/cpp_apply.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/cpp_apply/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/g++
```

##### 3. with auto prompt AND cpp_expected.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/cpp_expected.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/cpp_expected/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/g++
```


##### 4. with auto prompt AND cpp_variant.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/cpp_variant.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/cpp_variant/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/g++
```


#### C gcc-13.0.1
##### 1. with auto prompt AND c_23.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/c_23.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/c_23/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/gcc
```

##### 2. with auto prompt AND c_std.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/c_std.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/c_std/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/gcc
```

##### 3. with auto prompt AND c_typedef.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/c_typedef.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/c_typedef/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/gcc
```
##### 4. with auto prompt AND c_union.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/c_union.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/c_union/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/gcc
```


#### Python 3.10.15
##### 1. with auto prompt AND qiskit_opt_and_qasm.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/qiskit_opt_and_qasm.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/qiskit_opt_and_qasm/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target python
```
##### 2. with auto prompt AND qiskit_for_loop.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/qiskit_for_loop.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/qiskit_for_loop/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target python
```

##### 3. with auto prompt AND qiskit_linear_function.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/qiskit_linear_function.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/qiskit_linear_function/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target python
```

##### 4. with auto prompt AND qiskit_switch.md document:
```bash
cd Fuzz4All
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/qiskit_switch.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/qiskit_switch/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target python
```
#### Java
##### 1. java_std
```bash
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/java_std.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/java_std/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/javac/bin/javac
```
##### 2. java_finally

```bash
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/java_finally.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/java_finally/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/javac/bin/javac
```
##### 3. java_instanceof

```bash
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/java_instanceof.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/java_instanceof/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/javac/bin/javac
```

##### 4. java_synchronize

```bash
python3 /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/java_synchronize.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/java_synchronize/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/javac/bin/javac
```

### Coverage Computation
Preconditions install:
```bash
sudo apt-get install flex
sudo apt install lcov
```
Codes Fix:
change `/home/cxx/fuzz4all/scripts/build_gcc_coverage_cxx.sh`:
```bash
#!/bin/sh

# 该脚本用于构建带有覆盖选项的GCC
cd /home/cxx/fuzz4all/coverage

# 克隆GCC源代码
git clone git://gcc.gnu.org/git/gcc.git /home/cxx/fuzz4all/coverage/gcc-13
cd /home/cxx/fuzz4all/coverage/gcc-13

# 切换到GCC 13.1.0版本
git checkout releases/gcc-13.1.0

# 下载并安装GCC构建所需的依赖项
./contrib/download_prerequisites

# 创建构建目录
mkdir /home/cxx/fuzz4all/coverage/gcc-coverage-build
cd /home/cxx/fuzz4all/coverage/gcc-coverage-build

# 配置GCC，启用C和C++语言，并启用覆盖选项
/home/cxx/fuzz4all/coverage/gcc-13/configure --enable-languages=c,c++ --prefix=/home/cxx/fuzz4all/coverage/GCC-13-COVERAGE --enable-coverage
# 使用12个核心并行编译GCC
make -j 12
# 安装GCC
make install
```

Then edit `/home/cxx/fuzz4all/tools/coverage/CPP/collect_coverage.py` and `/home/cxx/fuzz4all/tools/coverage/C/collect_coverage.py` to set the correct compiler and coverage folder:

```bash
COMPILER = "/home/cxx/fuzz4all/coverage/GCC-13-COVERAGE/bin/g++"
COV_FOLDER = "/home/cxx/fuzz4all/coverage/gcc-coverage-build/gcc"
GCOV = "/home/cxx/fuzz4all/coverage/GCC-13-COVERAGE/bin/gcov"
```

Install JaCoCo (Optional):
https://www.jacoco.org/jacoco/

Mine: jacoco-0.8.12
```bash
# Two important path:
/home/cxx/fuzz4all/jacoco-0.8.12/lib/jacocoagent.jar
/home/cxx/fuzz4all/jacoco-0.8.12/lib/jacococli.jar
# Your java and javac path, choose official docker version
/home/cxx/fuzz4all/javac/bin/java
/home/cxx/fuzz4all/javac/bin/javac
```
Then add them to `/home/cxx/fuzz4all/tools/coverage/JAVA/collect_coverage_cxx.py`.

#### C++ example
```bash
cd /home/cxx/fuzz4all
conda activate fuzz4all
export PYTHONPATH=$PYTHONPATH:/home/cxx/fuzz4all
./scripts/build_gcc_coverage_cxx.sh # only once for c and cpp spend 1 hour time
python /home/cxx/fuzz4all/tools/coverage/CPP/collect_coverage.py --folder /home/cxx/fuzz4all/outputs/cpp_23 --interval 100 --start 0 --end 100
```
The Result terminal:
```bash
(fuzz4all) cxx@cxx-Precision-3660:~/fuzz4all$ python /home/cxx/fuzz4all/tools/coverage/CPP/collect_coverage.py --folder /home/cxx/fuzz4all/outputs/cpp_23 --interval 100 --start 0 --end 100
Deleting all .da files in . and subdirectories
Done.
147681 17264
Total valid: 31
Fuzzing •  99% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸  99/100 • 0:02:01
```
Then it creates a `coverage.csv` file and a `valid.txt` file in `/home/cxx/fuzz4all/outputs/cpp_23` directory.

#### C example
```bash
cd /home/cxx/fuzz4all
python /home/cxx/fuzz4all/tools/coverage/C/collect_coverage.py --folder /home/cxx/fuzz4all/outputs/c_std -interval 100 --start 0 --end 100
```
The Result terminal:
```bash
(fuzz4all) cxx@cxx-Precision-3660:~/fuzz4all$ python /home/cxx/fuzz4all/tools/coverage/C/collect_coverage.py --folder /home/cxx/fuzz4all/outputs/c_std --interval 100 --start 0 --end 100
Deleting all .da files in . and subdirectories
Done.
91781 12616
Total valid: 48
Fuzzing •  99% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸  99/100 • 0:00:55
```

#### Python example
```bash
cd /home/cxx/fuzz4all
#./scripts/build_qiskit_coverage_cxx.sh
python /home/cxx/fuzz4all/tools/coverage/QISKIT/collect_coverage.py --folder /home/cxx/fuzz4all/outputs/qiskit_opt_and_qasm --interval 100
```
The Result terminal:
```bash
Error in subprocess run: Command '['coverage', 'run', '/home/cxx/fuzz4all/outputs/qiskit_opt_and_qasm/99.fuzz']' returned non-zero exit status 1.
Error in subprocess run: Command '['coverage', 'run', '/home/cxx/fuzz4all/outputs/qiskit_opt_and_qasm/97.fuzz']' returned non-zero exit status 1.
End exec. duration 8.1261 seconds.
Run 100 files in this chunk.
[parallelism batch size: 24 - timeout per batch:5 seconds.]
Total success: 29. Total failure (timeout): 71
```
#### Java example (optional)
```bash
python3 /home/cxx/fuzz4all/tools/coverage/JAVA/collect_coverage_update.py --folder /home/cxx/fuzz4all/outputs/java_std --interval 100 --clip 100
python3 /home/cxx/fuzz4all/tools/coverage/JAVA/collect_coverage_update.py --folder /home/cxx/fuzz4all/outputs/java_finally --interval 100 --clip 100
python3 /home/cxx/fuzz4all/tools/coverage/JAVA/collect_coverage_update.py --folder /home/cxx/fuzz4all/outputs/java_instanceof --interval 100 --clip 100
python3 /home/cxx/fuzz4all/tools/coverage/JAVA/collect_coverage_update.py --folder /home/cxx/fuzz4all/outputs/java_synchronize --interval 100 --clip 100
```

collect coverage (during running):
```bash
/home/cxx/fuzz4all/javac/bin/java -jar /home/cxx/fuzz4all/jacoco-0.8.12/lib/jacocoagent.jar=destfile=/home/cxx/fuzz4all/outputs/java_std/combined/java-comb.exec,includes=java_std/src/main/java/ --classfiles /home/cxx/fuzz4all/outputs/java_std/classes --sourcefiles /home/cxx/fuzz4all/outputs/java_std/src/main/java/ --html /home/cxx/fuzz4all/outputs/java_std/combined/html/ --xml /home/cxx/fuzz4all/outputs/java_std/combined/xml/
```

generate a csv report:
```bash
/home/cxx/fuzz4all/javac/bin/java -jar /home/cxx/fuzz4all/jacoco-0.8.12/lib/jacococli.jar report /home/cxx/fuzz4all/outputs/java_std/combined/java-comb.exec \
    --classfiles /home/cxx/fuzz4all/outputs/java_std/classes \
    --csv /home/cxx/fuzz4all/outputs/java_std/combined/coverage.csv
    #-sourcefiles /home/cxx/fuzz4all/outputs/java_std/temp 


/home/cxx/fuzz4all/javac/bin/java -jar /home/cxx/fuzz4all/jacoco-0.8.12/lib/jacococli.jar report /home/cxx/fuzz4all/outputs/java_finally/combined/java-comb.exec \
    --classfiles /home/cxx/fuzz4all/outputs/java_finally/classes \
    --csv /home/cxx/fuzz4all/outputs/java_finally/combined/coverage.csv

/home/cxx/fuzz4all/javac/bin/java -jar /home/cxx/fuzz4all/jacoco-0.8.12/lib/jacococli.jar report /home/cxx/fuzz4all/outputs/java_instanceof/combined/java-comb.exec \
    --classfiles /home/cxx/fuzz4all/outputs/java_instanceof/classes \
    --csv /home/cxx/fuzz4all/outputs/java_instanceof/combined/coverage.csv

/home/cxx/fuzz4all/javac/bin/java -jar /home/cxx/fuzz4all/jacoco-0.8.12/lib/jacococli.jar report /home/cxx/fuzz4all/outputs/java_synchronize/combined/java-comb.exec \
    --classfiles /home/cxx/fuzz4all/outputs/java_synchronize/classes \
    --csv /home/cxx/fuzz4all/outputs/java_synchronize/combined/coverage.csv  
```


#### ERROR SUMMARY
Edit your path in `/home/cxx/fuzz4all/tools/coverage/ERROR/list.py`
```bash
# change the path to your own and your output folder
python3 /home/cxx/fuzz4all/tools/coverage/ERROR/py_validation_classification.py
python3 /home/cxx/fuzz4all/tools/coverage/ERROR/newer.py
```
It will generate `error_summary.csv` in output folder.
