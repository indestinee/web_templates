from index import *
from login import *

if __name__ == '__main__':
    app.run(host=web_cfg.host, port=web_cfg.port, debug=web_cfg.debug,\
            **web_cfg.app_params)
