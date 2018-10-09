class ConfigException(Exception):
    def __init__(self, message):
        super(ConfigException, self).__init__(message)
