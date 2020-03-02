import configparser
import logging
import os

class Islandora(object):
    def __init__(self):
        self.islandora_protocol = ''
        self.islandora_hostname = ''
        self.islandora_port = ''
        self.islandora_path = ''
        self.islandora_url = ''

        self.solr_protocol = ''
        self.solr_hostname = ''
        self.solr_port = ''
        self.solr_path = ''
        self.solr_url = ''

        self.fedora_protocol = ''
        self.fedora_hostname = ''
        self.fedora_port = ''
        self.fedora_path = ''

    def load_config_from(self, config_filename, section):
        try:
            config_data = configparser.ConfigParser()
            config_data.read_file(open(config_filename), source=config_filename)
        except FileNotFoundError:
            logging.error('No configuration file found. Configuration file %s required.' % config_filename)
            exit(1)
        try:
            myconfig = config_data[section]
        except KeyError:
            print("'%s' section not present in configuration file %s" % (section, config_filename))
            exit(1)

        try:
            self.islandora_protocol = myconfig['islandora_protocol']
            self.islandora_hostname = myconfig['islandora_hostname']
            self.islandora_port = myconfig['islandora_port']
            self.islandora_path = myconfig['islandora_path']
            self.islandora_url = f"{self.islandora_protocol}://{self.islandora_hostname}:{self.islandora_port}/{self.islandora_path}"

            self.solr_protocol = myconfig['solr_protocol']
            self.solr_hostname = myconfig['solr_hostname']
            self.solr_port = myconfig['solr_port']
            self.solr_path = myconfig['solr_path']
            self.solr_url = f"{self.solr_protocol}://{self.solr_hostname}:{self.solr_port}/{self.solr_path}"
        except KeyError as e:
            logging.error(f"Missing setting in {config_filename}: {e}")
            exit(1)

    def load_home_config(self, section):
        self.load_config_from(os.path.expanduser('~/') + '.islandora.cfg', section)
