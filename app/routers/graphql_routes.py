from flask import render_template_string, jsonify
from . import graphql_bp
from ..main import graphql_handler

@graphql_bp.route('/', methods=['POST'])
def graphql():
    return graphql_handler()

@graphql_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Job Tracker API is running'})

@graphql_bp.route('/playground')
def playground():
    """GraphQL Playground for testing queries"""
    playground_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GraphQL Playground</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.42/build/static/css/index.css" />
        <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.42/build/static/js/middleware.js"></script>
    </head>
    <body>
        <div id="root">
            <style>
                body {
                    background-color: rgb(23, 42, 69);
                    font-family: 'Open Sans', sans-serif;
                    height: 90vh;
                }
                #root {
                    height: 100%;
                    width: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .loading {
                    font-size: 32px;
                    font-weight: 200;
                    color: rgba(255, 255, 255, .6);
                    margin-left: 20px;
                }
                img {
                    width: 78px;
                    height: 78px;
                }
                .title {
                    font-weight: 400;
                }
            </style>
            <img src='https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.42/build/logo.png' alt=''>
            <div class="loading"> Loading
                <span class="title">GraphQL Playground</span>
            </div>
        </div>
        <script>window.addEventListener('load', function (event) {
            GraphQLPlayground.init(document.getElementById('root'), {
                endpoint: '/graphql'
            })
        })</script>
    </body>
    </html>
    """
    return playground_html 