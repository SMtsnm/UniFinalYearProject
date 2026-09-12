from webapp import create_app

app = create_app()

# runs the web application
if __name__ == "__main__":
    app.run(debug=True)
