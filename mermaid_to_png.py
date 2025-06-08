#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mermaid to PNG Converter (无依赖版本)
从Markdown文件中提取Mermaid图表并转换为PNG图片

功能:
- 扫描指定目录下的所有.md文件
- 提取文件中的mermaid代码块
- 通过Kroki API转换为PNG图片
- 保存图片到与源文件同级的专门文件夹中

特点:
- 仅使用Python标准库，无需安装额外依赖
- 自动创建专门的图片文件夹

作者: GitHub Copilot
日期: 2025-06-08
"""

import os
import re
import urllib.request
import urllib.parse
import urllib.error
import json
from pathlib import Path
import time
from typing import List, Tuple, Optional


class MermaidToPngConverter:
    """Mermaid图表转PNG转换器（无依赖版本）"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化转换器
        
        Args:
            output_dir: 输出目录，如果为None则在源文件同级目录创建专门文件夹
        """
        self.output_dir = output_dir
        
    def find_markdown_files(self, directory: str) -> List[str]:
        """
        查找目录下所有的Markdown文件
        
        Args:
            directory: 要搜索的目录路径
            
        Returns:
            Markdown文件路径列表
        """
        markdown_files = []
        directory_path = Path(directory)
        
        if directory_path.is_file() and directory_path.suffix == '.md':
            return [str(directory_path)]
            
        for file_path in directory_path.glob('**/*.md'):
            markdown_files.append(str(file_path))
            
        return markdown_files
    
    def extract_mermaid_blocks(self, markdown_content: str) -> List[Tuple[str, int]]:
        """
        从Markdown内容中提取Mermaid代码块
        
        Args:
            markdown_content: Markdown文件内容
            
        Returns:
            Mermaid代码块列表，每个元素是(代码, 序号)的元组
        """
        # 匹配mermaid代码块的正则表达式
        mermaid_pattern = r'```mermaid\n(.*?)\n```'
        matches = re.findall(mermaid_pattern, markdown_content, re.DOTALL)
        
        # 返回代码块和序号
        return [(match.strip(), i + 1) for i, match in enumerate(matches)]
    
    def convert_mermaid_to_png(self, mermaid_code: str) -> Optional[bytes]:
        """
        使用Kroki API将Mermaid代码转换为PNG
        
        Args:
            mermaid_code: Mermaid图表代码
            
        Returns:
            PNG图片的字节数据，失败时返回None
        """
        try:
            # 使用Kroki API
            api_url = "https://kroki.io/mermaid/png"
            
            print(f"    正在请求Kroki API...")
            print(f"    图表代码长度: {len(mermaid_code)} 字符")
            
            # 准备请求数据
            data = mermaid_code.encode('utf-8')
            
            # 创建请求
            req = urllib.request.Request(
                api_url,
                data=data,
                headers={
                    'Content-Type': 'text/plain; charset=utf-8',
                    'Accept': 'image/png',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Mermaid-Converter/1.0'
                }
            )
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        content = response.read()
                        print(f"    ✅ 成功获取PNG图片 ({len(content)} bytes)")
                        return content
                    else:
                        print(f"    ❌ 返回了非图片内容: {content_type}")
                        return None
                else:
                    print(f"    ❌ API请求失败: {response.status}")
                    return None
                    
        except urllib.error.HTTPError as e:
            print(f"    ❌ HTTP错误: {e.code} - {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"    ❌ URL错误: {e.reason}")
            return None
        except Exception as e:
            print(f"    ❌ 转换过程中发生错误: {e}")
            return None
    
    def save_png_image(self, png_data: bytes, output_path: str) -> bool:
        """
        保存PNG图片到文件
        
        Args:
            png_data: PNG图片字节数据
            output_path: 输出文件路径
            
        Returns:
            保存是否成功
        """
        try:
            # 确保输出路径是绝对路径
            output_path = os.path.abspath(output_path)
            print(f"    正在保存到: {output_path}")
            
            # 创建目录（如果不存在）
            output_dir = os.path.dirname(output_path)
            if output_dir:  # 确保不是空字符串
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(png_data)
            
            print(f"    ✅ 图片已保存: {output_path}")
            return True
            
        except Exception as e:
            print(f"    ❌ 保存图片失败 {output_path}: {e}")
            return False
    
    def generate_output_filename(self, md_file_path: str, block_index: int, mermaid_code: str) -> str:
        """
        生成输出文件名
        
        Args:
            md_file_path: Markdown文件路径
            block_index: 代码块序号
            mermaid_code: Mermaid代码内容
            
        Returns:
            输出PNG文件路径
        """
        md_path = Path(md_file_path)
        
        # 获取输出目录
        if self.output_dir:
            output_dir = Path(self.output_dir)
            # 确保输出目录存在
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            # 在md文件同级目录下创建专门的图片文件夹
            base_name = md_path.stem
            images_folder_name = f"{base_name}_mermaid_images"
            output_dir = md_path.parent / images_folder_name
            print(f"    📁 图片将保存到文件夹: {output_dir}")
            # 确保图片目录存在
            output_dir.mkdir(parents=True, exist_ok=True)
              # 尝试从代码中提取图表类型
        chart_type = "diagram"
        code_lower = mermaid_code.lower()
        if "flowchart" in code_lower:
            chart_type = "flowchart"
        elif "graph" in code_lower:
            chart_type = "graph"
        elif "sequencediagram" in code_lower or "sequence" in code_lower:
            chart_type = "sequence"
        elif "gantt" in code_lower:
            chart_type = "gantt"
        elif "pie" in code_lower:
            chart_type = "pie"
        elif "journey" in code_lower:
            chart_type = "journey"
        elif "gitgraph" in code_lower:
            chart_type = "gitgraph"
        elif "classDiagram" in mermaid_code or "class" in code_lower:
            chart_type = "class"
        elif "stateDiagram" in mermaid_code or "state" in code_lower:
            chart_type = "state"
            
        # 生成文件名
        base_name = md_path.stem
        filename = f"{base_name}_{chart_type}_{block_index:02d}.png"
        
        return str(output_dir / filename)
    
    def process_markdown_file(self, md_file_path: str) -> int:
        """
        处理单个Markdown文件
        
        Args:
            md_file_path: Markdown文件路径
            
        Returns:
            成功转换的图片数量
        """
        print(f"\n📖 正在处理文件: {md_file_path}")
        
        try:
            # 读取Markdown文件
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取Mermaid代码块
            mermaid_blocks = self.extract_mermaid_blocks(content)
            
            if not mermaid_blocks:
                print("   📝 未找到Mermaid代码块")
                return 0
            
            print(f"   🎯 找到 {len(mermaid_blocks)} 个Mermaid代码块")
            
            successful_conversions = 0
            
            for block_index, (mermaid_code, original_index) in enumerate(mermaid_blocks, 1):
                print(f"\n   🔄 正在转换第 {block_index} 个图表...")
                print(f"      代码预览: {mermaid_code[:50]}...")
                
                # 转换为PNG
                png_data = self.convert_mermaid_to_png(mermaid_code)
                
                if png_data:
                    # 生成输出文件名
                    output_path = self.generate_output_filename(
                        md_file_path, original_index, mermaid_code
                    )
                    
                    # 保存图片
                    if self.save_png_image(png_data, output_path):
                        successful_conversions += 1
                    
                    # 添加延时避免API限制
                    time.sleep(1)
                else:
                    print(f"   ❌ 第 {block_index} 个图表转换失败")
            
            print(f"\n   ✨ 完成! 成功转换 {successful_conversions}/{len(mermaid_blocks)} 个图表")
            return successful_conversions
            
        except Exception as e:
            print(f"   ❌ 处理文件时发生错误: {e}")
            return 0
    
    def process_directory(self, directory: str) -> None:
        """
        处理目录下的所有Markdown文件
        
        Args:
            directory: 目录路径
        """
        print(f"🚀 开始扫描目录: {directory}")
        
        markdown_files = self.find_markdown_files(directory)
        
        if not markdown_files:
            print("❗ 未找到任何Markdown文件")
            return
        
        print(f"📋 找到 {len(markdown_files)} 个Markdown文件")
        
        total_conversions = 0
        
        for md_file in markdown_files:
            conversions = self.process_markdown_file(md_file)
            total_conversions += conversions
        
        print(f"\n🎉 处理完成! 总共转换了 {total_conversions} 个Mermaid图表")


def main():
    """主函数"""
    import argparse
    
    print("🚀 Mermaid to PNG 转换器启动... (无依赖版本)")
    print("📁 图片将保存在与.md文件同级的专门文件夹中")
    print("🌐 使用 Kroki.io API 进行转换")
    
    parser = argparse.ArgumentParser(
        description="从Markdown文件中提取Mermaid图表并转换为PNG图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python mermaid_converter_final.py                    # 处理当前目录
  python mermaid_converter_final.py -d /path/to/dir    # 处理指定目录
  python mermaid_converter_final.py -f file.md         # 处理单个文件
  python mermaid_converter_final.py -o output_dir      # 指定统一输出目录

特点:
  - 无需安装额外依赖，仅使用Python标准库
  - 自动在每个.md文件同级目录创建专门的图片文件夹
  - 支持中文Mermaid图表
  - 文件夹命名格式: {文件名}_mermaid_images
        """
    )
    
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='要处理的目录路径 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='要处理的单个Markdown文件'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='统一输出目录 (默认: 在每个.md文件同级目录创建专门文件夹)'
    )
    
    args = parser.parse_args()
    
    # 创建转换器
    converter = MermaidToPngConverter(output_dir=args.output)
    
    # 处理文件或目录
    if args.file:
        if os.path.exists(args.file):
            converter.process_markdown_file(args.file)
        else:
            print(f"❌ 文件不存在: {args.file}")
    else:
        if os.path.exists(args.directory):
            converter.process_directory(args.directory)
        else:
            print(f"❌ 目录不存在: {args.directory}")


if __name__ == "__main__":
    main()
