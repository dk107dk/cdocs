from configparser import SafeConfigParser

class Config:
    parser = SafeConfigParser()
    parser.read('config/config.ini')

    @classmethod
    def get( cls, group, name ) -> str:
        return cls.parser.get(group, name)


