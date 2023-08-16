from epsilon_ecs import Manager, World
from logging import getLogger, Logger, basicConfig


class LoggingManager(Manager):
    loggers: dict[str, Logger] = dict()
    def init(self, world: World):
        basicConfig(level=logging.INFO, filename="engine.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(logger)s : %(message)s")
                    
    def after_init(self, world: World):
    	logger: Logger = self.new_logger("LoggingManager")
    	logger.info("LoggingManager started!")

    def new_logger(self, name: str) -> Logger:
        self.loggers[name] = getLogger(name)
        return self.loggers[name]

    def __getitem__(self, key: str) -> Logger:
        return self.loggers[key]

