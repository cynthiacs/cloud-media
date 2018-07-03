from flask import render_template, redirect, request, url_for, flash
from . import bp_test 
from .. import db


@bp_test.route('/test_js', methods=['GET', 'POST'])
def test_js():
    return render_template('test/test_js.html')

