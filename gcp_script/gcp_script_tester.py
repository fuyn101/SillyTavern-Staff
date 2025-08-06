#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本文件拖拽处理程序
当用户将txt文件拖拽到此Python脚本上时，程序会读取文件内容并按行存储到数组中
"""

import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import configparser
# 尝试导入gemini api库，如果失败则提示用户安装但不终止程序
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("警告：未找到google-generativeai库，Gemini API功能将不可用")
    print("请运行以下命令安装：pip install google-generativeai")

# 尝试导入requests库，如果失败则询问用户是否自动安装
try:
    import requests
    import json
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("警告：未找到requests库，网络请求功能将不可用")
    print("requests库是程序的核心依赖，没有它程序无法执行基本功能")
    
    # 询问用户是否要自动安装
    try:
        while True:
            user_input = input("是否要自动安装requests库？(y/n): ").strip().lower()
            if user_input in ['y', 'yes', '是']:
                print("正在安装requests库...")
                import subprocess
                import sys
                try:
                    # 使用pip安装requests库
                    result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'],
                                          capture_output=True, text=True, check=True)
                    print("requests库安装成功！")
                    print("请重新运行程序以使用完整功能。")
                    input("按回车键退出...")
                    sys.exit(0)
                except subprocess.CalledProcessError as e:
                    print(f"安装失败：{e}")
                    print("请手动运行以下命令安装：pip install requests")
                    input("按回车键退出...")
                    sys.exit(1)
                except Exception as e:
                    print(f"安装过程中发生错误：{e}")
                    print("请手动运行以下命令安装：pip install requests")
                    input("按回车键退出...")
                    sys.exit(1)
                break
            elif user_input in ['n', 'no', '否']:
                print("用户选择不安装requests库")
                print("程序将无法执行网络请求功能")
                break
            else:
                print("请输入 y 或 n")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)

# 线程锁，用于保护共享资源
print_lock = threading.Lock()

class ProgressBar:
    """
    进度条类，用于在同一行显示测试进度
    """
    def __init__(self, total, description="进度"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update_time = 0
        self.lock = threading.Lock()
        
    def update(self, increment=1):
        """更新进度"""
        with self.lock:
            self.current += increment
            current_time = time.time()
            
            # 每1秒更新一次显示，或者是最后一个
            if current_time - self.last_update_time >= 1.0 or self.current >= self.total:
                self.display()
                self.last_update_time = current_time
    
    def display(self):
        """显示进度条"""
        if self.total == 0:
            return
            
        percentage = (self.current / self.total) * 100
        elapsed_time = time.time() - self.start_time
        
        # 计算预估剩余时间
        if self.current > 0:
            avg_time_per_item = elapsed_time / self.current
            remaining_items = self.total - self.current
            eta = remaining_items * avg_time_per_item
            eta_str = f"剩余: {eta:.0f}s" if eta > 0 else "即将完成"
        else:
            eta_str = "计算中..."
        
        # 创建进度条
        bar_length = 30
        filled_length = int(bar_length * self.current // self.total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # 使用\r回到行首，覆盖之前的内容
        progress_text = f"\r{self.description}: [{bar}] {self.current}/{self.total} ({percentage:.1f}%) - 耗时: {elapsed_time:.1f}s - {eta_str}"
        print(progress_text, end='', flush=True)
        
        # 如果完成了，换行
        if self.current >= self.total:
            print()
    
    def finish(self):
        """完成进度条显示"""
        with self.lock:
            self.current = self.total
            self.display()

def write_error_log(api_key, error_message):
    """
    将错误信息写入celog.txt文件
    """
    try:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_entry = f"[{current_time}] API Key: {api_key}\nError: {error_message}\n{'-'*50}\n"
        
        with open('celog.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        with print_lock:
            print(f"写入错误日志时发生错误: {e}")

# 默认配置
DEFAULT_CONFIG = {
    'concurrent_mode': 'y',
    'concurrent_count': '20',
    'save_file': 'y',
    'parallel_mode': 'n',
    'parallel_count': '5'
}

def load_config():
    """
    从tcfg.ini文件加载配置，如果文件不存在则创建默认配置
    """
    config = configparser.ConfigParser()
    config_file = 'tcfg.ini'
    
    if os.path.exists(config_file):
        try:
            config.read(config_file, encoding='utf-8')
            if 'settings' in config:
                return {
                    'concurrent_mode': config.get('settings', 'concurrent_mode', fallback=DEFAULT_CONFIG['concurrent_mode']),
                    'concurrent_count': config.get('settings', 'concurrent_count', fallback=DEFAULT_CONFIG['concurrent_count']),
                    'save_file': config.get('settings', 'save_file', fallback=DEFAULT_CONFIG['save_file']),
                    'parallel_mode': config.get('settings', 'parallel_mode', fallback=DEFAULT_CONFIG['parallel_mode']),
                    'parallel_count': config.get('settings', 'parallel_count', fallback=DEFAULT_CONFIG['parallel_count'])
                }
        except Exception as e:
            print(f"读取配置文件时发生错误: {e}")
    
    # 如果文件不存在或读取失败，创建默认配置文件
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()

def save_config(config_dict):
    """
    将配置保存到tcfg.ini文件
    """
    config = configparser.ConfigParser()
    config['settings'] = config_dict
    
    try:
        with open('tcfg.ini', 'w', encoding='utf-8') as f:
            config.write(f)
        return True
    except Exception as e:
        print(f"保存配置文件时发生错误: {e}")
        return False

def show_config_menu():
    """
    显示配置菜单并处理用户输入
    """
    current_config = load_config()
    
    while True:
        print("\n" + "="*50)
        print("配置菜单")
        print("="*50)
        print("当前配置:")
        print(f"1. 并发模式（测试连接）: {'开启' if current_config['concurrent_mode'].lower() == 'y' else '关闭'}")
        print(f"2. 并发数（测试连接）: {current_config['concurrent_count']}")
        print(f"3. 并发模式（测试消息）: {'开启' if current_config['parallel_mode'].lower() == 'y' else '关闭'}")
        print(f"4. 并发数（测试消息）: {current_config['parallel_count']}")
        print(f"5. 保存文件: {'是' if current_config['save_file'].lower() == 'y' else '否'}")
        print("\n选项:")
        print("0. 退出程序")
        print("1. 修改并发模式（测试连接）")
        print("2. 修改并发数（测试连接）")
        print("3. 修改并发模式（测试消息）")
        print("4. 修改并发数（测试消息）")
        print("5. 修改保存文件设置")
        print("="*50)
        
        try:
            choice = input("请输入选项 (0-5): ").strip()
            
            if choice == '0':
                print("退出程序...")
                sys.exit(0)
            elif choice == '1':
                print(f"\n当前并发（测试连接）: {'开启' if current_config['concurrent_mode'].lower() == 'y' else '关闭'}")
                new_mode = input("请输入新的并发（测试连接）模式 (y/n): ").strip().lower()
                if new_mode in ['y', 'n']:
                    current_config['concurrent_mode'] = new_mode
                    if save_config(current_config):
                        print("并发（测试连接）已更新")
                    else:
                        print("保存配置失败")
                else:
                    print("无效输入，请输入 y 或 n")
            elif choice == '2':
                print(f"\n当前并发数（测试连接）: {current_config['concurrent_count']}")
                try:
                    new_count = input("请输入新的并发数（测试连接） (正整数): ").strip()
                    count_int = int(new_count)
                    if count_int > 0:
                        current_config['concurrent_count'] = str(count_int)
                        if save_config(current_config):
                            print("并发数（测试连接）已更新")
                        else:
                            print("保存配置失败")
                    else:
                        print("并发数必须是正整数")
                except ValueError:
                    print("无效输入，请输入正整数")
            elif choice == '3':
                print(f"\n当前并发（测试消息）: {'开启' if current_config['parallel_mode'].lower() == 'y' else '关闭'}")
                new_mode = input("请输入新的并发（测试消息）模式 (y/n): ").strip().lower()
                if new_mode in ['y', 'n']:
                    # 如果用户想要开启parallel_mode，先警告并要求二次确认
                    if new_mode == 'y' and current_config['parallel_mode'].lower() != 'y':
                        print("\n" + "="*60)
                        print("警告:使用并发模式发送测试消息具有高风险！")
                        print("="*60)
                        print("并发模式下，您将使用同一ip高频发送相似的请求，这可能导致:")
                        print("1. IP被谷歌标记，导致短期或永久无法使用gemini api")
                        print("2. 项目或账号被谷歌限制甚至封禁")
                        print("\n请再次确认您是否有快速测试大量key可用性的需求！")
                        print("="*60)
                        
                        # 要求用户二次确认
                        while True:
                            try:
                                confirm = input("确定要开启并发模式吗？请输入 'Y' 确认，或输入 'N' 取消: ").strip()
                                if confirm.upper() == 'Y':
                                    current_config['parallel_mode'] = new_mode
                                    if save_config(current_config):
                                        print("并发模式（测试消息）已更新为开启状态！")
                                    else:
                                        print("保存配置失败")
                                    break
                                elif confirm.upper() == 'N':
                                    print("已取消开启并发模式")
                                    break
                                else:
                                    print("请输入 'Y' 或 'N'")
                            except KeyboardInterrupt:
                                print("\n操作被用户中断")
                                break
                    else:
                        # 如果是关闭parallel_mode或者已经是开启状态，直接更新
                        current_config['parallel_mode'] = new_mode
                        if save_config(current_config):
                            print("并发（测试消息）已更新")
                        else:
                            print("保存配置失败")
                else:
                    print("无效输入，请输入 y 或 n")
            elif choice == '4':
                print(f"\n当前并发数（测试消息）: {current_config['parallel_count']}")
                try:
                    new_count = input("请输入新的并发数（测试消息） (正整数): ").strip()
                    count_int = int(new_count)
                    if count_int > 0:
                        current_config['parallel_count'] = str(count_int)
                        if save_config(current_config):
                            print("并发数（测试消息）已更新")
                        else:
                            print("保存配置失败")
                    else:
                        print("并发数必须是正整数")
                except ValueError:
                    print("无效输入，请输入正整数")
            elif choice == '5':
                print(f"\n当前保存文件设置: {'是' if current_config['save_file'].lower() == 'y' else '否'}")
                new_save = input("请输入新的保存文件设置 (y/n): ").strip().lower()
                if new_save in ['y', 'n']:
                    current_config['save_file'] = new_save
                    if save_config(current_config):
                        print("保存文件设置已更新")
                    else:
                        print("保存配置失败")
                else:
                    print("无效输入，请输入 y 或 n")
            else:
                print("无效选项，请输入 0-5")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            sys.exit(0)
        except Exception as e:
            print(f"发生错误: {e}")

def test_single_api_key(api_key, index, total, progress_bar=None):
    """
    测试单个API密钥的函数，用于并发执行
    """
    # 构建URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        # 发送GET请求
        response = requests.get(url, timeout=30)
        
        # 获取返回内容的全文
        response_text = response.text
        
        # 检查是否包含FAILED_PRECONDITION
        if 'FAILED_PRECONDITION' in response_text:
            write_error_log(api_key, f'FAILED_PRECONDITION - 响应内容: {response_text}')
            with print_lock:
                print(f"\n第 {index+1} 个API密钥检测到FAILED_PRECONDITION错误")
            return api_key, 'FAILED_PRECONDITION', True  # 第三个参数表示是否需要停止所有测试
        
        # 分析返回内容
        if 'SUSPENDED' in response_text:
            write_error_log(api_key, f'SUSPENDED - 账号已被封禁 - 响应内容: {response_text}')
            return api_key, '已封', False
        elif 'INVALID_ARGUMENT' in response_text:
            write_error_log(api_key, f'INVALID_ARGUMENT - API密钥无效 - 响应内容: {response_text}')
            return api_key, '无效', False
        else:
            return api_key, '有效', False
            
    except requests.exceptions.Timeout:
        error_msg = '请求超时'
        write_error_log(api_key, error_msg)
        return api_key, '超时', False
    except requests.exceptions.ConnectionError:
        error_msg = '网络连接错误'
        write_error_log(api_key, error_msg)
        return api_key, '连接错误', False
    except requests.exceptions.RequestException as e:
        error_msg = f'请求错误: {str(e)}'
        write_error_log(api_key, error_msg)
        return api_key, f'请求错误: {str(e)}', False
    except Exception as e:
        error_msg = f'未知错误: {str(e)}'
        write_error_log(api_key, error_msg)
        return api_key, f'未知错误: {str(e)}', False

def test_single_api_key_mode2(api_key, index, total, progress_bar=None):
    """
    测试单个API密钥的函数（模式2：实际调用API生成内容）
    """
    if not GENAI_AVAILABLE:
        return api_key, '库未安装', False
    
    try:
        # 创建客户端
        client = genai.Client(api_key=api_key)
        
        # 发送请求
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="hi",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        
        # 获取响应文本
        response_text = response.text
        
        # 如果有有效响应，标记为可用
        if response_text and len(response_text.strip()) > 0:
            return api_key, '可用', False
        else:
            error_msg = "响应为空"
            write_error_log(api_key, error_msg)
            return api_key, '响应为空', False
            
    except Exception as e:
        error_msg = str(e)
        write_error_log(api_key, error_msg)
        
        # 检查是否是地区限制错误
        if 'FAILED_PRECONDITION' in error_msg:
            with print_lock:
                print(f"\n第 {index+1} 个API密钥检测到FAILED_PRECONDITION错误（模式2）")
            return api_key, 'FAILED_PRECONDITION', True
        else:
            return api_key, f'错误: {error_msg}', False

def perform_api_requests(lines_array, config=None, test_mode=1):
    """
    使用并发或串行机制依次测试数组中的每一项作为API密钥发送请求，分析结果并保存有效的key
    test_mode: 1=连接测试模式, 2=实际调用测试模式
    """
    if not REQUESTS_AVAILABLE:
        print("无法执行网络请求：requests库未安装")
        print("requests库是程序的核心依赖，没有它程序无法执行基本功能")
        
        # 询问用户是否要自动安装
        try:
            while True:
                user_input = input("是否要自动安装requests库？(y/n): ").strip().lower()
                if user_input in ['y', 'yes', '是']:
                    print("正在安装requests库...")
                    import subprocess
                    try:
                        # 使用pip安装requests库
                        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'],
                                              capture_output=True, text=True, check=True)
                        print("requests库安装成功！")
                        print("请重新运行程序以使用完整功能。")
                        input("按回车键退出...")
                        sys.exit(0)
                    except subprocess.CalledProcessError as e:
                        print(f"安装失败：{e}")
                        print("请手动运行以下命令安装：pip install requests")
                        input("按回车键退出...")
                        sys.exit(1)
                    except Exception as e:
                        print(f"安装过程中发生错误：{e}")
                        print("请手动运行以下命令安装：pip install requests")
                        input("按回车键退出...")
                        sys.exit(1)
                    break
                elif user_input in ['n', 'no', '否']:
                    print("用户选择不安装requests库")
                    print("程序将无法执行网络请求功能")
                    return
                else:
                    print("请输入 y 或 n")
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            sys.exit(0)
    
    # 如果没有提供配置，使用默认配置
    if config is None:
        config = load_config()
    
    # 根据测试模式选择不同的配置参数
    if test_mode == 1:
        # 模式1：连接测试，使用concurrent相关参数
        concurrent_mode = config['concurrent_mode'].lower() == 'y'
        concurrent_count = int(config['concurrent_count'])
    else:
        # 模式2：实际调用测试，使用parallel相关参数
        concurrent_mode = config['parallel_mode'].lower() == 'y'
        concurrent_count = int(config['parallel_count'])
    
    save_file = config['save_file'].lower() == 'y'
    
    mode_desc = "连接测试" if test_mode == 1 else "实际调用测试"
    if concurrent_mode:
        print(f"开始执行网络请求（{mode_desc}，并发模式，最大并发数：{concurrent_count}）...")
    else:
        print(f"开始执行网络请求（{mode_desc}，串行模式）...")
    
    # 创建进度条
    progress_bar = ProgressBar(len(lines_array), f"测试API密钥({mode_desc})")
    
    start_time = time.time()
    
    # 存储API key的状态
    key_status = {}
    valid_keys = []
    failed_keys = []  # 新增：存储检测失败的密钥
    should_stop = False
    
    if concurrent_mode:
        # 并发模式
        with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            # 根据测试模式选择不同的测试函数
            test_function = test_single_api_key if test_mode == 1 else test_single_api_key_mode2
            
            # 提交所有任务
            future_to_key = {
                executor.submit(test_function, api_key, i, len(lines_array), progress_bar): (api_key, i)
                for i, api_key in enumerate(lines_array)
            }
            
            # 处理完成的任务
            completed_futures = []
            for future in as_completed(future_to_key):
                completed_futures.append(future)
                api_key, index = future_to_key[future]
                
                try:
                    key, status, stop_flag = future.result()
                    key_status[key] = status
                    
                    # 更新进度条
                    progress_bar.update()
                    
                    # 如果是有效密钥，添加到有效列表
                    if status in ['有效', '可用']:
                        valid_keys.append(key)
                    # 如果是检测失败的密钥，添加到失败列表
                    elif status == 'FAILED_PRECONDITION':
                        failed_keys.append(key)
                    
                    # 如果检测到FAILED_PRECONDITION，设置停止标志但继续处理已完成的任务
                    if stop_flag and not should_stop:
                        should_stop = True
                        print(f"\n⚠️  检测到FAILED_PRECONDITION错误，这可能是由于您的IP不在Gemini API的服务范围内，如中国大陆、香港、俄罗斯等国家或地区境内")
                        print(f"\n⚠️  请检查您的网络环境，如开启TUN模式等")
                        print(f"在第 {index+1} 个API密钥处检测到错误，正在停止后续测试并处理已完成的任务...")
                        
                        # 取消所有未完成的任务，防止继续向外网发送请求
                        cancelled_count = 0
                        for f in future_to_key.keys():
                            if not f.done() and f.cancel():
                                cancelled_count += 1
                        
                        print(f"已取消 {cancelled_count} 个未开始的任务，正在处理已完成的任务...")
                
                except Exception as e:
                    key_status[api_key] = f'处理错误: {str(e)}'
                    progress_bar.update()
                
                # 如果已经设置了停止标志，检查是否还有已完成但未处理的任务
                if should_stop:
                    # 继续处理已经完成的任务，但不等待新的任务完成
                    remaining_completed = []
                    for remaining_future in future_to_key.keys():
                        if remaining_future.done() and remaining_future not in completed_futures:
                            remaining_completed.append(remaining_future)
                    
                    # 处理剩余已完成的任务
                    for remaining_future in remaining_completed:
                        remaining_api_key, remaining_index = future_to_key[remaining_future]
                        try:
                            remaining_key, remaining_status, _ = remaining_future.result()
                            key_status[remaining_key] = remaining_status
                            progress_bar.update()
                            
                            if remaining_status in ['有效', '可用']:
                                valid_keys.append(remaining_key)
                            elif remaining_status == 'FAILED_PRECONDITION':
                                failed_keys.append(remaining_key)
                                
                        except Exception as e:
                            key_status[remaining_api_key] = f'处理错误: {str(e)}'
                            progress_bar.update()
                    
                    # 处理完已完成的任务后退出
                    break
        
        # 确保进度条完成
        progress_bar.finish()
        
    else:
        # 串行模式
        test_function = test_single_api_key if test_mode == 1 else test_single_api_key_mode2
        
        for i, api_key in enumerate(lines_array):
            try:
                key, status, stop_flag = test_function(api_key, i, len(lines_array), progress_bar)
                key_status[key] = status
                
                # 更新进度条
                progress_bar.update()
                
                # 如果是有效密钥，添加到有效列表
                if status in ['有效', '可用']:
                    valid_keys.append(key)
                # 如果是检测失败的密钥，添加到失败列表
                elif status == 'FAILED_PRECONDITION':
                    failed_keys.append(key)
                
                # 如果检测到FAILED_PRECONDITION，设置停止标志并退出
                if stop_flag:
                    should_stop = True
                    print(f"\n⚠️  检测到FAILED_PRECONDITION错误，这可能是由于您的IP不在Gemini API的服务范围内，如中国大陆、香港、俄罗斯等国家或地区境内")
                    print(f"\n⚠️  请检查您的网络环境，如开启TUN模式等")
                    print(f"在第 {i+1} 个API密钥处检测到错误，停止后续测试...")
                    print(f"已成功测试 {i+1} 个API密钥，剩余 {len(lines_array) - i - 1} 个未测试")
                    break
                    
            except Exception as e:
                error_msg = f'处理错误: {str(e)}'
                key_status[api_key] = error_msg
                write_error_log(api_key, f'串行模式处理异常: {str(e)}')
                print(f"\n处理第 {i+1} 个API密钥时发生错误: {str(e)}")
                progress_bar.update()
        
        # 确保进度条完成
        progress_bar.finish()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 显示统计结果
    print(f"\n{'='*60}")
    if should_stop:
        print("API密钥测试提前停止（检测到FAILED_PRECONDITION错误）")
    else:
        print("API密钥测试完成")
    
    print(f"实际测试: {len(key_status)} 个密钥（总共 {len(lines_array)} 个）")
    if should_stop and len(key_status) < len(lines_array):
        print(f"未测试: {len(lines_array) - len(key_status)} 个密钥（因提前停止）")
    
    print(f"总耗时: {elapsed_time:.2f} 秒")
    
    if len(key_status) > 0:
        print(f"平均每个密钥耗时: {elapsed_time/len(key_status):.2f} 秒")
    
    # 统计各状态数量
    status_count = {}
    for status in key_status.values():
        status_count[status] = status_count.get(status, 0) + 1
    
    for status, count in status_count.items():
        print(f"{status}: {count} 个")
    
    # 计算有效率
    print(f"\n{'='*60}")
    print("📊 有效率统计")
    
    # 重新计算有效和无效的数量，确保基于相同的测试集
    valid_count_from_tested = 0
    invalid_count_from_tested = 0
    
    # 只统计实际测试过的key的状态
    for status in key_status.values():
        if status in ['有效', '可用']:
            valid_count_from_tested += 1
        elif status in ['已封', '无效', '超时', '连接错误', 'FAILED_PRECONDITION', '响应为空', '库未安装'] or status.startswith('请求错误') or status.startswith('未知错误') or status.startswith('错误:'):
            invalid_count_from_tested += 1
    
    total_tested = len(key_status)
    untested_count = len(lines_array) - total_tested
    
    if total_tested > 0:
        # 使用实际测试过的key计算有效率
        effectiveness_rate = (valid_count_from_tested / total_tested) * 100
        print(f"实际测试的key数量: {total_tested} 个")
        print(f"可用的key数量: {valid_count_from_tested} 个")
        print(f"不可用的key数量: {invalid_count_from_tested} 个")
        if untested_count > 0:
            print(f"未测试的key数量: {untested_count} 个（因提前停止）")
        print(f"可用率: {effectiveness_rate:.2f}%（基于实际测试的{total_tested}个key）")
        
        # 如果有未测试的key，给出说明
        if untested_count > 0:
            print(f"\n⚠️  注意: 由于检测过程提前停止，还有 {untested_count} 个key未进行测试")
            print(f"完整的有效率需要测试完所有 {len(lines_array)} 个key才能准确计算")
        
        print(f"\n说明: 若有报错，请查看同目录下生成的celog.txt（其中为每个key对应的具体报错信息）确定key不可用的原因")
        print(f"仅代表在2.5flash的测试消息中的结果。上下文超过250k / 敏感内容 / 预设问题等仍可能导致2.5pro在酒馆等前端中不可用")
    else:
        print("没有测试任何key")
    
    # 根据配置决定是否保存有效的API密钥到文件
    if valid_keys and save_file:
        output_file = "valid_api_keys.txt"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for key in valid_keys:
                    f.write(key + '\n')
            print(f"\n已将 {len(valid_keys)} 个有效API密钥保存到文件: {output_file}")
        except Exception as e:
            print(f"保存文件时发生错误: {e}")
    elif valid_keys and not save_file:
        print(f"\n找到 {len(valid_keys)} 个有效API密钥（根据配置未保存到文件）")
    else:
        print("\n没有找到有效的API密钥")
    
    # 保存检测失败的API密钥到单独的文件
    if failed_keys and save_file:
        failed_output_file = "failed_api_keys.txt"
        try:
            with open(failed_output_file, 'w', encoding='utf-8') as f:
                for key in failed_keys:
                    f.write(key + '\n')
            print(f"已将 {len(failed_keys)} 个检测失败的API密钥保存到文件: {failed_output_file}")
        except Exception as e:
            print(f"保存检测失败密钥文件时发生错误: {e}")
    elif failed_keys and not save_file:
        print(f"找到 {len(failed_keys)} 个检测失败的API密钥（根据配置未保存到文件）")
    
    return key_status, valid_keys

def main():
    try:
        print("启动...")
        print(r"                             _                _            _            ")
        print(r"  __ _ _ __ ___  _ __       | | _____ _   _  | |_ ___  ___| |_ ___ _ __ ")
        print(r" / _` | '_ ` _ \| '_ \ _____| |/ / _ \ | | | | __/ _ \/ __| __/ _ \ '__|")
        print(r"| (_| | | | | | | | | |_____|   <  __/ |_| | | ||  __/\__ \ ||  __/ |   ")
        print(r" \__, |_| |_| |_|_| |_|     |_|\_\___|\__, |  \__\___||___/\__\___|_|   ")
        print(r" |___/                                |___/                             ")

        # 检查是否有命令行参数（拖拽的文件路径）
        if len(sys.argv) < 2:
            print(f"\n{'='*60}")
            print("本脚本作者: 类脑@KKTsN")
            print("使用方法：")
            print("1. 准备好一个内容为Gemini API Keys 的文件，每行一个，不含任何额外内容。")
            print("2. 在文件资源管理器中，将txt文件拖拽到tester.py上。或者在命令行中运行：python tester.py <文件路径>")
            print("若要修改配置，请直接双击运行tester.py。现在显示配置菜单：")
            
            # 显示配置菜单
            show_config_menu()
            return
        
        # 获取拖拽的文件路径
        file_path = sys.argv[1]
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件 '{file_path}' 不存在")
            input("按回车键退出...")
            return
        
        # 检查是否为文本文件
        if not file_path.lower().endswith('.txt'):
            print(f"警告：文件 '{file_path}' 不是txt文件，但仍会尝试读取")
        
        try:
            # 读取文件内容并按行存储到数组中
            with open(file_path, 'r', encoding='utf-8') as file:
                lines_array = file.readlines()
            
            # 去除每行末尾的换行符
            lines_array = [line.rstrip('\n\r') for line in lines_array]
            
            print(f"成功读取文件：{file_path}")
            print(f"文件共有 {len(lines_array)} 行")
            print("-" * 50)
            print("获取到文件内容：")
            
            # 打印数组内容
            for i, line in enumerate(lines_array):
                print(f"[{i}]: {line}")
            
            print("-" * 50)
            
            # 询问用户选择检测模式
            if len(lines_array) > 0:
                print("-" * 50)
                print("请选择检测模式：")
                print("1. 连接（仅检测能否获取模型列表，即酒馆中的连接，速度较快）")
                print("2. 测试消息（发送测试消息，若能收到有效回复则此key仍有额度）")
                
                while True:
                    try:
                        mode_choice = input("请输入模式选择 (1/2): ").strip()
                        if mode_choice in ['1', '2']:
                            test_mode = int(mode_choice)
                            break
                        else:
                            print("无效输入，请输入 1 或 2")
                    except KeyboardInterrupt:
                        print("\n\n程序被用户中断")
                        return
                    except Exception as e:
                        print(f"输入错误: {e}")
                
                print("-" * 50)
                mode_desc = "连接测试" if test_mode == 1 else "实际调用测试"
                print(f"开始使用 {len(lines_array)} 个key进行{mode_desc}...")
                
                # 如果选择模式2但genai库不可用，提示用户
                if test_mode == 2 and not GENAI_AVAILABLE:
                    print("模式2需要google-generativeai库，但该库未安装")
                    print("请运行以下命令安装：pip install google-generativeai")
                    print("将自动切换到模式1进行测试...")
                    test_mode = 1
                
                perform_api_requests(lines_array, test_mode=test_mode)
            else:
                print("错误：文件内容为空或无效，无法执行网络请求")
            
        except UnicodeDecodeError:
            # 如果UTF-8编码失败，尝试使用GBK编码（中文Windows系统常用）
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    lines_array = file.readlines()
                
                lines_array = [line.rstrip('\n\r') for line in lines_array]
                
                print(f"成功读取文件（使用GBK编码）：{file_path}")
                print(f"文件共有 {len(lines_array)} 行")
                print("-" * 50)
                print("获取到文件内容：")
                
                for i, line in enumerate(lines_array):
                    print(f"[{i}]: {line}")
                
                print("-" * 50)
                
                # 询问用户选择检测模式（GBK编码分支）
                if len(lines_array) > 0:
                    print("-" * 50)
                    print("请选择检测模式：")
                    print("1. 连接（仅检测能否获取模型列表，即酒馆中的连接，速度较快）")
                    print("2. 测试消息（发送测试消息，若能收到有效回复则此key仍有额度）")
                    
                    while True:
                        try:
                            mode_choice = input("请输入模式选择 (1/2): ").strip()
                            if mode_choice in ['1', '2']:
                                test_mode = int(mode_choice)
                                break
                            else:
                                print("无效输入，请输入 1 或 2")
                        except KeyboardInterrupt:
                            print("\n\n程序被用户中断")
                            return
                        except Exception as e:
                            print(f"输入错误: {e}")
                    
                    print("-" * 50)
                    mode_desc = "连接测试" if test_mode == 1 else "实际调用测试"
                    print(f"开始使用 {len(lines_array)} 个key进行{mode_desc}...")
                    
                    # 如果选择模式2但genai库不可用，提示用户
                    if test_mode == 2 and not GENAI_AVAILABLE:
                        print("模式2需要google-generativeai库，但该库未安装")
                        print("请运行以下命令安装：pip install google-generativeai")
                        print("将自动切换到模式1进行测试...")
                        test_mode = 1
                    
                    perform_api_requests(lines_array, test_mode=test_mode)
                else:
                    print("错误：文件内容为空或无效，无法执行网络请求")
                
            except Exception as e:
                print(f"读取文件时发生错误：{e}")
                input("按回车键退出...")
                return
        
        except Exception as e:
            print(f"读取文件时发生错误：{e}")
            input("按回车键退出...")
            return
        
        # 等待用户按键后退出
        input("按回车键退出...")
        
    except Exception as e:
        print(f"运行时发生严重错误：{e}")
        print("错误详情：")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()