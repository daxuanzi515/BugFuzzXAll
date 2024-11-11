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
docker load < Fuzz4All_Docker_Image.tar.gz # this may take a while.
docker run -it --rm --runtime=nvidia --gpus all fuzz4all/fuzz4all:v3 bash
cd /home/Fuzz4All

Get container id:
docker ps
docker cp id:/home/Fuzz4All/??? /home/cxx/fuzz4all/???

### PreDownload
original link: https://huggingface.co/bigcode/starcoder
docker tar: https://zenodo.org/records/10456883

### customize
export FUZZING_BATCH_SIZE=1
export FUZZING_MODEL="bigcode/starcoderbase"
export FUZZING_DEVICE="gpu"
export PYTHONPATH=$PYTHONPATH:/home/cxx/fuzz4all
export OPENAI_API_KEY=???
----

proxy: it is necessary.
env | grep -i proxy
remove socks:
unset all_proxy
----
cd Fuzz4All

python /home/cxx/fuzz4all/Fuzz4All/fuzz.py \
    --config /home/cxx/fuzz4all/config/cpp_demo.yaml \
    main_with_config \
    --folder /home/cxx/fuzz4all/outputs/demo/ \
    --batch_size 5 \
    --model_name bigcode/starcoderbase \
    --target /home/cxx/fuzz4all/gcc-13/bin/g++
----
fix something in model.py:
"out of memory" kill problem:
batch_size = 1
self.model = (
    AutoModelForCausalLM.from_pretrained(
	checkpoint,
	load_in_8bit=True,
	device_map="auto"
    )
)
                        
                        
