# Make a new tool

Make a new directory, and link the islandora_config.py file

```
mkdir newtool
ln -s ../
ln -s ../islandora_config.py .
```

Create a new file and instantiate the Islandora class in it

``` Python
from islandora_config import Islandora # Custom

my_islandora = Islandora()
my_islandora.load_home_config('prod')
print(my_islandora.solr_url)
```

Or, better yet, use a subclass:

```
from islandora_config import Islandora # Custom

class NewTool(Islandora):
    def get_solr_url(self):
        return self.solr_url

my_tool = NewTool()
my_tool.load_home_config('prod')
print(my_tool.get_solr_url())
```

See the branch in this repo called "newtool" for a working example.
