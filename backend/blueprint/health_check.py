from flasgger.utils import swag_from
from flask import Blueprint, jsonify

bp = Blueprint('health', __name__, url_prefix='/health-check')

doc_directory = '../apidocs/healthcheck/'


@bp.route('', methods=['POST'])
@swag_from(doc_directory + 'healthcheck_api.yml')
def heath_check():
    # import and run celery functions here if you want to test
    # from tasks.job import check_for_expire
    # check_for_expire()
    return jsonify({
        'status': True
    })

