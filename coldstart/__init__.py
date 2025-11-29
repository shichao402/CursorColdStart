"""
CursorColdStart - 项目AI冷启动初始化系统

一个模块化的项目初始化脚手架系统，支持跨平台（Windows/Mac/Linux）
"""

__version__ = '1.0.0'
__author__ = 'CursorColdStart Team'

from .initializer import ProjectInitializer
from .commands import InteractiveCommandSystem
from .main import main

__all__ = ['ProjectInitializer', 'InteractiveCommandSystem', 'main']


