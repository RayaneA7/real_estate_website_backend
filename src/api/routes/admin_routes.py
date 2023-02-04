from flask import Blueprint
from apiflask import APIBlueprint

from src.api.auth.auth import requires_auth
from src.api.controllers.admin_controller import ScrapAnnonce,get_website_stats,get_admin_annonces,scrap_beytic_website

admin_bp = APIBlueprint("admin_bp",__name__)


@admin_bp.get('/')
@requires_auth
def fetch(user):
    return ScrapAnnonce(user)
@admin_bp.get('/scrap')
def fill():
    return scrap_beytic_website(1)
@admin_bp.get('/stats')
@requires_auth
def getStats(user):
    return get_website_stats(user)
@admin_bp.get('/annonces')
@requires_auth
def getAdminAnnonces(user):
    return get_admin_annonces(user)