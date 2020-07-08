from islandora_config import Islandora # Custom

class NewTool(Islandora):
    def get_solr_url(self):
        return self.solr_url

my_tool = NewTool()
my_tool.load_home_config('prod')
print(my_tool.get_solr_url())
