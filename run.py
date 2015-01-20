# -*- coding: utf-8 -*-

import config
from gris import app

def run():
    app.run(config.HOST, config.PORT)

if __name__ == "__main__":
    run()
