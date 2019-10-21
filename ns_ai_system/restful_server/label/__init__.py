# coding=utf-8
"""
标签管理相关接口
"""
from flask import Blueprint

label_service = Blueprint("label_service", __name__)

from . import views
