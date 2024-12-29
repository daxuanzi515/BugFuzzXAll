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

