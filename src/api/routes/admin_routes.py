from flask import Blueprint
from apiflask import APIBlueprint

from src.api.controllers.admin_controller import ScrapAnnonce,get_website_stats
from src.api.controllers.beytic_scrap import scrap_beytic_website
admin_bp = APIBlueprint("admin_bp",__name__)


@admin_bp.get('/')
def fetch():
    return scrap_beytic_website(10)
@admin_bp.get('/stats')
def getStats():
    return get_website_stats()