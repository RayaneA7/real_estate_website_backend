from flask import Blueprint
from src.api.controllers.beytic_scrap import scrap_beytic_website

admin_bp = Blueprint("admin_bp",__name__)


@admin_bp.get('/')
def fetch():
    return scrap_beytic_website(12)