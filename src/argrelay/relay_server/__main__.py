from argrelay.relay_server.CustomFlaskApp import create_app


def main():
    app = create_app()
    app.run_with_config()


if __name__ == '__main__':
    main()
