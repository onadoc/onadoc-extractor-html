USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"

if __name__ == "__main__":
    import argparse
    import requests
    from bs4 import BeautifulSoup, PageElement
    from . import collectors
    import logging
            
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dump-raw', 
        action='store_true',
        help='dump the raw input HTML',
    )
    parser.add_argument(
        '--dump-local', 
        action='store_true',
        help='dump the structure of the document before processing',
    )
    parser.add_argument(
        '--dump-collected', 
        action='store_true',
        help='dump the structure of the document after processing',
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='maximum depth to dump',
    )
    parser.add_argument(
        '-u', '--url',
        help='load from this url',
    )
    parser.add_argument(
        '-f', '--file',
        help='load from this file',
    )
    parser.add_argument(
        '--test',
        help='load from test folder',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='print extra debugging information',
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='log in DEBUG mode',
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.test:
        import os
        args.file = os.path.join(
            os.path.dirname(__file__),
            "../tests/data",
            args.test,
        )

    if args.url:
        response = requests.get(args.url, headers={'User-Agent': USER_AGENT})
        response.raise_for_status()
        data = response.text
    elif args.file:
        with open(args.file, 'r') as file:
            data = file.read()
    else:
        parser.error('--url or --file required')

    if args.dump_raw:
        print(data)
    elif args.dump_local:
        soup = BeautifulSoup(data, "html.parser")
        collectors.dump_local(soup, max_depth=args.max_depth)
    elif args.dump_collected:
        soup = BeautifulSoup(data, "html.parser")
        collectors.dump_collected(soup, max_depth=args.max_depth)
    else:
        soup = BeautifulSoup(data, "html.parser")
        collectors.extract(soup, max_depth=args.max_depth, verbose=args.verbose)
