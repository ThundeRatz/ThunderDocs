from main import app

if __name__=="__main__":
    # If running locally, enable adhoc authentication
    app.run(ssl_context="adhoc")
    # app.run()
