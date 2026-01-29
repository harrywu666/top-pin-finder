"""
工具函数模块
提供各种辅助功能
"""

import time
import random
from typing import Callable, Any
from functools import wraps


def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大尝试次数
        delay: 重试之间的延迟（秒）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        print(f"第 {attempt} 次尝试失败: {e}, {delay}秒后重试...")
                        time.sleep(delay)
                    else:
                        print(f"重试 {max_attempts} 次后仍然失败")
            
            raise last_exception
        
        return wrapper
    return decorator


def format_number(number: int) -> str:
    """
    格式化数字，添加千位分隔符
    
    Args:
        number: 数字
    
    Returns:
        格式化后的字符串
    """
    return f"{number:,}"


def format_time(seconds: float) -> str:
    """
    格式化时间，转换为可读格式
    
    Args:
        seconds: 秒数
    
    Returns:
        格式化后的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def estimate_remaining_time(completed: int, total: int, elapsed: float) -> str:
    """
    估算剩余时间
    
    Args:
        completed: 已完成数量
        total: 总数量
        elapsed: 已用时间（秒）
    
    Returns:
        剩余时间字符串
    """
    if completed == 0:
        return "计算中..."
    
    rate = completed / elapsed  # 每秒完成数量
    remaining = total - completed
    remaining_seconds = remaining / rate if rate > 0 else 0
    
    return format_time(remaining_seconds)


def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """
    随机延迟，用于模拟人类行为
    
    Args:
        min_seconds: 最小延迟（秒）
        max_seconds: 最大延迟（秒）
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    截断字符串
    
    Args:
        text: 原始字符串
        max_length: 最大长度
    
    Returns:
        截断后的字符串
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


if __name__ == "__main__":
    # 测试工具函数
    
    # 测试重试装饰器
    @retry(max_attempts=3, delay=0.5)
    def unstable_function():
        import random
        if random.random() < 0.7:
            raise Exception("随机失败")
        return "成功"
    
    try:
        result = unstable_function()
        print(f"结果: {result}")
    except Exception as e:
        print(f"最终失败: {e}")
    
    # 测试其他函数
    print(f"\n格式化数字: {format_number(1234567)}")
    print(f"格式化时间: {format_time(3725)}")
    print(f"估算剩余时间: {estimate_remaining_time(30, 100, 60)}")
    print(f"截断字符串: {truncate_string('这是一个非常非常非常长的字符串', 20)}")
