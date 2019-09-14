from web import app
from web_config import web_cfg
import routers

import autorun

if __name__ == '__main__':
    app.run(host=web_cfg.host,
            port=web_cfg.args.port,
            debug=web_cfg.args.debug,
            **web_cfg.app_params)

