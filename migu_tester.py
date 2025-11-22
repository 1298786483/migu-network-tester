#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
咪咕视频网络测试工具
Migu Video Network Testing Tool
"""

import requests
import time
import threading
from datetime import datetime
import argparse
import sys

class MiguNetworkTester:
    def __init__(self, threads=1, interval=0, duration=0):
        """
        初始化测试器
        :param threads: 并发线程数
        :param interval: 请求间隔(秒)
        :param duration: 测试时长(秒)，0表示无限制
        """
        self.threads = threads
        self.interval = interval
        self.duration = duration
        self.total_bytes = 0
        self.total_requests = 0
        self.start_time = None
        self.running = True
        self.lock = threading.Lock()
        
        # 咪咕视频相关域名
        self.test_urls = [
            'https://www.migu.cn',
            'https://m.miguvideo.com',
            'https://www.miguvideo.com',
        ]
    
    def format_bytes(self, bytes_num):
        """格式化字节显示"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_num < 1024.0:
                return f"{bytes_num:.2f} {unit}"
            bytes_num /= 1024.0
        return f"{bytes_num:.2f} PB"
    
    def make_request(self, url):
        """发送HTTP请求"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            content_length = len(response.content)
            
            with self.lock:
                self.total_bytes += content_length
                self.total_requests += 1
            
            return True, content_length
        except Exception as e:
            return False, 0
    
    def worker(self, thread_id):
        """工作线程"""
        url_index = 0
        while self.running:
            if self.duration > 0:
                elapsed = time.time() - self.start_time
                if elapsed >= self.duration:
                    break
            
            url = self.test_urls[url_index % len(self.test_urls)]
            success, bytes_received = self.make_request(url)
            
            if success:
                print(f"[线程{thread_id}] 请求成功: {url} - {self.format_bytes(bytes_received)}")
            else:
                print(f"[线程{thread_id}] 请求失败: {url}")
            
            url_index += 1
            
            if self.interval > 0:
                time.sleep(self.interval)
    
    def print_stats(self):
        """打印统计信息"""
        while self.running:
            time.sleep(5)
            elapsed = time.time() - self.start_time
            
            with self.lock:
                speed = self.total_bytes / elapsed if elapsed > 0 else 0
                print(f"\n{'='*60}")
                print(f"运行时间: {elapsed:.2f} 秒")
                print(f"总请求数: {self.total_requests}")
                print(f"总流量: {self.format_bytes(self.total_bytes)}")
                print(f"平均速度: {self.format_bytes(speed)}/s")
                print(f"{'='*60}\n")
    
    def start(self):
        """启动测试"""
        print(f"\n{'='*60}")
        print("咪咕视频网络测试工具")
        print(f"{'='*60}")
        print(f"并发线程: {self.threads}")
        print(f"请求间隔: {self.interval} 秒")
        print(f"测试时长: {'无限制' if self.duration == 0 else f'{self.duration} 秒'}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        self.start_time = time.time()
        
        # 启动统计线程
        stats_thread = threading.Thread(target=self.print_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        # 启动工作线程
        workers = []
        for i in range(self.threads):
            t = threading.Thread(target=self.worker, args=(i+1,))
            t.daemon = True
            t.start()
            workers.append(t)
        
        try:
            # 等待所有工作线程完成
            for t in workers:
                t.join()
        except KeyboardInterrupt:
            print("\n\n检测到中断信号，正在停止...")
            self.running = False
        
        # 最终统计
        elapsed = time.time() - self.start_time
        print(f"\n{'='*60}")
        print("测试完成 - 最终统计")
        print(f"{'='*60}")
        print(f"总运行时间: {elapsed:.2f} 秒")
        print(f"总请求数: {self.total_requests}")
        print(f"总流量: {self.format_bytes(self.total_bytes)}")
        print(f"平均速度: {self.format_bytes(self.total_bytes / elapsed)}/s")
        print(f"{'='*60}\n")

    def main():
        parser = argparse.ArgumentParser(description='咪咕视频网络测试工具')
        parser.add_argument('-t', '--threads', type=int, default=1, help='并发线程数 (默认: 1)')
        parser.add_argument('-i', '--interval', type=float, default=0, help='请求间隔秒数 (默认: 0)')
        parser.add_argument('-d', '--duration', type=int, default=0, help='测试时长秒数 (默认: 0 无限制)')
        
        args = parser.parse_args()
        
        if args.threads < 1:
            print("错误: 线程数必须大于0")
            sys.exit(1)
        
        tester = MiguNetworkTester(
            threads=args.threads,
            interval=args.interval,
            duration=args.duration
        )
        
        tester.start()

    if __name__ == '__main__':
        main()