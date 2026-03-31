# For local elasticsearch
After setting up your own localelastic search on your docker (https://github.com/elastic/start-local?tab=readme-ov-file#-try-elasticsearch-and-kibana-locally) do a pip install 
elasticsearch (or run pip install -r requirements.txt). Then alter the information like username and password which apply to you (DO NOT PUSH THOSE CONFIG CHANGES) then run
"python create_index.py" which creates the index on your local elastic search. Then run "python insert_data.py" which should insert the articles from articles_raw.json into your
index. 
