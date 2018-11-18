# coding=utf-8
from flask import Blueprint

policy_service = Blueprint("policy_service", __name__)

from . import views
