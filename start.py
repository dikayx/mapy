import argparse

from mapy import app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ExifEx - Extract meta data from images")

    # General options
    parser.add_argument("-d", "--debug", action="store_true", default=False,
                        help="Enable debug mode")
    parser.add_argument("-b", "--bind", default="127.0.0.1", type=str,
                        help="Specify the bind address (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", default=8080, type=int,
                        help="Specify the port (default: 8080)")
    
    # SSL options
    parser.add_argument("-a", "--adhoc", action="store_true", default=False,
                        help="Enable SSL adhoc mode (for development only)")
    parser.add_argument("-c", "--cert", default=None, type=str, help="Specify the SSL certificate")
    parser.add_argument("-k", "--key", default=None, type=str, help="Specify the SSL key")

    args = parser.parse_args()
    ssl_context = 'adhoc' if args.adhoc else (args.cert, args.key) if args.cert and args.key else None

    web_app = app.create_app()
    web_app.run(debug=args.debug, host=args.bind, port=args.port, ssl_context=ssl_context)