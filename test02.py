import json
with open('links_data/single_malt_scotch_links.json', 'r') as f:
    data = json.load(f)

print(len(data))