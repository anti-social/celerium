from celerium.app import app


if __name__ == '__main__':
    app.run(host=app.config['CELERIUM_SERVER_ADDRESS'],
            port=app.config['CELERIUM_SERVER_PORT'])
