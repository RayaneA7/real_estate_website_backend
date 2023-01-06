import json
from flask import Blueprint
from src.api.controllers.annonce_controller import AddAnnonce,DeleteAnnonce, getAllAnnonces, getAnnonceDetails, SearchForAnnonce
from src.api.auth.auth import requires_auth


annonce_bp = Blueprint("annonce_bp", __name__)

@annonce_bp.route('/annonces')
@requires_auth
def get_annonces(user):
    print(user.toJson())
    return getAllAnnonces()

'''
ce route c'est pour avoir les details d'une annonce
'''


@annonce_bp.route('/<annonceId>')
def get_Annonce_Details(annonceId):
    return getAnnonceDetails(annonceId)

'''
route pour ajouter une annonce
'''
@annonce_bp.route('/',methods=['POST'])
@requires_auth
def Add_Annonce(user):
    return AddAnnonce(user)


'''
route pour supprimer une annonce
'''
@annonce_bp.route('/',methods=['DELETE'])
@requires_auth
def Delete_Annonce(user):
    return DeleteAnnonce(user)
'''
route pour chercher une annonce
'''
@annonce_bp.route('/')
def Search_Annonce():
    return SearchForAnnonce()
